import numpy as np
import cv2 as cv
import csv
import pandas as pd
import os

# Initialize Lists
cells = []
cell_num = []
droplets = []
droplets_count = []
masks = []
image_names = []
file_names = []

file_path = "/Users/Elise/Code/TETLAB/Images/INA/3.4.24/"

# Iterate through images in a given folder.
for file_name in os.listdir(file_path):
   if (file_name.endswith(".jpg") | file_name.endswith(".tiff")):
        file_names.append(file_name)


i = 0
while i < len(file_names):
    
    original = cv.imread(file_path + file_names[i], cv.IMREAD_GRAYSCALE)
    #cv.imwrite("original" + "_file_" + str(i) + ".jpg", original)
    assert original is not None, "file could not be read, check with os.path.exists()"

    # Preprocessing
    blur = cv.GaussianBlur(original, (3, 3), 0) 
    thresh = cv.adaptiveThreshold(blur, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2)
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv.dilate(thresh, kernel, iterations=1)
    eroded = cv.erode(dilated, kernel, iterations=1)

    # Connected Components
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
        
        cell_num.append(n)
        image_names.append(file_names[i])

        cell = np.copy(original)
        cell[~mask.astype(bool)] = 0
        spots = cv.adaptiveThreshold(cell, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2)
        circ, hierarchy = cv.findContours(spots, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        droplets_count.append(len(circ))


    debug = np.zeros(connected.shape, np.uint8)
    for n in range(len(masks)):
        debug[masks[n] == True] = (n + 1) * 8

    # for n in range(len(masks)):
    #  cell = np.copy(original)
    #  cell[~masks[n]] = 0
    #  cells.append(cell)

    # for n in range(1, N):
    #     spots = cv.adaptiveThreshold(cell, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2)
    #     circ, hierarchy = cv.findContours(spots, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    #     droplets_count.append(circ)

    # z = 0
    # while z < len(file_names):
    #  for n in droplets:
    #   circ, hierarchy = cv.findContours(n,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)
    #   droplets_count.append(len(circ))
    #   y += 1
        
    #cv.imwrite("blur" + "_file_" + str(i) + ".jpg", blur)
    #cv.imwrite("thresh" + "_file_" + str(i) + ".jpg", thresh)
    #cv.imwrite("dilated" + "_file_" + str(i) + ".jpg", dilated)
    #cv.imwrite("eroded" + "_file_" + str(i) + ".jpg", eroded)

    i += 1

print(len(cell_num))
print(len(image_names))
print(len(droplets_count))

dict = {'images': image_names, 'cells': cell_num, 'droplets': droplets_count}  
df = pd.DataFrame(dict) 
df.to_csv('lipid_count.csv') 




# # cv.imshow("original", original)
# # cv.imshow("thresh", thresh)
# # cv.imshow("dilated", dilated)
# # cv.imshow("eroded", eroded)
# # cv.imshow("debug", debug)
# #cv.waitKey(0)

     


