import cwgen
import os
import sys
import subprocess

try:
    import PySimpleGUI as sg
except ImportError:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", 'PySimpleGUI'])
finally:
    import PySimpleGUI as sg


class CwGenUI:
    # GUI - window config
    WINDOW_DESCRIPTION = 'CW training files generator by SP6HFE'

    # GUI - button config
    FILE_BROWSE_KEY = '-ADD FILE-'
    FILE_REMOVE_KEY = '-REMOVE FILE-'

    # GUI - input config
    FILE_PATH_INPUT_KEY = '-FILE PATH-'

    # GUI - table config
    FILES_DATA_TABLE_KEY = '-FILES DATA-'

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
        # Members
        self.files_table_idx = -1
        self.cw_gen = cwgen.CwGen()

        # GUI - create building blocks
        files_operation = [sg.Input(enable_events=True, visible=False, key=self.FILE_PATH_INPUT_KEY),
                           sg.FileBrowse(button_text="Add", file_types=(
                               ("ALL Files", "*.*"), ("CWOPS sessions", "*.cwo")), target=self.FILE_PATH_INPUT_KEY, key=self.FILE_BROWSE_KEY),
                           sg.Button(button_text="Remove selected", key=self.FILE_REMOVE_KEY)]

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
                                     headings=[name for name, _size,
                                               _visible in files_data_header],
                                     col_widths=[size for _name, size,
                                                 _visible in files_data_header],
                                     visible_column_map=[
                                         visible for _name, _size, visible in files_data_header],
                                     num_rows=10,
                                     justification='left',
                                     auto_size_columns=False,
                                     enable_events=True,
                                     key=self.FILES_DATA_TABLE_KEY
                                     )]

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

        left_col = [[sg.Frame('Dictionaries', [files_operation, files_data_table])],
                    [sg.Frame('Words letters count range', [letters_min, letters_max])]]

        right_col = []

        # App layout
        layout = [[sg.Column(left_col), sg.VSeparator(), sg.Column(right_col)]]

        # Configure and create the window
        self.window = sg.Window(self.WINDOW_DESCRIPTION, layout)

    def handle_dictionary_add(self, values):
        # on file selection cancel values[FILE_PATH_INPUT_KEY] is empty
        if len(values[self.FILE_PATH_INPUT_KEY]) > 0:
            file_path = os.path.normpath(values[self.FILE_PATH_INPUT_KEY])
            if os.path.isfile(file_path):
                file_name = os.path.basename(file_path)
                current_files_data = self.window[self.FILES_DATA_TABLE_KEY].get(
                )
                # file name should be distinct
                if file_name not in [row[0] for row in current_files_data]:
                    file_stat = self.cw_gen.get_dictionary_stat(file_path)
                    # add file when parsed properly
                    if file_stat[0] > 0:
                        current_files_data.append(
                            [file_name, file_path, file_stat[0], file_stat[1], file_stat[2], file_stat[3]])
                        self.window[self.FILES_DATA_TABLE_KEY].update(
                            values=current_files_data)
                        self.update_words_length_sliders_config(
                            values, self.calculate_words_length_range())
        # clear file path storage to properly handle CANCEL situation
        self.window[self.FILE_PATH_INPUT_KEY].update(value="")

    def handle_dictionary_delete(self, values):
        # self.files_table_idx == -1 when no dictionary in the table is selected
        if self.files_table_idx >= 0:
            updated_files_data = []
            current_files_data = self.window[self.FILES_DATA_TABLE_KEY].get()
            # locate and remove data related to selected record in the files table
            for idx, _files_data in enumerate(current_files_data):
                if idx is not self.files_table_idx:
                    updated_files_data.append(current_files_data[idx])
            self.window[self.FILES_DATA_TABLE_KEY].update(
                values=updated_files_data)
            self.update_words_length_sliders_config(
                values, self.calculate_words_length_range())
            # set table index to negative to properly handle dictionary remove button click
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

    def calculate_words_length_range(self):
        letters_min_count = 0
        letters_max_count = 0
        current_files_data = self.window[self.FILES_DATA_TABLE_KEY].get()

        if len(current_files_data) > 0:
            letters_min_count = 1000
            for _name, _path, _length, letters_min, letters_max, _stat in current_files_data:
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
