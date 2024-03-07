import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
from PIL import Image, ImageFilter


file_path = '/Users/Elise/Code/TETLAB/Images/INA/3.4.24/3.4.24_no6.jpg'

original = cv.imread(file_path, cv.IMREAD_GRAYSCALE)
assert original is not None, "file could not be read, check with os.path.exists()"

#Gaussian Blur & Adaptive Thresholding
blur = cv.GaussianBlur(original, (3, 3), 0) 
thresh = cv.adaptiveThreshold(blur,255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY,11,2)

#Dilation & Erosion Operations
kernel = np.ones((3, 3), np.uint8) 
dilated = cv.dilate(thresh, kernel, iterations=1)
eroded = cv.erode(dilated, kernel, iterations=1)

#Connected Components
N, connected, statistics, centroids = cv.connectedComponentsWithStats(eroded)
sizes = statistics[:,-1]

masks = []
for n in range(1, N):
    if sizes[n] >= 1000:
        mask = np.zeros(connected.shape, np.uint8)
        mask[connected == n] = 1

        kernel = np.ones((3, 3), np.uint8) 
        mask = cv.dilate(mask, kernel, iterations=8)
        mask = cv.erode(mask, kernel, iterations=8)

        mask = mask == 1
        masks.append(mask)

debug = np.zeros(connected.shape, np.uint8)
for n in range(len(masks)):
    debug[masks[n] == True] = (n + 1) * 8

cells = []
for n in range(len(masks)):
    cell = np.copy(original)
    cell[~masks[n]] = 0
    cells.append(cell)

    

cv.imshow("original", original)
cv.imshow("thresh", thresh)
cv.imshow("dilated", dilated)
cv.imshow("eroded", eroded)
cv.imshow("debug", debug)
cv.waitKey(0)
