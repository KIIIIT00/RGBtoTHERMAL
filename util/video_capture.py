"""
赤外カメラとRGBカメラの動画から，1秒ごとに画像を抽出する
"""

import cv2
import os
from natsort import natsorted
import re

files = os.listdir('./Data/rgb_img')
files_video = os.listdir('./Data/rgb_video')
count = 0
# print(len(files))
#print(os.path.isfile('./Data/rgb_img/'))
# ファイルが存在しない場合
if len(files) == 0:
    print('No')
    count = 0
else:
    # ディレクトリのファイルを取る
    files = os.listdir('./Data/rgb_img')
    files = natsorted(files)
    lastfile = files[len(files) -1]
    # 拡張子なしのファイル名の取得
    lastfile_name = os.path.splitext(os.path.basename(lastfile))[0]
    num = int(re.sub(r'[^0-9]', '', lastfile_name))
    count = num+ 1
    print(count)

rgb_capture = cv2.VideoCapture('./Data/rgb_video/1.mp4')   
thermal_capture = cv2.VideoCapture('./Data/thermal_video/1.mp4')
rgb_fps =  rgb_capture.get(cv2.CAP_PROP_FPS)
thermal_fps = thermal_capture.get(cv2.CAP_PROP_FPS)
print(rgb_fps)
print(thermal_fps)
anscount = 0
fpscount = 0
while True:
    rgb_ret, rgb_frame = rgb_capture.read()
    thermal_ret, thermal_frame = thermal_capture.read()

    if not rgb_ret and not thermal_ret: # 読み込めなかった場合はループを抜ける
        break
    
    if int(fpscount % rgb_fps) == 0 and int(fpscount % thermal_fps) == 0: #１秒ごとにフレームを保存
        print(anscount)
        cv2.imwrite('.//Data/png/rgb_img/'f'pic{count}.png', rgb_frame)
        cv2.imwrite('./Data/png/thermal_img/'f'pic{count}.png', thermal_frame)
        anscount += 1
        count += 1
        
    fpscount += 1
