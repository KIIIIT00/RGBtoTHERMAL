import cv2
import numpy as np
import os
import glob
from tqdm import tqdm    # 繰り返し処理の進捗を表示するためもの

# Defining the dimensions of checkerboard
CHECKERBOARD = (7,10)       # チェスボードの交点の縦と横の個数，今回は7×10個の交点があるチェスボードを用いる

# cv2.TERM_CRITERIA_EPS:指定された精度(epsilon)に到達したら繰り返し計算を終了する
# cv2.TERM_CRITERIA_MAX_ITER:指定された繰り返し回数(max_iter)に到達したら繰り返し計算を終了する
# cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER : 上記のどちらかの条件が満たされた時に繰り返し計算を終了する
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Creating vector to store vectors of 3D points for each checkerboard image
objpoints = []          # 三次元座標(ワールド座標)を格納する配列
# Creating vector to store vectors of 2D points for each checkerboard image
imgpoints = []          # 二次元座標(画像座標)を格納する配列


# Defining the world coordinates for 3D points
objp = np.zeros((1, CHECKERBOARD[0]*CHECKERBOARD[1], 3), np.float32)                # チェスボードの交点の個数分だけ[0,0,0]を作る
objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)      # チェスボードの交点のワールド座標

# Extracting path of individual image stored in a given directory
images = glob.glob('./pics/*.png')

print("全ての画像の交点の画像座標を求めています")
for filepath in tqdm(images):       # ※tqdmは繰り返し処理の進捗を表示するためのもの
    img = cv2.imread(filepath)                      # 変数filepathが持っている名前の画像を開く
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)     # 白黒画像にする
    # Find the chess board corners
    # If desired number of corners are found in the image then ret = tr
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE)   # 画像から7×10個の交点を見つける
    
    if ret == True:     # 交点を見つけられたら
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