import cv2
import numpy as np

#カメラの設定
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # 幅の設定
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # 高さの設定

while True:
    ret1, frame = cap.read()
    if ret1:
        key =cv2.waitKey(1)
        #カメラの画像の出力
        cv2.imshow('camera' , frame)

        # キャプチャ
        if key== ord('c'):
            cv2.imwrite('./Calibration/circle_grid.jpg', frame)
            break

        #繰り返し分から抜けるためのif文
        
        if key == 27:   #Escで終了
            break

cap.release()
cv2.destroyAllWindows()
