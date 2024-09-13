import numpy as np
import cv2

# 3次元座標を描画
def draw(img, corners, imgpts):
    #corner = tuple(corners[0].ravel())
    img = cv2.line(img, (int(corners[0][0][0]), int(corners[0][0][1])), (int(imgpts[0][0][0]), int(imgpts[0][0][1])), (255,0,0), 5)   # x
    img = cv2.line(img, (int(corners[0][0][0]), int(corners[0][0][1])), (int(imgpts[1][0][0]), int(imgpts[1][0][1])), (0,255,0), 5)   # y
    img = cv2.line(img, (int(corners[0][0][0]), int(corners[0][0][1])), (int(imgpts[2][0][0]), int(imgpts[2][0][1])), (0,0,255), 5)   # z
    return img



# 円グリッドのサイズを指定
grid_size = (4, 9)  # 例として (rows, cols)
ret2 = False #　交点を見つけたかどうか

#カメラの設定
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # 幅の設定
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 512)  # 高さの設定
# 3Dオブジェクトポイント（ワールド座標系の座標）
objp = np.zeros((np.prod(grid_size), 3), dtype=np.float32)
objp[:, :2] = np.mgrid[0:grid_size[0], 0:grid_size[1]].T.reshape(-1, 2)

# 内部パラメータと歪み係数
#mtx = np.array(["""***************ここにあらかじめ求めておいた内部パラメータを書く***************"""]).reshape(3,3)
mtx = np.array([622.56592404, 0, 318.24063181, 0, 623.20968839, 245.37576884, 0, 0, 1]).reshape(3,3)
#dist = np.array(["""***************ここにあらかじめ求めておいた歪み係数を書く***************"""])
dist = np.array([ 0.14621503, -0.26374155, -0.00065967,  -0.00055428, 0.25360545])

while True:
    ret1, frame = cap.read()
    if not ret1:
        print("Can't Open Camera")
    
    img = frame.copy()
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    #ret, img_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
    cv2.imshow('frame',frame)

    key =cv2.waitKey(1)
    if key == 27:   #Escで終了
        break
