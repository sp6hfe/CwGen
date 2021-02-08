import os
import sys

dict_dir_name = "ispell-pl-20021127"


class CwGen:

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


def main():
    test_dict = "A"

    cw_gen = CwGen()

    script_path = os.path.dirname(sys.argv[0])
    dict_path = os.path.join(os.path.dirname(
        script_path), dict_dir_name, test_dict)

    words_stat = cw_gen.get_dictionary_stat(dict_path)
    print(words_stat)


if __name__ == '__main__':
    main()
