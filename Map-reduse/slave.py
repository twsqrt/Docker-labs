import requests
import json
import socket
import sys
import time

from bs4 import BeautifulSoup
from textblob import TextBlob

if len(sys.argv) != 2:
    raise Exception()

RECV_BUFF_SIZE = 512

port = int(sys.argv[1])

sock = socket.socket()
sock.bind(('', port))
sock.listen(1)

conn, _ = sock.accept()

def get_words_count_on_page(url: str) -> dict:
    request_result = requests.get(url)
    if request_result.status_code == 200:
        page = BeautifulSoup(request_result.text, 'html.parser')
        content = page.find('div', id='mw-content-text')
        words_count = {} 
        if content is not None:
            text_to_parse = content.get_text().lower()
            for word in TextBlob(text_to_parse).words:
                if word in words_count:
                    words_count[word] += 1
                else:
                    words_count[word] = 1
        return words_count
    return None

while True:
    data = conn.recv(RECV_BUFF_SIZE)
    if data == b'':
        break
    url = data.decode('utf-8')
    print(f'recived page: {url}')
    words_count = get_words_count_on_page(url)
    conn.send(bytes(json.dumps(words_count), 'utf-8'))
    time.sleep(1)
    