#gui_functions.py
import numpy as np
import cv2 as cv
import csv
from pathlib import Path
import PySimpleGUI as sg
import matplotlib.pyplot as plt
import skimage as ski
from skimage import img_as_float, exposure, io
from skimage.filters import try_all_threshold, threshold_triangle, median, difference_of_gaussians, window
from skimage.morphology import disk
from IPython.display import Image, display
import process_functions

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
                
                original = cv.imread(str(file_path))
                gray = cv.cvtColor(original, cv.COLOR_BGR2GRAY) 

                assert original is not None, "file could not be read, check with pathlib.Path.exists()"
                cv.imshow("original_" + str(file_path.name), original)
                cv.waitKey(0)
                
                if ski.exposure.is_low_contrast(gray):
                    print ("Image contrast is too low for accurate analysis.")
                    break

                ## Preprocessing
                # Normalize
                #normal = ski.exposure.rescale_intensity(gray)
                #normal = cv.normalize(normal, None, alpha=0, beta=800, norm_type=cv.NORM_MINMAX, dtype=cv.CV_8U)
                #cv.imwrite("normal" + "_file_" + str(file_path.name) + ".jpg", normal)

                # Gaussian Blur
                blur = cv.GaussianBlur(gray, (1, 1), 0)
                cv.imwrite("blur" + "_file_" + str(file_path.name) + ".jpg", blur)

                # Thresholding for Whole Cell
                thresh_cells = ski.filters.threshold_triangle(blur)
                cell_mask = blur > thresh_cells

                cell_mask = cell_mask.astype(int)
                cell_mask = np.uint8(cell_mask)

                result = cv.bitwise_and(blur, blur, mask = cell_mask)
                cv.imshow("result" + str(file_path.name), result)
                cv.waitKey(0)

                equal = ski.exposure.adjust_gamma(result, gamma = 1.5)
                cv.imshow("equal" + str(file_path.name), equal)
                cv.waitKey(0)

                # Smooth out the Cell Mask
                cell_mask = cv.dilate(cell_mask, KERNEL1, iterations=1)
                cell_mask = cv.erode(cell_mask, KERNEL1, iterations=1)
                cv.imshow("cell_mask" + str(file_path.name), cell_mask)
                cv.waitKey(0)
                cv.imwrite("cell_mask" + "_file_" + str(file_path.name) + ".jpg", cell_mask)

                # Connected Components (counting # of cells in image)
                N_cell, connected_cell, statistics_cell, centroids_cell = cv.connectedComponentsWithStats(cell_mask)
                sizes_cell = statistics_cell[:,-1]
                
                cell_num = 0
                for n in range(1, N_cell):
                    if sizes_cell[n] >= 2000:
                        mask_cell = np.zeros(connected_cell.shape, np.uint8)
                        mask_cell[connected_cell == n] = 1

                        mask_cell = cv.dilate(mask_cell, KERNEL1, iterations=8)
                        mask_cell = cv.erode(mask_cell, KERNEL1, iterations=8)

                        cell = np.copy(blur)
                        cell[~mask_cell.astype(bool)] = 0

                        # Count Droplets
                        biggest = np.amax(original)
                        smallest = np.amin(original)
                        pixel_range = biggest - smallest
                        drop_tval = (pixel_range/2)

                        thresh_drops = ski.filters.threshold_yen(equal)
                        drop_mask = blur > thresh_drops
                        drop_mask = drop_mask.astype(np.uint8)
                        ret, thresh_drops2 = cv.threshold(equal, drop_tval, 255, cv.THRESH_BINARY)

                        # Connected Components (counting # of droplets in image)
                        N_drop, connected_drop, statistics_drop, centroids_drop = cv.connectedComponentsWithStats(cell_mask)
                        sizes_drop = statistics_drop[:,-1]

                        # drop_num = 0
                        # for n in range(1, N_drop):
                        #     if sizes_drop[n] < 2000:
                        #         drop_num += 1


                        circ, hierarchy = cv.findContours(drop_mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
                        circ2, hierarchy = cv.findContours(thresh_drops2, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
                        contours_img = cv.drawContours(original, circ, -1, (0, 255, 0), 3) 
                        cv.imshow("contours_img" + str(file_path.name), contours_img)
                        cv.imwrite("contours_img" + "_file_" + str(file_path.name) + ".jpg", contours_img)
                        cv.waitKey(0)
                        
                        writer.writerow({
                            'image_name': file_path.name,
                            'cell_num': cell_num + 1,
                            'droplets_count_yen': len(circ),
                            'droplets_count_bin': len(circ2)
                        })

                        cell_num += 1
                    cv.destroyAllWindows()
