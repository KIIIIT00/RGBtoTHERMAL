import numpy as np
import cv2
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from utils.CameraCalibration import CameraCalibration
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

# RGB画像読み込み
thermal_image_path = './Calibration/chessboard_calibration_data/thermal/pic63.jpg'

# RGB画像読み込み
rgb_image_path = './Calibration/chessboard_calibration_data/rgb/pic63.jpg'

# 赤外線画像におけるコーナーの検知
thermal_finder = EllipseFinder(thermal_image_path)
thermal_corners = thermal_finder.run()
if thermal_corners is not False:
        print("thermnal corner:", len(thermal_corners))

rgb_finder = EllipseFinder(rgb_image_path)
rgb_corners = rgb_finder.run()

if rgb_corners is not False:
        print("rgb corner:", len(rgb_corners))

thermal_calibration = ExternalParameterCalculator(chessboard_size, thermal_mtx, thermal_dist)
thermal_corners2 = thermal_calibration.add_corners(thermal_image_path, thermal_corners)

thermal_ret, thermal_rotation_vector, thermal_translation_vector = thermal_calibration.calculate_external_parameters(thermal_corners2)
print("Ret:", thermal_ret)
print("Rotation Vector:")
print(thermal_rotation_vector)
print("Rotation Vector shape:", thermal_rotation_vector.shape)
print("Translation Vector:")
print(thermal_translation_vector)
print("Translation Vector shape:", thermal_translation_vector.shape)

print("corner:", thermal_corners)
# 画像座標
image_point = np.array([[thermal_corners[0]], [thermal_corners[1]]], dtype=np.float32)
image_point_5 = np.array([[thermal_corners[8]], [thermal_corners[9]]], dtype=np.float32)
image_point_20 = np.array([[thermal_corners[40]], [thermal_corners[41]]], dtype=np.float32)
image_point_25 = np.array([[thermal_corners[48]], [thermal_corners[49]]], dtype=np.float32)
# 画像座標をカメラ座標に変換
#camera_point = calibration.image_to_camera(image_point)
camera_point = thermal_calibration.undistort_points(image_point)
camera_point_5 = thermal_calibration.undistort_points(image_point_5)
camera_point_20 = thermal_calibration.undistort_points(image_point_20)
camera_point_25 = thermal_calibration.undistort_points(image_point_25)

print("カメラ座標:", camera_point)
print("カメラ座標5:", camera_point_5)
print("カメラ座標20:", camera_point_20)
print("カメラ座標25:", camera_point_25)

# カメラ座標をワールド座標に変換
world_point = thermal_calibration.camerapoint_to_worldpoint(camera_point, thermal_rotation_vector, thermal_translation_vector)
world_point_5 = thermal_calibration.camerapoint_to_worldpoint(camera_point_5, thermal_rotation_vector, thermal_translation_vector)
world_point_20 = thermal_calibration.camerapoint_to_worldpoint(camera_point_20,thermal_rotation_vector, thermal_translation_vector)
world_point_25 = thermal_calibration.camerapoint_to_worldpoint(camera_point_25, thermal_rotation_vector, thermal_translation_vector)

# カメラの位置と視点方向を表示
camera_position, camera_direction = thermal_calibration.wolrd_in_camerapoint(image_point, thermal_rotation_vector, thermal_translation_vector)
#world_point = calibration.camera_to_world(camera_point, rotation_vector, translation_vector)
print("ワールド座標:", world_point)# 3Dプロット
print("ワールド座標5:", world_point_5)#
print("ワールド座標20:", world_point_20)#
print("ワールド座標25:", world_point_25)#
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# ワールド座標の点をプロット
#ax.scatter(world_point[0], world_point[1], world_point[2], c='r', marker='o')
#ax.scatter(world_point_5[0], world_point_5[1], world_point_5[2], c='g', marker='o')
#ax.scatter(world_point_20[0], world_point_20[1], world_point_20[2], c='b', marker='o')
#ax.scatter(world_point_25[0], world_point_25[1],world_point_20[2], c='y', marker='o')
# カメラの位置をプロット
ax.scatter(camera_position[0], camera_position[1], camera_position[2], c='b', marker='x', label='Camera Position')

# カメラの視点方向をプロット
ax.quiver(camera_position[0], camera_position[1], camera_position[2], 
          camera_direction[0], camera_direction[1], camera_direction[2], 
          length=5.0, color='b', label='Camera Direction')
# ラベルを設定
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

# 表示
plt.show()