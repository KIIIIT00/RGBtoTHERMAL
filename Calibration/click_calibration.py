"""
画像をクリックしたところでカメラキャリブレーションを行う
"""

import cv2
import numpy as np
import glob
from utils.cameracalibration import CameraCalibration
from Calibration.utils.EllipseFinder import EllipseFinder

chessboard_size = (5, 5)
calibration = CameraCalibration(chessboard_size)

images = glob.glob('./Calibration/chessboard_calibration_data/thermal/*.jpg')
cal_count = 1
for fname in images:
    print("-----start add corners-----")
    finder = EllipseFinder(fname)
    corners = finder.run()
    if corners is not False:
        print(len(corners))
        calibration.add_corners(fname, corners)
        print(f'calibration count:', cal_count)
        cal_count += 1

    print("-----finish add corners-----")

image_size = (640, 512)
ret, mtx, dist, rvecs, tvecs = calibration.calibrate(image_size)

print("キャリブレーション結果:")
print("リプロジェクションエラー:", ret)
print("カメラ行列:\n", mtx)
print("歪み係数:\n", dist)