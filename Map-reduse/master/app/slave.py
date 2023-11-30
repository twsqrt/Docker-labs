from socket import socket as Socket
import json

RECV_BUFF_SIZE = 100 * 1024

class SlaveSocket:
    def __init__(self, address: str):
        host, port = address.split(':')
        sock = Socket()
        sock.connect((host, int(port)))
        sock.setblocking(False)
        self.__socket = sock
        self.__is_working = False
        self.__current_result_dict = None

    def is_working(self) -> bool:
        return self.__is_working
    
    def has_result(self) -> bool:
        return self.__current_result_dict != None
    
    def send_page(self, page: str) -> None:
        if self.__is_working:
            raise Exception('Slave is working right now!')
        self.__socket.send(bytes(page, 'utf-8'))
        self.__current_result_dict = None
        self.__is_working = True

    def update(self) -> None:
        try:
            data = self.__socket.recv(RECV_BUFF_SIZE)
        except BlockingIOError:
            return 
        self.__current_result_dict = json.loads(data.decode('utf-8'))
        self.__is_working = False

    def take_result(self) -> dict:
        result = self.__current_result_dict
        self.__current_result_dict = None
        return result
    
    def close(self) -> None:
        self.__socket.close()