"""
テスト用データを採集する
"""

# インポート
import numpy as np
import cv2
from dynamixel_sdk import *
from utils.DynamixelMX106 import DynamixelMX106
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

def crop(rgb_img):
    """
    rgb画像をクロップする
    """
    rgb_img = rgb_img[29:420,71:571,:]
    return rgb_img

def resize(rgb_img, thermal_img):
    """
    rgb画像と赤外線画像のサイズをそろえる
    """
    rgb_h, rgb_w = rgb_img.shape[:2]
    thermal_img = cv2.resize(thermal_img,(rgb_w, rgb_h))
    return thermal_img

def logo_cut(rgb_img, thermal_img):
    """
    FLIRのロゴをカットする
    """
    rgb_img = rgb_img[45:, :, :]
    thermal_img = thermal_img[45:,:,:]
    return rgb_img, thermal_img

def resize_aspect_ratio(rgb_img, thermal_img):
    """
    アスペクト比4:3になるように変換する
    """
    rgb_img = rgb_img[1:, 20:480, :]
    thermal_img = thermal_img[1:,20:480,:]
    return rgb_img, thermal_img

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

# 出力フォルダ
# OUTPUT_THERMAL = './Calibration/ExternalParameter_Chessboard/THERMAL/'
# OUTPUT_RGB = './Calibration/ExternalParameter_Chessboard/RGB/'

#視野合わせる用のディレクトリ
# OUTPUT_THERMAL = './Calibration/FOV/THERMAL/'
# OUTPUT_RGB = './Calibration/FOV/RGB/'

# データセット用のディレクトリ
OUTPUT_THERMAL = './DataSet/Scene2/THERMAL/test/'
OUTPUT_RGB = './DataSet/Scene2/RGB/test/'
# フレームカウント
rgb_file_list = os.listdir(OUTPUT_RGB)
thermal_file_list = os.listdir(OUTPUT_THERMAL)
rgbcount = thermalcount = min(len(rgb_file_list), len(thermal_file_list)) + 1
# Dynamixel MX106の設定
motor = DynamixelEX106(port_name='COM3', baudrate=57600, dxl_id=1)
motor.cw_rotate_90()
print(motor.read_position())
motor.set_speed(100)
INIT_POS = 580
ROTATION_POS = 3515

# 加速度センサの設定
serial = SerialSetting(port_name='COM5', baud_rate=57600)

# 赤外線カメラが上にあるとき
flag_init = True

# タイマーが起動したかどうか
flag_timer = False

# RGB画像と赤外線画像を取得したかどうか
thermal_cap_flag = False
rgb_cap_flag = False

while True:

    _, rgb_frame = rgb_cap.read()
    _, thermal_frame = thermal_cap.read()
    
    # rgb_frame = undistort(rgb_frame, rgb_mtx, rgb_dist)
    # thermal_frame = undistort(thermal_frame, thermal_mtx, thermal_dist)
    rgb_frame = crop(rgb_frame)
    thermal_frame = resize(rgb_frame, thermal_frame)
    rgb_frame, thermal_frame = logo_cut(rgb_frame, thermal_frame)
    
    # アスペクト比を考慮する
    rgb_frame, thermal_frame = resize_aspect_ratio(rgb_frame, thermal_frame)
    
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
            if -0.03 <= y and y <= 0.98:
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
                    thermal_cap_flag = True
                    # rgb_filename = os.path.join(OUTPUT_RGB,''f'rgb_{rgbcount}.jpg')
                    # cv2.imwrite(rgb_filename, rgb_frame)
                    # rgbcount += 1
                    motor.ccw_rotate_90()
                    flag_init = False
                    flag_timer = False

        elif ROTATION_POS - 4 <= present_pos and present_pos <= ROTATION_POS + 4:
            # モータが180°回転したとき
            if -0.94 <= y and y <= 0.98:
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
                    rgb_cap_flag = True
                    # thermal_filename = os.path.join(OUTPUT_THERMAL,''f'thermal_{thermalcount}.jpg')
                    # cv2.imwrite(thermal_filename, thermal_frame)
                    # thermalcount += 1
                    motor.cw_rotate_90()
                    flag_init = True
                    flag_timer = False

    # 両方の写真が取れたら，終了
    if thermal_cap_flag and rgb_cap_flag:
        break
motor.disable_torque()
cv2.destroyAllWindows()  