# Core module

from migmig import configuration
from migmig import utils
from migmig import downloader
from migmig import log
from socket import error as sockerr

from threading import Event
import sys
import xmlrpclib


class Core():

	def __init__(self, arguments):

		# arguments is a {dic} object of all options and commands from sys.argv
		command, args, options = utils.parse_doc_arguments(arguments)

		self.log_constructor = log.logger()
		self.logger = self.log_constructor.get_logger(__name__)
		self.logger.debug('initiate the core...')
		self.config = configuration.Configuration(self.log_constructor, options)

		self.event = Event()

		# register commands in command_pool !
		self.commands = {
			'get': self.command_get,
			'status': self.command_status,
			'merge': self.command_merge,
			'release': self.command_release,
			# I have no idea what this update command supposed to be :D
			'update': self.command_update
		}
		
		# initiate xml proxy server. It doesnt raise exception if server is unavailavle !
		self.proxy = xmlrpclib.ServerProxy(self.config.get_server(), allow_none = True)

		self.start(command, args, options)

	
	def start(self, command, args, options):
		# do more stuff !
		# 1 - check args validity (because docops cant do this ofcourse)
		# 2 - log this command! with specific time and date


		if command in self.commands.keys():		# no need to check, but anyway...
			# run the command
			self.commands[command](args, options)



	def command_get(self, args, options):
		#
		# 1- send identifier and options to server (RPC) (server would save client informations)
		# 		and get {HASH} as new identifier and {client_id} from server (save them)
		#		replace the old identifier by new identifier !
		identifier = args['<identifier>']
		client_id = self.config.get('client_id')
		wanted_keys = ['chunk-size', 'number-of-clients']		# maybe later i'll add more options
		relevant_options = dict([ (key, options[key]) for key in wanted_keys])

		try:
			# proxy.new() returns a dict object
			download_info = self.proxy.new(identifier, client_id, relevant_options)
			print download_info

		except xmlrpclib.ProtocolError as err:
			# TO-DO : log ProtocolErrors !
			print "Error code: %d" % err.errcode
			print "URL: %s" % err.url
			sys.exit(0)
		except xmlrpclib.Fault as fault:
			# TO-DO : log ProtocolErrors !
			print fault
			sys.exit(0)
		except sockerr:
			# TO-DO: Log connection refuse (or maybe something else !)
			print '[+] something is wrong with socket: %s' % self.config.get_server()
			sys.exit(0)


		# 2- check for this identifier in config file, if there is a identifier like this
		# 		it means download is running on another terminal ! or maybe something is wrong !?
		if download_info['status'] == self.config.RESUME_NOT_SUPPORTED:
			# The given URL cant be spilited into chunks !
			# TO-DO: log
			print 'resume not supported ...'
			sys.exit(0)

		elif download_info['status'] != self.config.OK:
			# meaning server got a problem with this url !
			# TO-DO: log
			print '[+] download info failed.'
			sys.exit(0)


		if self.config.get('identifier') == download_info['identifier']:
			# if there is another terminal that is downloading the <identifier>
			#  exit normally with showing a message !!
			# TO-DO: log
			print '[+] Download is already running ...'
			# sys.exit(0)

		# if everything is fine, save the new info !
		print self.config.set(
			identifier = download_info['identifier'],
			client_id=download_info['client_id'],
			url = download_info['URL']
			)

		if not self.config.get('daemon'):
			# 4- Run a thread for prog_bar if its neccessary !
			# if daemon is True, dont show progress bar
			# TO-DO : start the program in daemon mode
			# this feature is not gonna work in 0.1 version !!
			pass


		# 5- IN A WHILE LOOP
		#		start getting http range from server (chunk)
		#		run threads to download that chunk
		#		sleep until chunk download completes !
		#		wake on event.set()
		while True:
			'''
			fetch_restult:
				status
				start_byte
				chunk_size
				chunk_num
				file_name
			'''

			try:
				fetch_restult = self.proxy.fetch(
					self.config.get('identifier'),
					self.config.get('client_id'),
					self.config.get('latest_chunk')
					)
			except:
				print '[+] Cant fetch from server %s', self.config.get_server()
				sys.exit(0)

			if fetch_restult['status'] == self.config.DONE:
				# download is done . you can merge it later !
				# TO-DO: log.
				print 'Download is Done !'
				break

			elif fetch_restult['status'] == self.config.SOMETHING:
				break

			elif fetch_restult['status'] == self.config.OK:
				# create a new Download object
				# download the given chunk
				# save it on disk
				# save the last_chunk in config
				# distroy the object
				# and try again (for new chunk)
				download = downloader.Download( self.config,
												self.log_constructor,
												self.event,
												fetch_restult['start_byte'],
												fetch_restult['chunk_size'],
												fetch_restult['file_name']
												)

				# sleep
				# wake on event
				self.event.wait()
				self.event.clear()

		#
		# 6- do the termination stuff !
		#	for example : delete all the clients stuff in .ini file.
		# 
		

	def command_status(self, args, options):
		print args
		print
		print options

	def command_merge(self, args, options):
		pass

	def command_release(self, args, options):
		pass

	def command_update(self, args, options):
		pass

