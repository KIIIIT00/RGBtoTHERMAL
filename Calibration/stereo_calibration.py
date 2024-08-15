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

thermal_mtx = np.array([793.51781303, 0, 282.89351446,
                        0, 790.70983425, 241.89215578,
                        0 ,0 ,1]).reshape(3, 3)
#print("thermal_mtx:", thermal_mtx.shape)
# 赤外線カメラの内部パラメータ
thermal_dist = np.array([-5.61011023e-1, 7.12516498e+00, -7.80341451e-3, -1.77081043e-2, -2.80952846e+1])
thermal_mtx = thermal_mtx.astype(np.float32)
thermal_dist = thermal_dist.astype(np.float32)

# RGBカメラの内部パラメータ
rgb_mtx = np.array([621.80090236, 0, 309.61717191, 0, 624.22815912, 234.27475688, 0, 0, 1]).reshape(3,3)
rgb_dist = np.array([ 0.1311874, -0.21356334, -0.00798234,  -0.00648277, 0.10214072])
rgb_mtx = rgb_mtx.astype(np.float32)
rgb_dist = rgb_dist.astype(np.float32)

# 赤外線画像読み込み
thermal_image_path = './Calibration/ExternalParameter_Chessboard/THERMAL/thermal_325.jpg'

# RGB画像読み込み
rgb_image_path = './Calibration/ExternalParameter_Chessboard/RGB/rgb_325.jpg'

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

if len(thermal_corners) == 50 and len(rgb_corners) == 50:
        # プロジェクション誤差
        projection_thermal, projection_rgb = stereo_calibration.get_projection_error()

        # エピポーラ誤差
        epipolar_error = stereo_calibration.get_epipolar_error()

print("projection_thermal:", projection_thermal)
print("projection_rgb:", projection_rgb)
print("epipolar_error:", epipolar_error)

# プロット
stereo_calibration.plot_cameras()

stereo_calibration.plot_cameras_pos()