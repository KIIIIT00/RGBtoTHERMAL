import cv2

#img_gray = cv2.imread('./Calibration/demo/cold_rgb_38.png', cv2.IMREAD_GRAYSCALE)
img_gray = cv2.imread('./Calibration/thermal_threshold100.png', cv2.IMREAD_GRAYSCALE)
print(type(img_gray))
img = cv2.imread('./Calibration/thermal_threshold100.png')
#img = cv2.imread('./Calibration/demo/cold_rgb_.png')
circles = cv2.HoughCircles(img_gray, cv2.HOUGH_GRADIENT, dp=2.5, minDist=10, param1=90, param2=40, minRadius=10, maxRadius=60)

cv2.imshow("img_gray", img_gray)
for circle in circles[0]:
    x = int(circle[0])
    y = int(circle[1])
    r = int(circle[2])
    cv2.circle(img, center=(x, y), radius=r, color=(0, 0, 0), thickness=5, lineType=cv2.LINE_4, shift=0)

cv2.imshow("Circle", img)
cv2.waitKey(100000)
print(circles)