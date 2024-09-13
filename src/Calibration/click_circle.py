import cv2
import numpy as np
import matplotlib.pyplot as plt

# 円を検出するための関数
def detect_circles(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=30, param1=50, param2=30, minRadius=10, maxRadius=50)
    return circles

# 円の中心点がクリックされたかどうかをチェックする関数
def is_point_in_circle(x, y, circle):
    cx, cy, r = circle
    return (x - cx) ** 2 + (y - cy) ** 2 <= r ** 2

# クリックイベントのコールバック関数
def on_click(event, x, y, flags, param):
    global img, circles

    if event == cv2.EVENT_LBUTTONDOWN:
        for circle in circles[0, :]:
            if is_point_in_circle(x, y, circle):
                cv2.circle(img, (circle[0], circle[1]), circle[2], (0, 0, 255), -1)
                break

# 画像を読み込み
img = cv2.imread('./Calibration/demo/giza1.png')

# 円を検出
circles = detect_circles(img)

# 円を描画
if circles is not None:
    circles = np.round(circles[0, :]).astype("int")
    for (x, y, r) in circles:
        cv2.circle(img, (x, y), r, (0, 255, 0), 4)

# 画像を表示し、クリックイベントを設定
cv2.namedWindow('image')
cv2.setMouseCallback('image', on_click)

while True:
    cv2.imshow('image', img)
    if cv2.waitKey(1) & 0xFF == 27:  # ESCキーで終了
        break

cv2.destroyAllWindows()
