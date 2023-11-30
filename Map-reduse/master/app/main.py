import sys
import argparse
import time 

import slave as slv
import ratedict as rd
import database as db

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--links_file', type=str, required=True, dest='links_file_path')
    parser.add_argument('--db_path', type=str, required=True)
    parser.add_argument('--db_files_count', type=int, default=10)
    parser.add_argument('--top_count', type=int, default=10)
    parser.add_argument('--buffer_size_limit', type=int, default=500)
    parser.add_argument('-s', '--slaves', type=str, nargs='+', dest='slave_addresses')
    return parser.parse_args()


def parse_links(links_file_path: str) -> list:
    with open(links_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip('\n')
            if line == '' or line[0] == '#':
                continue
            if line == 'end':
                break
            yield line


def main() -> None:
    args = parse_args()

    pages = list(parse_links(args.links_file_path))
    slaves = [slv.SlaveSocket(address) for address in args.slave_addresses]
    buffer = rd.RateDict()
    database = db.WordRateDB(args.db_path, args.db_files_count)

    while len(pages) > 0 or len(slaves) > 0:
        for slave in slaves:
            slave.update()
            if slave.has_result():
                buffer.add_dict(slave.take_result())
                if len(pages) == 0:
                    slave.close()
                    slaves.remove(slave)
            if not slave.is_working() and len(pages) > 0:
                page = pages.pop()
                slave.send_page(page)
                print(f'send page: {page}')
        if len(buffer) > args.buffer_size_limit:
            database.dump(buffer)
            buffer.clear()
            print('created memory dump!')
        time.sleep(0.2)
    
    for word, rate in database.get_top(args.top_count):
        print(f'{word}\t {rate}')
    

if __name__ == '__main__':
    main()