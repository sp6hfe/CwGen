import cwgen
import os
import sys

import PySimpleGUI as sg


class CwGenUI:
    # GUI - window config
    WINDOW_DESCRIPTION = 'CW training material generator by SP6HFE'

    # GUI - text config
    E2CW_VER_LOCAL_KEY = '-E2CW VER LOCAL-'
    E2CW_VER_ONLINE_KEY = '-E2CW VER ONLINE-'

    # GUI - button config
    FILE_BROWSE_KEY = '-ADD FILE-'
    FILE_REMOVE_KEY = '-REMOVE FILE-'
    E2CW_DOWNLOAD_KEY = '-E2CW DOWNLOAD-'

    # GUI - input config
    FILE_PATH_INPUT_KEY = '-FILE PATH-'

    # GUI - table config
    FILES_DATA_TABLE_KEY = '-FILES DATA-'
    WORDS_FILTERED_TABLE_KEY = '-WORDS FILTERED-'

    # GUI - sliders config
    H_SLIDER_WIDTH = 21
    H_SLIDER_HEIGHT = 10
    LETTERS_MIN_KEY = '-LETTERS MIN-'
    LETTERS_MAX_KEY = '-LETTERS MAX-'
    LETTERS_MIN_RANGE_START_KEY = '-LETTERS MIN RANGE START-'
    LETTERS_MIN_RANGE_STOP_KEY = '-LETTERS MIN RANGE STOP-'
    LETTERS_MAX_RANGE_START_KEY = '-LETTERS MAX RANGE START-'
    LETTERS_MAX_RANGE_STOP_KEY = '-LETTERS MAX RANGE STOP-'
    E2CW_WPM_KEY = '-E2CW WPM-'
    E2CW_WPM_RANGE_START_KEY = '-E2CW WPM RANGE START-'
    E2CW_WPM_RANGE_STOP_KEY = '-E2CW WPM RANGE STOP-'
    E2CW_FARNS_KEY = '-E2CW FARNS-'
    E2CW_FARNS_RANGE_START_KEY = '-E2CW FARNS RANGE START-'
    E2CW_FARNS_RANGE_STOP_KEY = '-E2CW FARNS RANGE STOP-'
    E2CW_PITCH_KEY = '-E2CW PITCH-'
    E2CW_PITCH_RANGE_START_KEY = '-E2CW PITCH RANGE START-'
    E2CW_PITCH_RANGE_STOP_KEY = '-E2CW PITCH RANGE STOP-'

    # GUI - combo config
    COMBO_LETTERS_SET_KEY = '-LETTERS SET-'
    COMBO_MATERIAL_GENERATION_KEY = '-MATERIAL GENERATION-'

    def __init__(self):
        """Class initialization"""

        # Members
        self.files_table_idx = -1
        self.cw_gen = cwgen.CwGen()
        self.letters_sets = self.cw_gen.get_letters_sets()
        self.training_generator_schemes = self.cw_gen.get_training_generator_schemes()

        ebook2cw_version_local = self.cw_gen.get_ebook2cw_version_local()
        ebook2cw_version_online = self.cw_gen.get_ebook2cw_version_online()

        # GUI - header columns -> name, column size, visible?
        files_data_header = [
            ("UUID",       0, False),
            ("File name", 20, True),
            ("Words",      6, True),
            ("Min len",    7, True),
            ("Max len",    7, True)
        ]

        words_filtered_header = [
            ("Word length", 15, True),
            ("Count",       15, True)
        ]

        # GUI - tables
        files_data_table = [sg.Table(values=[],
                                     headings=[name for name, _size,
                                               _visible in files_data_header],
                                     col_widths=[size for _name, size,
                                                 _visible in files_data_header],
                                     visible_column_map=[
                                         visible for _name, _size, visible in files_data_header],
                                     num_rows=5,
                                     justification='left',
                                     auto_size_columns=False,
                                     enable_events=True,
                                     key=self.FILES_DATA_TABLE_KEY
                                     )]

        words_filtered_table = [sg.Table(values=[],
                                         headings=[
                                             name for name, _size, _visible in words_filtered_header],
                                         col_widths=[
                                             size for _name, size, _visible in words_filtered_header],
                                         num_rows=5,
                                         justification='left',
                                         auto_size_columns=False,
                                         key=self.WORDS_FILTERED_TABLE_KEY)]

        # GUI - rows
        files_operation = [sg.Input(enable_events=True, visible=False, key=self.FILE_PATH_INPUT_KEY),
                           sg.FileBrowse(button_text="Add", file_types=(
                               ("ALL Files", "*.*"), ("CWOPS sessions", "*.cwo")), target=self.FILE_PATH_INPUT_KEY, key=self.FILE_BROWSE_KEY),
                           sg.Button(button_text="Remove selected", key=self.FILE_REMOVE_KEY)]

        letters_min = [sg.Text("MIN:", size=(4, 1)),
                       sg.Text("0", size=(2, 1),
                               key=self.LETTERS_MIN_RANGE_START_KEY),
                       sg.Slider(range=(0, 0), size=(self.H_SLIDER_WIDTH, self.H_SLIDER_HEIGHT),
                                 orientation='h', enable_events=True, key=self.LETTERS_MIN_KEY),
                       sg.Text("0", size=(2, 1), key=self.LETTERS_MIN_RANGE_STOP_KEY)]

        letters_max = [sg.Text("MAX:", size=(4, 1)),
                       sg.Text("0", size=(2, 1),
                               key=self.LETTERS_MAX_RANGE_START_KEY),
                       sg.Slider(range=(0, 0), size=(self.H_SLIDER_WIDTH, self.H_SLIDER_HEIGHT),
                                 orientation='h', enable_events=True, key=self.LETTERS_MAX_KEY),
                       sg.Text("0", size=(2, 1), key=self.LETTERS_MAX_RANGE_STOP_KEY)]

        letters_set = [sg.Text('From set:'),
                       sg.Combo(values=([name for _id, name in self.letters_sets.items()]),
                                default_value=list(
                                    self.letters_sets.items())[0][1],
                                size=(max(len(name)
                                          for _id, name in self.letters_sets.items()), 1),
                                readonly=True,
                                enable_events=True,
                                key=self.COMBO_LETTERS_SET_KEY)]

        generator_scheme = [sg.Text('Using scheme:'),
                            sg.Combo(values=([name for _id, name in self.training_generator_schemes.items()]),
                                     default_value=list(
                                         self.training_generator_schemes.items())[0][1],
                                     size=(
                                         max(len(name) for _id, name in self.training_generator_schemes.items()), 1),
                                     readonly=True,
                                     enable_events=True,
                                     key=self.COMBO_MATERIAL_GENERATION_KEY)]

        e2cw_ver_local = [sg.Text('Local:', size=(7, 1)),
                          sg.Text(ebook2cw_version_local, key=self.E2CW_VER_LOCAL_KEY)]

        e2cw_ver_online = [sg.Text('Online:', size=(7, 1)),
                           sg.Text(ebook2cw_version_online, key=self.E2CW_VER_ONLINE_KEY)]

        e2cw_download_button = [
            sg.Button('Download / Update', key=self.E2CW_DOWNLOAD_KEY)]

        e2cw_wpm = [sg.Text("WPM:", size=(6, 1)),
                    sg.Text("0", size=(2, 1),
                            key=self.E2CW_WPM_RANGE_START_KEY),
                    sg.Slider(range=(0, 0), size=(self.H_SLIDER_WIDTH, self.H_SLIDER_HEIGHT),
                              orientation='h', enable_events=True, key=self.E2CW_WPM_KEY),
                    sg.Text("0", size=(2, 1), key=self.E2CW_WPM_RANGE_STOP_KEY)]

        e2cw_farns = [sg.Text("FARNS:", size=(6, 1)),
                      sg.Text("0", size=(2, 1),
                              key=self.E2CW_FARNS_RANGE_START_KEY),
                      sg.Slider(range=(0, 0), size=(self.H_SLIDER_WIDTH, self.H_SLIDER_HEIGHT),
                                orientation='h', enable_events=True, key=self.E2CW_FARNS_KEY),
                      sg.Text("0", size=(2, 1), key=self.E2CW_FARNS_RANGE_STOP_KEY)]

        e2cw_pitch = [sg.Text("PITCH:", size=(6, 1)),
                      sg.Text("0", size=(2, 1),
                              key=self.E2CW_PITCH_RANGE_START_KEY),
                      sg.Slider(range=(0, 0), size=(self.H_SLIDER_WIDTH, self.H_SLIDER_HEIGHT),
                                orientation='h', enable_events=True, key=self.E2CW_PITCH_KEY),
                      sg.Text("0", size=(2, 1), key=self.E2CW_PITCH_RANGE_STOP_KEY)]

        # GUI - columns
        left_col = [
            [sg.Frame('Dictionaries', [files_operation, files_data_table])],
            [sg.Frame('Letters selection', [letters_set])],
            [sg.Frame('Words length', [letters_min, letters_max])],
            [sg.Frame('Material generation', [generator_scheme])],
            [sg.Frame('Training material', [words_filtered_table])]]

        right_col = [
            [sg.Frame('Ebook2CW version', [e2cw_ver_local,
                                           e2cw_ver_online, e2cw_download_button])],
            [sg.Frame('Audible parameters', [e2cw_wpm, e2cw_farns, e2cw_pitch])]]

        # App layout
        layout = [[sg.Column(left_col), sg.VSeparator(), sg.Column(right_col)]]

        # Configure and create the window
        self.window = sg.Window(self.WINDOW_DESCRIPTION, layout)

    def _update_ui(self, values):
        """Updates UI according to the data collected by cwgen

        Args:
            values (dict): Dictionary containing GUI event values

        Returns:
            None
        """

        table_data = []
        sliders_range = (0, 0)

        # get information related to already loaded data
        dictionaries_info = self.cw_gen.get_dictionaries_info()
        words_info = self.cw_gen.get_words_info()

        # generate updated data for UI elements
        if len(dictionaries_info) > 0:
            for dictionary_data in dictionaries_info:
                row = [dictionary_data['uuid'],
                       dictionary_data['name'],
                       dictionary_data['stat']['words_count'],
                       dictionary_data['stat']['min_length'],
                       dictionary_data['stat']['max_length']]
                table_data.append(row)

            if len(words_info) > 0:
                sliders_range = (words_info['min_length'],
                                 words_info['max_length'])

        # update UI
        self.window[self.FILES_DATA_TABLE_KEY].update(
            values=table_data)
        words_min_length, words_max_length = self.update_words_length_sliders_config(
            values, (sliders_range))
        self._update_words_stat(values, words_min_length, words_max_length)

    def _update_words_stat(self, values, min_length, max_length):
        '''Updates words stat with filtered result
            which allow user to see the data out of which
            training material could be generated.

        Args:
            values (dict): Dictionary containing GUI event values
            min_length (int): Minimal words length
            max_length (int): Maximal words length

        Returns:
            None
        '''

        # get filtered words stat
        words_stat = self.cw_gen.get_words_stat_filtered(
            min_length, max_length)

        # assemble summary table
        stat = []
        for key in sorted(words_stat.keys()):
            stat.append([key, words_stat[key]])

        # update UI
        self.window[self.WORDS_FILTERED_TABLE_KEY].update(values=stat)

    def handle_dictionary_add(self, values):
        """Handle new dictionary addition
            by passing file path to cwgen. UI gets updated.

        Args:
            values (dict): Dictionary containing GUI event values

        Returns:
            None
        """

        # on file selection cancel values[FILE_PATH_INPUT_KEY] is empty
        if len(values[self.FILE_PATH_INPUT_KEY]) > 0:
            file_path = os.path.normpath(values[self.FILE_PATH_INPUT_KEY])
            if os.path.isfile(file_path):
                if self.cw_gen.add_dictionary(file_path):
                    self._update_ui(values)

            # clear file path storage to properly handle CANCEL situation
            self.window[self.FILE_PATH_INPUT_KEY].update(value="")

    def handle_dictionary_delete(self, values):
        """Handle dictionary deletion
            by passing its generated UUID to cwgen. UI gets updated.

        Args:
            values (dict): Dictionary containing GUI event values

        Returns:
            None
        """
        # self.files_table_idx == -1 when no dictionary in the table is selected
        if self.files_table_idx >= 0:
            table_data = self.window[self.FILES_DATA_TABLE_KEY].get()
            selected_dictionary_uuid = table_data[self.files_table_idx][0]
            if self.cw_gen.remove_dictionary(selected_dictionary_uuid):
                self._update_ui(values)

            # set table index to negative to properly handle dictionary remove button click
            self.files_table_idx = -1

    def handle_words_length_sliders(self, event, values):
        """Handle words length sliders movement
            to not let their values become ridiculous.
            It also updates words statistics table.

        Args:
            event (str): GUI event name
            values (dict): Dictionary containing GUI event values

        Returns:
            None
        """

        # get current positions
        slider_min_val = values[self.LETTERS_MIN_KEY]
        slider_max_val = values[self.LETTERS_MAX_KEY]

        # update them if needed
        if event == self.LETTERS_MIN_KEY:
            if slider_min_val > slider_max_val:
                slider_max_val = slider_min_val
                self.window[self.LETTERS_MAX_KEY].update(
                    value=slider_max_val)
        if event == self.LETTERS_MAX_KEY:
            if slider_max_val < slider_min_val:
                slider_min_val = slider_max_val
                self.window[self.LETTERS_MIN_KEY].update(
                    value=slider_min_val)

        # trigger words statistics calculation
        self._update_words_stat(values, slider_min_val, slider_max_val)

    def update_words_length_sliders_config(self, values, new_range):
        """Updates UI part related to words length sliders change their range
            assuring that sliders values gets updated when needed

        Args:
            values (dict): Dictionary containing GUI event values
            new_range (tuple): New value range

        Returns:
            new_min_val, new_max_val (tuple): Updated words length sliders values
        """

        current_range_min, current_range_max = self.window[self.LETTERS_MIN_KEY].Range
        current_min_val = int(values[self.LETTERS_MIN_KEY])
        current_max_val = int(values[self.LETTERS_MAX_KEY])

        new_range_min, new_range_max = new_range
        new_min_val = current_min_val
        new_max_val = current_max_val

        # range min value may affect sliders position
        if new_range_min > current_range_min:
            if new_range_min > current_min_val:
                new_min_val = new_range_min
            if new_min_val > current_max_val:
                new_max_val = new_min_val
        # range max value may affect sliders position
        if new_range_max < current_range_max:
            if new_range_max < current_max_val:
                new_max_val = new_range_max
            if new_max_val < current_min_val:
                new_min_val = new_max_val

        self.window[self.LETTERS_MIN_KEY].update(
            range=new_range, value=new_min_val)
        self.window[self.LETTERS_MAX_KEY].update(
            range=new_range, value=new_max_val)
        self.window[self.LETTERS_MIN_RANGE_START_KEY].update(
            value=new_range_min)
        self.window[self.LETTERS_MIN_RANGE_STOP_KEY].update(
            value=new_range_max)
        self.window[self.LETTERS_MAX_RANGE_START_KEY].update(
            value=new_range_min)
        self.window[self.LETTERS_MAX_RANGE_STOP_KEY].update(
            value=new_range_max)

        return (new_min_val, new_max_val)

    def handleGui(self):
        """GUI main loop
            where all events gets dispatched for handling

        Args:
            None

        Returns:
            None
        """

        event, values = self.window.read()
        # See if user wants to quit or window was closed
        if event == sg.WINDOW_CLOSED:
            self.window.close()
            return False

        # Remember index of selected table row
        if event == self.FILES_DATA_TABLE_KEY:
            self.files_table_idx = values[self.FILES_DATA_TABLE_KEY][0]

        # Add a dictionary to the list
        if event == self.FILE_PATH_INPUT_KEY:
            self.handle_dictionary_add(values)

        # remove dictionary from the list
        if event == self.FILE_REMOVE_KEY:
            self.handle_dictionary_delete(values)

        # handle words length change
        if (event == self.LETTERS_MIN_KEY) or (event == self.LETTERS_MAX_KEY):
            self.handle_words_length_sliders(event, values)

        return True


# UI theming
sg.theme('Default1')

# Start the GUI
ui = CwGenUI()

# Display and interact with the GUI using an Event Loop
while ui.handleGui():
    pass

# Game over
del ui
