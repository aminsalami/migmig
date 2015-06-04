import os
import glob
import shutil
from operator import itemgetter
from ConfigParser import RawConfigParser


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
            self.base_info = RawConfigParser()
            self.base_info.read(self.base_dir + '/' + 'merge.info')
            self.file_name = self.base_info.get('info', 'file_name')
            self.total_chunks = self.base_info.get('info', 'total_chunks')
        else:
            # TO-DO: log, there is no merge in this directory
            print 'There is no "merge.info" in given directory'

        # Find merge.info for second directory
        if self.second_dir and os.path.exists(self.second_dir + '/' + 'merge.info'):
            self.second_info = RawConfigParser()
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
        if not self.single_merge(self.base_dir):
            # TO-DO: log, cannot merge, maybe there is no valid chunk
            return

        if self.second_info:
            self.single_merge(self.second_dir)
            # now merge two directory together
            self.single_merge(self.base_dir, self.second_dir)

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

    def sort(self, list, mode=1):
        """
        Sort the list by chunks number
        :param list:
        :return:
        """
        if mode == 1:
            return sorted(list)
        length = len(list)
        unsorted = []

        def get_number(index):
            start_chunk = list[index].split('.')[-1]
            start_chunk_num = start_chunk.split('-')[0]
            return int(start_chunk_num)

        for index in range(length):
            num = get_number(index)
            unsorted.append((num, list[index]))

        s = sorted(unsorted, key=itemgetter(0))
        result = []
        for i in range(length):
            result.append(s[i][1])
        return result

    def single_merge(self, directory, second_directory=None):
        """

        :param directory:
        :return:
        """
        ready = []
        mode = 1
        chunk_list = self.chunk_list(directory)
        if not chunk_list:
            return

        split_path = chunk_list[0].split('.')
        file_path = ".".join(split_path[i] for i in range(len(split_path) - 1))

        if second_directory:
            second_chunk_list = self.chunk_list(second_directory)
            chunk_list += second_chunk_list
            mode = 2
        chunk_list = self.sort(chunk_list, mode)
        print 'Sorted chunk list:\n', chunk_list

        for index in range(len(chunk_list)):
            succ = self.successor(index, chunk_list)
            ready.append(chunk_list[index])
            if not succ:
                self.chunk_merge(ready, file_path)
                ready = []

    def chunk_merge(self, list, file_path):
        if len(list) == 1:  # No merge is needed when there is only one chunk !
            print 'Len is 1, no merge'
            return

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
                shutil.copyfileobj(open(chunk, 'rb'), f, 200 * 1024)  # buffer size: 200KB, for faster copy
                os.remove(chunk)
        print '[+] Merge DONE !'
