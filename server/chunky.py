
from twisted.internet import defer
import urllib2

import constants as setting


class Chunky():
	def __init__(self, hash, url, first_client_id, user_preferences = None):

		self.clients = []

		self.HASH = hash
		self.URL = url
		self.file_name = None
		self.clients.append(first_client_id)
		self.user_preferences = user_preferences

		self.content_len = None
		self.content_type = None
		self.accept_ranges = None
		self.chunk_size = 0
		self.status = setting.UNKNOWN

		# Requst for URL (make sure url is valid)
		# Get headers of the URL
		# Calculate appropriate chunk-size
		# Generate {status}

		## BLOCKING
		self.get_headers()
		## BLOCKING


	def add_client(self, cl):
		self.clients.append(cl)


	def new(self, client_id):
		'''
			Return a dictionary containing URL status and len and other informations.
				return : {status, identifier, URL, file_name, client_id, content_len}
		'''
		if self.status == setting.UNKNOWN:
			if (not self.accept_ranges) or (self.accept_ranges != 'bytes'):
				self.status = setting.RANGE_NOT_SUPPORTED
			elif not self.content_len:
				self.status = setting.UNKNOWN_HEADER
			else:
				self.status = setting.OK

		result = {
			'status': self.status,
			'identifier': self.HASH,
			'url': self.URL,
			'client_id': client_id,
			'file_name': self.file_name,
			'content_len': self.content_len
		}
		print '+', result
		return result


	def fetch(self):
		pass




	def get_headers(self):
		'''
			Apparantly twisted dont have any SIMPLE method equivalent to urlopen !
			I wrote this method 'BLOCKING'. i shouldnt do this, but who cares ? :D
		'''
		try:
			url_obj = urllib2.urlopen(self.URL)

			self.content_type = url_obj.info().getheader('content-type')
			self.content_len = url_obj.info().getheader('content-length')
			self.accept_ranges = url_obj.info().getheader('accept-ranges')
			self.file_name = self.extract_file_name(url_obj.info().getheader('content-disposition'))

			return url_obj

		except urllib2.HTTPError, e:
			if e.code == 404:
				# BAD URL, file not fount
				self.status = setting.NOT_FOUND

	def extract_file_name(self, disposition = None):
		'''
		Extract file name. it can be done by extracting 'content-disposition' in 
		HTTP header, or using URL.
		'''
		# TO-D0: what about urls that redirect the requester ?
		if disposition:
			return disposition

		base_name = self.URL.split('/')[-1]
		if '?' in base_name:
			base_name = base_name.split('?')[0]
		return base_name

		
