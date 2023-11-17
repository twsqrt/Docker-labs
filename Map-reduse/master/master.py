import socket
import os
import glob
import json
import sys
import time 

RECV_BUFF_SIZE = 100 * 1024
MAX_WORDS_RATE_DICT_SIZE = 100
NUMBER_OF_TOP_LIST = 30
NUMBER_OF_DATA_FILES = 10
DATA_PATH_FORMAT = 'data/{0}.txt'

class Slave:
    def __init__(self, address: str):
        host, port = address.split(':')
        sock = socket.socket()
        sock.connect((host, int(port)))
        sock.setblocking(False)
        self.__socket = sock
        self.__is_working = False
        self.__has_result = False
        self.__current_result_dict = None

    def get_is_working_flag(self) -> bool:
        return self.__is_working
    
    def get_has_result_flag(self) -> bool:
        return self.__has_result
    
    is_working = property(get_is_working_flag)
    has_result = property(get_has_result_flag)

    def send_page(self, page: str) -> None:
        if self.__is_working:
            raise Exception('Slave is working right now!')
        self.__socket.send(bytes(page, 'utf-8'))
        self.__has_result = False
        self.__is_working = True

    def status_update(self) -> bool:
        try:
            data = self.__socket.recv(RECV_BUFF_SIZE)
        except BlockingIOError:
            return False
        self.__current_result_dict = json.loads(data.decode('utf-8'))
        self.__has_result = True
        self.__is_working = False
        return True

    def get_result(self) -> dict:
        if self.__has_result:
            return self.__current_result_dict
        return None
    
    def close(self) -> None:
        self.__socket.close()


def all_slaves_free(slaves: list):
    for slave in slaves:
        if not slave.is_free():
            return False
    return True

def add_words_rate(to_dict: dict, from_dict: dict) -> None:
    for word, count in from_dict.items():
        if word in to_dict:
            to_dict[word] += count
        else:
            to_dict[word] = count

def split_words_rate_by_hash(words_rate_dict: dict) -> dict:
    words_rate_by_hash = {}
    for i in range(0, NUMBER_OF_DATA_FILES):
        words_rate_by_hash[i] = {}
    for word, rate in words_rate_dict.items():
        file_id = hash(word) % NUMBER_OF_DATA_FILES
        words_rate_by_hash[file_id][word] = rate
    return words_rate_by_hash

def dump_wrods_rate(words_rate_dict: dict) -> None:
    words_rate_by_hash = split_words_rate_by_hash(words_rate_dict)
    for file_id, words_rate in words_rate_by_hash.items():
        file_words_rate = {}
        with open(DATA_PATH_FORMAT.format(file_id), 'r') as file:
            for line in file:
                word, rate_str = line.split(' ')
                file_words_rate[word] = int(rate_str)
        add_words_rate(file_words_rate, words_rate)
        with open(DATA_PATH_FORMAT.format(file_id), 'w') as file:
            for word, rate in sorted(file_words_rate.items(), key=lambda x: x[1], reverse=True):
                file.write('{w} {r}\n'.format(w=word, r=rate))

def get_file_top_words_rate(file_id: int, number_of_top: int) -> dict:
    with open(DATA_PATH_FORMAT.format(file_id), 'r') as file:
        file_top_words_rate = {}
        for _ in range(0, number_of_top):
            word, rate_str = next(file).split(' ')
            file_top_words_rate[word] = int(rate_str)
        return file_top_words_rate

if __name__ == '__main__':
    if len(sys.argv) < 3:
        raise Exception('Master musl have at least one slave!')

    addresses = sys.argv[2:]
    slaves = [Slave(address) for address in addresses]
    words_rate_dict = {}

    pages = []
    pages_file = open(sys.argv[1], 'r', encoding='utf-8')
    for line in pages_file.readlines():
        line = line.strip('\n')
        if line == '' or line[0] == '#':
            continue
        if line == 'end':
            break
        pages.append(line)

    for file in glob.glob('data/*.txt'):
        os.remove(file)

    for i in range(0, NUMBER_OF_DATA_FILES):
        open(DATA_PATH_FORMAT.format(i), 'a').close()    

    while len(pages) > 0:
        for slave in slaves:
            slave.status_update()
            if slave.has_result:
                result_dict = slave.get_result()
                add_words_rate(words_rate_dict, result_dict)
            if not slave.is_working and len(pages) > 0:
                page = pages.pop()
                slave.send_page(page)
                print(f'send page: {page}')
        if len(words_rate_dict) > MAX_WORDS_RATE_DICT_SIZE:
            print(f'created memory dump!')
            dump_wrods_rate(words_rate_dict)
            words_rate_dict.clear()
        time.sleep(0.2)
        
    while len(slaves) > 0:
        for slave in slaves:
            slave.status_update()
            if slave.has_result:
                result_dict = slave.get_result()
                add_words_rate(words_rate_dict, result_dict)
                slave.close()
                slaves.remove(slave)
        if len(words_rate_dict) > MAX_WORDS_RATE_DICT_SIZE:
            print(f'created memory dump!')
            dump_wrods_rate(words_rate_dict)
            words_rate_dict.clear()
        time.sleep(0.2)

    top_words_rate = {}
    for file_id in range(0, NUMBER_OF_DATA_FILES):
        file_top_words_rate = get_file_top_words_rate(file_id, NUMBER_OF_TOP_LIST)
        add_words_rate(top_words_rate, file_top_words_rate)
        sorted_words_rate_list = sorted(top_words_rate.items(), key=lambda x: x[1], reverse=True)
        top_words_rate = dict(sorted_words_rate_list[:NUMBER_OF_TOP_LIST])
    
    print(top_words_rate)