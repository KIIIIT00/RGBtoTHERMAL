import numpy as np
import cv2
from dynamixel_sdk import *
from utils.DynamixelMX106 import DynamixelMX106

# カメラの設定

rgb_cap = cv2.VideoCapture(1)
thermal_cap = cv2.VideoCapture(0)

count = 1

# サーマルのカメラが上にあるとき
flag_init = True

rgb_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
rgb_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
thermal_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
thermal_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Dynamixel MX106の設定
motor = DynamixelMX106(port_name='COM8', baud_rate=57600, motor_id=1)
motor.enable_torque()
motor.init_position()

while True:
    _, rgb_frame = rgb_cap.read()
    _, thermal_frame = thermal_cap.read()

    cv2.imshow('RGB', rgb_frame)
    cv2.imshow('Thermal', thermal_frame)

    key = cv2.waitKey(1)
    # 'q'キーを押したら終了
    if key == ord('q'):
        break
    elif key == ord('r'):
        if flag_init:
            motor.rotate_to_180()
            flag_init = False
        else:
            motor.init_position()
            flag_init = True
    elif key == ord('c'):
        if count % 2 == 1:
            thermal_count = count + 1
        else:
            thermal_count = count - 1
        if flag_init:
            rgb_frame = cv2.flip(cv2.flip(rgb_frame, 0), 1)
            thermal_frame = cv2.flip(cv2.flip(thermal_frame, 0), 1)
        cv2.imwrite(f'./ExternalParameter/rgb_{count}.png', rgb_frame)
        cv2.imwrite(f'./ExternalParameter/thermal_{thermal_count}.png', thermal_frame)
        count += 1
    

rgb_cap.release()
thermal_cap.release()
motor.disable_torque()
cv2.destroyAllWindows()

