import hashlib
import os
import platform
import sys
import urllib.request
import uuid

dict_dir_name = "ispell-pl-20021127"


class CwGen:
    """Class handling CW learning material generation"""

    def __init__(self):
        """Class initialization"""

        self.dictionary_list = []

    def _md5(self, file_path):
        """Calculate MD5 hash out of provided file

        Args:
            file_path (str): Path to the file to calculate MD5 out of

        Returns:
            string: A string containing HEX representation of calculated MD5 hash
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for data_chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(data_chunk)

        return hash_md5.hexdigest()

    def _get_file_from_web(self, file_url, file_path):
        """Downloads specified file from provided URL and store in selected location.
            In order to keep data integrity file after downloading is saved with
            suffix and later on is renamed to the original name assuring already
            existing file gets deleted.

        Args:
            file_url  (str): URL of the file to download
            file_path (str): Path to the resulting file (incl. file name)

        Returns:
            None
        """

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
        """Verifies if file's calculated MD5 hash match the one stored in other file.
            File with pre-calculated MD5 hashes should contain
            a row with hash and file name separated by space.

        Args:
            file_path     (str): Path to the file being verified
            md5_file_path (str): Path to the file containing pre-calculated MD5 hashes

        Returns:
            bool: True when MD5 verification succeeded, False otherwise

        """

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
        """Generate a statistics on a dictionary data.

        Args:
            words_dictionary (dict): as generated in _load_dictionary_from_file()

        Returns:
            dict: Dictionary
                'words_count' -> number of words in dictionary
                'min_length' -> minimal length of the words
                'max_length' -> maximal length of the words
                'words_stat' -> Dictionary{key, words_by_key}
                    key -> word length
                    words_by_key -> number of words having the same length
        """

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
        """Load dictionary data from file
            and calculate its statistics.

        Args:
            file_path (str): Path to the dictionary file

        Returns:
            dict: Dictionary
                'uuid': generated UUID
                'name': file name
                'path': dictionary path
                'stat': words statistics as generated in _get_words_stat()
                'data': Dictionary {key, value}
                    key: word length
                    value (list): [word, meta_data, occurence]
                        word (str): a word
                        meta_data (str): additional information (ispell dictionaries)
                        occurence (int): number of occurences in a probe (the higher the more frequently used)
        """

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
            result['uuid'] = uuid.uuid1()
            result['name'] = os.path.basename(file_path)
            result['path'] = file_path
            result['stat'] = self._get_words_stat(words_dictionary)
            result['data'] = words_dictionary

        return result

    def add_dictionary(self, file_path):
        """Adds dictionary (loaded from file) to the internal list

        Args:
            file_path (str): Path to the dictionary file

        Returns:
            bool: True when dictionary was added, False otherwise
        """

        # add only distinct file (verification based on file path)
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
        """Removes dictionary from the internal list
            using UUID to select right one.

        Args:
            dictionary_uuid (str): Dictionary assigned UUID

        Returns:
            bool: True when dictionary was removed, False otherwise
        """

        if_removed = False

        for index, dictionary in enumerate(self.dictionary_list):
            if dictionary['uuid'] == dictionary_uuid:
                del self.dictionary_list[index]
                if_removed = True
                break

        return if_removed

    def get_dictionaries_stat(self):
        """Gets aggregated statistics of the data loaded from all added dictionaries

        Args:
            None

        Returns:
            dict: Dictionary
                    'overal': -> dict:
                        'words_count': -> total number of words colected
                        'min_length':  -> minimal word length
                        'max_length:   -> maximal word length
                    'data': -> list of dict:
                        'uuid': -> dictionary uuid (generated for identification purposes)
                        'name': -> dictionary name
                        'stat': -> words statistics returned by _get_words_stat()
        """

        stat = {}
        overal_stat = {}
        dictionaries_data = []

        min_length = 1000
        max_length = 0
        total_words_count = 0

        for dictionary in self.dictionary_list:
            data = {}
            data['uuid'] = dictionary['uuid']
            data['name'] = dictionary['name']
            data['stat'] = dictionary['stat']
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
        """Downloads proper version of the ebook2cw
            performing MD5 verification for integrity check.

        Args:
            None

        Returns:
            bool: True when executable was downloaded, False otherwise
        """

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
    print("To be implemented...")


if __name__ == '__main__':
    main()
