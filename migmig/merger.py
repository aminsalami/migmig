import os
import glob
import shutil
from ConfigParser import SafeConfigParser


class Merger:
    def __init__(self, log_constructor, config, base_dir, second_dir=None):
        """

        :param log_constructor:
        :param config:
        :param base_dir:
        :param second_dir:
        :return:
        :Note: docopt automatically changes "~" to "/home/user/"
        """
        self.logger = log_constructor.get_logger(__name__)
        self.config = config

        self.base_dir = base_dir
        self.second_dir = second_dir
        self.base_info = None
        self.second_info = None
        self.file_name = ''
        self.total_chunks = 0

        if not self.base_dir:
            self.base_dir = self.config.get('download_path')

        print 'base: %s   second:%s' % (base_dir, second_dir)

        # Find merge.info for base directory
        if os.path.exists(self.base_dir + '/' + 'merge.info'):
            print 'base info exist'
            self.base_info = SafeConfigParser()
            self.base_info.read(self.base_dir + '/' + 'merge.info')
            self.file_name = self.base_info.get('info', 'file_name')
            self.total_chunks = self.base_info.get('info', 'total_chunks')

        # Find merge.info for second directory
        if self.second_dir and os.path.exists(self.second_dir + '/' + 'merge.info'):
            self.second_info = SafeConfigParser()
            self.second_info.read(self.second_dir + '/' + 'merge.info')

    def run(self):
        # 1. merge each directory by itself
        if not self.base_info:
            # TO-DO: LOG, there is no merge info in this directory
            return
        if self.second_info:
            if not self.check():
                # TO-DO : log, can not merge
                return

        # merge base directory with itself
        self.single_merge(self.base_dir)

    def chunk_list(self, directory):
        """
        Returns a list containing chunk path
        :param directory:
        :return:
        """
        path = directory + '/' + self.file_name
        return glob.glob(path + '.*')

    def check(self):
        """
        Check if base directory and second directory representing same file.
        :return:
        """
        base_file_name = self.base_info.items('info', 'file_name')
        second_file_name = self.second_info.items('info', 'file_name')

        base_content_len = self.base_info.items('info', 'content_len')
        second_content_len = self.second_info.items('info', 'content_len')

        if (base_file_name == second_file_name) and (base_content_len == second_content_len):
            return True
        return False

    def successor(self, index, list):
        """
        Returns True if two chunks in a row can be merged
        :return: boolean
        """
        current = list[index].split('.')[-1]  # current == '0000-0001' or '0000'

        if index >= len(list) - 1:
            return False
        next = list[index + 1].split('.')[-1]

        begin_chunk = current.split('-')[-1]
        end_chunk = next.split('-')[0]

        if int(begin_chunk) == int(end_chunk) - 1:
            return True

        return False

    def predecessor(self):
        pass

    def single_merge(self, directory):
        """

        :param directory:
        :return:
        """
        ready = []
        chunk_list = self.chunk_list(directory)
        chunk_list = sorted(chunk_list)
        # print 'LEN:', len(chunk_list)

        for index in range(len(chunk_list)):
            succ = self.successor(index, chunk_list)
            ready.append(chunk_list[index])
            if not succ:
                self.chunk_merge(ready)
                ready = []

    def chunk_merge(self, list):
        if len(list) == 1:  # No merge is needed when there is only one chunk !
            print 'Len is 1, no merge'
            return

        split_path = list[0].split('.')
        file_path = ".".join(split_path[i] for i in range(len(split_path) - 1))

        start_chunk = list[0].split('.')[-1]
        start_chunk_number = start_chunk.split('-')[-1]

        end_chunk = list[-1].split('.')[-1]
        end_chunk_number = end_chunk.split('-')[-1]

        if int(start_chunk_number) == 0 and int(end_chunk_number) == int(self.total_chunks) - 1:
            destination = file_path
        else:
            destination = file_path + '.' + start_chunk_number + '-' + end_chunk_number

        print 'Destination:', destination
        with open(destination, 'wb') as f:
            for chunk in list:
                shutil.copyfileobj(open(chunk, 'rb'), f, 200 * 1024)    # buffer size: 200KB, for faster copy
                os.remove(chunk)
        print '[+] Merge DONE !'


