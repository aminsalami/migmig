# Configuration module

#
## tmp note: you should add logger module and modify this module
#

from ConfigParser import SafeConfigParser
import os


program_name = "migmig"
# config file short path (hard coded !)
cfg_short_path = "~/." + program_name + ".ini"
server_address = "localhost"
server_port = "50001"


class Configuration():

	def __init__(self, logger):
		# constant variables
		self.OK = 99
		self.BAD_URL = 98
		self.BLAHBLAH = 97


		self.logger = logger
		self.parser = SafeConfigParser()
		self.cfg_path = self.validate_path(cfg_short_path)

		if not self.cfg_path:
			# create config file and initate configurations
			self.cfg_path = os.path.expanduser(cfg_short_path)
			self.initate()

		self.parser.read(self.cfg_path)

		self.check_download_path()


	def initate(self):
		# Sections
		self.parser.add_section("Setting")
		self.parser.add_section("Client")

		# Options
		self.parser.set("Setting", "download_path", os.path.expanduser("~/Downloads/" + program_name))
		self.parser.set("Setting", "default_merge_path", os.path.expanduser("~/Downloads/" + program_name + "/merged"))
		self.parser.set("Setting", "max_connections", "6")
		self.parser.set("Setting", "number_of_tries", "3")
		self.parser.set("Setting", "verbose_level", "1")

		self.parser.set('Setting', 'server_address', server_address)
		self.parser.set('Setting', 'server_port', server_port)

		self.parser.set('Client', 'identifier', 'None')
		self.parser.set('Client', 'URL', 'None')
		self.parser.set('Client', 'client_id', 'None')

		# write settings to ini file
		self.write()



	def get(self, name):
		'''
			This method looks for given name in all secion,
			it returns the first value that is matched.
		'''
		for section in self.parser.sections():
			for item, val in self.parser.items(section):
				if name == item:
					return val
		return None

		# try:
		# 	return self.parser.get('Client', value)
		# except:
		# 	return None

	def set(self, **kwargs):
		'''
			Like get method, this only works for "Client" section.
		'''
		try:
			for key, value in kwargs.items():
				self.parser.set('Client', key, value)

			self.write()
			return True
		except:
			# log the python error. how?
			return False

	def write(self):
		'''
			Write (synchronize) the parser object to .ini file !
		'''
		# TO-DO : ...
		with open(self.cfg_path, "wb") as tmp:
				self.parser.write(tmp)

	def get_server(self):
		addr = self.parser.get('Setting','server_address')
		port = self.parser.get('Setting','server_port')
		return "http://" + addr + ':' + port
		


	def check_download_path(self):
		'''
			If download_path does not exist, create !
		'''
		d_path = self.parser.get('Setting', 'download_path')
		if not os.path.exists(d_path):
			try:
				os.makedirs(d_path)
			except:
				# TO-D0: log
				# maybe permission denied ?
				print 'path cant be created !'
				return False
		return True

	
	def validate_path(self, path):
		'''
			Check whether path exists or not
		'''
		path = os.path.expanduser(path)
		if os.path.exists(path):
			return path
		return None
