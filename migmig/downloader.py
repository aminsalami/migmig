# Download module

from concurrent import futures
from migmig import utils

import urllib2
import time
import os



class ManagedThreadPoolExecutor(futures.ThreadPoolExecutor):
    '''
    '''
    def __init__(self, max_workers):
        futures.ThreadPoolExecutor.__init__(self, max_workers)
        self._futures = []


    def submit(self, fn, *args, **kwargs):
        future = super(ManagedThreadPoolExecutor, self).submit(fn, *args, **kwargs)
        self._futures.append(future)

        return future


    def done(self):
        '''
            This method returns True if all the future objects
            successfully cancelled or finished running.
        '''
        # all() returns true if all of the elemnts of itarable object is true.
        return all([x.done() for x in self._futures])
    

    def get_exceptions(self):
        l = []
        for x in self._futures:
            if x.exception():
                l.append(x.exception())
        return l


class Download():

    def __init__(self, config, logger, event, start_byte, chunk_size, file_name):
        time.sleep(1)

        self.config = config
        self.logger = logger
        self.event = event
        self.start_byte = start_byte
        self.chunk_size = chunk_size
        self.timeout = 4
        self.file_name = file_name
        self.mini_chunks = []

        self.retries = self.config.get('retries')

        self.headers = {'User-Agent': utils.get_random_useragent()}

        self.threads_count = self.config.get('max-conn')
        self.url = self.config.get('url')
        self.file_path = self.config.get('download_path') + '/' + self.file_name
        

        self.pool = ManagedThreadPoolExecutor(self.threads_count)

        self.bytes_range = utils.calc_bytes_range(int(self.chunk_size), int(self.threads_count))

        self.run()


    def run(self):
        '''
            Runs all the threads.
        '''
        for count, byte_range in enumerate(self.bytes_range):
            start_byte = byte_range[0]
            end_byte = byte_range[1]
            # print count, byte_range

            future_obj = self.pool.submit(
                                self.download,
                                self.url,
                                self.file_path + '.%.3d' % count,
                                start_byte,
                                end_byte,
                                self.headers,
                                self.timeout,
                                self.retries
                                )
            # add mini_chunk names to a list for later use
            self.mini_chunks.append( str(self.file_path + '.%.3d' % count) )

            '''
            From the python doc:
                add_done_callback(fn) attaches the callable fn to the future.
                fn will be called, with the future as its only 
                argument, when the future is cancelled or finishes running.
            '''
            future_obj.add_done_callback(self.check_done)


    def check_done(self, arg):
        if self.pool.done():
            '''
                pool.done() returns True, it means download cancelled 
                or finished successfully.
            '''
            # i think i should check the download status!

            # if download_status == True:
            self.merge_mini_chunks()
            for each_ex in self.pool.get_exceptions():
                print each_ex

            # download of this chunk finished, you can release the main thread
            self.event.set()


    def merge_mini_chunks(self):
        '''
            merge the mini_chunks downloaded by threads.
            
            merge the list of mini_chunks -> [file.0001.000, file.0001.001, file.0001.002 ... ]
            to a single file -> "file.0001"
        '''
        path = self.mini_chunks[0][0:-4]

        with open(path, "wb") as f:
            for mini_chunk in self.mini_chunks:
                with open(mini_chunk, "rb") as old:
                    f.write(old.read())

                # remove the old mini_chunks
                os.remove(mini_chunk)



    def download(self, url, dest_path, start_byte, end_byte, headers, timeout, retries):
        '''
            Starts downloading the chunk. this method runs in several threads.
        '''
        headers['Range'] = 'bytes=%d-%d' % (start_byte, end_byte)
        req = urllib2.Request(url, headers=headers)

        try:
            urlObj = urllib2.urlopen(req, timeout=timeout)
        except urllib2.HTTPError, e:
            if e.code == 416:
                '''
                HTTP 416 Error: Requested Range Not Satisfiable. Happens when we ask
                for a range that is not available on the server. It will happen when
                the server will try to send us a .html page that means something like
                "you opened too many connections to our server". If this happens, we
                will wait for the other threads to finish their connections and try again.
                '''
                if retries:
                    print '[+] is retrying !'
                    time.sleep(2)
                    self.retries -= 1
                    # run again, check that there isnt a problem with this way!
                    # delete old files before trying ? (or just overwrite them)
                    return self.run()
            else:
                # TO-DO: log the raise error
                raise

        except urllib2.URLError:
            print '[+] URL error'
            raise
            

        block = 2048            # 2KB
        with open(dest_path, "wb") as f:
            while True:
                try:
                    buff = urlObj.read(block)
                except Exception, e:
                    # TO-DO: log error ! (what erroe ?)
                    print 'buffer error ! cant read block.'
                if not buff:
                    break

                f.write(buff)
        urlObj.close()

