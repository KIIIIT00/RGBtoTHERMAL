"""
rgbカメラの動画とサーマルカメラの動画を取得する
そのときの画像も取得する
"""
"""
カメラのゆがみ補正を行った
キーボード s入力で、録画スタート
キーボード f入力で,録画ストップ
キーボード c入力で、画像を取得
キーボード i入力で,1秒ごとの画像の取得をスタートする
キーボード q入力で,1秒ごとの画像の取得をストップする
Escでプログラム終了

FLIRのロゴを消すために, 640x425にする

関節モードでモータを動かす

<やるべきこと>
・モータを動かした後の視野の位置合わせ
・キーボード入力cを毎回しなくても，回転させたら，キャプションするものを作る

"""

import numpy as np
import cv2
import os
from natsort import natsorted
import re
import pyautogui
import time

"""
モーターの設定
"""

#####################################################
from dxl_module import DXL

from dynamixel_sdk import *  # Uses Dynamixel SDK library

# Protocol version
PROTOCOL_VERSION        = 1  # See which protocol version is used in the Dynamixel

# Default setting
DXL_ID                  = 10    # Dynamixel ID
BAUDRATE                = 1000000
DEVICENAME              = "COM3"  # Check which port is being used on your controller

TORQUE_ENABLE           = 1    # Value for enabling the torque
TORQUE_DISABLE          = 0    # Value for disabling the torque
DXL_MINIMUM_POSITION_VALUE  = 100  # Dynamixel will rotate between this value
DXL_MAXIMUM_POSITION_VALUE  = 4000  # and this value
DXL_MOVING_STATUS_THRESHOLD = 10  # Dynamixel moving status threshold

portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

# 150度基準から-90度の場所にあるとき，0
rotate_flag = 0
#####################################################

"""
関数定義
"""
#####################################################

# 画像の大きさを合わせる
def match_size(img_rgb, img_thermal):
    h_rgb, w_rgb, _ = img_rgb.shape
    h_thermal, w_thermal, _ = img_thermal.shape
    h_max = max([h_rgb, h_thermal])
    w_max = max([w_rgb, w_thermal])
    img_rgb = cv2.resize(img_rgb, dsize=(w_max, h_max))
    img_thermal = cv2.resize(img_thermal, dsize=(w_max, h_max))
    return img_rgb, img_thermal

# 画像の大きさを256x256にする
def match_256x256(img_rgb, img_thermal):
    img_rgb = cv2.resize(img_rgb, dsize=(256, 256))
    img_thermal = cv2.resize(img_thermal, dsize=(256, 256))
    return img_rgb, img_thermal

# 画像の大きさを512x512にする
def match_512x512(img_rgb, img_thermal):
    img_rgb = cv2.resize(img_rgb, dsize=(512, 512))
    img_thermal = cv2.resize(img_thermal, dsize=(512, 512))
    return img_rgb, img_thermal

# IMG_SIZEの大きさに合わせる
def match_custom(img_rgb, img_thermal):
    img_rgb = cv2.resizeee(img_rgb, dsize=IMG_SIZE)
    img_thermal = cv2.resize(img_thermal, dsize=IMG_SIZE)
    return img_rgb, img_thermal

# 上下反転させる
def UpsideDown(img):
    return cv2.flip(cv2.flip(img, 0), 1)

# フォルダ内のファイルが存在するか
def fileExist(folder):
    return len(folder) != 0

# フォルダ内のfile名になりうる次の番号を返す
def fileNameNext(folder):
    if fileExist(folder):
        print('No')
        count = 1
    else:
        # ディレクトリのファイルを取る
        files = natsorted(folder)
        lastfile = files[len(files) -1]
        # 拡張子なしのファイル名の取得
        lastfile_name = os.path.splitext(os.path.basename(lastfile))[0]
        num = int(re.sub(r'[^0-9]', '', lastfile_name))
        print(num)
        count = num+ 1

# waitKeyによって，操作を変える
def waitKeyOperation(key):
    # 録画をスタート
    if key == ord('s') and not is_recording:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out_rgb = cv2.VideoWriter(rgb_videos + f'{video_count}.mp4', fourcc, fps_rgb,VIDEO_SIZE, isColor=True)
        out_thermal = cv2.VideoWriter(thermal_videos +f'{video_count}.mp4', fourcc, fps_rgb, VIDEO_SIZE)
        # 録画を開始
        is_recording = True
        print("Recording started...")

     # 動画のストップ
    if key == ord('f') and is_recording:
        is_recording = False
        out_rgb.release()
        out_thermal.release()
        print("Recording stopped...")
    
    # 写真を保存
    if key == ord('c'):
        for i in range(2):
            if not is_rotation:
                is_rotation = dx.movejoint()
                # 0.5秒待機
                time.sleep(0.5)
                cv2.imwrite(rgb_imgs+f'pic{img_count}.jpg',dst)
                cv2.imwrite(thermal_imgs + f'pic{img_count + 1}.jpg', frame_thermal)
                time.sleep(0.5)
            else:
                is_rotation = dx.movejoint()
                # 0.5秒待機
                time.sleep(0.5)
                cv2.imwrite(rgb_imgs+f'pic{img_count}.jpg',dst)
                cv2.imwrite(thermal_imgs + f'pic{img_count + 1}.jpg', frame_thermal)
                time.sleep(0.5)
        count += 1
    
    # Escで終了
    if key == 27:
        if is_recording:
            out_rgb.release()
            out_thermal.release()
    
    if is_recording:
        # 録画中のフレームを書き込む
        out_rgb.write(dst)
        out_thermal.write(frame_thermal)

# imgの歪み補正とトリミングを行う
def undistortANDcrop(img):
    img2 = img.copy()
    h, w = img2.shape[:2]
    newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))     # 周りの画像の欠損を考慮した内部パラメータと，トリミング範囲を作成

    dst = cv2.undistort(img2, mtx, dist, None, newcameramtx)        # ここで歪み補正を行っている
    ##cv2.imshow('before undistort', dst)

    # crop the image
    x,y,w,h = roi
    dst = dst[y:y+h, x:x+w]     # 画像の端が黒くなっているのでトリミング
    dst, frame_thermal = match_size(dst, frame_thermal)
    return dst
    
#########################################################################
# 画角合わせ
#def resize_rgb(img_rgb):
    

tate = 7    # 縦の交点の個数
yoko = 10   # 横の交点の個数

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((tate*yoko,3), np.float32)
objp[:,:2] = np.mgrid[0:yoko,0:tate].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

#カメラの設定
cap_rgb = cv2.VideoCapture(1,cv2.CAP_DSHOW)
cap_thermal = cv2.VideoCapture(0,cv2.CAP_MSMF)
print(cap_rgb.isOpened())
print(cap_thermal.isOpened())

cap_rgb.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # 幅の設定
cap_rgb.set(cv2.CAP_PROP_FRAME_HEIGHT, 512)  # 高さの設定
cap_thermal.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # 幅の設定
cap_thermal.set(cv2.CAP_PROP_FRAME_HEIGHT, 512)  # 高さの設定

fps_rgb = int(cap_rgb.get(cv2.CAP_PROP_FPS))
w_rgb = int(cap_rgb.get(cv2.CAP_PROP_FRAME_WIDTH))
h_rgb = int(cap_rgb.get(cv2.CAP_PROP_FRAME_HEIGHT))

fps_thermal = int(cap_thermal.get(cv2.CAP_PROP_FPS))
w_thermal = int(cap_thermal.get(cv2.CAP_PROP_FRAME_WIDTH))
h_thermal = int(cap_thermal.get(cv2.CAP_PROP_FRAME_HEIGHT))

print("RGB_FPS {}:".format(fps_rgb))
print("THEMAL_FPS {}:".format(fps_thermal))
# 録画状況を管理するフラグ
is_recording = False

# 1秒ごとに写真を保存するフラグ
is_captureFrame = False

# -90度の位置にいるときはFalse
is_rotation = False

####################　ユーザーが変更するところ ####################

# 内部パラメータと歪み係数
#mtx = np.array(["""***************ここにあらかじめ求めておいた内部パラメータを書く***************"""]).reshape(3,3)
mtx = np.array([622.56592404, 0, 318.24063181, 0, 623.20968839, 245.37576884, 0, 0, 1]).reshape(3,3)
#dist = np.array(["""***************ここにあらかじめ求めておいた歪み係数を書く***************"""])
dist = np.array([ 0.14621503, -0.26374155, -0.00065967,  -0.00055428, 0.25360545])

# 保存するフォルダを明記
rgb_imgs = os.listdir('./Data/rgb_img/Scene2/')
thermal_imgs = os.listdir('./Data/thermal_img/Scene2/')
rgb_videos = os.listdir('./Data/rgb_video/')
thermal_videos = os.listdir('./Data/thmermal_video/')
IMG_SIZE = (256, 256)
VIDEO_SIZE = (256, 256)

################################################################

video_count = 0
# print(len(files))
#print(os.path.isfile('./Data/rgb_img/'))

# 画像ファイルの次の名前と成りうる番号
img_count = fileNameNext(rgb_imgs)
print(img_count)   

# 動画ファイルの次の名まえとなりうる番号
video_count = fileNameNext(rgb_videos)

idx = 0
#dx = DXL
#繰り返しのためのwhile文
dx = DXL()

while True:
    
    key =cv2.waitKey(1)

    #カメラからの画像取得
    ret1, frame_rgb = cap_rgb.read()
    ret2, frame_thermal = cap_thermal.read()

    # 上下反転
    frame_thermal = cv2.flip(cv2.flip(frame_thermal, 0), 1)

    # ロゴを削除するために、画像を抽出
    #frame_thermal = frame_thermal[0:425, 0:640]
    
    # frame_imgの歪み補正とトリミングを行う
    dst = undistortANDcrop(frame_rgb)

    # サーマルと画像の位置合わせ
    # dst = dst[51:446,31:585]
    dst = dst[80:453, 15 :580]

    # FLIRのロゴを消す
    #frame_thermal = frame_thermal[0:425, 0:640]
    

    #dst, frame_thermal = match_size(dst, frame_thermal)

    # FLIRのロゴを消す
    #dst = dst[0:425, 0:640]
    #frame_thermal = frame_thermal[0:425, 0:640]

    # 画像の大きさを256x256にする
    dst, frame_thermal = match_custom(dst, frame_thermal)

    # keyの値によって，操作を変更
    waitKeyOperation(key)
    
    cv2.imshow("undistort", dst)
    cv2.imshow("thermal", frame_thermal)

    #繰り返し分から抜けるためのif文
    if key == 27:   #Escで終了
        break

cap_rgb.release()
cap_thermal.release()
#out.release()
cv2.destroyAllWindows()
# Close port
portHandler.closePort()

"""
参考:
    https://qiita.com/hirobf10/items/ed81618d62a292a1ec6e
"""
