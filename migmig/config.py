# Configuration module

#
## tmp note: you should add logger module and modify this module
#

from ConfigParser import SafeConfigParser
import os


program_name = "migmig"
# config file short path (hard coded !)
cfg_short_path = "~/." + program_name + ".cfg"


class Config():

	def __init__(self, logger):
		self.logger = logger
		self.parser = SafeConfigParser()
		self.cfg_path = self.validate_path(cfg_short_path)

		if not self.cfg_path:
			# create config file and initate configurations
			self.cfg_path = os.path.expanduser(cfg_short_path)
			self.initate()

		self.parser.read(self.cfg_path)


	def initate(self):
		# Sections
		self.parser.add_section("Setting")
		self.parser.add_section("Client")

		# Options
		self.parser.set("Setting", "default_download_path", os.path.expanduser("~/Downloads/" + program_name))
		self.parser.set("Setting", "default_merge_path", os.path.expanduser("~/Downloads/" + program_name + "/merged"))
		self.parser.set("Setting", "max_connections", "6")
		self.parser.set("Setting", "number_of_tries", "3")
		self.parser.set("Setting", "verbose_level", "1")

		# write settings to cfg file
		with open(self.cfg_path, "wb") as tmp:
				self.parser.write(tmp)


	def insert_id(self):
		pass


	def default_download_path(self, new_path):
		new_path = self.validate_path(new_path)
		if not new_path:
			self.parser.set("Setting", "default_download_path", new_path)

	
	def validate_path(self, path):
		'''
			Check whether path exists or not
		'''
		path = os.path.expanduser(path)
		if os.path.exists(path):
			return path
		return None
