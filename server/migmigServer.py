# First version of Migmi server 

from twisted.internet import reactor, defer
from twisted.web import xmlrpc, server

from twisted.internet import protocol
import constants as setting

import chunky
import urlparse, urllib
import os, sys
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
		if ('.' in identifier) or ('/' in identifier):
			# Identifier's type is URL.
			url = self.amend_url(identifier)
			hash = self.generate_hash(url)

			if hash in self.hash_pool:
				# It means the given URL is already exists in server
				chunky_obj = self.hash_pool[hash]
			else:
				# create new client_id
				print 'old client_id: ', client_id
				client_id = self.generate_hash(os.urandom(16))
				# create new chunky object and initate it
				chunky_obj = chunky.Chunky(hash, url, client_id, options)
				self.hash_pool[hash] = chunky_obj
		else:
			url = None
			hash = self.complete_hash(identifier)
			if not hash:
				# the given identifier neither is URL nor a correct HASH.
				return {'status':setting.BAD_IDENTIFIER}
			chunky_obj = self.hash_pool[hash]

		# chunky_obj.
		# 				1. fetch the url header (make sure to use the defer for non-blocking)
		#				2. determine the status, file_name, content_len
		#				3. send these informations to client ( NOTE: whoever creates a defer, he should fire it !)
		return chunky_obj.new(client_id)

			


	def amend_url(self, url, charset = 'utf-8'):
		'''
		This method, changes the given url to a standard URL.
		for example, given url is "www.example.com/file.zip"
		and the complete url should be : "http://www.example.com/file.zip"

		Following the syntax specifications in RFC 1808, urlparse recognizes 
		a netloc only if it is properly introduced by "//". Otherwise the input 
		is presumed to be a relative URL and thus to start with a path component.
		'''

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

		url = urlparse.urlunsplit( (scheme, netloc, path, qs, anchor) )

		return url


	def generate_hash(self, string):
		'''
		Generate md5 hash string.
		'''
		m = hashlib.md5()
		m.update(string)
		return m.hexdigest()


	def complete_hash(self, hash):
		'''
		Users can give part of a hash string, so server 
		have to find the complete hash string if there is any.
		'''
		if len(hash) >= 32:		# md5 hash len is 32
			return hash

		if len(hash) < self.hash_completion:
			return None

		for each_hash in self.hash_pool:
			if each_hash.startswith(hash):
				return each_hash

		return None




reactor.listenTCP(50001, server.Site(MigmigServer()))

print 'Running the reactor ...'
reactor.run()