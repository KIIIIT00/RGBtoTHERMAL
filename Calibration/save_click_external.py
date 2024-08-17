"""
外部パラメータを求めて，そのプロット画像を保存する
"""
import numpy as np
import cv2
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from utils.cameracalibration import CameraCalibration
from utils.EllipseFinder import EllipseFinder
from utils.ExternalParameter import ExternalParameterCalculator

    
chessboard_size = (5, 5)
thermal_mtx = np.array([770.61648493, 0, 336.94307903,
                         0, 774.81856137, 203.23000118,
                         0 ,0 ,1]).reshape(3, 3)
#print("thermal_mtx:", thermal_mtx.shape)
# 赤外線カメラの内部パラメータ
thermal_dist = np.array([2.64764544e-01, -4.18415905e+00, -2.55476500e-02, 1.19220012e-03, 1.52325890e+01])
thermal_mtx = thermal_mtx.astype(np.float32)
thermal_dist = thermal_dist.astype(np.float32)

# RGBカメラの内部パラメータ
rgb_mtx = np.array([621.80090236, 0, 309.61717191, 0, 624.22815912, 234.27475688, 0, 0, 1]).reshape(3,3)
rgb_dist = np.array([ 0.1311874, -0.21356334, -0.00798234,  -0.00648277, 0.10214072])
rgb_mtx = rgb_mtx.astype(np.float32)
rgb_dist = rgb_dist.astype(np.float32)

#image_count = 216
start_count = 303
finish_count = 327
for image_count in range(start_count, finish_count):
    # 赤外線画像読み込み
    thermal_image_path = './Calibration/ExternalParameter_Chessboard/THERMAL/thermal_'+str(image_count) + '.jpg'
    thermal_img = cv2.imread(thermal_image_path)

    # RGB画像読み込み
    rgb_image_path = './Calibration/ExternalParameter_Chessboard/RGB/rgb_'+str(image_count)+'.jpg'
    rgb_img = cv2.imread(rgb_image_path)

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
    #world_point = thermal_calibration.camerapoint_to_worldpoint(camera_point, thermal_rotation_vector, thermal_translation_vector)
    # カメラの位置と視点方向を表示
    camera_position, camera_direction = thermal_calibration.world_in_camerapoint(image_point, thermal_rotation_vector, thermal_translation_vector)
    #world_point = calibration.camera_to_world(camera_point, rotation_vector, translation_vector)
    print("ワールド座標:", camera_position)# 3Dプロット

    # RGB画像座標
    rgb_image_point = np.array([[rgb_corners[0]], [rgb_corners[1]]], dtype=np.float32)
    # 画像座標をカメラ座標に変換
    rgb_camera_point = rgb_calibration.undistort_points(rgb_image_point)
    print("RGBカメラ座標:", rgb_camera_point)
    # カメラ座標をワールド座標に変換
    #rgb_world_point = rgb_calibration.camerapoint_to_worldpoint(rgb_camera_point, rgb_rotation_vector, rgb_translation_vector)
    # RGBカメラの位置と視点方向を表示
    rgb_camera_position, rgb_camera_direction = rgb_calibration.world_in_camerapoint(rgb_image_point, rgb_rotation_vector, rgb_translation_vector)
    print("RGBワールド座標:", rgb_camera_position)
    thermal_projection = thermal_calibration.get_projection_errors()
    rgb_projection = rgb_calibration.get_projection_errors()

    print("thermal projection:", thermal_projection)
    print("rgb projection:", rgb_projection)
    
    # カメラの位置や再投影誤差などをテキストファイルに保存
    save_txt =  './Calibration/Calibration_result/external/cameras_position'+str(image_count) + '.txt'
    with open(save_txt, 'w') as file:
        file.write("Thermal Camera Position:\n")
        file.write(f"x:{str(camera_position[0])}, y:{str(camera_position[1])}, z:{str(camera_position[2])} \n")
        file.write("Thermal Camera Direcion: \n")
        file.write(f"x:{str(camera_direction[0])}, y:{str(camera_direction[1])}, z:{str(camera_direction[2])} \n")
        file.write("RGB Camera Position \n")
        file.write(f"x:{str(rgb_camera_position[0])}, y:{str(rgb_camera_position[1])}, z:{str(rgb_camera_position[2])} \n")
        file.write("RGB Camera Direcion: \n")
        file.write(f"x:{str(rgb_camera_direction[0])}, y:{str(rgb_camera_direction[1])}, z:{str(rgb_camera_direction[2])} \n")
        file.write("Thermal Projection: \n")
        file.write(f"{str(thermal_projection)} \n" )
        file.write("RGB Projection: \n")
        file.write(f"{str(rgb_projection)} \n")
        
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    # 再投影した画像を保存するファイル名
    thermal_projection_img = './Calibration/Calibration_result/external/thermal_projection_'+str(image_count) + '.jpg'
    rgb_projection_img = './Calibration/Calibration_result/external/rgb_projection_'+str(image_count) + '.jpg'
    thermal_calibration.re_draw(thermal_img, thermal_projection_img)
    rgb_calibration.re_draw(rgb_img, rgb_projection_img)
    
    # npyファイルに保存する
    thermal_imgpoints2_npy = './Calibration/Calibration_result/external/thermal_imgpoints2_'+str(image_count) + '.npy'
    thermal_corners_npy = './Calibration/Calibration_result/external/thermal_corners_'+str(image_count) + '.npy'
    rgb_imgpoints2_npy = './Calibration/Calibration_result/external/rgb_imgpoints2_'+str(image_count) + '.npy'
    rgb_corners_npy = './Calibration/Calibration_result/external/rgb_corners_'+str(image_count) + '.npy'
    thermal_calibration.save_imgpoints2_npy(thermal_imgpoints2_npy)
    thermal_calibration.save_corners_npy(thermal_corners_npy)
    rgb_calibration.save_imgpoints2_npy(rgb_imgpoints2_npy)
    rgb_calibration.save_corners_npy(rgb_corners_npy)
    
    # ワールド座標の点をプロット
    #ax.scatter(world_point[0], world_point[1], world_point[2], c='r', marker='o')
    #ax.scatter(world_point_5[0], world_point_5[1], world_point_5[2], c='g', marker='o')
    #ax.scatter(world_point_20[0], world_point_20[1], world_point_20[2], c='b', marker='o')
    #ax.scatter(world_point_25[0], world_point_25[1],world_point_20[2], c='y', marker='o')
    # カメラの位置をプロット
    ax.scatter(camera_position[0], camera_position[1], camera_position[2], c='b', marker='x', label='Camera Position')

    # カメラの位置を表示
    print("Thermal Camera Position: x:{x}, y:{y}, z:{z}".format(x = camera_position[0], y = camera_position[1], z=camera_position[2]))
    print("RGB Camera Position: x:{x}, y:{y}, z:{z}".format(x =rgb_camera_position[0], y = rgb_camera_position[1], z = rgb_camera_position[2]))

    # カメラの視線方向を表示
    print("Thermal Camera Direction: x:{x}, y:{y}, z:{z}".format(x = camera_direction[0], y = camera_direction[1], z = camera_direction[2]))
    print("RGB Camera Direction: x:{x}, y:{y}, z:{z}".format(x = rgb_camera_direction[0], y = rgb_camera_direction[1], z = rgb_camera_direction[2]))

    # RGBカメラの位置をプロット
    ax.scatter(rgb_camera_position[0], rgb_camera_position[1], rgb_camera_position[2], c='r', marker='o', label='RGB Camera Position')

    # カメラの視線方向をプロット
    ax.quiver(camera_position[0], camera_position[1], camera_position[2], 
          camera_direction[0], camera_direction[1], camera_direction[2], 
          length=5.0, color='b', label=' Thermal Camera Direction')

    ax.quiver(rgb_camera_position[0], rgb_camera_position[1], rgb_camera_position[2], 
         rgb_camera_direction[0], rgb_camera_direction[1], rgb_camera_direction[2], 
         length=5.0, color='r', label='RGB Camera Direction')
    
    # ラベルを設定
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    
    # プロットした画像を保存する
    plot_img =  './Calibration/Calibration_result/external/cameras_plot'+str(image_count) + '.jpg'
    plt.savefig(plot_img, format='jpg', dpi=500)
    # 表示
    plt.show()
    