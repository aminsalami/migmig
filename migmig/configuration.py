# Configuration module
#
## tmp note: you should add logger module and modify this module
#

from ConfigParser import RawConfigParser
import os
from traceback import format_exc

program_name = "migmig"
# config file short path (hard coded !)
cfg_short_path = "~/." + program_name + ".ini"
server_address = "localhost"
server_port = "50001"


class Configuration:
    def __init__(self, logger, user_options):
        # constant variables
        self.OK = '200'
        self.DONE = '199'
        self.BAD_URL = '98'
        self.BAD_IDENTIFIER = '97'
        self.NOT_FOUND = '404'
        self.RANGE_NOT_SUPPORTED = '198'
        self.SOMETHING = '197'

        self.logger = logger.get_logger()
        self.user_options = user_options
        self.parser = RawConfigParser()
        self.cfg_path = self.validate_path(cfg_short_path)

        if not self.cfg_path:
            # create config file and initiate configurations
            self.cfg_path = self.validate_path(cfg_short_path)
            self.logger.info('Configuration path doesnt exist, creating new one in %s', self.cfg_path)
            self.initate()

        self.logger.info('Initiating Safe Config Parser. ')
        self.parser.read(self.cfg_path)

        self.check_download_path()

    def initate(self):
        # Sections
        self.parser.add_section("Setting")
        self.parser.add_section("Client")

        # Options
        self.reset_setting()

    # write settings to ini file
    # self.write()			# no need for this line

    def get(self, name):
        """
            This method looks for given name in all sections,
            returns the first value that is matched.

            User's options priority is higher, so if an option
            is specified by user, that option returns.
        """
        self.logger.debug('Getting %s from config parser.' % name)
        try:
            if name in self.user_options:
                val = self.user_options[name]
                if val:
                    return val

            for section in self.parser.sections():
                for item, val in self.parser.items(section):
                    if name == item:
                        return val
        except:
            # TO-DO: Log, maybe this option doesn not exist at all!
            self.logger.warning('%s doesn\'t exist in config file.' % name)
            return None

    def set(self, section=None, **kwargs):
        """
        Default section to write in is "client".
        :return: boolean
        """
        self.logger.debug('Writing options to config file. options are: (%s)' % str(kwargs))
        if not section:
            section = 'Client'
        try:
            for key, value in kwargs.items():
                value = str(value)
                self.parser.set(section, key, value)

            self.write()
            return True
        except:
            self.logger.error(format_exc().split('\n')[-2])
            self.logger.error('Cannot set (or write) the key, value.')
            return False


    def write(self):
        """
            Write (synchronize) the parser object to .ini file !
        """
        with open(self.cfg_path, "wb") as tmp:
            self.parser.write(tmp)

    def get_server(self):
        addr = self.parser.get('Setting', 'server_address')
        port = self.parser.get('Setting', 'server_port')
        return "http://" + addr + ':' + port

    def check_download_path(self):
        """
            If download_path does not exist, create !
        """
        d_path = self.get('download_path')
        if not self.validate_path(d_path):
            self.logger.info('download path (%s) doesnt exist, creating the path.' % d_path)
            try:
                os.makedirs(d_path)
            except:
                # maybe permission denied ?
                self.logger.critical('(%s) cannot be created.' % d_path)
                raise
        return True

    def validate_path(self, path, is_directory=None):
        """
            Check whether path exists or not
        """
        path = os.path.expanduser(path)
        if os.path.exists(path):
            if is_directory and path[-1] != '/':
                path += '/'
            return path
        return None

    def reset_client(self):
        # removes all the options in "Client" section
        self.parser.remove_section('Client')
        self.parser.add_section('Client')
        self.write()

    def reset_setting(self):
        self.parser.set("Setting", "download_path", os.path.expanduser("~/Downloads/" + program_name))
        self.parser.set("Setting", "merge_path", os.path.expanduser("~/Downloads/" + program_name + "/merged"))
        self.parser.set("Setting", "max-conn", "6")
        self.parser.set("Setting", "retries", "3")
        self.parser.set("Setting", "number-of-clients", '1')

        self.parser.set('Setting', 'server_address', server_address)
        self.parser.set('Setting', 'server_port', server_port)
        # update the file
        self.write()

    def create_info(self):
        """

        :return:
        """
        download_path = self.validate_path(self.get('download_path'), True)
        if not download_path:
            return None

        tmp_parser = RawConfigParser()
        tmp_parser.add_section('info')
        tmp_parser.set('info', 'file_name', self.get('file_name'))
        tmp_parser.set('info', 'content_len', self.get('content_len'))
        tmp_parser.set('info', 'total_chunks', self.get('total_chunks'))

        with open(download_path + 'merge.info', 'wb') as f:
            tmp_parser.write(f)
