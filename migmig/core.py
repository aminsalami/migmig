# Core module

from migmig import configuration
from migmig import utils
from migmig import downloader
from migmig import log
from socket import error as sockerr

from threading import Event
import sys
import xmlrpclib
from traceback import format_exc

# TO-DO: add "ctrl+c" handler to handle the un normal exiting.

class Core:
    def __init__(self, arguments):

        # arguments is a {dic} object of all options and commands from sys.argv
        command, args, options = utils.parse_doc_arguments(arguments)

        self.log_constructor = log.logger(options['verbose'], options['console'])
        self.logger = self.log_constructor.get_logger(__name__)

        self.logger.info('Initate the core.')
        self.logger.debug('Requsted command is: %s\tOptions are: %s\targuments are:%s' % (command, options, args))

        try:
            self.config = configuration.Configuration(self.log_constructor, options)
        except OSError:
            self.logger.error('config initiation failed.')
            self.terminate()

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
        self.logger.info('Making a XML-RPC server proxy (%s)' % self.config.get_server())
        self.proxy = xmlrpclib.ServerProxy(self.config.get_server(), allow_none=True)

        self.start(command, args, options)

    def start(self, command, args, options):
        # do more stuff !
        # 1 - check args validity (because docops cant do this ofcourse)
        # 2 - log this command! with specific time and date
        if command in self.commands.keys():  # no need to check, but anyway...
            # run the command
            self.commands[command](args, options)

    def command_get(self, args, options):
        #
        # send identifier and options to server (RPC) (server would save client info)
        # and get {HASH} as new identifier and {client_id} from server (save them)
        # replace the old identifier by new identifier !
        identifier = args['<identifier>']
        client_id = self.config.get('client_id')
        wanted_keys = ['chunk-size', 'number-of-clients']  # maybe later i'll add more options
        relevant_options = dict([(key, options[key]) for key in wanted_keys])

        try:
            self.logger.info(
                'First request. register this client on server by:\tidentifier: %s\tclient id:%s\toptions:%s' % (
                    identifier, client_id, relevant_options))

            download_info = self.proxy.new(identifier, client_id, relevant_options)

            self.logger.debug('Proxy answer to the register request:\n%s' % str(download_info))

        except xmlrpclib.ProtocolError as err:
            # TO-DO : log ProtocolErrors !
            self.logger.critical('PROTOCOL ERROR. error code: %s' % err.errcode)
            self.logger.critical(format_exc().split('\n')[-2])
            self.terminate()
        except xmlrpclib.Fault as fault:
            # TO-DO : log ProtocolErrors !
            self.logger.error(format_exc().split('\n')[-2])
            self.terminate()
        except sockerr:
            # print '[+] something is wrong with socket: %s' % self.config.get_server()
            # self.logger.exception(sockerr)
            self.logger.error(format_exc().split('\n')[-2])
            self.terminate()

        if self.config.BAD_IDENTIFIER == download_info['status']:
            self.logger.error('You entered a bad hash string.')
            self.terminate()

        if self.config.get('identifier') == download_info['identifier']:
            # if there is another console that is downloading the <identifier>, exit normally.
            self.logger.info('Another migmig client with the same URI/HASH is running on this system.')
            self.terminate()

        if self.config.RANGE_NOT_SUPPORTED == download_info['status']:
            # The given URL cant be spilited into chunks !
            self.logger.error('RANGE NOT SUPPORTED. The given URI doesn\'t accept HTTP requests with range bytes.')
            self.terminate()

        elif self.config.OK != download_info['status']:
            self.logger.error('Server cannot handle the given URI.')
            self.terminate()
        # if everything is fine, save the new info !
        self.config.set(
            identifier=download_info['identifier'],
            client_id=download_info['client_id'],
            url=download_info['url']
        )

        if not self.config.get('daemon'):
            # Run a thread for prog_bar if its neccessary !
            # if daemon is True, dont show progress bar
            # TO-DO : start the program in daemon mode
            # this feature is not gonna work in this version !!
            pass

        while True:
            '''
            fetch_result:
                status
                start_byte
                chunk_size
                chunk_num
                chunk_name
            '''
            try:
                self.logger.info('Fetching download information from server.')
                fetch_result = self.proxy.fetch(
                    self.config.get('identifier'),
                    self.config.get('client_id'),
                    self.config.get('latest_chunk')
                )
            except:
                self.logger.error('Can not fetch download information.')
                self.logger.error(format_exc().split('\n')[-2])
                self.terminate()

            if fetch_result['status'] == self.config.DONE:
                self.logger.info('All chunks have been downloaded successfully.')
                break

            elif fetch_result['status'] == self.config.SOMETHING:
                break

            elif fetch_result['status'] == self.config.OK:
                # create a new Download object
                # download the given chunk
                # save it on disk
                # save the last_chunk in config
                # distroy the object
                # and try again (for new chunk)
                self.logger.info('Is going to download the chunk number "%d"' % int(fetch_result['chunk_num']))
                download = downloader.Download(self.config,
                                               self.log_constructor,
                                               self.event,
                                               fetch_result['start_byte'],
                                               fetch_result['end_byte'],
                                               fetch_result['chunk_size'],
                                               fetch_result['chunk_name']
                                               )
                download.run()

                # sleep
                # wake on event
                self.event.wait()
                self.event.clear()
                self.config.set(latest_chunk=fetch_result['chunk_num'])
        #
        # 6- do the termination stuff !
        # for example : delete all the clients stuff in .ini file.
        #
        self.terminate()

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

    def terminate(self, terminate_status=None):
        # delete client stuff from config file

        self.logger.debug('Resetting client settings.')
        self.config.reset_client()

        self.logger.info('Terminating normally ...')
        sys.exit(0)
