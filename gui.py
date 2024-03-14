#gui.py
import numpy as np
import cv2 as cv
import csv
from pathlib import Path
import PySimpleGUI as sg

#GUI
sg.theme('Dark')
sg.set_options(element_padding = (0,0))   
#Select the folder containing the fluorescent microscope images.
#Select the folder containing the light microscope images.
#Select the folder which you want the file to be saved to.
#Specify a name for the file to be saved. 
layout1 = [[sg.Text('Fluorescent ',
                    pad = ((3,0),0),
                    size = (12,1), 
                    font = ('Georgia', 16)),
                    sg.Input(key = '-fluoro_path-'),
                    sg.FolderBrowse()],
            [sg.Text('Light',
                    pad = ((3,0),0),
                    size = (12,1), 
                    font = ('Georgia', 16)),
                    sg.Input(key = '-light_path-'),
                    sg.FolderBrowse()],
            [sg.Text('Output',
                    pad = ((3,0),0),
                    size = (12,1),
                    font = ('Georgia', 16)),
                    sg.Input(key = '-output_path-'),
                    [sg.FolderBrowse()],
            [sg.Text('File Name',
                    pad = ((3,0),0),
                    size = (12,1),
                    font = ('Georgia', 16)),
                    sg.Input(key = '-file_name-'),
            [sg.Push(), sg.Button('Go',
                        font = ('Georgia', 12),
                        button_color = ('white', 'springgreen4')),
             sg.Button('Cancel',
                        font = ('Georgia', 12),
                        button_color = ('white', 'firebrick3'))]
            ]]  

window1 = sg.Window('Folder Selection',
                    layout1,
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
        file_name = str(values1['-file_name-'])

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

