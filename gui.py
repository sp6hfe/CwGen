import PySimpleGUI as sg
import cwgen
import os

sg.theme('Default1')

# Left column - input data
left_col = [
            [sg.Input(enable_events=True, visible=False, key='_file_to_add_'),
             sg.FileBrowse(button_text="Add dictionary", file_types=(("ALL Files", "*.*"),("CWOPS sessions", "*.cwo")), target='_file_to_add_', key='-ADD FILE-'),
             sg.Button(button_text="Remove selected", key='-REMOVE FILE-')],
            [sg.Frame('Dictionaries', [[sg.Listbox(values=[], select_mode="LISTBOX_SELECT_MODE_MULTIPLE", disabled=True , size=(50, 10), key=('-FILE NAMES-'))], [sg.Listbox(values=[], visible=False, key='-FILE PATHS-')]])]
           ]

# Right column - config based on data
right_col = [[sg.T('TEST')]]

# App layout
layout = [[sg.Column(left_col), sg.VSeparator(), sg.Column(right_col)]]

# Create the window
window = sg.Window('CW generator GUI', layout)

# Display and interact with the Window using an Event Loop
while True:
    event, values = window.read()
    # See if user wants to quit or window was closed
    if event == sg.WINDOW_CLOSED:
        break

    # Add a dictionary to the list
    if event == '_file_to_add_':
        file_path, file_name = os.path.split(values['_file_to_add_'])
        current_file_names = window['-FILE NAMES-'].get_list_values()
        current_file_paths = window['-FILE PATHS-'].get_list_values()
        if file_name not in current_file_names:
            current_file_names.append(file_name)
            current_file_paths.append(file_path)
            window['-FILE NAMES-'].update(disabled=False, values=current_file_names)
            window['-FILE PATHS-'].update(disabled=False, values=current_file_paths)

    # remove dictionary from the list
    if event == '-REMOVE FILE-':
        selected_files_indexes = window['-FILE NAMES-'].get_indexes()
        if len(selected_files_indexes) > 0:
            updated_file_names = []
            updated_file_paths = []
            current_file_names = window['-FILE NAMES-'].get_list_values()
            for index, file_name in enumerate(current_file_names):
                if index not in selected_files_indexes:
                    updated_file_names.append(current_file_names[index]) 
                    updated_file_paths.append(current_file_paths[index]) 
            window['-FILE NAMES-'].update(disabled=False, values=updated_file_names)
            window['-FILE PATHS-'].update(disabled=False, values=current_file_paths)

# Finish up by removing from the screen
window.close()