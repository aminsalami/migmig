# migmig logger module

import logging
import sys

console = True
class logger():
	def __init__(self):
		logging.basicConfig(level=logging.DEBUG, filename='test/mylog.txt', format='%(name)s \t%(message)s')
		self.handlers = []
		if console:
			self.handlers.append(logging.StreamHandler(sys.stdout))



	def get_logger(self, mod_name):
		return logging.getLogger(mod_name)

	def h(self):
		self.root_logger.addHandler(self.handlers[0])

