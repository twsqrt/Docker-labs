import os
import glob

import ratedict as rd

FILE_NAME_FORMAT = 'part_{0}.txt'
DATA_FORMAT = '{0} {1}\n'
SPLIT_DATA_SYMBOL = ' '

class WordRateDB:
    def __init__(self, directory: str, number_of_files: int):
        self.__number_of_files = number_of_files
        self.__file_path_format = os.path.join(directory, FILE_NAME_FORMAT)

        self.clear()
        for i in range(0, number_of_files):
            open(self.__file_path_format.format(i), 'a').close()

    def __split_data_by_hash(self, words_rate: rd.RateDict) -> list:
        words_rate_by_hash = [{} for _ in range(0, self.__number_of_files)]
        for word, rate in words_rate.items():
            index = hash(word) % self.__number_of_files
            words_rate_by_hash[index][word] = rate
        return words_rate_by_hash

    def __add_data_to_file(self, file_path: str, new_words_rate: rd.RateDict) -> None:
        temp_file = file_path + '.temp'
        with open(temp_file, 'w') as new_file, open(file_path, 'r') as old_file:
            for line in old_file:
                word, rate_str = line.split(SPLIT_DATA_SYMBOL)
                rate = int(rate_str)
                if word in new_words_rate:
                    new_file.write(
                        DATA_FORMAT.format(word, rate + new_words_rate[word])
                    )
                    del new_words_rate[word] 
                else:
                    new_file.write(line)
            for word, rate in new_words_rate.items():
                new_file.write(DATA_FORMAT.format(word, rate))
        os.remove(file_path)
        os.rename(temp_file, file_path)

    def dump(self, words_rate: rd.RateDict) -> None:
        words_rate_by_hash = self.__split_data_by_hash(words_rate)
        for file_id in range(0, self.__number_of_files):
            file_path = self.__file_path_format.format(file_id)
            self.__add_data_to_file(file_path, words_rate_by_hash[file_id]) 
    
    def clear(self) -> None:
        for file in glob.glob(self.__file_path_format.format('*')):
            os.remove(file)
    
    def __get_top_in_file(self, file_path: str, top_count: int) -> list:
        top_list = []
        min_rate = 1
        with open(file_path, 'r') as file:
            for line in file:
                word, rate_str = line.split(SPLIT_DATA_SYMBOL)
                rate = int(rate_str)
                if rate >= min_rate:
                    top_list.append((word, rate))
                if len(top_list) > top_count:
                    top_list = sorted(
                        top_list, 
                        key=lambda p: p[1], 
                        reverse=True
                    )[:top_count]
                    min_rate = top_list[-1][1]
        return top_list
    
    def get_top(self, top_count: int) -> list:
        top_list = []
        for file_id in range(0, self.__number_of_files):
            file_path = self.__file_path_format.format(file_id)
            file_top_list = self.__get_top_in_file(file_path, top_count)
            top_list = sorted(
                top_list + file_top_list,
                key=lambda p: p[1],
                reverse=True
            )[:top_count]
        return top_list