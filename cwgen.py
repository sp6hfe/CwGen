import hashlib
import os
import platform
import sys
import urllib.request
import uuid

dict_dir_name = "ispell-pl-20021127"


class CwGen:
    def __init__(self):
        self.dictionary_list = []

    def _md5(self, file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for data_chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(data_chunk)

        return hash_md5.hexdigest()

    def _get_file_from_web(self, file_url, file_path):
        TEMP_FILE_SUFFIX = '_tmp'

        # make sure directories are there
        file_directory = os.path.dirname(file_path)
        if not os.path.exists(file_directory):
            os.makedirs(file_directory)

        # download the file with temporary suffix
        temp_file_path = file_path + TEMP_FILE_SUFFIX
        urllib.request.urlretrieve(file_url, temp_file_path)

        # verify if another copy already exist
        if os.path.exists(file_path):
            os.remove(file_path)

        # rename downloaded file
        os.rename(temp_file_path, file_path)

    def _verify_file_md5(self, file_path, md5_file_path):
        is_verified = False

        if os.path.exists(file_path) and os.path.exists(md5_file_path):
            file_name = os.path.basename(file_path)

            with open(os.path.normpath(md5_file_path), mode="r") as md5_file:
                for line in md5_file:
                    split_data = line.strip().split(None, 1)

                    if split_data[1] == file_name and split_data[0] == self._md5(file_path):
                        is_verified = True
                        break

        return is_verified

    def _get_words_stat(self, words_dictionary):
        stat = {}
        words_stat = {}

        # generate words stat [words count, min length, max length, dictionary with stat of key: length, value: words count]
        words_count = 0
        for key, value in words_dictionary.items():
            if isinstance(value, list):
                words_by_key = len(value)
                # words number of key length
                words_stat.setdefault(key, words_by_key)
                # words in total
                words_count += words_by_key

        # generate extended stat
        if words_count > 0:
            words_length_sorted = sorted(words_stat)
            stat['words_count'] = words_count
            stat['min_length'] = words_length_sorted[0]
            stat['max_length'] = words_length_sorted[-1]
            stat['words_stat'] = words_stat

        return stat

    def _load_dictionary_from_file(self, file_path):
        result = {}
        words_dictionary = {}

        with open(os.path.normpath(file_path), mode="r", encoding="ISO-8859-1") as dictionary:
            for line in dictionary:
                # populate dictionary (key: word letters count, value: list of words with same length)
                split_data = line.strip().split(None, 1)

                data_count = len(split_data)

                # handle simple dictionary with words only
                if data_count == 1:
                    words_dictionary.setdefault(len(split_data[0]), []).append([
                        split_data[0], 'None', 'None'])
                # handle more complex dictionary having additional data like ispell [word/metadata occurence]
                elif data_count == 2:
                    # split word metadata - if attached
                    wm_list = split_data[0].split("/", 1)
                    wm_list_len = len(wm_list)
                    if wm_list_len == 1:
                        words_dictionary.setdefault(len(wm_list[0]), []).append(
                            [wm_list[0], 'None', split_data[1]])
                    elif wm_list_len >= 2:
                        words_dictionary.setdefault(len(wm_list[0]), []).append(
                            [wm_list[0], wm_list[1], split_data[1]])
                # no other type is supported for now
                else:
                    words_dictionary.clear()
                    break

        # assemble result
        if len(words_dictionary) > 0:
            result['name'] = os.path.basename(file_path)
            result['path'] = file_path
            result['stat'] = self._get_words_stat(words_dictionary)
            result['data'] = words_dictionary
            result['uuid'] = uuid.uuid1()

        return result

    def add_dictionary(self, file_path):
        # add only distinct file
        for dictionary in self.dictionary_list:
            if os.path.normpath(dictionary['path']) == os.path.normpath(file_path):
                return False

        # load data from file
        new_dictionary = self._load_dictionary_from_file(file_path)

        # add new dictionary if it contains data
        if len(new_dictionary) > 0:
            self.dictionary_list.append(new_dictionary)

        return True

    def remove_dictionary(self, dictionary_uuid):
        if_removed = False

        for index, dictionary in enumerate(self.dictionary_list):
            if dictionary['uuid'] == dictionary_uuid:
                del self.dictionary_list[index]
                if_removed = True
                break

        return if_removed

    def get_dictionaries_stat(self):
        stat = {}
        overal_stat = {}
        dictionaries_data = []

        min_length = 1000
        max_length = 0
        total_words_count = 0

        for dictionary in self.dictionary_list:
            data = {}
            data['name'] = dictionary['name']
            data['stat'] = dictionary['stat']
            data['uuid'] = dictionary['uuid']
            dictionaries_data.append(data)

            total_words_count += dictionary['stat']['words_count']

            if dictionary['stat']['min_length'] < min_length:
                min_length = dictionary['stat']['min_length']
            if dictionary['stat']['max_length'] > max_length:
                max_length = dictionary['stat']['max_length']

        if len(dictionaries_data) > 0:
            overal_stat['words_count'] = total_words_count
            overal_stat['min_length'] = min_length
            overal_stat['max_length'] = max_length

            stat['overal'] = overal_stat
            stat['data'] = dictionaries_data

        return stat

    def get_ebook2cw(self):
        if_downloaded_ok = False

        BASE_URL = 'https://fkurz.net/ham/ebook2cw/'
        EXECUTABLE_BASE_NAME = 'ebook2cw'
        HASH_FILE_NAME = 'md5sums-bin.txt'

        current_os = platform.system()
        if current_os == 'Windows' or current_os == 'Linux':
            cwgen_path = os.path.dirname(sys.argv[0])
            executable_local_base_path = os.path.normpath(os.path.join(
                cwgen_path, 'ebook2cw'))

            # prepare files urls/paths
            executable_name = EXECUTABLE_BASE_NAME
            if current_os == 'Windows':
                executable_name += '.exe'
            executable_url = BASE_URL + executable_name
            executable_local_path = os.path.normpath(os.path.join(
                executable_local_base_path, executable_name))

            hash_file_url = BASE_URL + HASH_FILE_NAME
            hash_file_local_path = os.path.normpath(os.path.join(
                executable_local_base_path, HASH_FILE_NAME))

            # download files (executable + md5)
            self._get_file_from_web(
                executable_url, executable_local_path)
            self._get_file_from_web(
                hash_file_url, hash_file_local_path)

            # verify executable integrity
            if self._verify_file_md5(
                    executable_local_path, hash_file_local_path):
                if_downloaded_ok = True
            else:
                os.remove(executable_local_path)

        return if_downloaded_ok


def main():
    # test_dict1 = "A"
    # test_dict2 = "B"

    # cw_gen = CwGen()

    # script_path = os.path.dirname(sys.argv[0])

    # dict1_path = os.path.join(os.path.dirname(
    #     script_path), dict_dir_name, test_dict1)

    # dict2_path = os.path.join(os.path.dirname(
    #     script_path), dict_dir_name, test_dict2)

    # cw_gen.add_dictionary(dict1_path)
    # cw_gen.add_dictionary(dict2_path)

    # dictionaries_stat = cw_gen.get_dictionaries_stat()
    # print(dictionaries_stat)

    # uuid1 = dictionaries_stat['data'][0]['uuid']
    # uuid2 = dictionaries_stat['data'][1]['uuid']
    # print(uuid)

    # cw_gen.remove_dictionary(uuid1)

    # dictionaries_stat = cw_gen.get_dictionaries_stat()
    # print(dictionaries_stat)

    # cw_gen.remove_dictionary(uuid2)

    # dictionaries_stat = cw_gen.get_dictionaries_stat()
    # print(dictionaries_stat)

    # cw_gen.get_ebook2cw()


if __name__ == '__main__':
    main()
