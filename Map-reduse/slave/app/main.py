import requests
import json
import socket
import time
import argparse
import bs4
import textblob as tb

RECV_BUFF_SIZE = 512

def is_ascii_encoding(text: str) -> bool:
    for _, char in enumerate(text):
        if ord(char) > 127:
            return False
    return True


def get_words_rate_on_page(link: str) -> dict:
    request_result = requests.get(link)
    if request_result.status_code != 200:
        raise Exception()
    page = bs4.BeautifulSoup(request_result.text, 'html.parser')
    content = page.find('div', id='mw-content-text')
    if content == None:
        return {}
    words_rate = {} 
    text_to_parse = content.get_text().lower()
    for word in tb.TextBlob(text_to_parse).words:
        if word in words_rate:
            words_rate[word] += 1
        elif is_ascii_encoding(word):
            words_rate[word] = 1
    return words_rate


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', required=True, type=int)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    sock = socket.socket()
    sock.bind(('localhost', args.port))
    sock.listen(1)

    conn, _ = sock.accept()

    while True:
        data = conn.recv(RECV_BUFF_SIZE)
        if data == b'':
            break
        link = data.decode('utf-8')
        print(f'recived link: {link}')
        words_count = get_words_rate_on_page(link)
        conn.send(bytes(json.dumps(words_count), 'utf-8'))
        time.sleep(0.2)
    
if __name__ == '__main__':
    main()