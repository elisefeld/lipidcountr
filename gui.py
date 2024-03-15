#gui.py
import numpy as np
import cv2 as cv
import csv
from pathlib import Path
import PySimpleGUI as sg


#GUI
sg.theme('Dark')
sg.set_options(element_padding = (0,0))   

def make_input():
     layout_input = [[sg.Text('Fluorescent',
                    pad = ((3,0),0),
                    size = (12,1), 
                    font = ('Georgia', 16)),
                    sg.Input(key = '-fluoro_path-'),
                    sg.FolderBrowse(font = ('Georgia', 12), pad = ((10,10),5))],
            [sg.Text('Light',
                    pad = ((3,0),0),
                    size = (12,1), 
                    font = ('Georgia', 16)),
                    sg.Input(key = '-light_path-'),
                    sg.FolderBrowse(font = ('Georgia', 12), pad = ((10,10),5))],
            [sg.Text('Output',
                    pad = ((3,0),0),
                    size = (12,1),
                    font = ('Georgia', 16)),
                    sg.Input(key = '-output_path-'),
                    sg.FolderBrowse(font = ('Georgia', 12), pad = ((10,10),5))],
            [sg.Text('File Name',
                    pad = ((3,0),0),
                    size = (12,1),
                    font = ('Georgia', 16)),
                    sg.Input(key = '-file_name-')],
            
            [sg.Help(font = ('Georgia', 12),
                     button_color = ('white', 'springgreen4'),
                     pad = ((3,0),5)),
            sg.Push(),
                 sg.Submit(font = ('Georgia', 12),
                           button_color = ('white', 'springgreen4'),
                           pad = ((3,0),5)),
                 sg.Cancel(font = ('Georgia', 12),
                           button_color = ('white', 'firebrick3'),
                           pad = ((3,0),5))],
            ]
     return sg.Window('Folder Selection',
                    layout_input,
                    auto_size_buttons=False,
                    element_justification='l',
                    finalize = True)

def make_help():
   layout_help = [[sg.Text('Fluorescent: Select the folder containing the fluorescent microscope images. EX: /User/Name/Downloads/fluorescent/',
                    pad = ((3,0),0),
                    size = (12,1), 
                    font = ('Georgia', 16))],
                    
            [sg.Text('Light: Select the folder containing the light microscope images. EX: /User/Name/Downloads/light/',
                    pad = ((3,0),0),
                    size = (12,1), 
                    font = ('Georgia', 16))],
                    
            [sg.Text('Output: Select the folder which you want the file to be saved to. EX: /User/Name/Downloads/',
                    pad = ((3,0),0),
                    size = (12,1),
                    font = ('Georgia', 16))],
            [sg.Text('File Name: Specify a name for the file to be saved. EX: lipid_count ',
                    pad = ((3,0),0),
                    size = (12,1),
                    font = ('Georgia', 16))],

            [sg.OK(font = ('Georgia', 12),
                        button_color = ('white', 'springgreen4'),
                        pad = ((3,0),5))]]
   return sg.Window('Folder Selection Help',
                    layout_help,
                    auto_size_buttons=False,
                    element_justification='l',
                    finalize = True)


def make_confirm():
    layout2 = [[sg.Text('You selected these folders:',
                #size = (12,1),
                font = ('Helvetica Bold', 20),
                expand_x = True,)],
        [sg.Text(fluoro_path,
                #size = (12,1), 
                font = ('Helvetica Bold', 16),
                expand_x = True,)],
        [sg.Text(light_path,
                #size = (12,1), 
                font = ('Helvetica Bold', 16),
                expand_x = True,)],
        [sg.Text(output_path,
                #size = (12,1),
                font = ('Helvetica Bold', 16),
                expand_x = True,)],
        [sg.OK(),
            sg.Exit()
        ],
                ]
    return sg.Window('Folders Selected',
                      layout2,
                      finalize = True)

def main_help():
     window_help = make_help()
     while True: 
        event_help, values_help = window_help.read()
        if event_help == sg.WIN_CLOSED:
            break
        elif event_help == 'OK':
            window_help.Close()
            break

def main_input():
     window_input = make_input()
     while True: 
        event_input, values_input = window_input.read()
        if event_input == sg.WIN_CLOSED:
            break
        if event_input == 'Cancel':
            break
        if event_input == 'Help':
            main_help()
        if event_input == 'Submit':
             global fluoro_path
             fluoro_path = str(values_input['-fluoro_path-'])
             global light_path
             light_path = str(values_input['-light_path-'])
             global output_path
             output_path = str(values_input['-output_path-'])
             global file_name
             file_name = str(values_input['-file_name-'])
             main_confirm()
            
    
def main_confirm():
    window_confirm = make_confirm()
    while True:
        event_confirm, values_confirm = window_confirm.read()
        if event_confirm == sg.WIN_CLOSED:
            break
        elif event_confirm == 'Exit':
            fluoro_path = ""
            light_path = ""
            output_path = ""
            window_confirm.Close()
            window_confirm.active = False
            break
        elif event_confirm == 'OK':
            window_confirm.Close()
            window_confirm.active = False
            break
                    
    
main_input()
        
       



#PROCESSING
KERNEL = np.ones((3, 3), np.uint8)
FLUORO_PATH = Path(fluoro_path)
LIGHT_PATH = Path(light_path)
OUTPUT_PATH = Path(output_path)
FILE_NAME = file_name

with open(str(OUTPUT_PATH) + FILE_NAME +".csv", 'w', newline='') as file:

    writer = csv.DictWriter(file, ['image_name', 'cell_num', 'droplets_count'])
    writer.writeheader()

    # Iterate through images in a given folder.
    for file_path in FLUORO_PATH.glob('*'):
        if (file_path.suffix == '.jpg')|\
           (file_path.suffix == '.jpeg')|\
           (file_path.suffix == '.tif')|\
           (file_path.suffix == '.tiff'):
        
            original = cv.imread(str(file_path), cv.IMREAD_GRAYSCALE)
            cv.imshow("original_" + str(file_path.name), original)
            cv.waitKey(500)
            #cv.imwrite("original" + "_file_" + str(i) + ".jpg", original)
            assert original is not None, "file could not be read, check with pathlib.Path.exists()"

            # Preprocessing
            blur = cv.GaussianBlur(original, (3, 3), 0) 
            thresh = cv.adaptiveThreshold(blur, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2)
            cv.imshow("thresh" + str(file_path.name), thresh)
            cv.waitKey(500)
            dilated = cv.dilate(thresh, KERNEL, iterations=1)
            cv.imshow("dilated" + str(file_path.name), dilated)
            cv.waitKey(500)
            eroded = cv.erode(dilated, KERNEL, iterations=1)
            cv.imshow("eroded" + str(file_path.name), eroded)
            cv.waitKey(500)

            # Connected Components
            N, connected, statistics, centroids = cv.connectedComponentsWithStats(eroded)
            sizes = statistics[:,-1]
            
            cell_num = 0
            for n in range(1, N):
                if sizes[n] >= 1000:
                    mask = np.zeros(connected.shape, np.uint8)
                    mask[connected == n] = 1

                    mask = cv.dilate(mask, KERNEL, iterations=8)
                    mask = cv.erode(mask, KERNEL, iterations=8)

                    cell = np.copy(original)
                    cell[~mask.astype(bool)] = 0

                    # Count Droplets
                    spots = cv.adaptiveThreshold(cell, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2)
                    circ, hierarchy = cv.findContours(spots, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
                    writer.writerow({
                        'image_name': file_path.name,
                        'cell_num': cell_num + 1,
                        'droplets_count': len(circ)
                    })

                    cell_num += 1
layout3 = [[sg.Text('Processing Complete! ',
                    size=(12,1), 
                    font=('Helvetica Bold', 16),
                    expand_x=True,)]]
window3 = sg.Window('Window 3',
                            layout3)


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

