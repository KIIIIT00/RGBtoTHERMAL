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


"""

import numpy as np
import cv2
import os
from natsort import natsorted
import re
import pyautogui

"""
関数定義
"""
#############################################################################################

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

def match_512x512(img_rgb, img_thermal):
    img_rgb = cv2.resize(img_rgb, dsize=(512, 512))
    img_thermal = cv2.resize(img_thermal, dsize=(512, 512))
    return img_rgb, img_thermal

#############################################################################################
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
cap_rgb = cv2.VideoCapture(1)
cap_thermal = cv2.VideoCapture(0)

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

# 内部パラメータと歪み係数
#mtx = np.array(["""***************ここにあらかじめ求めておいた内部パラメータを書く***************"""]).reshape(3,3)
mtx = np.array([652.16543875, 0, 334.56278851, 0, 652.73887052, 211.97831963, 0, 0, 1]).reshape(3,3)
#dist = np.array(["""***************ここにあらかじめ求めておいた歪み係数を書く***************"""])
dist = np.array([-4.53267525e-01, 5.46379835e-01, 8.86693500e-04, -1.84251987e-03, -1.06001180e+00])

files = os.listdir('./Data/rgb_img')
files_video = os.listdir('./Data/rgb_video')
video_count = 0
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
    print(num)
    count = num+ 1
print(count)   

# 動画ファイルが存在しない場合
if len(files_video) == 0:
    video_count = 0
else:
    files_video = natsorted(files_video)
    lastvideofile = files[len(files_video) -1]
    # 拡張なしのファイル名を取得
    lastvideofile_name = os.path.splitext(os.path.basename(lastvideofile))[0]
    video_num = int(re.sub(r'[^0-9]', '',lastvideofile))
    print("video_num:" + video_num)
    video_count = video_count + 1
print("video_count:" + str(video_count))

idx = 0
#繰り返しのためのwhile文
while True:
    

    key =cv2.waitKey(1)

    #カメラからの画像取得
    ret1, frame_rgb = cap_rgb.read()
    ret2, frame_thermal = cap_thermal.read()

    # 上下反転
    frame_thermal = cv2.flip(cv2.flip(frame_thermal, 0), 1)

    # ロゴを削除するために、画像を抽出
    #frame_thermal = frame_thermal[0:425, 0:640]

    # 動画のスタート
    if key == ord('s') and not is_recording:
        #fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out_rgb = cv2.VideoWriter('./Data/rgb_video/'f'{video_count}.mp4', fourcc, fps_rgb, (w_rgb, h_rgb), isColor=True)
        out_thermal = cv2.VideoWriter('./Data/thermal_video/'f'{video_count}.mp4', fourcc, fps_rgb, (w_thermal, h_thermal))
        # 録画を開始
        is_recording = True
        print("Recording started...")

     # 動画のストップ
    if key == ord('f') and is_recording:
        is_recording = False
        out_rgb.release()
        out_thermal.release()
        print("Recording stopped...")

    img2 = frame_rgb.copy()
    h, w = img2.shape[:2]
    newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))     # 周りの画像の欠損を考慮した内部パラメータと，トリミング範囲を作成

    dst = cv2.undistort(img2, mtx, dist, None, newcameramtx)        # ここで歪み補正を行っている
    ##cv2.imshow('before undistort', dst)

    # crop the image
    x,y,w,h = roi
    dst = dst[y:y+h, x:x+w]     # 画像の端が黒くなっているのでトリミング
    dst, frame_thermal = match_size(dst, frame_thermal)

    # サーマルと画像の位置合わせ
    dst = dst[51:446,31:585]
    

    dst, frame_thermal = match_size(dst, frame_thermal)

    # FLIRのロゴを消す
    dst = dst[0:425, 0:640]
    frame_thermal = frame_thermal[0:425, 0:640]

    # 画像の大きさを256x256にする
    dst, frame_thermal = match_512x512(dst, frame_thermal)

    # 1秒ごとの写真を保存するフラグをtrueに
    if key ==  ord('i') and not is_captureFrame:
        is_captureFrame = True

    # 1秒ごとの写真を保存するフラグをFalseにすることで，その処理をやめる
    if key == ord('q') and is_captureFrame:
        is_captureFrame = False
    
    # 1秒ごとの写真を保存する
    """
    if is_captureFrame:
        # 0秒のフレームを保存
        if cap_rgb.get(cv2.CAP_PROP_POS_FRAMES) == 1 and cap_thermal.get(cv2.CAP_PROP_POS_FRAMES) ==1:
            cv2.imwrite('./Data/rgb_img/'f'pic{count}.png',dst)
            cv2.imwrite('./Data/thermal_img/'f'pic{count}.png', frame_thermal)
            count += 1

        elif idx < cap_rgb.get(cv2.CAP_PROP_FPS):
            continue
        else: # 1秒ずつフレームを保存
            cv2.imwrite('./Data/rgb_img/'f'pic{count}.png',dst)
            cv2.imwrite('./Data/thermal_img/'f'pic{count}.png', frame_thermal)
            count += 1
            idx = 0
        """
            

    # 写真の保存をする
    if key == ord('c'):
        cv2.imwrite('./Data/rgb_img/'f'pic{count}.png',dst)
        cv2.imwrite('./Data/thermal_img/'f'pic{count}.png', frame_thermal)
        count += 1
    cv2.imshow("undistort", dst)
    cv2.imshow("thermal", frame_thermal)

    
    if is_recording:
        # 録画中のフレームを書き込む
        out_rgb.write(dst)
        out_thermal.write(frame_thermal)
    """
    if ret1:
        #カメラの画像の出力
        cv2.imshow('camera' , frame)

        img = frame.copy()
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        # Find the chess board corners　交点を見つける
        ret2, corners = cv2.findChessboardCorners(gray, (yoko,tate),None)
        # If found, add object points, image points (after refining them)　交点が見つかったなら描画
        if ret2:
            rvecs = []
            tvecs = []
            objpoints.append(objp)      # object point

            corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
            imgpoints.append(corners2)

            # パラメータの表示
            # Draw and display the corners
            img = cv2.drawChessboardCorners(img, (yoko,tate), corners2,ret2)     # 交点を見つけて印を付ける
            cv2.imshow('drawChessboardCorners',img)     # 印の付いた画像を出力

            ret3, rvecs, tvecs, _ = cv2.solvePnPRansac(objp, corners2, mtx, dist)      # ここで外部パラメータを求めている


            ###
            ###mtx：camera matrix，内部パラメータ
            ###dist：distortion coefficients，歪み係数
            ###rvecs：rotation vectors，外部パラメータの回転行列
            ###tvecs：translation vectors，外部パラメータの並進ベクトル
            ###

            if ret3:
                # 歪み補正の準備
                img2 = frame.copy()
                cv2.imshow('frame', img2)
                h, w = img2.shapqe[:2]
                newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))     # 周りの画像の欠損を考慮した内部パラメータと，トリミング範囲を作成

                dst = cv2.undistort(img2, mtx, dist, None, newcameramtx)        # ここで歪み補正を行っている

                # crop the image
                x,y,w,h = roi
                dst = dst[y:y+h, x:x+w]     # 画像の端が黒くなっているのでトリミング
                if is_recording:
                    # 録画中のフレームを書き込む
                    out.write(dst)
                #カメラの画像の出力
                #cv2.imshow('undistort' , dst)   # 歪み補正された画像を出力
    """
    #繰り返し分から抜けるためのif文
    if key == 27:   #Escで終了
        break
if is_recording:
    out_rgb.release()
    out_thermal.release()
cap_rgb.release()
cap_thermal.release()
#out.release()
cv2.destroyAllWindows()

"""
参考:
    https://qiita.com/hirobf10/items/ed81618d62a292a1ec6e
"""
