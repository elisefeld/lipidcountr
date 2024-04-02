#gui_functions.py
import numpy as np
import cv2 as cv
import csv
from pathlib import Path
import PySimpleGUI as sg
import matplotlib.pyplot as plt
import skimage as ski

#GUI
sg.theme('Dark')
sg.set_options(element_padding = (0,0))   

#FIRST WINDOW: INPUT
def make_input():
     layout_input = [[sg.Text('Image Folder',
                    pad = ((3,0),10),
                    size = (12,1), 
                    font = ('Georgia', 16)),
                    sg.Input(key = '-fluoro_path-'),
                    sg.FolderBrowse(font = ('Georgia', 12), pad = ((10,10),5))],
            [sg.Text('Output Folder',
                    pad = ((3,0),10),
                    size = (12,1),
                    font = ('Georgia', 16)),
                    sg.Input(key = '-output_path-'),
                    sg.FolderBrowse(font = ('Georgia', 12), pad = ((10,10),5))],
            [sg.Text('File Name',
                    pad = ((3,0),10),
                    size = (12,1),
                    font = ('Georgia', 16)),
                    sg.Input(key = '-file_name-'),],
            
            [sg.Help(font = ('Georgia', 12),
                     button_color = ('white', 'springgreen4'),
                     pad = ((3,0),10)),
            sg.Push(),
                 sg.Submit(font = ('Georgia', 12),
                           button_color = ('white', 'springgreen4'),
                           pad = ((3,0),10)),
                 sg.Cancel(font = ('Georgia', 12),
                           button_color = ('white', 'firebrick3'),
                           pad = ((3,0),10))],
            ]
     return sg.Window('Folder Selection',
                    layout_input,
                    auto_size_buttons=False,
                    element_justification='l',
                    finalize = True)

#HELP WINDOW
def make_help():
   layout_help = [[sg.Text("Fluorescent: Select the folder containing the microscope images. EX: /User/Name/Downloads/tetrahymena/",
                    pad = ((3,0),0),
                    size = (12,1), 
                    expand_x = True,
                    font = ('Georgia', 16))],                
            [sg.Text('Output: Select the folder which you want the file to be saved to. EX: /User/Name/Downloads/',
                    pad = ((3,0),0),
                    size = (12,1),
                    expand_x = True,
                    font = ('Georgia', 16))],
            [sg.Text('File Name: Specify a name for the file to be saved. EX: lipid_count ',
                    pad = ((3,0),0),
                    size = (12,1),
                    expand_x = True,
                    font = ('Georgia', 16))],

            [sg.OK(font = ('Georgia', 12),
                        button_color = ('white', 'springgreen4'),
                        pad = ((3,0),5))]]
   return sg.Window('Folder Selection Help',
                    layout_help,
                    auto_size_buttons=False,
                    element_justification='l',
                    size = (500, 100),
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
            cv.destroyAllWindows()
            break
        if event_input == 'Cancel':
            cv.destroyAllWindows()
            break
        if event_input == 'Help':
            main_help()
        if event_input == 'Submit':
             if str(values_input['-fluoro_path-']) == "":
                 break
             else:     
                global fluoro_path
                fluoro_path = str(values_input['-fluoro_path-'])
                global output_path
                output_path = str(values_input['-output_path-'])
                global file_name
                file_name = str(values_input['-file_name-'])
                img_process()

# MAIN IMAGE PROCESSING
def img_process():
    #PROCESSING
    FLUORO_PATH = Path(fluoro_path)
    OUTPUT_PATH = Path(output_path)
    FILE_NAME = file_name
    KERNEL1 = np.ones((3, 3), np.uint8)

    with (OUTPUT_PATH / (FILE_NAME + ".csv")).open('w', newline='') as file:

        writer = csv.DictWriter(file, ['image_name', 'cell_num', 'droplets_count_bin', "droplets_count_yen"])
        writer.writeheader()

        # Iterate through images in a given folder.
        for file_path in FLUORO_PATH.glob('*'):
            if (file_path.suffix.lower() == '.jpg')|\
               (file_path.suffix.lower() == '.jpeg')|\
               (file_path.suffix.lower() == '.tif')|\
               (file_path.suffix.lower() == '.tiff'):
            
                img = cv.imread(str(file_path), cv.IMREAD_ANYDEPTH)
                assert img is not None, "file could not be read, check with pathlib.Path.exists()"
                
                #Add check for number of channels
                #gray = ski.color.rgb2gray(original)
                #gray = cv.cvtColor(original, cv.COLOR_BGR2GRAY) 

             # Preprocessing
                # Gaussian Blur
                blur = cv.GaussianBlur(img, (3, 3), 0)
                #cv.imwrite("blur" + "_file_" + str(file_path.name) + ".jpg", blur)

                if (img.dtype) == "uint16":
                    img_16 = np.copy(blur)
                    img_8 = cv.normalize(img_16, None, 0, 255, cv.NORM_MINMAX, dtype=cv.CV_8UC1) 
                    cv.imshow("img_8" + str(file_path.name), img_8)
                    cv.waitKey(0)
                elif (img.dtype) == "uint8":
                    img_8 = np.copy(blur)
                    img_8 = cv.normalize(img_8, None, 0, 255, cv.NORM_MINMAX, dtype=cv.CV_8UC1) 
                    cv.imshow("img_8" + str(file_path.name), img_8)
                    cv.waitKey(0)
                
                plt.hist(img_8.ravel(), bins=256, range=(0, 255), fc='k', ec='k') 
                plt.show()

                # Thresholding for Whole Cell (Triangle)
                thresh_cells = ski.filters.threshold_triangle(img_8)
                cell_mask = blur > thresh_cells
                cell_mask = ski.util.img_as_ubyte(cell_mask)

                # Smooth out the Cell Mask
                cell_mask = cv.dilate(cell_mask, KERNEL1, iterations=1)
                cell_mask = cv.erode(cell_mask, KERNEL1, iterations=1)

                #Creates a mask of only cells. 
                result = cv.bitwise_and(blur, blur, mask = cell_mask)
                result = cv.normalize(result, None, 0, 255, cv.NORM_MINMAX, dtype=cv.CV_8UC1) 
                cv.imshow("result" + str(file_path.name), result)
                cv.waitKey(0)

                # Connected Components (counting # of cells in image)
                N_cell, connected_cell, statistics_cell, centroids_cell = cv.connectedComponentsWithStats(cell_mask)
                sizes_cell = statistics_cell[:,-1]
                
                cell_num = 0
                for n in range(1, N_cell):
                    if sizes_cell[n] >= 1000:
                        mask_cell = np.zeros(connected_cell.shape, np.uint8)
                        mask_cell[connected_cell == n] = 1
                        mask_cell = cv.dilate(mask_cell, KERNEL1, iterations=8)
                        mask_cell = cv.erode(mask_cell, KERNEL1, iterations=8)

                        cell = np.copy(img_8)
                        cell[~ski.util.img_as_bool(mask_cell)] = 0

                        biggest = np.amax(img_8)
                        smallest = np.amin(img_8)
                        pixel_range = biggest - smallest
                        drop_tval = (pixel_range/2)

                    # Count Droplets
                        # Yen Thresholding Method
                        thresh_drops_yen = ski.filters.threshold_yen(result)
                        thresh_drops_yen = result > thresh_drops_yen
                        thresh_drops_yen = ski.util.img_as_ubyte(thresh_drops_yen)
                        cv.imshow("thresh_drops_yen" + str(file_path.name), thresh_drops_yen)
                        cv.waitKey(0)
                        circ_yen, hierarchy = cv.findContours(thresh_drops_yen, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
                        contours_yen = cv.drawContours(np.copy(img_8), circ_yen, -1, (0, 255, 0), 3) 
                        cv.imshow("contours_yen" + str(file_path.name), contours_yen)
                        cv.waitKey(0)
                        cv.imwrite("contours_yen" + "_file_" + str(file_path.name) + ".jpg", contours_yen)


                        # Binary Thresholding Method
                        ret, thresh_drops_bin = cv.threshold(result, drop_tval, 255, cv.THRESH_BINARY)
                        #thresh_drops_bin = cv.adaptiveThreshold(img_8, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY,11,2)
                        cv.imshow("thresh_drops_bin" + str(file_path.name), thresh_drops_bin)
                        cv.waitKey(0)
                        print(type(thresh_drops_bin))
                        print(thresh_drops_bin.dtype)

                        thresh_drops_bin = ski.util.img_as_ubyte(thresh_drops_bin)
                        #circ_bin, hierarchy = cv.findContours(thresh_drops_bin, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
                        #circ_bin, hierarchy = cv.findContours(thresh_drops_bin, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
                        circ_bin, hierarchy = cv.findContours(thresh_drops_bin, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)
                        #circ_bin, hierarchy = cv.findContours(thresh_drops_bin, cv.RETR_FLOODFILL, cv.CHAIN_APPROX_SIMPLE)
                        contours_bin = cv.drawContours(np.copy(img_8), circ_bin, -1, (0, 255, 0), 3) 
                        cv.imshow("contours_bin" + str(file_path.name), contours_bin)
                        cv.waitKey(0)                      
                        cv.imwrite("contours_bin" + "_file_" + str(file_path.name) + ".jpg", contours_bin)
      
                        
                        writer.writerow({
                            'image_name': file_path.name,
                            'cell_num': cell_num + 1,
                            'droplets_count_yen': len(circ_yen),
                            'droplets_count_bin': len(circ_bin)
                                        })

                        cell_num += 1
                    cv.destroyAllWindows()
