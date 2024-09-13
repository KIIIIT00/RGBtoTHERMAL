"""
輪郭検出
"""
import os
import cv2
import numpy as np


img = cv2.imread('./Calibration/pic4.jpg', cv2.IMREAD_GRAYSCALE)
img = cv2.bitwise_not(img)
#print(os.path.isfile('./Calibration/thermal_threshold99.jpg'))
img_disp = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# 円の大きさの閾値（最小半径と最大半径）
min_radius = 10
max_radius = 100

# 輪郭の点の描画
for contour in contours:
    # 輪郭を囲む円を求める
    (x, y), radius = cv2.minEnclosingCircle(contour)
    
    # 中心座標と半径を整数に変換
    center = (int(x), int(y))
    radius = int(radius)
    
    # 円の大きさが閾値内であるかを確認
    if min_radius <= radius <= max_radius:
        # 中心座標を整数に変換
        center = (int(x), int(y))
        print(f'x : {x}, y : {y}')
        
        # 中心に円を描画
        cv2.circle(img_disp, center, 5, (0, 255, 0), -1)  # 中心点を緑色で描画
        cv2.circle(img_disp, center, radius, (255, 0, 0), 2)  # 輪郭を囲む円を青色で描画
cv2.imshow("Image", img_disp)
cv2.imwrite("./Calibration/findContours110.jpg", img_disp)
cv2.waitKey()