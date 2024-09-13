import cv2
import numpy as np

#カメラの設定
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # 幅の設定
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # 高さの設定
while True:
    # 画像の読み込み
    #img = cv2.imread('calibration_image.jpg')
    ret1, frame = cap.read()
    if ret1:
        #カメラの画像の出力
        cv2.imshow('camera' , frame)


    # グレースケールに変換
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 円グリッドのサイズを指定
    grid_size = (4, 9)  # 例として (rows, cols)

    # 円グリッドを検出
    #criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    found, corners = cv2.findCirclesGrid(gray, grid_size, flags=cv2.CALIB_CB_ASYMMETRIC_GRID)

    if found:
        # カメラキャリブレーション
        objp = np.zeros((np.prod(grid_size), 3), dtype=np.float32)
        objp[:, :2] = np.mgrid[0:grid_size[0], 0:grid_size[1]].T.reshape(-1, 2)

        objpoints = []
        imgpoints = []

        objpoints.append(objp)
        imgpoints.append(corners)

        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

        # 外部パラメータの取得
        rotation_vector = rvecs[0]  # 回転ベクトル
        translation_vector = tvecs[0]  # 並進ベクトル

        print("Rotation Vector:")
        print(rotation_vector)
        print("Translation Vector:")
        print(translation_vector)
    else:
        print("円グリッドが見つかりませんでした。")


        #繰り返し分から抜けるためのif文
        key =cv2.waitKey(1)
        if key == 27:   #Escで終了
            break
cap.release()
cv2.destroyAllWindows()
