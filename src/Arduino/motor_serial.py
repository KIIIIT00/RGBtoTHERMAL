"""
モータが回転しているときの加速度センサの値を取得する
"""
from utils.DynamixelEX106 import DynamixelEX106
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
motor = DynamixelEX106(port_name='COM3', baudrate=57600, dxl_id=1)
motor.enable_torque()
motor.set_speed(100)
motor.cw_rotate_90()
# time.sleep(3)
INIT_POS = 579
ROTATION_POS = 3517

# モータの現在位置がINIT_POSにあるかどうか
flag_init = True

# タイマーが起動したかどうか
flag_timer = False

# 前の時刻と現在の加速度が一致したカウント
match_count = 0

# 前の時刻の加速度
pre_acceleration = 0

# 加速度センサの設定
serial = SerialSetting(port_name='COM5', baud_rate=57600)

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
    present_pos = motor.read_position()
    print("present_pos:", present_pos)
    accelerometer_data = serial.read_accelerometer()
    x, y, z = accelerometer_data
    y = y * 9.8
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
        if INIT_POS - 3 <= present_pos and present_pos <= INIT_POS + 4:
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
                motor.ccw_rotate_90()
                flag_init = False
                flag_timer = False
        elif ROTATION_POS - 3 <= present_pos and present_pos <= ROTATION_POS + 3:
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
                motor.cw_rotate_90()
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

np.savez(".results/Ardiuino/motor_accelerations_fig/motor_acceleration.npz", time_stamps, motor_angles, motor_accelerations_x, motor_accelerations_y, motor_accelerations_z)

print("time_stamps size:", time_stamps.size)
print("motor_angles size:", motor_angles.size)
# グラフの作成
fig, ax1 = plt.subplots()

# 角度のプロット
ax1.set_xlabel('時間[s]', fontsize = 14)
ax1.set_ylabel('現在の位置', fontsize = 14)
ax1.plot(time_stamps, motor_angles, color='tab:blue', label='Dynamixel EX-106+の現在の位置')
ax1.tick_params(axis = 'y')

# 加速度のプロット
ax2 = ax1.twinx()
ax2.set_ylabel('加速度[m/s²] ')
#ax2.plot(time_stamps, motor_accelerations_x, color='tab:red', label='加速度センサのX軸')
ax2.plot(time_stamps, motor_accelerations_y, color='tab:green', label='加速度')
#ax2.plot(time_stamps, motor_accelerations_z, color='tab:orange', label='加速度センサのZ軸')
ax2.tick_params(axis='y')

# グラフのタイトル
plt.title('Dynamixel EX-106+の関節モードにおける現在の位置と加速度', fontsize = 16)

# レジェンドの追加
fig.tight_layout()
ax1.legend(loc='upper left', fontsize = 12)
ax2.legend(loc='upper right', fontsize = 12)

# グラフの表示
plt.show()