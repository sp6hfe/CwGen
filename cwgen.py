import ebook2cw as e2cw
import helpers
import os
import sys
import uuid

dict_dir_name = "ispell-pl-20021127"


class CwGen:
    """Class handling CW learning material generation"""

    def __init__(self):
        """Class initialization"""

        DATA_FOLDER = 'data'

        self.e2cw = e2cw.Ebook2Cw(os.path.dirname(sys.argv[0]), DATA_FOLDER)
        self.dictionary_list = []

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
        return self.e2cw.get_executable()


def main():
    print("To be implemented...")


if __name__ == '__main__':
    main()
