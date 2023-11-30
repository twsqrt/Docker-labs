import requests
import json
import socket
import sys
import time
import argparse

from bs4 import BeautifulSoup
from textblob import TextBlob

RECV_BUFF_SIZE = 512

def check_ascii_encoding(word: str) -> bool:
    for _, char in enumerate(word):
        if ord(char) > 127:
            return False
    return True

def get_words_rate_on_page(url: str) -> dict:
    request_result = requests.get(url)
    if request_result.status_code == 200:
        page = BeautifulSoup(request_result.text, 'html.parser')
        content = page.find('div', id='mw-content-text')
        words_rate = {} 
        if content is not None:
            text_to_parse = content.get_text().lower()
            for word in TextBlob(text_to_parse).words:
                if word in words_rate:
                    words_rate[word] += 1
                elif check_ascii_encoding(word):
                    words_rate[word] = 1
        return words_rate
    return None

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', required=True, type=int)
    return parser.parse_args()

    
if __name__ == '__main__':
    args = parse_args()

    sock = socket.socket()
    sock.bind(('', args.port))
    sock.listen(1)

    conn, _ = sock.accept()

    while True:
        data = conn.recv(RECV_BUFF_SIZE)
        if data == b'':
            break
        url = data.decode('utf-8')
        print(f'recived page: {url}')
        words_count = get_words_rate_on_page(url)
        conn.send(bytes(json.dumps(words_count), 'utf-8'))
        time.sleep(0.2)