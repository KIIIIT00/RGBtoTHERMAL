import numpy as np
import cv2
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from utils.cameracalibration import CameraCalibration
from utils.EllipseFinder import EllipseFinder
from utils.ExternalParameter import ExternalParameterCalculator

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
thermal_image_path = './Calibration/ExternalParameter_Chessboard/THERMAL/thermal_2.jpg'

# RGB画像読み込み
rgb_image_path = './Calibration/ExternalParameter_Chessboard/RGB/rgb_2.jpg'

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

# 赤外線カメラの外部パラメータを求める
thermal_calibration = ExternalParameterCalculator(chessboard_size, thermal_mtx, thermal_dist)
thermal_corners2 = thermal_calibration.add_corners(thermal_image_path, thermal_corners)
thermal_ret, thermal_rotation_vector, thermal_translation_vector = thermal_calibration.calculate_external_parameters(thermal_corners2)
print("--------------------")
print("Ret:", thermal_ret)
print("Rotation Vector:", thermal_rotation_vector)
print("Rotation Vector shape:", thermal_rotation_vector.shape)
print("Translation Vector:", thermal_translation_vector)
print("Translation Vector shape:", thermal_translation_vector.shape)
print("corner:", thermal_corners)
print("--------------------")

# RGBカメラの外部パラメータを求める
rgb_calibration = ExternalParameterCalculator(chessboard_size, rgb_mtx, rgb_dist)
rgb_corners2 = rgb_calibration.add_corners(rgb_image_path, rgb_corners)
rgb_ret, rgb_rotation_vector, rgb_translation_vector = rgb_calibration.calculate_external_parameters(rgb_corners2)
print("Ret:", rgb_ret)
print("Rotation Vector:", rgb_rotation_vector)
print("Rotation Vector shape:", rgb_rotation_vector.shape)
print("Translation Vector:", rgb_translation_vector)
print("Translation Vector shape:", rgb_translation_vector.shape)
print("corner:", rgb_corners)
print("--------------------")

# 画像座標
image_point = np.array([[thermal_corners[0]], [thermal_corners[1]]], dtype=np.float32)
# 画像座標をカメラ座標に変換
#camera_point = calibration.image_to_camera(image_point)
camera_point = thermal_calibration.undistort_points(image_point)
print("カメラ座標:", camera_point)
# カメラ座標をワールド座標に変換
world_point = thermal_calibration.camerapoint_to_worldpoint(camera_point, thermal_rotation_vector, thermal_translation_vector)
# カメラの位置と視点方向を表示
camera_position, camera_direction = thermal_calibration.world_in_camerapoint(image_point, thermal_rotation_vector, thermal_translation_vector)
#world_point = calibration.camera_to_world(camera_point, rotation_vector, translation_vector)
print("ワールド座標:", world_point)# 3Dプロット

# RGB画像座標
rgb_image_point = np.array([[rgb_corners[0]], [rgb_corners[1]]], dtype=np.float32)
# 画像座標をカメラ座標に変換
rgb_camera_point = rgb_calibration.undistort_points(rgb_image_point)
print("RGBカメラ座標:", rgb_camera_point)
# カメラ座標をワールド座標に変換
rgb_world_point = rgb_calibration.camerapoint_to_worldpoint(rgb_camera_point, rgb_rotation_vector, rgb_translation_vector)
# RGBカメラの位置と視点方向を表示
rgb_camera_position, rgb_camera_direction = rgb_calibration.world_in_camerapoint(rgb_image_point, rgb_rotation_vector, rgb_translation_vector)
print("RGBワールド座標:", rgb_world_point)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# ワールド座標の点をプロット
#ax.scatter(world_point[0], world_point[1], world_point[2], c='r', marker='o')
#ax.scatter(world_point_5[0], world_point_5[1], world_point_5[2], c='g', marker='o')
#ax.scatter(world_point_20[0], world_point_20[1], world_point_20[2], c='b', marker='o')
#ax.scatter(world_point_25[0], world_point_25[1],world_point_20[2], c='y', marker='o')
# カメラの位置をプロット
ax.scatter(camera_position[0], camera_position[1], camera_position[2], c='b', marker='x', label='Camera Position')

# RGBカメラの位置をプロット
ax.scatter(rgb_camera_position[0], rgb_camera_position[1], rgb_camera_position[2], c='r', marker='o', label='RGB Camera Position')

# カメラの視線方向をプロット
ax.quiver(camera_position[0], camera_position[1], camera_position[2], 
          camera_direction[0], camera_direction[1], camera_direction[2], 
          length=5.0, color='b', label='Camera Direction')

ax.quiver(rgb_camera_position[0], rgb_camera_position[1], rgb_camera_position[2], 
         rgb_camera_direction[0], rgb_camera_direction[1], rgb_camera_direction[2], 
         length=5.0, color='r', label='RGB Camera Direction')
# ラベルを設定
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

# 表示
plt.show()