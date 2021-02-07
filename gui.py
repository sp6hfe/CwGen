import PySimpleGUI as sg
import cwgen
import os

class UserInterface:
    # GUI - window config
    WINDOW_DESCRIPTION = 'CW training files generator by SP6HFE'

    # GUI - button config
    FILE_BROWSE_KEY = '-ADD FILE-'
    FILE_REMOVE_KEY = '-REMOVE FILE-'

    # GUI - input config
    FILE_PATH_INPUT_KEY = '-FILE PATH-'

    # GUI - table config
    FILES_DATA_TABLE_KEY = '-FILES DATA-'

    # GUI - listbox config
    FILES_LISTBOX_WIDTH = 40
    FILES_LISTBOX_HEIGHT = 10
    FILE_NAMES_KEY = '-FILE NAMES-'
    FILE_PATHS_KEY = '-FILE PATHS-'
    FILE_STATS_KEY = '-FILE STATS-'

    # GUI - sliders config
    H_SLIDER_WIDTH = 21
    H_SLIDER_HEIGHT = 10
    LETTERS_MIN_KEY = '-LETTERS MIN-'
    LETTERS_MAX_KEY = '-LETTERS MAX-'
    LETTERS_MIN_RANGE_START_KEY = '-LETTERS MIN RANGE START-'
    LETTERS_MIN_RANGE_STOP_KEY = '-LETTERS MIN RANGE STOP-'
    LETTERS_MAX_RANGE_START_KEY = '-LETTERS MAX RANGE START-'
    LETTERS_MAX_RANGE_STOP_KEY = '-LETTERS MAX RANGE STOP-'

    def __init__(self):
        # State variables
        self.files_table_idx = -1

        # GUI - create building blocks
        files_operation = [sg.Input(enable_events=True, visible=False, key=self.FILE_PATH_INPUT_KEY),
                        sg.FileBrowse(button_text="Add", file_types=(("ALL Files", "*.*"),("CWOPS sessions", "*.cwo")), target=self.FILE_PATH_INPUT_KEY, key=self.FILE_BROWSE_KEY),
                        sg.Button(button_text="Remove selected", key=self.FILE_REMOVE_KEY)]

        files_data = [sg.Listbox(values=[], select_mode="LISTBOX_SELECT_MODE_SINGLE", size=(self.FILES_LISTBOX_WIDTH, self.FILES_LISTBOX_HEIGHT), key=(self.FILE_NAMES_KEY)),
                    sg.Listbox(values=[], visible=False, key='-FILE PATHS-'),
                    sg.Listbox(values=[], visible=False, key='-FILE STATS-')]

        # GUI - header columns -> name, column size, visible?
        files_data_header = [
            ("Name",   20, True),
            ("Path",    0, False),
            ("Words",   6, True),
            ("Min len", 7, True),
            ("Max len", 7, True),
            ("Stat",    0, False)
        ]

        files_data_table = [sg.Table(values=[],
                                    headings=[name for name, _size, _visible in files_data_header],
                                    col_widths=[size for _name, size, _visible in files_data_header],
                                    visible_column_map=[visible for _name, _size, visible in files_data_header],
                                    num_rows=10,
                                    justification='left',
                                    auto_size_columns=False,
                                    enable_events=True,
                                    key=self.FILES_DATA_TABLE_KEY
                                    )]

        letters_min = [sg.Text("MIN:", size=(4, 1)),
                    sg.Text("0", size=(2,1), key=self.LETTERS_MIN_RANGE_START_KEY),
                    sg.Slider(range=(0, 0), size=(self.H_SLIDER_WIDTH, self.H_SLIDER_HEIGHT), orientation='h', enable_events=True, key=self.LETTERS_MIN_KEY),
                    sg.Text("0", size=(2,1), key=self.LETTERS_MIN_RANGE_STOP_KEY)]

        letters_max = [sg.Text("MAX:", size=(4, 1)),
                    sg.Text("0", size=(2,1), key=self.LETTERS_MAX_RANGE_START_KEY),
                    sg.Slider(range=(0, 0), size=(self.H_SLIDER_WIDTH, self.H_SLIDER_HEIGHT), orientation='h', enable_events=True, key=self.LETTERS_MAX_KEY),
                    sg.Text("0", size=(2,1), key=self.LETTERS_MAX_RANGE_STOP_KEY)]

        left_col = [[sg.Frame('Dictionaries', [files_operation, files_data_table, files_data])],
                    [sg.Frame('Words letters count range', [letters_min, letters_max])]]

        right_col = []

        # App layout
        layout = [[sg.Column(left_col), sg.VSeparator(), sg.Column(right_col)]]

        # Configure and create the window
        sg.theme('Default1')
        self.window = sg.Window(self.WINDOW_DESCRIPTION, layout)

    def handle_dictionary_add(self, values):
            # on file selection cancel values[FILE_PATH_INPUT_KEY] is empty
            if len(values[self.FILE_PATH_INPUT_KEY]) > 0:
                file_path = os.path.normpath(values[self.FILE_PATH_INPUT_KEY])
                if os.path.isfile(file_path):
                    file_path = os.path.normpath(values[self.FILE_PATH_INPUT_KEY])
                    file_name = os.path.basename(file_path)
                    current_file_names = self.window[self.FILE_NAMES_KEY].get_list_values()
                    current_file_paths = self.window[self.FILE_PATHS_KEY].get_list_values()
                    current_file_stats = self.window[self.FILE_STATS_KEY].get_list_values()
                    current_files_data = self.window[self.FILES_DATA_TABLE_KEY].get()
                    print(current_files_data)
                    # file name should be distinct
                    if file_name not in current_file_names:
                        # get file statistics to asses if it may be used
                        file_stat = cwgen.get_stat(file_path)
                        if file_stat[0] > 0:
                            current_file_names.append(file_name)
                            current_file_paths.append(file_path)
                            current_file_stats.append(file_stat)
                            current_files_data.append([file_name, file_path, file_stat[0], file_stat[1], file_stat[2], file_stat[3]])
                            self.window[self.FILE_NAMES_KEY].update(values=current_file_names)
                            self.window[self.FILE_PATHS_KEY].update(values=current_file_paths)
                            self.window[self.FILE_STATS_KEY].update(values=current_file_stats)
                            self.window[self.FILES_DATA_TABLE_KEY].update(values=current_files_data)
                            self.update_words_length_sliders_config(values, self.calculate_words_length_range(current_file_stats))
            # clear file path storage to properly handle CANCEL situation
            self.window[self.FILE_PATH_INPUT_KEY].update(value="")

    def handle_dictionary_delete(self, values):
            # selected_files_indexes = window[FILE_NAMES_KEY].get_indexes()
            # if len(selected_files_indexes) > 0:
            if self.files_table_idx >= 0:
                updated_file_names = []
                updated_file_paths = []
                updated_file_stats = []
                updated_files_data = []
                current_file_names = self.window[self.FILE_NAMES_KEY].get_list_values()
                current_file_paths = self.window[self.FILE_PATHS_KEY].get_list_values()
                current_file_stats = self.window[self.FILE_STATS_KEY].get_list_values()
                current_files_data = self.window[self.FILES_DATA_TABLE_KEY].get()
                # for file_index, _file_name in enumerate(current_file_names):
                for idx, _files_data in enumerate(current_files_data):
                    # if file_index not in selected_files_indexes:
                    if idx is not self.files_table_idx:
                        updated_file_names.append(current_file_names[idx])
                        updated_file_paths.append(current_file_paths[idx])
                        updated_file_stats.append(current_file_stats[idx])
                        updated_files_data.append(current_files_data[idx])
                self.window[self.FILE_NAMES_KEY].update(values=updated_file_names)
                self.window[self.FILE_PATHS_KEY].update(values=updated_file_paths)
                self.window[self.FILE_STATS_KEY].update(values=updated_file_stats)
                self.window[self.FILES_DATA_TABLE_KEY].update(values=updated_files_data)
                self.update_words_length_sliders_config(values, self.calculate_words_length_range(updated_file_stats))
                # set table index to negatove to properly handle dictionary remove button click
                self.files_table_idx = -1

    def handle_words_length_sliders(self, event, values):
        slider_min_val = values[self.LETTERS_MIN_KEY]
        slider_max_val = values[self.LETTERS_MAX_KEY]

        if event == self.LETTERS_MIN_KEY:
            if slider_min_val > slider_max_val:
                self.window[self.LETTERS_MAX_KEY].update(value=slider_min_val)
        if event == self.LETTERS_MAX_KEY:
            if slider_max_val < slider_min_val:
                self.window[self.LETTERS_MIN_KEY].update(value=slider_max_val)

    def calculate_words_length_range(self, words_stat):
        letters_min_count = 0
        letters_max_count = 0

        if len(words_stat) > 0:
            letters_min_count = 1000
            for _words_count, letters_min, letters_max, _stat in words_stat:
                if letters_min_count > letters_min:
                    letters_min_count = letters_min
                if letters_max_count < letters_max:
                    letters_max_count = letters_max

        return (letters_min_count, letters_max_count)

    def update_words_length_sliders_config(self, values, new_range):
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
        
        self.window[self.LETTERS_MIN_KEY].update(range=new_range, value=new_min_val)
        self.window[self.LETTERS_MAX_KEY].update(range=new_range, value=new_max_val)
        self.window[self.LETTERS_MIN_RANGE_START_KEY].update(value=new_range_min)
        self.window[self.LETTERS_MIN_RANGE_STOP_KEY].update(value=new_range_max)
        self.window[self.LETTERS_MAX_RANGE_START_KEY].update(value=new_range_min)
        self.window[self.LETTERS_MAX_RANGE_STOP_KEY].update(value=new_range_max)

    def handleGui(self):
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
        if (event == self.LETTERS_MIN_KEY) or (event == self.LETTERS_MAX_KEY) :
            self.handle_words_length_sliders(event, values)

        return True

# Start the GUI
ui = UserInterface()

# Display and interact with the GUI using an Event Loop
while ui.handleGui(): pass
