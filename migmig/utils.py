# Python utils for migmig project

import random


def parse_doc_arguments(arguments):
    options, args, command = {}, {}, None
    for key, value in arguments.items():
        if key[0:2] == "--":
            options[key[2:]] = value
        elif key[0] == "<":
            args[key] = value
        else:
            if value:
                command = key

    return command, args, options


def calc_bytes_range(chunk_size, threads_count):
    """
        calculate "start byte" and "end byte" to give to each thread.
        return a list including tuples: (start, end)
    """
    # 6291456
    bytes_range = []

    mini_chunk = chunk_size // threads_count
    pos = 0
    for i in range(threads_count):
        start_byte = pos
        end_byte = start_byte + mini_chunk
        if end_byte > chunk_size - 1:
            end_byte = chunk_size

        pos = end_byte + 1
        bytes_range.append((start_byte, end_byte))

    return bytes_range


def get_random_useragent():
    """
    Returns a random popular user-agent.
    Taken from `here <http://techblog.willshouse.com/2012/01/03/most-common-user-agents/>`_, last updated on 01/02/2014.

    :returns: user-agent
    :rtype: string
    """
    l = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.73.11 (KHTML, like Gecko) Version/7.0.1 Safari/537.73.11',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.76 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.77 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:26.0) Gecko/20100101 Firefox/26.0',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 7_0_4 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11B554a Safari/9537.53',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 5.1; rv:26.0) Gecko/20100101 Firefox/26.0',
    ]
    return random.choice(l)
