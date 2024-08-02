"""
加速度センサを用いた写真の撮影
"""

# インポート
import numpy as np
import cv2
from dynamixel_sdk import *
from utils.DynamixelMX106 import DynamixelMX106
from utils.SerialSetting import SerialSetting
import os
import time
import keyboard

# カメラの設定
rgb_cap = cv2.VideoCapture(0)
thermal_cap = cv2.VideoCapture(1)

# 各カメラの撮影時の解像度の設定
rgb_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
rgb_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 512)
thermal_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
thermal_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 512)

# 出力フォルダ
OUTPUT_THERMAL = './Calibration/ExternalParameter_Chessboard/THERMAL/'
OUTPUT_RGB = './Calibration/ExternalParameter_Chessboard/RGB/'
# フレームカウント
rgbcount = 23
thermalcount = 23

# Dynamixel MX106の設定
motor = DynamixelMX106(port_name='COM3', baud_rate=57600, motor_id=1)
motor.enable_torque()
motor.rotate_to_180()
print(motor.get_present_position())
motor.setting_speed(100)
INIT_POS = 1024
ROTATION_POS = 3072

# 加速度センサの設定
serial = SerialSetting(port_name='COM5', baud_rate=57600)

# 赤外線カメラが上にあるとき
flag_init = True

# タイマーが起動したかどうか
flag_timer = False

while True:

    _, rgb_frame = rgb_cap.read()
    _, thermal_frame = thermal_cap.read()

    cv2.imshow('RGB', rgb_frame)
    cv2.imshow('Thermal', thermal_frame)
        
    key = cv2.waitKey(1)
    is_moving = motor.is_moving()
    present_pos = motor.get_present_position()
    print("is_moving", is_moving)
    #print("present_pos", present_pos)

    #if is_moving:
    # モータが動いていないとき
    accelerometer_data = serial.read_accelerometer()
    x, y, z = accelerometer_data
    print('x:', x)

    if not is_moving:
        # モータが動作していないとき
        if INIT_POS - 2 <= present_pos and present_pos <= INIT_POS + 2:
            # モータが初期位置に到達したとき
            if 0.00 <= x and x <= 0.02:
                # x方向の加速度が0から0.02[g]以下のとき
                if not flag_timer:
                    # タイマーが起動していないとき
                    # タイマーを起動させる
                    start = time.time()
                    flag_timer = True
                current = time.time() - start
                if current >= 1.5:
                    # 1.5秒経過したとき
                    rgb_filename = os.path.join(OUTPUT_RGB,''f'rgb_{rgbcount}.jpg')
                    cv2.imwrite(rgb_filename, rgb_frame)
                    rgbcount += 1
                    motor.rotate_to_180()
                    flag_init = False
                    flag_timer = False

        elif ROTATION_POS - 2 <= present_pos and present_pos <= ROTATION_POS + 2:
            # モータが180°回転したとき
            if -0.07 <= x and x <= 0.00:
                # x方向の加速度が-0.07から0[g]以下のとき
                if not flag_timer:
                    # タイマーが起動していないとき
                    # タイマーを起動させる
                    start = time.time()
                    flag_timer = True
                current = time.time() - start
                if current >= 1.5:
                    thermal_filename = os.path.join(OUTPUT_THERMAL,''f'thermal_{thermalcount}.jpg')
                    cv2.imwrite(thermal_filename, thermal_frame)
                    thermalcount += 1
                    motor.init_position()
                    flag_init = True
                    flag_timer = False

    if keyboard.is_pressed('escape'):
        print('Escが押されました')
        break
    # if not is_moving:
    #     print('present_pos', present_pos)
    #      # モータが動作していないとき
    #     if (-0.06<= x and x <= 0) or (0 <= x and x <= 0.01):
    #         # 加速度センサのxが0から0.01の間のとき
    #         #if INIT_POS - 1 <= present_pos and present_pos <= INIT_POS + 1:
    #         if ROTATION_POS == present_pos:
    #             print("ROTATION")
    #             thermal_filename = os.path.join(OUTPUT_THERMAL,''f'thermal_{thermalcount}.jpg')
    #             cv2.imwrite(thermal_filename, thermal_frame)
    #             thermalcount += 1
    #             motor.init_position()
    
    #         elif INIT_POS == present_pos:
    #             # 初期位置に達したとき
    #         #elif ROTATION_POS - 2 <= present_pos and present_pos <= ROTATION_POS + 2:
    #             print("INIT")
    #             rgb_filename = os.path.join(OUTPUT_RGB,''f'rgb_{rgbcount}.jpg')
    #             cv2.imwrite(rgb_filename, rgb_frame)
    #             rgbcount += 1
    #             motor.rotate_to_180()
    
    # if key == ord('r'):
    #     motor.rotate_to_180()
    # elif key == ord('i'):
    #     motor.init_position()
    # elif key == ord('a'):
    #     accelerometer_data = serial.read_accelerometer()
    #     if accelerometer_data:
    #         x, y, z = accelerometer_data
    #         print(f"加速度: x={x} [g], y={y} [g], z={z} [g]")
    # elif key == ord('q'):
    #     break

    # if keyboard.is_pressed('up'):
    #     motor.rotate_to_180()
    # if keyboard.is_pressed('down'):
    #     motor.init_position()
    # if keyboard.is_pressed('enter'):
    #     accelerometer_data = serial.read_accelerometer()
    #     if accelerometer_data:
    #         x, y, z = accelerometer_data
    #         print(f"加速度: x={x} [g], y={y} [g], z={z} [g]")
    # if keyboard.is_pressed('esc'):
    #     break
    # motor.init_position()
    # motor.rotate_to_180()
    


motor.disable_torque()
cv2.destroyAllWindows()  