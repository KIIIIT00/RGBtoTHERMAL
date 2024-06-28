import cv2
import numpy as np

# 画像の読み込み
img = cv2.imread('./Calibration/circle_grid.jpg')

# グレースケールに変換
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 円グリッドのサイズを指定
grid_size = (4, 9)  # 例として (rows, cols)

# 円グリッドを検出
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

