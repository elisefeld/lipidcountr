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

#GUI
sg.theme('Dark')
sg.set_options(element_padding = (0,0))   

#FIRST WINDOW: INPUT
def make_input():
     layout_input = [[sg.Text('Fluorescent',
                    pad = ((3,0),10),
                    size = (12,1), 
                    font = ('Georgia', 16)),
                    sg.Input(key = '-fluoro_path-'),
                    sg.FolderBrowse(font = ('Georgia', 12), pad = ((10,10),5))],
            [sg.Text('Output',
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
   layout_help = [[sg.Text("Fluorescent: Select the folder containing the fluorescent microscope images. EX: /User/Name/Downloads/fluorescent/",
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


#CONFIRM WINDOW
def make_confirm():
    layout2 = [[sg.Text('You selected these folders:',
                #size = (12,1),
                font = ('Helvetica Bold', 20),
                expand_x = True,)],
        [sg.Text(fluoro_path,
                #size = (12,1), 
                font = ('Helvetica Bold', 16),
                expand_x = True,)],
        [sg.Text(output_path,
                #size = (12,1),
                font = ('Helvetica Bold', 16),
                expand_x = True,)],
        [sg.OK(pad = ((5,5),10)),
            sg.Exit(pad = ((5,5),10))
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
                main_confirm()
            
    
def main_confirm():
    window_confirm = make_confirm()
    while True:
        event_confirm, values_confirm = window_confirm.read()
        if event_confirm == sg.WIN_CLOSED:
            cv.destroyAllWindows()
            break
        elif event_confirm == 'Exit':
            fluoro_path = ""
            output_path = ""
            window_confirm.Close()
            window_confirm.active = False
            cv.destroyAllWindows()
            break
        elif event_confirm == 'OK':
            window_confirm.Close()
            window_confirm.active = False
            #window_input.Close()
            img_process()
            break

# MAIN IMAGE PROCESSING
def img_process():
    #PROCESSING
    KERNEL = np.ones((3, 3), np.uint8)
    FLUORO_PATH = Path(fluoro_path)
    OUTPUT_PATH = Path(output_path)
    FILE_NAME = file_name

    with (OUTPUT_PATH / (FILE_NAME + ".csv")).open('w', newline='') as file:

        writer = csv.DictWriter(file, ['image_name', 'cell_num', 'droplets_count'])
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
                #cv.imwrite("original" + "_file_" + str(i) + ".jpg", original)
                if ski.exposure.is_low_contrast(gray):
                    print ("Image contrast is too low for accurate analysis.")
                    break

                # Preprocessing
                normal = ski.exposure.rescale_intensity(gray)
                blur = cv.GaussianBlur(normal, (1, 1), 0)

                # Thresholding for Whole Cell
                thresh_cells = ski.filters.threshold_triangle(blur)
                binary_cells = blur > thresh_cells

                binary_cells = binary_cells.astype(int)
                binary_cells = np.uint8(binary_cells)

                result = cv.bitwise_and(blur, blur, mask = binary_cells)
                cv.imshow("cell_mask" + str(file_path.name), binary_cells)
                cv.imshow("result" + str(file_path.name), result)
                cv.waitKey(0)


                # Thresholding for Droplets
                # fig1, axes = plt.subplots(ncols = 2, nrows = 2, figsize = (8, 3))
                # ax = axes.ravel()

                # ax[0].imshow(blur, cmap=plt.cm.gray)
                # ax[0].set_title('Original image')

                # ax[1].imshow(binary_drops, cmap=plt.cm.gray)
                # ax[1].set_title('Droplets')

                # ax[2].imshow(binary_cells, cmap=plt.cm.gray)
                # ax[2].set_title('Cell')

                # ax[3].imshow(colored_label_image, cmap=plt.cm.viridis)
                # ax[3].set_title('Color Labeled Droplets')

                # for a in ax:
                #     a.axis('off')

                # plt.show()  

                dilated = cv.dilate(binary_cells, KERNEL, iterations=1)
                cv.imshow("dilated" + str(file_path.name), dilated)
                cv.waitKey(0)

                eroded = cv.erode(dilated, KERNEL, iterations=1)
                cv.imshow("eroded" + str(file_path.name), eroded)
                cv.waitKey(0)

                # Connected Components
                N, connected, statistics, centroids = cv.connectedComponentsWithStats(binary_cells)
                sizes = statistics[:,-1]
                
                cell_num = 0
                for n in range(1, N):
                    if sizes[n] >= 2000:
                        mask = np.zeros(connected.shape, np.uint8)
                        mask[connected == n] = 1

                        mask = cv.dilate(mask, KERNEL, iterations=8)
                        mask = cv.erode(mask, KERNEL, iterations=8)

                        cell = np.copy(blur)
                        cell[~mask.astype(bool)] = 0

                        # Count Droplets
                        biggest = np.amax(original)
                        smallest = np.amin(original)
                        pixel_range = biggest - smallest
                        drop_tval = (biggest - (pixel_range/2.5))

                        thresh_drops = ski.filters.threshold_yen(result)
                        ret, thresh_drops2 = cv.threshold(result, drop_tval, 255, cv.THRESH_BINARY)

                        kernel = np.ones((3,3),np.uint8)
                        opening = cv.morphologyEx(thresh_drops2,cv.MORPH_OPEN,kernel, iterations = 2)

                        # sure background area
                        sure_bg = cv.dilate(opening,kernel,iterations=3)
                        # Finding sure foreground area
                        dist_transform = cv.distanceTransform(opening,cv.DIST_L2,5)
                        ret, sure_fg = cv.threshold(dist_transform,0.7*dist_transform.max(),255,0)
                        # Finding unknown region
                        sure_fg = np.uint8(sure_fg)
                        unknown = cv.subtract(sure_bg,sure_fg)
                        # Marker labelling
                        ret, markers = cv.connectedComponents(sure_fg)
                        # Add one to all labels so that sure background is not 0, but 1
                        markers = markers+1
                        # Now, mark the region of unknown with zero
                        markers[unknown==255] = 0
                        markers = cv.watershed(original,markers)
                        mark = original[markers == -1] = [255,0,0]
                        print(len((mark)) - 1)
        



                        # labeled_image, count = ski.measure.label(binary_drops, return_num=True)
                        # colored_label_image = ski.color.label2rgb(labeled_image, bg_label=0, colors=('red','yellow','blue','green','purple'))

                        # binary_drops = binary_drops.astype(int)
                        # binary_drops = np.uint8(binary_drops)
    

                        circ, hierarchy = cv.findContours(thresh_drops2, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

                        # fig1, axes = plt.subplots(ncols = 2, figsize = (8, 3))
                        # ax = axes.ravel()

                        # ax[0].imshow(blur, cmap=plt.cm.gray)
                        # ax[0].set_title('Original image')

                        # ax[1].imshow(binary_drops, cmap=plt.cm.gray)
                        # ax[1].set_title('Droplets')

                        # for a in ax:
                        #     a.axis('off')

                        # plt.show()                
                        
                        writer.writerow({
                            'image_name': file_path.name,
                            'cell_num': cell_num + 1,
                            'droplets_count': len(circ)
                        })

                        cell_num += 1
                    cv.destroyAllWindows()


