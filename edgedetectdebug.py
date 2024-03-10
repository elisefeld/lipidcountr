import numpy as np
import cv2 as cv
import csv
from pathlib import Path

DIRECTORY_PATH = Path("/Users/Elise/Code/TETLAB/Images/INA/3.4.24/")

with open('lipid_count.csv', 'w', newline='') as file:

    # TODO: find argument to DictWriter to write headers to CSV.

    writer = csv.DictWriter(file, ['image_name', 'cell_num', 'droplets_count'])
    writer.writeheader()

    # Iterate through images in a given folder.
    for file_path in DIRECTORY_PATH.glob('*'):
        if (file_path.suffix == '.jpg') | (file_path.suffix == '.tiff'):
        
            original = cv.imread(str(file_path), cv.IMREAD_GRAYSCALE)
            #cv.imwrite("original" + "_file_" + str(i) + ".jpg", original)
            assert original is not None, "file could not be read, check with pathlib.Path.exists()"

            # Preprocessing
            blur = cv.GaussianBlur(original, (3, 3), 0) 
            thresh = cv.adaptiveThreshold(blur, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2)
            kernel = np.ones((3, 3), np.uint8)
            dilated = cv.dilate(thresh, kernel, iterations=1)
            eroded = cv.erode(dilated, kernel, iterations=1)

            # Connected Components
            N, connected, statistics, centroids = cv.connectedComponentsWithStats(eroded)
            sizes = statistics[:,-1]
            
            cell_num = 0
            for n in range(1, N):
                if sizes[n] >= 1000:
                    mask = np.zeros(connected.shape, np.uint8)
                    mask[connected == n] = 1

                    mask = cv.dilate(mask, kernel, iterations=8)
                    mask = cv.erode(mask, kernel, iterations=8)

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
