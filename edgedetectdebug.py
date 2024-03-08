import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
from PIL import Image, ImageFilter
import csv
import glob
import pandas as pd
import os

image_name = []
cell_num = []
cells = []
masks = []

kernel = np.ones((3, 3), np.uint8)

file_path = "/Users/Elise/Code/TETLAB/Images/INA/3.4.24/"
file_names = os.listdir(r"/Users/Elise/Code/TETLAB/Images/INA/3.4.24")

print(file_names)

i = 0
while i <= len(file_names):
    
    original = cv.imread(file_path + file_names[i], cv.IMREAD_GRAYSCALE)
    cv.imwrite("original" + "_file_" + str(i) + ".jpg", original)
    assert original is not None, "file could not be read, check with os.path.exists()"

    #Gaussian Blur
    blur = cv.GaussianBlur(original, (3, 3), 0) 
    cv.imwrite("blur" + "_file_" + str(i) + ".jpg", blur)

    #Adaptive Thresholding
    thresh = cv.adaptiveThreshold(blur, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2)
    cv.imwrite("thresh" + "_file_" + str(i) + ".jpg", thresh)

    #Dilation & Erosion Operations
    dilated = cv.dilate(thresh, kernel, iterations=1)
    cv.imwrite("dilated" + "_file_" + str(i) + ".jpg", dilated)
    eroded = cv.erode(dilated, kernel, iterations=1)
    cv.imwrite("eroded" + "_file_" + str(i) + ".jpg", eroded)

    #Connected Components
    N, connected, statistics, centroids = cv.connectedComponentsWithStats(eroded)
    sizes = statistics[:,-1]
    
    for n in range(1, N):
      if sizes[n] >= 1000:
        mask = np.zeros(connected.shape, np.uint8)
        mask[connected == n] = 1

        mask = cv.dilate(mask, kernel, iterations=8)
        mask = cv.erode(mask, kernel, iterations=8)

        mask = mask == 1
        masks.append(mask)

    debug = np.zeros(connected.shape, np.uint8)
    for n in range(len(masks)):
        debug[masks[n] == True] = (n + 1) * 8

    for n in range(len(masks)):
     cell = np.copy(original)
     cell[~masks[n]] = 0
     cells.append(cell)

     for n in cell_num:
        cell_num.append(n)
    i += 1
        


    # for n in range(len(cells)):
    #     cv.imshow(f"Cell {n}", cells[n])


# droplets = []
# for image_path in images:
#     for n in cells:
#      spot = cv.adaptiveThreshold(cells[n],255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY,11,2)
#      droplets.append(spot)

# droplets_count = []
# for image_path in images:
#     for n in droplets:
#      image, circ, hierarchy = cv.findContours(droplets[n],cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)
#      droplets_count.append(len(circ))


# dict = {'images': images, 'cells': cell_num, 'droplets': droplets_count}  
# df = pd.DataFrame(dict) 
# df.to_csv('lipid_count.csv') 

# print(images)
# print(cell_num)
# print(droplets_count)

# # cv.imshow("original", original)
# # cv.imshow("thresh", thresh)
# # cv.imshow("dilated", dilated)
# # cv.imshow("eroded", eroded)
# # cv.imshow("debug", debug)
# #cv.waitKey(0)

     


