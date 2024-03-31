#csvworking.py
#for fluorescent images

import numpy as np
import cv2 as cv
import csv
from pathlib import Path

SCALE_PIXELS = 80
OBJ_SCALE = 50
MAGNIF = 80*OBJ_SCALE

# 1 pixel = this many uM
CONVERT = OBJ_SCALE/SCALE_PIXELS

KERNEL = np.ones((3, 3), np.uint8)
DIRECTORY_PATH = Path("/Users/Elise/Code/TETLAB/Images/INA/24.03.19/fluoro/")


with open('lipid_count.csv', 'w', newline='') as file:

    writer = csv.DictWriter(file, ['image_name', 'cell_num', 'droplets_count'])
    writer.writeheader()

    # Iterate through images in a given folder.
    for file_path in DIRECTORY_PATH.glob('*'):
        if (file_path.suffix == '.jpg') | (file_path.suffix == '.tif'):
        
            original = cv.imread(str(file_path), cv.IMREAD_GRAYSCALE)
            cv.imshow("original_" + str(file_path.name), original)
            cv.waitKey(0)
            normal = cv.normalize(original, None, alpha=0, beta=700, norm_type=cv.NORM_MINMAX, dtype=cv.CV_8U)
            cv.imshow("normal" + str(file_path.name), normal)
            cv.waitKey(0)
            cv.imwrite("normal" + str(file_path.name), normal)
            #cv.imwrite("original" + "_file_" + str(i) + ".jpg", original)
            assert original is not None, "file could not be read, check with pathlib.Path.exists()"

            # Preprocessing
            blur = cv.GaussianBlur(normal, (3, 3), 0) 
            thresh = cv.adaptiveThreshold(blur, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2)
            cv.imshow("thresh" + str(file_path.name), thresh)
            cv.waitKey(0)
            dilated = cv.dilate(thresh, KERNEL, iterations=1)
            cv.imshow("dilated" + str(file_path.name), dilated)
            cv.waitKey(0)
            eroded = cv.erode(dilated, KERNEL, iterations=1)
            cv.imshow("eroded" + str(file_path.name), eroded)
            cv.waitKey(0)

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
                        'cell_num': cell_num,
                        'droplets_count': len(circ)
                    })

                    cell_num += 1