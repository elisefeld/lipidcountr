import numpy as np
import cv2 as cv
import csv
from pathlib import Path

KERNEL = np.ones((3, 3), np.uint8)
CLAHE = cv.createCLAHE(clipLimit=5,tileGridSize=(2,2))
NORM_IMG = np.zeros((800, 800))

DIRECTORY_PATH = Path("/Users/Elise/Code/TETLAB/Images/INA/3.10.24/")
assert DIRECTORY_PATH.exists() is not False, "path does not exist"

with open('lipid_count.csv', 'w', newline='') as file:

    writer = csv.DictWriter(file, ['image_name', 'cell_num', 'droplets_count'])
    writer.writeheader()

    # Iterate through images in a given folder.
    for file_path in DIRECTORY_PATH.glob('*'):

        file_suffix = file_path.suffix
        if ((file_suffix.lower() == '.jpg')) |\
           ((file_suffix.lower() == '.jpeg'))|\
           ((file_suffix.lower() == '.tif')) |\
           ((file_suffix.lower() == '.tiff')):
             
            if ((file_suffix.lower() == '.jpg')) | ((file_suffix.lower() == '.jpeg')):
                    original = cv.imread(str(file_path), -1)
                    original = cv.cvtColor(original, cv.COLOR_RGB2GRAY)

            elif ((file_suffix.lower() == '.tif')) | ((file_suffix.lower() == '.tiff')):
                original = cv.imread(str(file_path), -1)
                original = (original/256).astype('uint8')
            

            # Preprocessing
            cv.imshow("original_" + str(file_path.name), original)
            cv.waitKey(0)

            normal = cv.normalize(original,  NORM_IMG, 0, 255, cv.NORM_MINMAX)
            cv.imshow("normal_" + str(file_path.name), normal)
            cv.waitKey(0)

            if ((file_suffix.lower() == '.tif')) | ((file_suffix.lower() == '.tiff')):
                normal = CLAHE.apply(normal)
                cv.imshow("clahe_equalized_" + str(file_path.name), normal)
                cv.waitKey(0)

            blur = cv.GaussianBlur(normal, (5, 5), 0) 
            thresh = cv.adaptiveThreshold(blur, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 25, 2)
            dilated = cv.dilate(thresh, KERNEL, iterations=1)
            eroded = cv.erode(dilated, KERNEL, iterations=1)

            #cv.imwrite("thresh_" + str(file_path.name) + ".jpg", thresh)
            # cv.imshow("thresh_" + str(file_path.name), thresh)
            # cv.waitKey(0)

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

                    cell = np.copy(normal)
                    cell[~mask.astype(bool)] = 0

                    # Count Droplets
                    drop_thresh = cv.adaptiveThreshold(cell, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 3, 2)
                    drop_contour, hierarchy = cv.findContours(drop_thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
                    contours = cv.drawContours(normal, drop_contour, -1, (0, 255, 0), 3) 

                    # Draw Cell Contours
                    cell_thresh = cv.adaptiveThreshold(cell, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 11, 2)
                    cell_contour, hierarchy = cv.findContours(cell_thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
                    cell_contours = cv.drawContours(normal, cell_contour, -1, (0, 255, 0), 3) 

                    # cv.imwrite("dilated_" + str(file_path.name) + ".jpg", dilated)
                    # cv.imshow("dilated_" + str(file_path.name), dilated)
                    # cv.waitKey(0)

                    # cv.imwrite("eroded_" + str(file_path.name) + ".jpg", eroded)
                    # cv.imshow("eroded_" + str(file_path.name), eroded)
                    # cv.waitKey(0)

                    # cv.imwrite("drop_thresh" + str(file_path.name) + ".jpg", drop_thresh)
                    # cv.imshow("drop_thresh_" + str(file_path.name), drop_thresh)
                    # cv.waitKey(0)

                    # cv.imwrite("cell_thresh_" + str(file_path.name) + ".jpg", cell_thresh)
                    cv.imshow("cell_thresh_" + str(file_path.name), cell_thresh)
                    cv.waitKey(0)

                    # cv.imwrite("cell_contours_" + str(file_path.name) + ".jpg", cell_contours)
                    cv.imshow("cell_contours_" + str(file_path.name), cell_contours)
                    cv.waitKey(0)


                    canny = cv.Canny(cell, 0, 200)
                    cv.imshow("canny_" + str(file_path.name), canny)
                    cv.waitKey(0)

            writer.writerow({
                'image_name': file_path.name,
                'cell_num': cell_num,
                'droplets_count': len(drop_contour)
            })
            
            cell_num += 1
