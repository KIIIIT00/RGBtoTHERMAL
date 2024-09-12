"""
RGB画像と赤外線画像の画像領域を合わせる
"""

# インポート
import numpy as np
import cv2
from dynamixel_sdk import *
from utils.DynamixelEX106 import DynamixelEX106
from utils.SerialSetting import SerialSetting
import os
import time
import keyboard

def undistort(img, mtx, dist):
        h, w = img.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
        dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
        x, y, w, h = roi
        dst = dst[y:y+h, x:x+w]
        return dst

def feature_ditection(rgb_img, thermal_img):
    """
    特徴点を検出する
    """
    thermal_img = cv2.cvtColor(thermal_img, cv2.COLOR_BGR2GRAY)
    # RGB画像をグレースケールに変換
    gray_rgb_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2GRAY)
    
    # ヒストグラム平坦化する
    equalized_rgb_image = cv2.equalizeHist(gray_rgb_img)
    equalized_ir_image = cv2.equalizeHist(thermal_img)
    
    # 特徴点の検出
    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(equalized_rgb_image, None)
    kp2, des2 = sift.detectAndCompute(equalized_ir_image, None)
    
    # 特徴点マッチング
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)
    
    # アウトライエルの除去
    src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    
    # ホモグラフィー行列の適用と画像のアライメント
    height, width = thermal_img.shape[:2]
    aligned_rgb_image = cv2.warpPerspective(rgb_img, H, (width, height))
    
    cv2.imshow('Aligned RGB Image', aligned_rgb_image)
    return aligned_rgb_image

def crop(rgb_img, thermal_img):
    """
    画像領域を合わせる
    """
    # 視野角の割合
    ratio_crop_h = 0.577
    ratio_crop_w = 0.846
    
    thermal_H, thermal_W = thermal_img.shape[:2]
    rgb_H, rgb_W = rgb_img.shape[:2]
    half_rgb_H = (int)(rgb_H /2)
    half_rgb_W = (int)(rgb_W /2)
    crop_rgb_H = rgb_H * ratio_crop_h
    crop_rgb_W = rgb_W * ratio_crop_w
    half_crop_rgb_H = (int)(crop_rgb_H/2)
    half_crop_rgb_W = (int)(crop_rgb_W/2)
    rgb_img = rgb_img[half_rgb_H - half_crop_rgb_H:half_rgb_H+ half_crop_rgb_H, half_rgb_W - half_crop_rgb_W: half_rgb_W + half_crop_rgb_W]
    return rgb_img
    
# 赤外線カメラの内部パラメータ
thermal_mtx = np.array([773.41392054, 0, 329.198468,
                        0, 776.32513558, 208.53439152,
                        0 ,0 ,1]).reshape(3, 3)
thermal_dist = np.array([1.67262996e-01, -2.94477097e+00, -2.30689758e-02, -1.33138573e-03, 1.02082943e+01])

# RGBカメラの内部パラメータ
rgb_mtx = np.array([621.80090236, 0, 309.61717191, 
                    0, 624.22815912, 234.27475688, 
                    0, 0, 1]).reshape(3,3)
rgb_dist = np.array([ 0.1311874, -0.21356334, -0.00798234,  -0.00648277, 0.10214072])

# カメラの設定
rgb_cap = cv2.VideoCapture(1)
thermal_cap = cv2.VideoCapture(0)

# 各カメラの撮影時の解像度の設定
rgb_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
rgb_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
thermal_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
thermal_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

#視野合わせる用のディレクトリ
OUTPUT_THERMAL = './Calibration/FOV/THERMAL/'
OUTPUT_RGB = './Calibration/FOV/RGB/'

# フレームカウント
rgbcount = thermalcount = 18

# Dynamixel EX-106+の設定
motor = DynamixelEX106(port_name='COM3', baudrate=57600, dxl_id=1)
motor.cw_rotate_90()
print(motor.read_position())
motor.set_speed(100)
INIT_POS =579
ROTATION_POS = 3515

# 加速度センサの設定
serial = SerialSetting(port_name='COM5', baud_rate=57600)

# 赤外線カメラが上にあるとき
flag_init = True

# タイマーが起動したかどうか
flag_timer = False

while True:

    _, rgb_frame = rgb_cap.read()
    _, thermal_frame = thermal_cap.read()
    
    rgb_frame = undistort(rgb_frame, rgb_mtx, rgb_dist)
    thermal_frame = undistort(thermal_frame, thermal_mtx, thermal_dist)
    
    # 画像領域を抽出
    #rgb_frame = crop(rgb_frame,thermal_frame)

    cv2.imshow('RGB', rgb_frame)
    cv2.imshow('Thermal', thermal_frame)
        
    key = cv2.waitKey(1)
    is_moving = motor.is_moving()
    present_pos = motor.read_position()
    print("is_moving", is_moving)
    #print("present_pos", present_pos)

    #if is_moving:
    # モータが動いていないとき
    accelerometer_data = serial.read_accelerometer()
    x, y, z = accelerometer_data
    print('y:', y)
    print('POS:', present_pos)

    if not is_moving:
        # モータが動作していないとき
        if INIT_POS - 4 <= present_pos and present_pos <= INIT_POS + 4:
            # モータが初期位置に到達したとき
            if -0.03 <= y and y <= 0.97:
                # x方向の加速度が0から0.02[g]以下のとき
                if not flag_timer:
                    # タイマーが起動していないとき
                    # タイマーを起動させる
                    start = time.time()
                    flag_timer = True
                current = time.time() - start
                if current >= 1.5:
                    # 1.5秒経過したとき
                    thermal_filename = os.path.join(OUTPUT_THERMAL,''f'thermal_{thermalcount}.jpg')
                    cv2.imwrite(thermal_filename, thermal_frame)
                    thermalcount += 1
                    # rgb_filename = os.path.join(OUTPUT_RGB,''f'rgb_{rgbcount}.jpg')
                    # cv2.imwrite(rgb_filename, rgb_frame)
                    # rgbcount += 1
                    motor.ccw_rotate_90()
                    flag_init = False
                    flag_timer = False

        elif ROTATION_POS - 4 <= present_pos and present_pos <= ROTATION_POS + 4:
            # モータが180°回転したとき
            if -0.94 <= y and y <= 0.05:
                # x方向の加速度が-0.07から0[g]以下のとき
                if not flag_timer:
                    # タイマーが起動していないとき
                    # タイマーを起動させる
                    start = time.time()
                    flag_timer = True
                current = time.time() - start
                if current >= 1.5:
                    rgb_filename = os.path.join(OUTPUT_RGB,''f'rgb_{rgbcount}.jpg')
                    cv2.imwrite(rgb_filename, rgb_frame)
                    rgbcount += 1
                    # thermal_filename = os.path.join(OUTPUT_THERMAL,''f'thermal_{thermalcount}.jpg')
                    # cv2.imwrite(thermal_filename, thermal_frame)
                    # thermalcount += 1
                    motor.cw_rotate_90()
                    flag_init = True
                    flag_timer = False

    if keyboard.is_pressed('escape'):
        print('Escが押されました')
        break
    
motor.disable_torque()
cv2.destroyAllWindows()  