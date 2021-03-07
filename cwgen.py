import ebook2cw as e2cw
import os
import sys
import uuid


class CwGen:
    """Class handling CW learning material generation"""

    def __init__(self):
        """Class initialization"""

        E2CW_SUBFOLDER = 'ebook2cw'

        self.letters_sets = {
            'all':   {'description': 'All letters and numbers', 'letters': '*'},
            'cwo1':  {'description': 'CWOPS session 1',         'letters': 'tean'},
            'cwo2':  {'description': 'CWOPS session 2',         'letters': 'teanois14'},
            'cwo3':  {'description': 'CWOPS session 3',         'letters': 'teanoisrhdl1425'},
            'cwo4':  {'description': 'CWOPS session 4',         'letters': 'teanoisrhdluc1425'},
            'cwo5':  {'description': 'CWOPS session 5',         'letters': 'teanoisrhdlucmw142536?'},
            'cwo6':  {'description': 'CWOPS session 6',         'letters': 'teanoisrhdlucmwfy142536?'},
            'cwo7':  {'description': 'CWOPS session 7',         'letters': 'teanoisrhdlucmwfypg14253679?/'},
            'cwo8':  {'description': 'CWOPS session 8',         'letters': 'teanoisrhdlucmwfypgbv14253679?/'},
            'cwo9':  {'description': 'CWOPS session 9',         'letters': 'teanoisrhdlucmwfypgbvkj1425367980?/'},
            'cwo10': {'description': 'CWOPS session 10',        'letters': 'teanoisrhdlucmwfypgbvkjxqz1425367980?/'},
        }

        self.training_generator_schemes = {
            'rand':  'Random words',
            'equal': 'Equalize number of all lengths',
            'short': 'Prioritize shorter words',
            'long':  'Prioritize longer words'
        }

        self.e2cw = e2cw.Ebook2Cw(os.path.join(
            os.path.dirname(__file__), E2CW_SUBFOLDER))
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
                'data': Dictionary {key, value}
                    key: word length
                    value (list): words list of the same length
        """

        result = {}
        words_dictionary = {}

        with open(os.path.normpath(file_path), mode="r", encoding="ISO-8859-1") as dictionary:
            for line in dictionary:
                # populate dictionary (key: word letters count, value: list of words with same length)
                split_data = line.strip().split(None, 1)
                # ignore empty lines and comments
                if len(split_data) > 0 and split_data[0][0] != '#':
                    # handle multi word row (starting with %)
                    if split_data[0][0] == '%':
                        print('Multi word line: ', end='[')
                        print(*split_data[1:], end='] ')
                        print('not supported yet.')
                    else:
                        # handle simple or more complex dictionary having additional data separated with '/' (like ispell -> [word/metadata occurence])
                        word_meta_list = split_data[0].split("/", 1)
                        words_dictionary.setdefault(
                            len(word_meta_list[0]), []).append([word_meta_list[0]])

        # assemble result
        if len(words_dictionary) > 0:
            result['uuid'] = uuid.uuid1()
            result['name'] = os.path.basename(file_path)
            result['path'] = file_path
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

    def get_dictionaries_info(self):
        """Gets basic information of all loaded dictionaries

        Args:
            None

        Returns:
            list: list of dict
                'uuid': -> dictionary uuid (generated for identification purposes)
                'name': -> dictionary name
                'stat': -> words statistics returned by _get_words_stat()
        """

        dictionaries_info = []

        for dictionary in self.dictionary_list:
            data = {}
            data['uuid'] = dictionary['uuid']
            data['name'] = dictionary['name']
            data['stat'] = self._get_words_stat(dictionary['data'])
            dictionaries_info.append(data)

        return dictionaries_info

    def get_words_info(self):
        """Gets aggregated words info from all loaded dictionaries.

        Args:
            None

        Returns:
            dict: Dictionary
                'words_count': -> total number of words
                'min_length': -> minimal word length
                'max_length': -> maximal word length
                'words_stat': -> Dictionary{key, words_by_key}
                    key -> word length
                    words_by_key -> number of words having the same length
        """

        words_info = {}
        aggregated_words_stat = {}
        words_count = 0
        min_length = 1000
        max_length = 0

        for dictionary in self.dictionary_list:
            single_stat = self._get_words_stat(dictionary['data'])

            # aggregate data - if any
            if len(single_stat) > 0:
                words_count += single_stat['words_count']
                if single_stat['min_length'] < min_length:
                    min_length = single_stat['min_length']
                if single_stat['max_length'] > max_length:
                    max_length = single_stat['max_length']

                for key, value in single_stat['words_stat'].items():
                    if key in aggregated_words_stat.keys():
                        aggregated_words_stat[key] += value
                    else:
                        aggregated_words_stat.setdefault(key, value)

        # assemble information - if any
        if words_count > 0:
            words_info['words_count'] = words_count
            words_info['min_length'] = min_length
            words_info['max_length'] = max_length
            words_info['words_stat'] = aggregated_words_stat

        return words_info

    def get_letters_sets(self):
        return self.letters_sets

    def get_training_generator_schemes(self):
        '''Gets information on supported material generation schemes.

        Args:
            None

        Returns:
            dict: Dictionary (key, value)
                key -> material generation scheme identifier
                value -> scheme description for UI
        '''

        return self.training_generator_schemes

    def get_words_stat_filtered(self, min_length, max_length, letters_set, generator_scheme):
        """Gets words statistics containing words length and their number
            to visualize words set that can be used for training material generation.

        Args:
            min_length (int): Minimal words length  
            max_length (int): Maximal words length
            letters_set (str): Id of the letters set out of which words could be made up
                (check self.letters_sets)
            generator_scheme (str): Id of the geerator scheme to use
                (check self.training_generator_schemes)

        Returns:
            dict: Dictionary (key, words_by_key)
                key -> word length
                words_by_key -> number of words having the same length
        """

        words_stat = {}

        # parameters validation
        if min_length < 1 or max_length < min_length:
            return words_stat
        if letters_set not in self.letters_sets.keys():
            return words_stat
        if generator_scheme not in self.training_generator_schemes.keys():
            return words_stat

        # aggregate and filter words statistics
        for dictionary in self.dictionary_list:
            stat = self._get_words_stat(dictionary['data'])['words_stat']
            for word_len in stat.keys():
                # filter words length
                if word_len >= min_length and word_len <= max_length:
                    # update result
                    if word_len not in words_stat.keys():
                        words_stat[word_len] = stat[word_len]
                    else:
                        words_stat[word_len] += stat[word_len]

        return words_stat

    def get_ebook2cw_version_online(self):
        """Gets online ebook2cw version.

        Args:
            None

        Returns:
            str: "0" when service is not accessible, otherwise version string
        """

        return self.e2cw.get_executable_version_online()

    def get_ebook2cw_version_local(self):
        """Gets local ebook2cw version.

        Args:
            None

        Returns:
            str: "0" when program is not accessible, otherwise version string
        """

        return self.e2cw.get_executable_version_local()

    def get_ebook2cw(self, force_latest):
        """Downloads proper version of the ebook2cw
            performing MD5 verification for integrity check.

        Args:
            None

        Returns:
            bool: True when executable was downloaded, False otherwise
        """
        return self.e2cw.get_executable(force_latest)


def main():
    print("To be implemented...")


if __name__ == '__main__':
    main()
