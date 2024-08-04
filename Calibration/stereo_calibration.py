"""
RGBカメラと赤外線カメラをステレオカメラとみなしたカメラキャリブレーション
"""

# インポート
import numpy as np
import cv2
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from utils.cameracalibration import CameraCalibration
from utils.EllipseFinder import EllipseFinder
from utils.ExternalParameter import ExternalParameterCalculator
from utils.StereoCameraCalibration import StereoCameraCalibration


# チェスボードの設定
chessboard_size = (5, 5)

thermal_mtx = np.array([769.34777275, 0, 284.87790552,
                        0, 771.09576331, 247.82882986,
                        0 ,0 ,1]).reshape(3, 3)
#print("thermal_mtx:", thermal_mtx.shape)
# 赤外線カメラの内部パラメータ
thermal_dist = np.array([-7.91810594e-1, 9.81301368e+00, -8.42753413-3, -1.46486095e-2, -3.88815631e+1])
thermal_mtx = thermal_mtx.astype(np.float32)
thermal_dist = thermal_dist.astype(np.float32)

# RGBカメラの内部パラメータ
rgb_mtx = np.array([622.56592404, 0, 318.24063181, 0, 623.20968839, 245.37576884, 0, 0, 1]).reshape(3,3)
rgb_dist = np.array([ 0.14621503, -0.26374155, -0.00065967,  -0.00055428, 0.25360545])
rgb_mtx = rgb_mtx.astype(np.float32)
rgb_dist = rgb_dist.astype(np.float32)

# 赤外線画像読み込み
thermal_image_path = './Calibration/ExternalParameter_Chessboard/THERMAL/thermal_174.jpg'

# RGB画像読み込み
rgb_image_path = './Calibration/ExternalParameter_Chessboard/RGB/rgb_174.jpg'

rgb_gray = cv2.imread(rgb_image_path, cv2.COLOR_BGR2GRAY)

# 赤外線画像におけるコーナーの検知
thermal_finder = EllipseFinder(thermal_image_path)
thermal_corners = thermal_finder.run()
if thermal_corners is not False:
        print("thermnal corner:", len(thermal_corners))

# RGB画像におけるコーナーの検知
rgb_finder = EllipseFinder(rgb_image_path)
rgb_corners = rgb_finder.run()

if rgb_corners is not False:
        print("rgb corner:", len(rgb_corners))

# ステレオキャリブレーション
stereo_calibration = StereoCameraCalibration(chessboard_size, rgb_mtx, rgb_dist, thermal_mtx, thermal_dist)

# コーナー追加
stereo_calibration.add_corners(rgb_image_path, rgb_corners, thermal_image_path, thermal_corners)

# キャリブレーション
stereo_calibration.stereo_calibration()

# プロット
stereo_calibration.plot_cameras()

stereo_calibration.plot_cameras_pos()