"""
Asymmetry-CircleGridでカメラキャリブレーションを行う
"""

import numpy as np
import cv2
import os
import glob
from tqdm import tqdm    # 繰り返し処理の進捗を表示するためもの
grid_size = (4, 9)

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Creating vector to store vectors of 3D points for each checkerboard image
objpoints = []          # 三次元座標(ワールド座標)を格納する配列
# Creating vector to store vectors of 2D points for each checkerboard image
imgpoints = []          # 二次元座標(画像座標)を格納する配列

# 3Dオブジェクトポイント（ワールド座標系の座標）
objp = np.zeros((np.prod(grid_size), 3), dtype=np.float32)
objp[:, :2] = np.mgrid[0:grid_size[0], 0:grid_size[1]].T.reshape(-1, 2)

images = glob.glob('./Calibration/calibration_data/*.jpg')
print("全ての画像の交点の画像座標を求めています")
for filepath in tqdm(images):       # ※tqdmは繰り返し処理の進捗を表示するためのもの
    img = cv2.imread(filepath)                      # 変数filepathが持っている名前の画像を開く
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    found, corners = cv2.findCirclesGrid(gray, grid_size, flags=cv2.CALIB_CB_ASYMMETRIC_GRID)

    if found:
        objpoints.append(objp)          # 交点のワールド座標をobjpointsに追加
        # refining pixel coordinates for given 2d points.
        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        
        imgpoints.append(corners2)

print("\nカメラキャリブレーションを行っています")
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)    # ここでカメラキャリブレーションを行っている

print(f'\n内部パラメータ: \n{mtx}')
print(f'\n歪み係数: \n{dist}')
#print(f'\n外部パラメータの回転行列：\n{rvecs}')
#print(f'\n外部パラメータの並進ベクトル：\n{tvecs}')

# 予め求めておくことができるのは内部パラメータと歪み係数である．
# カメラの位置を動かすと外部パラメータは変わってしまうので，この段階で求めた外部パラメータは必要ない．

#【参考】
# https://miyashinblog.com/opencv-undistort/