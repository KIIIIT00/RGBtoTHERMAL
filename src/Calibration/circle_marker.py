import numpy as np
import cv2

# 円グリッドのサイズを指定
grid_size = (4, 9)  # 例として (rows, cols)

#カメラの設定
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # 幅の設定
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 512)  # 高さの設定
# 3Dオブジェクトポイント（ワールド座標系の座標）
objp = np.zeros((np.prod(grid_size), 3), dtype=np.float32)
objp[:, :2] = np.mgrid[0:grid_size[0], 0:grid_size[1]].T.reshape(-1, 2)
#内部パラメータと歪み係数
#mtx = np.array(["""***************ここにあらかじめ求めておいた内部パラメータを書く***************"""]).reshape(3,3)
mtx = np.array([622.56592404, 0, 318.24063181, 0, 623.20968839, 245.37576884, 0, 0, 1]).reshape(3,3)
#dist = np.array(["""***************ここにあらかじめ求めておいた歪み係数を書く***************"""])
dist = np.array([ 0.14621503, -0.26374155, -0.00065967,  -0.00055428, 0.25360545])
#繰り返しのためのwhile文
# 画像座標系における検出した点のリスト
imgpoints = []

while True:
    #カメラからの画像取得
    ret1, frame = cap.read()
    if ret1:
        print("Camera open")
    
    img = frame.copy()
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    #ret, img_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
    cv2.imshow('frame',frame)

    found, corners = cv2.findCirclesGrid(gray, grid_size, flags=cv2.CALIB_CB_SYMMETRIC_GRID)
    
    if found:
        dots_frame = cv2.drawChessboardCorners(img, grid_size, corners, found)
        cv2.imshow('dots', dots_frame)

        key =cv2.waitKey(1)
        if key == 27:   #Escで終了
            break
    else:
        print("円グリッドが見つかりませんでした")
