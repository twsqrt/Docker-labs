import argparse
import time 

import config
import slave as slv
import ratedict as rd
import database as db
import toplist as tl

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--links_file', type=str, required=True, dest='links_file_path')
    parser.add_argument('--db_path', type=str, required=True)
    parser.add_argument('--db_files_count', type=int, 
        default=config.default_db_file_count
    )
    parser.add_argument('--top_count', type=int, default=config.default_top_count)
    parser.add_argument('--buffer_size_limit', type=int, 
        default=config.default_buffer_size_limit
    )
    parser.add_argument('--buffer_cache_size', type=int, 
        default=config.default_buffer_cache_size
    )
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

    links = list(parse_links(args.links_file_path))
    slaves = [slv.SlaveSocket(address) for address in args.slave_addresses]
    buffer = rd.RateDict()
    database = db.WordRateDB(args.db_path, args.db_files_count)

    while len(links) > 0 or len(slaves) > 0:
        for slave in slaves:
            slave.update()
            if slave.has_result():
                buffer.add_dict(slave.take_result())
                if len(links) == 0:
                    slave.close()
                    slaves.remove(slave)
            if not slave.is_working() and len(links) > 0:
                link = links.pop()
                slave.send_link(link)
                print(f'send link: {link}')
        if len(buffer) > args.buffer_size_limit:
            sorted_buffer_items = sorted(buffer.items(), 
                key=lambda p: p[1], 
                reverse=True
            )
            database.dump(sorted_buffer_items[args.buffer_cache_size:])
            buffer = rd.RateDict(dict(sorted_buffer_items[:args.buffer_cache_size]))
            print('created memory dump!')
        time.sleep(0.2)
    
    top_list = tl.TopList(args.top_count, lambda p: p[1])
    for word_rate_pair in database.items():
        top_list.add(word_rate_pair)
    top_list.add_list(buffer.items())

    for word, rate in top_list.get_top():
        print(f'{word}\t {rate}')
    

if __name__ == '__main__':
    main()