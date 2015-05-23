from twisted.internet import reactor, defer
from twisted.web import xmlrpc, server

from twisted.internet import protocol
import constants as setting

import chunky
import urlparse
import urllib
import os
import sys
import hashlib


class MigmigServer(xmlrpc.XMLRPC):
    def __init__(self):
        xmlrpc.XMLRPC.__init__(self)

        # key in hash_pool is HASH string and value is object refrence.
        self.hash_pool = {}
        self.hash_completion = 6

    def xmlrpc_new(self, identifier, client_id, options):
        # check the identifier: if exist in server's pool, so extract the relavant object
        # if doesnt exist, make a new object of chunky
        if not client_id:
            client_id = self.generate_hash(os.urandom(16))

        if ('.' in identifier) or ('/' in identifier):
            # Identifier's type is URL.
            url = self.amend_url(identifier)
            HASH = self.generate_hash(url)

            if HASH in self.hash_pool:
                # It means the given URL is already exists in server
                chunky_obj = self.hash_pool[HASH]
                # register the client_id
                chunky_obj.register(client_id)
            else:
                # create new chunky object and initate it
                chunky_obj = chunky.Chunky(HASH, url, client_id, options)
                self.hash_pool[HASH] = chunky_obj
        else:
            url = None
            HASH = self.complete_hash(identifier)
            if not HASH:
                # the given identifier neither is URL nor a correct HASH.
                return {'status': setting.BAD_IDENTIFIER}
            chunky_obj = self.hash_pool[HASH]
            chunky_obj.register(client_id)

        # chunky_obj.
        # 1. fetch the url header (make sure to use the defer for non-blocking)
        # 2. determine the status, file_name, content_len
        # 3. send these information to client ( NOTE: whoever creates a defer, he should fire it !)
        return chunky_obj.new(client_id)

    def xmlrpc_fetch(self, identifier, client_id, latest_chunk):
        """
        :return: dict
        """
        if identifier in self.hash_pool:  # this statement must be True all the times.
            chunky_obj = self.hash_pool[identifier]
            return chunky_obj.fetch(client_id, latest_chunk)
        # else: return ERROR

    def xmlrpc_terminating(self, identifier, client_id):
        """
         A client is going to be terminated. if there is no chunk to be downloaded, the identifier and its
         object should be cleaned.
        :return: boolean
        """
        if identifier in self.hash_pool:
            chunky_obj = self.hash_pool[identifier]
            if chunky_obj.is_cleaned():
                del self.hash_pool[identifier]
            return True
        return False

    def amend_url(self, url, charset='utf-8'):
        """
        This method, changes the given url to a standard URL.
        for example, given url is "www.example.com/file.zip"
        and the complete url should be : "http://www.example.com/file.zip"

        Following the syntax specifications in RFC 1808, urlparse recognizes
        a netloc only if it is properly introduced by "//". Otherwise the input
        is presumed to be a relative URL and thus to start with a path component.
        :return: str
        """

        '''
        Sometimes you get an URL by a user that just isn't a real
        URL because it contains unsafe characters like ' ' and so on. This
        function can fix some of the problems in a similar way browsers
        handle data entered by the user:
        >>> url_fix(u'http://de.wikipedia.org/wiki/Elf (Begriffsklarung)')
        'http://de.wikipedia.org/wiki/Elf%20%28Begriffskl%C3%A4rung%29'
        :param s: Url address.
        :type s: string
        :param charset: The target charset for the URL if the url was
        given as unicode string. Default is 'utf-8'.
        :type charset: string
        :rtype: string
        (taken from 'werkzeug.utils <http://werkzeug.pocoo.org/docs/utils/>'_)
        '''
        if not url.startswith('http'):
            # default protocol is 'HTTP'
            url = 'http://' + url

        if sys.version_info < (3, 0) and isinstance(url, unicode):
            url = url.encode(charset, 'ignore')
        scheme, netloc, path, qs, anchor = urlparse.urlsplit(url)
        netloc = netloc.lower()
        path = urllib.quote(path, '/%')
        qs = urllib.quote_plus(qs, ':&=')

        url = urlparse.urlunsplit((scheme, netloc, path, qs, anchor))

        return url

    def generate_hash(self, string):
        """
        Generate md5 hash string.
        """
        m = hashlib.md5()
        m.update(string)
        return m.hexdigest()

    def complete_hash(self, HASH):
        """
        Users can give part of a hash string, so server
        have to find the complete hash string if there is any.
        """
        if len(HASH) >= 32:  # md5 hash len is 32
            return HASH

        if len(HASH) < self.hash_completion:
            return None

        for each_hash in self.hash_pool:
            if each_hash.startswith(HASH):
                return each_hash

        return None


reactor.listenTCP(50001, server.Site(MigmigServer()))

print 'Running the reactor ...'
reactor.run()
