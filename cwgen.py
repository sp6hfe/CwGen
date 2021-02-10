import hashlib
import os
import platform
import sys
import urllib.request

dict_dir_name = "ispell-pl-20021127"


class CwGen:
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

    def load_dictionary(self, dictionary_path):
        loaded_dictionary = dict()

        with open(os.path.normpath(dictionary_path), mode="r", encoding="ISO-8859-1") as dictionary:
            for line in dictionary:
                # populate dictionary (index -> word_len)
                split_data = line.strip().split(None, 1)

                data_count = len(split_data)

                # handle simple dictionary with words only
                if data_count == 1:
                    loaded_dictionary.setdefault(len(split_data[0]), []).append([
                        split_data[0], 'None', 'None'])
                # handle more complex dictionary having additional data like ispell [word/metadata occurence]
                elif data_count == 2:
                    # split word metadata - if attached
                    wm_list = split_data[0].split("/", 1)
                    wm_list_len = len(wm_list)
                    if wm_list_len == 1:
                        loaded_dictionary.setdefault(len(wm_list[0]), []).append(
                            [wm_list[0], 'None', split_data[1]])
                    elif wm_list_len >= 2:
                        loaded_dictionary.setdefault(len(wm_list[0]), []).append(
                            [wm_list[0], wm_list[1], split_data[1]])
                # no other type is supported for now
                else:
                    loaded_dictionary.clear()
                    break

        return loaded_dictionary

    def get_dictionary_stat(self, dictionary_path):
        dictionary = self.load_dictionary(dictionary_path)
        words_stat = {}

        # generate words stat
        words_count = 0
        for key, value in dictionary.items():
            if isinstance(value, list):
                words_by_key = len(value)
                # words number of key length
                words_stat.setdefault(key, words_by_key)
                # words in total
                words_count += words_by_key

        # generate extended stat
        if words_count > 0:
            words_length_sorted = sorted(words_stat)
            return [words_count, words_length_sorted[0], words_length_sorted[-1], words_stat]
        else:
            return [0, 0, 0, {}]

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
    test_dict = "A"

    cw_gen = CwGen()

    script_path = os.path.dirname(sys.argv[0])
    dict_path = os.path.join(os.path.dirname(
        script_path), dict_dir_name, test_dict)

    words_stat = cw_gen.get_dictionary_stat(dict_path)
    print(words_stat)

    cw_gen.get_ebook2cw()


if __name__ == '__main__':
    main()
