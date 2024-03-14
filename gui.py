#gui.py
from pathlib import Path
import PySimpleGUI as sg

sg.theme('Dark Blue 3')
layout1 = [[sg.Text('Fluorescent ',
                    size=(12,1), 
                    font=('Helvetica Bold', 16),
                    expand_x=True,),
                    sg.Input(key='-fluoro_path-'),
                    sg.FolderBrowse()],
            [sg.Text('Light',
                    size=(12,1), 
                    font=('Helvetica Bold', 16),
                    expand_x=True,),
                    sg.Input(key='-light_path-'),
                    sg.FolderBrowse()],
            [sg.Text('Output',
                    size=(12,1),
                    font=('Helvetica Bold', 16),
                    expand_x=True,),
                    sg.Input(key='-output_path-'),
                    sg.FolderBrowse()],
            [sg.Button('Go'), sg.Button('Cancel')],
            ]   

window1 = sg.Window('Folder Selection',
                    layout1,
                    size=(715,250),
                    auto_size_buttons=True,
                    element_justification='l')
window2_active=False


while True:             
    event1, values1 = window1.read()
    if event1 == sg.WIN_CLOSED:
        break
    elif event1 == 'Cancel':
        break
    elif event1 == 'Go':
        fluoro_path = str(values1['-fluoro_path-'])
        light_path = str(values1['-light_path-'])
        output_path = str(values1['-output_path-'])

        layout2 = [[sg.Text('You selected these folders:',
                    #size = (12,1),
                    font=('Helvetica Bold', 20),
                    expand_x=True,)],
            [sg.Text(fluoro_path,
                    #size=(12,1), 
                    font=('Helvetica Bold', 16),
                    expand_x=True,)],
            [sg.Text(light_path,
                    #size=(12,1), 
                    font=('Helvetica Bold', 16),
                    expand_x=True,)],
            [sg.Text(output_path,
                    #size=(12,1),
                    font=('Helvetica Bold', 16),
                    expand_x=True,)],
            [sg.Button('Continue'), sg.Button('Exit')],
                  ]
        
        window2 = sg.Window('Folders Selected',
                            layout2)
        
        window2.active = True
        window1.hide()

        while True:
            event2, values2 = window2.read()
            if event2 == sg.WIN_CLOSED:
                break
            elif event2 == 'Exit':
                fluoro_path = ""
                light_path = ""
                output_path = ""
                window1.Close()
                window1.active = False
                window2.Close()
                window2.active = False
                break
            elif event2 == 'Continue':
                window2.Close()
                window2.active = False
                window1.Close()
                window1.active = False
                break


def window2():

    tab1_layout =  [[sg.T('This is inside tab 1')]]    

    tab2_layout = [[sg.T('This is inside tab 2')],    
            [sg.In(key='in')]]    

    layout = [[sg.TabGroup([[sg.Tab('Tab 1', tab1_layout, tooltip='tip'), sg.Tab('Tab 2', tab2_layout)]], tooltip='TIP2')],    
        [sg.Button('Read')]]    

    window = sg.Window('My window with tabs', layout, default_element_size=(12,1))    

    while True:    
        event, values = window.read()    
        print(event,values)    
        if event == sg.WIN_CLOSED:           
            break  

