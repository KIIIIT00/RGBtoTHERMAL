"""
モータが回転しているときの加速度センサの値を取得する
"""
from utils.DynamixelMX106 import DynamixelMX106
from utils.SerialSetting import SerialSetting
from dynamixel_sdk import *
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib
import keyboard

def check_convergence_accelerations(pre_acceleration, acceleration, match_count):
    """
    加速度が収束したかどうかを判断する

    Parameters
    -------------
    pre_acceleration : 前の時刻の加速度
    acceleration : 現在の加速度
    match_count : 前の時刻の加速度と現在の加速度が連続で一致した回数
    """
    if pre_acceleration == acceleration:
        match_count += 1
    else:
        match_count = 0
    
    return match_count

# Dynamixel MX106の設定
motor = DynamixelMX106(port_name='COM3', baud_rate=57600, motor_id=1)
motor.enable_torque()
print(motor.get_present_position())
motor.init_position()
print(motor.get_present_position())
motor.setting_speed(100)
INIT_POS = 1024
ROTATION_POS = 3072

# モータの現在位置がINIT_POSにあるかどうか
flag_init = True

# タイマーが起動したかどうか
flag_timer = False

# 前の時刻と現在の加速度が一致したカウント
match_count = 0

# 前の時刻の加速度
pre_acceleration = 0

# 加速度センサの設定
serial = SerialSetting(port_name='COM6', baud_rate=57600)

# モータの角度とそのときの加速度を格納するリスト
motor_angles = []
motor_accelerations_x = []
motor_accelerations_y = []
motor_accelerations_z = []

# 時刻を格納するリスト
time_stamps = []

start_time = time.time() 
# 10回繰り返す
while True:
    current_time = time.time() - start_time
    time_stamps.append(current_time)
    present_pos = motor.get_present_position()
    accelerometer_data = serial.read_accelerometer()
    x, y, z = accelerometer_data
    print('x:', x)
    print('y:', y)
    print('z:', z)
    is_moving = motor.is_moving()

    motor_angles.append(present_pos)
    motor_accelerations_x.append(x)
    motor_accelerations_y.append(y)
    motor_accelerations_z.append(z)


    # if not is_moving:
    #     if -0.07 == x:
    #         if ROTATION_POS == present_pos:
    #             motor.init_position()
    #     elif 0.02 == x:
    #         if INIT_POS == present_pos:
    #             motor.rotate_to_180()

    if not is_moving:
        if INIT_POS - 2 <= present_pos and present_pos <= INIT_POS + 2:
            # if not flag_timer:
            #     print('------------ start ----------------------')
            #     start = time.time()
            #     flag_timer = True
            # current = time.time() - start
            # if current > 3:
            match_count = check_convergence_accelerations(pre_acceleration, x, match_count)
            if match_count >= 3:
                print('------------ finish ----------------------')
                # 3秒経過したとき
                motor.rotate_to_180()
                flag_init = False
                flag_timer = False
        elif ROTATION_POS - 2 <= present_pos and present_pos <= ROTATION_POS + 2:
            # if not flag_timer:
            #     print('------------ start rotation ----------------------')
            #     start = time.time()
            #     flag_timer = True
            # current = time.time() - start
            # if current > 3:
            match_count = check_convergence_accelerations(pre_acceleration, x, match_count)
            if match_count >= 3:
                print('------------ finish rotation ----------------------')
                # 3秒経過したとき
                motor.init_position()
                flag_init = True
                flag_timer = False

    # 現在の位置を登録
    pre_acceleration = x
    if keyboard.is_pressed('escape'):
        print('Escが押されました')
        break

motor.disable_torque()
motor.close_port()

# リストをnp.arrayに変換
time_stamps = np.array(time_stamps)
motor_angles = np.array(motor_angles)
motor_accelerations_x = np.array(motor_accelerations_x)
motor_accelerations_y = np.array(motor_accelerations_y)
motor_accelerations_z = np.array(motor_accelerations_z)

print("time_stamps size:", time_stamps.size)
print("motor_angles size:", motor_angles.size)
# グラフの作成
fig, ax1 = plt.subplots()

# 角度のプロット
ax1.set_xlabel('時間[s]')
ax1.set_ylabel('現在位置', color='tab:blue')
ax1.plot(time_stamps, motor_angles, color='tab:blue', label='モータの現在位置')
ax1.tick_params(axis = 'y', labelcolor='tab:blue')

# 加速度のプロット
ax2 = ax1.twinx()
ax2.set_ylabel('加速度[g]')
ax2.plot(time_stamps, motor_accelerations_x, color='tab:red', label='加速度 X軸')
ax2.plot(time_stamps, motor_accelerations_y, color='tab:green', label='加速度 Y軸')
ax2.plot(time_stamps, motor_accelerations_z, color='tab:orange', label='加速度 Z軸')
ax2.tick_params(axis='y')

# グラフのタイトル
plt.title('Dynamixelの関節モードにおける角度と3軸加速度')

# レジェンドの追加
fig.tight_layout()
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

# グラフの表示
plt.show()