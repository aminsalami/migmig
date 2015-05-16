# migmig logger module

import logging
import sys

class logger():
	def __init__(self, verbose, console = None):
		'''
		Python doc :
			https://docs.python.org/2/library/logging.html#logrecord-attributes

			Levels:
				0: NOTSET - 0
				1: DEBUG - 10
				2: INFO - 20
				3: WARNING - 30
				4: ERROR - 40
				5: CRITICAL - 50
		'''
		levels = {
					0: logging.WARNING,
					1: logging.INFO,
					2: logging.DEBUG
				 }
		if verbose in levels:
			# Note: if user doesnt specify the verbose level, default will be zero (0:Warning)
			level = levels[verbose]
		else:
			# user wants the maximus log level
			level = levels[2]

		
		FORMAT = '%(levelname).30s:%(name).30s %(asctime)s \t[%(message)s]'
		DATEFORMAT = '%m/%d/%Y %I:%M %p'
		LOG_PATH = 'test/migmig.log'

		logging.basicConfig(level=level, filename=LOG_PATH, format=FORMAT, datefmt = DATEFORMAT)
		self.root_logger = logging.getLogger()

		if console:
			'''
				User wants logs on his console
			'''
			self.console_handler()




	def get_logger(self, logger_name = None):
		return logging.getLogger(logger_name)


	def console_handler(self):
		hdlr = logging.StreamHandler(sys.stdout)

		# the logging format of console
		FORMAT = '%(module)s:   [%(message)s]'

		fo = logging.Formatter(FORMAT)
		hdlr.setFormatter(fo)
		self.root_logger.addHandler(hdlr)

