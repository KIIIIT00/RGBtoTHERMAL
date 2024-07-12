"""
楕円を検出する
"""
import cv2
import numpy as np
import matplotlib.pyplot as plt

# 画像の読み込み
image = cv2.imread('./Calibration/chessboard_calibration_data/thermal/pic62.jpg')
image = cv2.bitwise_not(image)
# グレースケールに変換
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 閾値処理
# 赤外線のとき
_, thresh = cv2.threshold(gray,93, 255, cv2.THRESH_BINARY)
# RGBのとき
#_, thresh = cv2.threshold(gray, 125, 255, cv2.THRESH_BINARY)

# 輪郭を検出
contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
# 赤外線のとき
min_axis_length = 35 # 最小軸長
max_axis_length = 80  # 最大軸長
# RGBのとき
#min_axis_length = 15 # 最小軸長
#max_axis_length = 50  # 最大軸長

# 楕円の中心(x,y)を格納する辞書
point_list = []
# 楕円をフィット
for contour in contours:
    if len(contour) >= 5:  # 楕円フィッティングには最低5つの点が必要
        ellipse = cv2.fitEllipse(contour)
        (center, axes, angle) = ellipse
        (major_axis, minor_axis) = (max(axes), min(axes))  # 長軸と短軸

        # 楕円の大きさを制限
        if min_axis_length <= major_axis <= max_axis_length and min_axis_length <= minor_axis <= max_axis_length:
            center = (int(center[0]), int(center[1]))  # 楕円の中心
            print(f'x:{center[0]}, y:{center[1]}')
            point_list.append([int(center[0]), int(center[1])])
            cv2.ellipse(image, ellipse, (0, 255, 0), 2)  # 楕円を描画
            cv2.circle(image, center, 5, (0, 0, 255), -1)  # 中心を描画

# y座標でソート
point_list_sorted = sorted(point_list, key=lambda coord: coord[1])


print("----------sorted-----------")
for point in point_list_sorted:
    x, y = point
    print(f'x:{x}, y:{y}')
# 画像を表示
plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
plt.show()
