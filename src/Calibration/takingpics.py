"""
カメラキャリブレーション用の写真を撮影する
"""

import numpy as np
import cv2

# カメラの設定、デバイスID
cap = cv2.VideoCapture(0)
count = 0

# カメラの解像度を設定
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    _, frame = cap.read()

    cv2.imshow('camera', frame)

    # 繰り返しから抜けるためのif文
    key = cv2.waitKey(1)
    if key == ord('a'):
        cv2.imwrite('./Calibration/'f'pic{count}.jpg', frame)
        # cv2.imwrite('./Calibration/chessboard_calibration_data/rgb/'f'pic{count}.jpg', frame)
        #cv2.imwrite('./Calibration/circlegrid_calibration_data/rgb/'f'pic{count}.jpg', frame)
        count += 1

    elif key == 27: #Escで終了
        break

cap.release()
cv2.destroyAllWindows()