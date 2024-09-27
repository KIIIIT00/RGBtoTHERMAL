import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib
import keyboard

INPUT_NPZ_FILE = "./results/Arduino/motor_accelerations_fig/motor_acceleration.npz"

# npzファイルを読み込む
npz = np.load(INPUT_NPZ_FILE)

# np配列を割り当て
time_stamps = npz['arr_0']
motor_angles = (npz['arr_1'] - 579) /16.32
motor_accelerations_x = npz['arr_2']
motor_accelerations_y = npz['arr_3']
motor_accelerations_z = npz['arr_4']

print("time_stamps size:", time_stamps.size)
print("motor_angles size:", motor_angles.size)

# グラフの作成
fig, ax1 = plt.subplots()

# 角度のプロット
ax1.set_xlabel('時間[s]', fontsize = 28)
ax1.set_ylabel('角度[°]', fontsize = 28)
ax1.plot(time_stamps, motor_angles, color='tab:red', linestyle = "dashed", label='角度', linewidth = 3)
ax1.tick_params(axis = 'x', labelsize=26, width=2)
ax1.tick_params(axis = 'y', labelsize=26, width=2)

# y軸の範囲を設定 (最小値0、最大値180)
ax1.set_ylim(None, 200)

# 加速度のプロット
ax2 = ax1.twinx()
ax2.set_ylabel('加速度[m/s²] ', fontsize = 28)
#ax2.plot(time_stamps, motor_accelerations_x, color='tab:red', label='加速度センサのX軸')
ax2.plot(time_stamps, motor_accelerations_y, color='tab:blue',label='加速度', linewidth = 3)
#ax2.plot(time_stamps, motor_accelerations_z, color='tab:orange', label='加速度センサのZ軸')
ax2.tick_params(axis='y', labelsize=26, width=3)

# グラフのタイトル
# plt.title('Dynamixel EX-106+の関節モードにおける現在の位置と加速度')

# レジェンドの追加
fig.tight_layout()
ax1.legend(loc='upper left', fontsize = 26)
ax2.legend(loc='upper right', fontsize = 26)

# グラフの表示
plt.show()