import json
import socket
import sys
import time 

if len(sys.argv) < 3:
    print("master must have at least one slave")
    raise Exception()

RECV_BUFF_SIZE = 100000

pages = []
pages_file = open(sys.argv[1], 'r')
for line in pages_file.readlines():
    line = line.strip('\n')
    if line == '' or line[0] == '#':
        continue
    if line == 'end':
        break
    pages.append(line)

class Slave:
    def __init__(self, address: str):
        host, port = address.split(':')
        sock = socket.socket()
        sock.connect((host, int(port)))
        sock.setblocking(False)
        self.__socket = sock
        self.__is_free = True

    def is_free(self) -> bool:
        return self.__is_free
    
    def send_page(self, page: str) -> None:
        self.__socket.send(bytes(page, 'utf-8'))
        self.__is_free = False
    
    def get_result(self) -> list:
        if self.__is_free:
            return None
        try:
            data = self.__socket.recv(RECV_BUFF_SIZE)
        except BlockingIOError:
            return None
        self.__is_free = True
        return json.loads(data.decode('utf-8'))
    
    def close(self) -> None:
        self.__socket.close()

addresses = sys.argv[2:]
slaves = [Slave(address) for address in addresses]
words_count = {}

def get_free_slave() -> Slave:
    for slave in slaves:
        if slave.is_free():
            return slave
    return None

def all_slaves_free() -> bool:
    for slave in slaves:
        if not slave.is_free():
            return False
    return True

def add_words_count(slave_words_count: dict) -> None:
    for word, count in slave_words_count.items():
        if word in words_count:
            words_count[word] += count
        else:
            words_count[word] = count

def update_words_count() -> None:
    for slave in slaves:
        slave_words_count = slave.get_result()
        if slave_words_count is not None:
            add_words_count(slave_words_count)

while len(pages) > 0:
    update_words_count()
    slave = get_free_slave()
    if slave is not None:
        page = pages.pop()
        print(f'send page: {page}')
        slave.send_page(page)
    time.sleep(1)
    
while not all_slaves_free():
    update_words_count()
    time.sleep(1)

for slave in slaves:
    slave.close()


number_of_top_list = 30

print('result:')
for word, count in sorted(words_count.items(), key = lambda x: -x[1])[:number_of_top_list]:
    print(f'{word}\t matches:{count}')