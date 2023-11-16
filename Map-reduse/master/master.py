import socket
import json
import sys
import time 

RECV_BUFF_SIZE = 100 * 1024
NUMBER_OF_TOP_LIST = 30


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
        self.__current_result_dict =  json.loads(data.decode('utf-8'))
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
        time.sleep(0.2)
        
    while len(slaves) > 0:
        for slave in slaves:
            slave.status_update()
            if slave.has_result:
                result_dict = slave.get_result()
                add_words_rate(words_rate_dict, result_dict)
                slave.close()
                slaves.remove(slave)
        time.sleep(0.2)

    print('result:')
    sorted_word_rate_dict = sorted(words_rate_dict.items(), key=lambda x: x[1], reverse=True) 
    for word, count in sorted_word_rate_dict[:NUMBER_OF_TOP_LIST]:
        print(f'{word}\t matches:{count}')