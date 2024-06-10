"""
ボツ
"""

import cv2
import sys
import numpy as np

if __name__ == "__main__":
    img1 = cv2.imread('./Data/rgb_img/pic13.png')
    img2 = cv2.imread('./Data/thermal_img/pic13.png')

    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY).astype(np.float32)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY).astype(np.float32)

    (x, y), r = cv2.phaseCorrelate(gray1, gray2)
    print(x, y, r)
    W = img1.shape[1]
    H = img1.shape[0]

    if x < 0:
        x11, x12 = abs(int(x)), W
        x21, x22 = 0, W-abs(int(x))
    else:
        x21, x22 = abs(int(x)), W
        x11, x12 = 0, W-abs(int(x))
    
    if y < 0:
        y11, y12 = abs(int(y)), H
        y21, y22 = 0, H-abs(int(y))
    else:
        y21, y22 = abs(int(y)), H
        y11, y12 = 0, H-abs(int(y))
    

    print(W, x12-x11, x22-x21)
    cv2.imwrite("out1.png", img1[y11:y12, x11:x12])
    cv2.imwrite("out2.png", img2[y21:y22, x21:x22])