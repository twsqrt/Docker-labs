import sys
import time 

import slave as slv
import ratedict as rd
import database as db

DATA_DIRECTORY = 'data'
BUFFER_SIZE_LIMIT = 100
NUMBER_OF_TOP_LIST = 30
NUMBER_OF_DATA_FILES = 10


def main() -> None:
    if len(sys.argv) < 3:
        raise Exception('Master must have at least one slave!')

    addresses = sys.argv[2:]
    slaves = [slv.SlaveSocket(address) for address in addresses]
    buffer = rd.RateDict()
    database = db.WordRateDB(DATA_DIRECTORY, NUMBER_OF_DATA_FILES)

    pages = []
    pages_file = open(sys.argv[1], 'r', encoding='utf-8')
    for line in pages_file.readlines():
        line = line.strip('\n')
        if line == '' or line[0] == '#':
            continue
        if line == 'end':
            break
        pages.append(line)

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
        if len(buffer) > BUFFER_SIZE_LIMIT:
            database.dump(buffer)
            buffer.clear()
            print('created memory dump!')
        time.sleep(0.2)
    
    for word, rate in database.get_top(NUMBER_OF_TOP_LIST):
        print(f'{word}\t {rate}')
    

if __name__ == '__main__':
    main()