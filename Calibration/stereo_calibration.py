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

thermal_mtx = np.array([773.41392054, 0, 329.198468,
                        0, 776.32513558, 208.53439152,
                        0 ,0 ,1]).reshape(3, 3)
#print("thermal_mtx:", thermal_mtx.shape)
# 赤外線カメラの内部パラメータ
thermal_dist = np.array([1.67262996e-01, -2.94477097e+00, -2.30689758e-02, -1.33138573e-03, 1.02082943e+01])
thermal_mtx = thermal_mtx.astype(np.float32)
thermal_dist = thermal_dist.astype(np.float32)

# RGBカメラの内部パラメータ
rgb_mtx = np.array([621.80090236, 0, 309.61717191, 0, 624.22815912, 234.27475688, 0, 0, 1]).reshape(3,3)
rgb_dist = np.array([0.1311874, -0.21356334, -0.00798234,  -0.00648277, 0.10214072])
rgb_mtx = rgb_mtx.astype(np.float32)
rgb_dist = rgb_dist.astype(np.float32)

image_count = 716
# 赤外線画像読み込み
thermal_image_path = f'./Calibration/ExternalParameter_Chessboard/THERMAL/thermal_{str(image_count)}.jpg'

# RGB画像読み込み
rgb_image_path = f'./Calibration/ExternalParameter_Chessboard/RGB/rgb_{str(image_count)}.jpg'

thermal_imgpoints2_npy = './Calibration/Calibration_result/external/thermal_imgpoints2_'+str(image_count) + '.npy'
thermal_corners_npy = './Calibration/Calibration_result/external/thermal_corners_'+str(image_count) + '.npy'
rgb_imgpoints2_npy = './Calibration/Calibration_result/external/rgb_imgpoints2_'+str(image_count) + '.npy'
rgb_corners_npy = './Calibration/Calibration_result/external/rgb_corners_'+str(image_count) + '.npy'

rgb_gray = cv2.imread(rgb_image_path, cv2.COLOR_BGR2GRAY)

# 赤外線画像におけるコーナーの検知
# thermal_finder = EllipseFinder(thermal_image_path)
# thermal_corners = thermal_finder.run()
# if thermal_corners is not False:
#         print("thermnal corner:", len(thermal_corners))

# # RGB画像におけるコーナーの検知
# rgb_finder = EllipseFinder(rgb_image_path)
# rgb_corners = rgb_finder.run()

# if rgb_corners is not False:
#         print("rgb corner:", len(rgb_corners))

# ステレオキャリブレーション
stereo_calibration = StereoCameraCalibration(chessboard_size, rgb_mtx, rgb_dist, thermal_mtx, thermal_dist)

# コーナー追加
# stereo_calibration.add_corners(rgb_image_path, rgb_corners, thermal_image_path, thermal_corners)

# npyファイル読み込み
stereo_calibration.load_imapoints_npy(thermal_imgpoints2_npy, rgb_imgpoints2_npy)

# キャリブレーション
stereo_calibration.stereo_calibration()

# if len(thermal_corners) == 50 and len(rgb_corners) == 50:
#         # プロジェクション誤差
#         projection_thermal, projection_rgb = stereo_calibration.get_projection_error()

#         # エピポーラ誤差
#         epipolar_error = stereo_calibration.get_epipolar_error()
# 再投影誤差
projection_thermal, projection_rgb = stereo_calibration.get_projection_error()

# エピポーラ誤差
epipolar_error = stereo_calibration.get_epipolar_error()
print("projection_thermal:", projection_thermal)
print("projection_rgb:", projection_rgb)
print("epipolar_error:", epipolar_error)

# プロット
stereo_calibration.plot_cameras()

stereo_calibration.plot_cameras_pos()