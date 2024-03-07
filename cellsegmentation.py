import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

#Doesn't Work
#file_path = '/Users/Elise/Code/TETLAB/Images/INA/Image_31681.jpg'

#Does Work
file_path = '/Users/Elise/Code/TETLAB/Images/INA/Image_31486.jpg'

original = cv.imread(file_path, cv.IMREAD_GRAYSCALE)
assert original is not None, "file could not be read, check with os.path.exists()"

#equal = cv.equalizeHist(original) 

#threshold, thresholded = cv.threshold(original, 55, 75, cv.THRESH_BINARY)
threshold, thresholded = cv.threshold(original, 50, 100, cv.THRESH_BINARY)

kernel = np.ones((3, 3), np.uint8) 
dilated = cv.dilate(thresholded, kernel, iterations=3)
eroded = cv.erode(dilated, kernel, iterations=3)

# https://stackoverflow.com/questions/42798659/how-to-remove-small-connected-objects-using-opencv

N, connected, statistics, centroids = cv.connectedComponentsWithStats(eroded)
sizes = statistics[:,-1]

masks = []
for n in range(1, N):
    if sizes[n] >= 2000:
        mask = np.zeros(connected.shape, np.uint8)
        mask[connected == n] = 1

        kernel = np.ones((3, 3), np.uint8) 
        mask = cv.dilate(mask, kernel, iterations=25)
        mask = cv.erode(mask, kernel, iterations=25)

        mask = mask == 1
        masks.append(mask)

debug = np.zeros(connected.shape, np.uint8)
for n in range(len(masks)):
    debug[masks[n] == True] = (n + 1) * 5

cells = []
for n in range(len(masks)):
    cell = np.copy(original)
    cell[~masks[n]] = 0
    cells.append(cell)


cv.imshow("original", original)

#cv.imshow("equal", equal)

cv.imwrite("thresholded.jpg", thresholded)
cv.imshow("thresholded", thresholded)

cv.imwrite("dilated.jpg", dilated)
cv.imshow("dilated", dilated)

cv.imwrite("eroded.jpg", eroded)
cv.imshow("eroded", eroded)

cv.imwrite("debug.jpg", debug)
cv.imshow("debug", debug)

#for n in range(len(cells)):
#    cv.imshow(f"Cell {n}", cells[n])

cv.waitKey(0) 


#img = (img*255)

#clahe = cv.createCLAHE(clipLimit = 1.0, tileGridSize=(8, 8)) 
#claheNorm = clahe.apply(img)  

#ret2,th2 = cv.threshold(claheNorm,40,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
#cv.imwrite('ret2.png', ret2) 
#cv.imwrite('th2.png', th2) 

#cv.imshow("th2", th2)
#cv.waitKey(0) 






# blur = cv.GaussianBlur(img, (9, 9), 0) 
# cv.imwrite('blur.png', blur) 
# cv.imshow("blur", blur)
# cv.waitKey(0) 

# retval, threshold = cv.threshold(blur, 40, 255, cv.THRESH_BINARY)
# cv.imwrite('threshold.png', threshold) 
# cv.imshow("threshold", threshold)
# cv.waitKey(0) 

# kernel = np.ones((30,30),np.uint8)
# tophat = cv.morphologyEx(blur, cv.MORPH_TOPHAT, kernel)

# canny1 = cv.Canny(tophat, 20, 30) 
# cv.imwrite('canny1.png', canny1) 
# cv.imshow("canny1", canny1) 
# cv.waitKey(0) 

# kernel = np.ones((7, 7), np.uint8) 
# img_dilation = cv.dilate(canny1, kernel, iterations=5)

# cv.imwrite('img_dilation.png', img_dilation) 
# cv.imshow("img_dilation", img_dilation)
# cv.waitKey(0) 

# canny2 = cv.Canny(img_dilation, 100, 200) 
# cv.imwrite('canny2.png', canny2) 
# cv.imshow("canny2", canny2) 
# cv.waitKey(0) 