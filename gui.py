import PySimpleGUI as sg
import cwgen
import os

# window config
WINDOW_DESCRIPTION = 'CW training files generator by SP6HFE'

# button config
FILE_BROWSE_KEY = '-ADD FILE-'
FILE_REMOVE_KEY = '-REMOVE FILE-'

# input config
FILE_PATH_INPUT_KEY = '_file_to_add_'

# listbox config
FILES_LISTBOX_WIDTH = 40
FILES_LISTBOX_HEIGHT = 10
FILE_NAMES_KEY = '-FILE NAMES-'
FILE_PATHS_KEY = '-FILE PATHS-'

# sliders config
H_SLIDER_WIDTH = 28
H_SLIDER_HEIGHT = 10
LETTERS_MIN_KEY = '-LETTERS MIN-'
LETTERS_MAX_KEY = '-LETTERS MAX-'

def handle_dictionary_add(window, values):
        # on file selection cancel values[FILE_PATH_INPUT_KEY] is empty
        if len(values[FILE_PATH_INPUT_KEY]) > 0:
            file_path = os.path.normpath(values[FILE_PATH_INPUT_KEY])
            file_name = os.path.basename(file_path)
            current_file_names = window[FILE_NAMES_KEY].get_list_values()
            current_file_paths = window[FILE_PATHS_KEY].get_list_values()
            if file_name not in current_file_names:
                current_file_names.append(file_name)
                current_file_paths.append(file_path)
                window[FILE_NAMES_KEY].update(disabled=False, values=current_file_names)
                window[FILE_PATHS_KEY].update(disabled=False, values=current_file_paths)
        # clear file path storage to properly handle CANCEL situation
        window[FILE_PATH_INPUT_KEY].update(value="")

def handle_dictionary_delete(window, values):
        selected_files_indexes = window[FILE_NAMES_KEY].get_indexes()
        if len(selected_files_indexes) > 0:
            updated_file_names = []
            updated_file_paths = []
            current_file_names = window[FILE_NAMES_KEY].get_list_values()
            current_file_paths = window[FILE_PATHS_KEY].get_list_values()
            for index, file_name in enumerate(current_file_names):
                if index not in selected_files_indexes:
                    updated_file_names.append(current_file_names[index]) 
                    updated_file_paths.append(current_file_paths[index]) 
            window[FILE_NAMES_KEY].update(disabled=False, values=updated_file_names)
            window[FILE_PATHS_KEY].update(disabled=False, values=updated_file_paths)

def handle_words_length_sliders(event, values):
    min_val = values[LETTERS_MIN_KEY]
    max_val = values[LETTERS_MAX_KEY]

    if event == LETTERS_MIN_KEY:
        if min_val > max_val:
            window[LETTERS_MAX_KEY].update(value=min_val)
    if event == LETTERS_MAX_KEY:
        if max_val < min_val:
            window[LETTERS_MIN_KEY].update(value=max_val)
# window theme
sg.theme('Default1')

# window building blocks
files_operation = [sg.Input(enable_events=True, visible=False, key=FILE_PATH_INPUT_KEY),
                       sg.FileBrowse(button_text="Add new", file_types=(("ALL Files", "*.*"),("CWOPS sessions", "*.cwo")), target=FILE_PATH_INPUT_KEY, key=FILE_BROWSE_KEY),
                       sg.Button(button_text="Remove selected", key=FILE_REMOVE_KEY)]

files_data = [sg.Listbox(values=[], select_mode="LISTBOX_SELECT_MODE_MULTIPLE", disabled=True , size=(FILES_LISTBOX_WIDTH, FILES_LISTBOX_HEIGHT), key=(FILE_NAMES_KEY)), sg.Listbox(values=[], visible=False, key='-FILE PATHS-')]

letters_min = [sg.Text("MIN", size=(4, 1)), sg.Slider(size=(H_SLIDER_WIDTH, H_SLIDER_HEIGHT), orientation='h', enable_events=True, key=LETTERS_MIN_KEY)]

letters_max = [sg.Text("MAX", size=(4, 1)), sg.Slider(size=(H_SLIDER_WIDTH, H_SLIDER_HEIGHT), orientation='h', enable_events=True, key=LETTERS_MAX_KEY)]

left_col = [[sg.Frame('Dictionaries', [files_operation, files_data])],
            [sg.Frame('Words letters count', [letters_min, letters_max])]]

right_col = [[sg.T('TEST')]]

# App layout
layout = [[sg.Column(left_col), sg.VSeparator(), sg.Column(right_col)]]

# Create the window
window = sg.Window(WINDOW_DESCRIPTION, layout)

# Display and interact with the Window using an Event Loop
while True:
    event, values = window.read()
    # See if user wants to quit or window was closed
    if event == sg.WINDOW_CLOSED:
        break

    # Add a dictionary to the list
    if event == FILE_PATH_INPUT_KEY:
        handle_dictionary_add(window, values)

    # remove dictionary from the list
    if event == FILE_REMOVE_KEY:
        handle_dictionary_delete(window, values)

    # handle words length change
    if (event == LETTERS_MIN_KEY) or (event == LETTERS_MAX_KEY) :
        handle_words_length_sliders(event, values)

# Finish up by removing from the screen
window.close()