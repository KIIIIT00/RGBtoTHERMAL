"""
非同期関数でwebカメラを動作中に,あるPosに到達したとき,
設定されたディレクトリに写真を格納する

サーマルとRGB画像を格納する
この時に，視野の位置，画像サイズ，画像の向きを合わせる
キーボード'q'を押したときに
"""

# インポート
import cv2
import threading
from dynamixel_sdk import *                    # Uses Dynamixel SDK library
from Dxl import Dxl
import numpy as np
import os
from natsort import natsorted
import re

############################ 初期設定 ############################
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

DXL_MINIMUM_POSITION_VALUE = Dxl.deg_2_pos(-90)       
DXL_MAXIMUM_POSITION_VALUE = Dxl.deg_2_pos(90)        
DXL_ID = 12                                   # Dynamixel ID: 1
DEVICENAME = "COM3"                   # Check which port is being used on your controller
                                               # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"
DXL_MOVING_STATUS_THRESHOLD = 20               # Dynamixel moving status threshold

# 内部パラメータと歪み係数
#mtx = np.array(["""***************ここにあらかじめ求めておいた内部パラメータを書く***************"""]).reshape(3,3)
mtx = np.array([622.56592404, 0, 318.24063181, 0, 623.20968839, 245.37576884, 0, 0, 1]).reshape(3,3)
#dist = np.array(["""***************ここにあらかじめ求めておいた歪み係数を書く***************"""])
dist = np.array([ 0.14621503, -0.26374155, -0.00065967,  -0.00055428, 0.25360545])

RGB_FILES_IMGS = './Data/rgb_img/Scene2/'
THERMAL_FILES_IMGS = './Data/thermal_img/Scene2/'
RGB_FILES_VIDEOS = './Data/rgb_video/'
THERMAL_FILES_VIDEOS = './Data/thermal_video/'

rgb_imgs = os.listdir(RGB_FILES_IMGS)
thermal_imgs = os.listdir(THERMAL_FILES_IMGS)
rgb_videos = os.listdir(RGB_FILES_VIDEOS)
thermal_videos = os.listdir(THERMAL_FILES_VIDEOS)
IMG_SIZE = (512, 512)
VIDEO_SIZE = (256, 256)

##############################################################
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

# フレームのカウント
frame_count = 1
# サーマルのカウント
thermal_count = 2

# サーマルカメラが上にあるか
isThermalUpper = True

# キーボード'q'を入力したか
isPushKeyboard = False

# プログラムを終了する
isExit = False
#xl = Dxl(DXL_ID, DEVICENAME)

"""
関数定義
"""
def file_exist(folder):
    """
    フォルダ内にファイルが存在するかどうか

    Parameters
    -------------
    folder : str
        対象フォルダのパス

    Returns
    -------------
    isExist : boolean
        ファイルが存在するとき,True
        ファイルが存在しないとき,False
    """
    isExist = len(folder) != 0
    return isExist

def file_name_exist(folder):
    """
    フォルダ内の連番になっているファイルの次の連番番号を返す

    Parameters
    -------------
    folder : str
        対象のフォルダのパス
    
    Returns
    -------------
    count : int
        次のファイルの番号を返す
    """
    if not file_exist(folder):
        #print('No')
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
    return count

def save_rgb_image(frame):
    """
    rgb_frameの写真を保存する

    Parameters
    -------------
    frame : ndarray
        rgb映像のフレーム
    """
    global frame_count
    global thermal_count
    filename = 'rgb' + f'{frame_count}' + '.jpg'
    if frame_count % 2 == 1:
        thermal_count = frame_count + 1
    else:
        thermal_count = frame_count - 1
    
    print("img, thermal :"+f'{frame_count}'+"," + f'{thermal_count}')
    cv2.imwrite(filename, frame)
    print(f"Image saved as {filename}")
    

def save_thermal_image(frame):
    """
    thermal_frameの写真を保存する

    Parameters
    --------------
    frame : ndarray
        thermal映像のフレーム
    """
    global frame_count
    global thermal_count
    global isThermalUpper


    filename = 'thermal' + f'{thermal_count}' + '.jpg'
    cv2.imwrite(filename, frame)
    print(f"Image saved as {filename}")

def save_rgb_and_thermal_image(img_rgb, img_thermal):
    """
    rgb画像とサーマル画像を保存する

    Parameters
    --------------
    img_rgb : ndarray
        img映像のフレーム
    img_thermal : ndarray
        thermal映像のフレーム
    """
    global frame_count
    global isThermalUpper
    save_rgb_image(img_rgb)
    save_thermal_image(img_thermal)
    frame_count += 1

def match_camera_size(img_rgb, img_thermal):
    """
    rgb画像とサーマル画像の大きさを(640, 512)にする

    Parameters
    --------------
    img_rgb : ndarry
        rgb画像の配列
    img_thermal : ndarray
        thermal画像の配列
    
    Returns
    --------------
    img_rgb : ndarray
        画像の大きさをそろえたimg_rgb
    img_themral : ndarray
        画像の大きさをそろえたimg_thermal
    """

    img_rgb = cv2.resize(img_rgb, dsize=(640, 512))
    img_thermal = cv2.resize(img_thermal, dsize=(640, 512))
    return img_rgb, img_thermal

def match_size(img_rgb, img_thermal):
    """
    rgb画像とサーマル画像の大きさを合わせる

    Parameters
    --------------
    img_rgb : ndarry
        rgb画像の配列
    img_thermal : ndarray
        thermal画像の配列
    
    Returns
    --------------
    img_rgb : ndarray
        画像の大きさをそろえたimg_rgb
    img_themral : ndarray
        画像の大きさをそろえたimg_thermal
    """
    h_rgb, w_rgb, _ = img_rgb.shape
    h_thermal, w_thermal, _ = img_thermal.shape
    h_max = max([h_rgb, h_thermal])
    w_max = max([w_rgb, w_thermal])
    img_rgb = cv2.resize(img_rgb, dsize=(w_max, h_max))
    img_thermal = cv2.resize(img_thermal, dsize=(w_max, h_max))
    return img_rgb, img_thermal

def match_custom(img_rgb, img_thermal):
    """
    rgb画像とサーマル画像の大きさをIMG_SIZEに合わせる

    Parameters
    --------------
    img_rgb : ndarray
        rgb画像の配列
    img_thermal : ndarray
        サーマル画像の配列

    Returns
    --------------
    img_rgb : ndarray
        画像のサイズがIMG_SIZEになったrgb画像の配列
    img_thermal : ndarray
        画像のサイズがIMG_SIZEになったサーマル画像の配列
    """
    img_rgb = cv2.resize(img_rgb, dsize=IMG_SIZE)
    img_thermal = cv2.resize(img_thermal, dsize=IMG_SIZE)
    return img_rgb, img_thermal

def fov_match(img_rgb, img_thermal, isThermalUpper):
    """
    rgb画像とサーマル画像の視野を合わせる
    赤外線カメラが上にあるときかどうかで変える

    Parameters
    --------------
    img_rgb : ndarray
        rgb画像の配列
    img_thermal : ndarray
        サーマル画像の配列
    isThermalUpper : boolean
        赤外線カメラが上にあるかどうか
        上にあるときTrue
        下にあるときfalse
    """
    # 赤外線カメラが上にあるときは，webカメラは，下にある
    if isThermalUpper:
        img_rgb = img_rgb[56:463, 48:572]
    else:
        img_rgb = img_rgb[36:453, 55:601]
    
    return img_rgb, img_thermal

def cut_logo(img_rgb, img_thermal, isThermalUpper):
    """
    FLIRのロゴを消す
    
    Parameters
    --------------
    img_rgb : ndarray
        rgb画像の配列
    frame_thermal : ndarray
        FLIRのロゴを削除する赤外線カメラ(640x512)
    isThermalUpper : boolean
        赤外線カメラが上にあるかどうか
        赤外線カメラが上にあるときTrue

    Returns
    --------------
    img_rgb : ndarray
        rgb画像の配列
    frame_thermal : ndarray
        FLIRのロゴを削除した赤外線カメラ
    """
    # 画像サイズを640x512にする
    img_rgb, img_thermal = match_camera_size(img_rgb, img_thermal)
    
    # 赤外線カメラが上にあるときは，webカメラは下にある
    if isThermalUpper:
        img_thermal = img_thermal[0:425, 0:640]
        img_rgb = img_rgb[87:512, 0:640]
    else:
        img_thermal = img_thermal[87:512, 0:640]
        img_rgb = img_rgb[0:425, 0:640]
    return img_rgb, img_thermal

def undistort_and_crop(img):
    """
    imgの歪み補正とトリミングを行う

    Parameters
    --------------
    img : ndarray
        歪み補正を行う画像
    
    Returns
    --------------
    dst : ndarray
        歪み補正とトリミングを行った後の画像
    """
    img2 = img.copy()
    h, w = img2.shape[:2]
    newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))     # 周りの画像の欠損を考慮した内部パラメータと，トリミング範囲を作成

    dst = cv2.undistort(img2, mtx, dist, None, newcameramtx)        # ここで歪み補正を行っている
    ##cv2.imshow('before undistort', dst)

    # crop the image
    x,y,w,h = roi
    dst = dst[y:y+h, x:x+w]     # 画像の端が黒くなっているのでトリミング
    return dst

def upside_down(img):
    """
    imgの画像を上下左右反転させて,返す

    Parameters
    --------------
    img : ndarray
        対象の画像の配列

    Returns
    --------------
    upside_down_img : ndarray
        対象の画像に対して上下左右反転させた後の画像の配列
    """
    upside_down_img = cv2.flip(cv2.flip(img, 0), 1)
    return upside_down_img

def open_camera():
    """
    Webカメラを起動する

    Returns
    --------------
    cap_rgb : RGBカメラのVideoCapture
    cap_thermal : 赤外線カメラのVideoCapture
    """
    cap_rgb = cv2.VideoCapture(1)  # 0 is the default camera
    cap_thermal = cv2.VideoCapture(0)
    
    cap_rgb.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # 幅の設定
    cap_rgb.set(cv2.CAP_PROP_FRAME_HEIGHT, 512)  # 高さの設定
    cap_thermal.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # 幅の設定
    cap_thermal.set(cv2.CAP_PROP_FRAME_HEIGHT, 512)  # 高さの設定
    if not cap_rgb.isOpened():
        print("Cannot open RGB camera")
        return
    if not cap_thermal.isOpened():
        print("Cannot open Thermal camera")
    return cap_rgb, cap_thermal

def process(dxl,cap_rgb, cap_thermal):
    """
    非同期関数
    """
    global frame_count
    global isPushKeyboard
    global isExit

    """
    cap_rgb = cv2.VideoCapture(1)  # 0 is the default camera
    cap_thermal = cv2.VideoCapture(0)
    if not cap_rgb.isOpened():  
        print("Cannot open RGB camera")
        return
    if not cap_thermal.isOpened():
        print("Cannot open Thermal camera")
    """

    print("Process started")
    # Set speed in joint mode
    dxl.set_speed(350)
    moving = False
    while True:
        dxl_present_position = dxl.print_present_position()

        # 現在地が-90度のとき，サーマルは下にある
        if dxl_present_position == DXL_MINIMUM_POSITION_VALUE:
            isThermalUpper = False
        else:
            isThermalUpper = True
        dxl.print_present_position()
        print('isThermalUpper :' + f'{isThermalUpper}')
        moving = dxl.print_moving_state()

        ret_rgb, frame_rgb = cap_rgb.read()
        ret_thermal, frame_thermal = cap_thermal.read()
        frame_rgb, frame_thermal = match_camera_size(frame_rgb, frame_thermal)

        frame_rgb = undistort_and_crop(frame_rgb)
        
        if isThermalUpper:
            frame_rgb = upside_down(frame_rgb)
            frame_thermal = upside_down(frame_thermal)

        # 視野合わせ
        frame_rgb, frame_thermal = fov_match(frame_rgb, frame_thermal, isThermalUpper)
        # 画像のサイズを合わせる
        frame_rgb, frame_thermal = match_camera_size(frame_rgb, frame_thermal)
        # ロゴを切り取る
        frame_rgb, frame_thermal = cut_logo(frame_rgb, frame_thermal, isThermalUpper)
        # 画像のサイズをそろえる
        frame_rgb, frame_thermal = match_camera_size(frame_rgb, frame_thermal)
        # IMG_SIZEにする
        frame_rgb, frame_thermal =match_custom(frame_rgb, frame_thermal)
                
        if ret_rgb and ret_thermal:
            cv2.imshow('RGB', frame_rgb)
            cv2.imshow('Thermal', frame_thermal)

        # Check if motor is moving
        #if abs(dxl_present_position - target_position) <= DXL_MOVING_STATUS_THRESHOLD:
        if moving == 0:
            if isThermalUpper:
                isThermalUpper = False
            else:
                isThermalUpper = True
            # ブレをなくす
            stop_for_seconds(2.5)
            save_rgb_and_thermal_image(frame_rgb, frame_thermal)
            stop_for_seconds(3)
            moving = 1
        #else:
            #moving = True

        if cv2.waitKey(1) & 0xFF == ord('q'):
            isPushKeyboard = True
            print(frame_count)
            print("AND1:" + f'{isPushKeyboard & (frame_count % 2 == 0)}')
            
        print("isPushKeyboard:"+f'{isPushKeyboard}')
        print("AND:" + f'{isPushKeyboard & (frame_count % 2 == 0)}')

        if isPushKeyboard and (frame_count % 2 == 0):
            isExit = True
            break

    print("Process resumed")
    cap_rgb.release()
    cap_thermal.release()
    cv2.destroyAllWindows()

def stop_for_seconds(seconds):
    """
    seconds秒停止

    Parameters
    --------------
    seconds : float
        停止させる秒数
    """
    print("Waiting for " + f'{seconds}' + " seconds...")
    event = threading.Event()
    event.wait(seconds)  # wait for specified seconds

def main():
    global isExit
    start = time.time()
    cap_rgb, cap_thremal = open_camera()
    end = time.time()
    print("elapsed time:"+f'{end - start}')
    time.sleep(40)
    # dynamixel_moduleのDXLクラスの呼び出し
    dxl = Dxl(DXL_ID, DEVICENAME)

    dxl.enable_torque()

    dxl.set_goal_position(DXL_MINIMUM_POSITION_VALUE)

    # process関数を別のスレッドで実行
    thread = threading.Thread(target=process, args=(dxl,cap_rgb, cap_thremal,))
    thread.start()

    global target_position
    target_position = DXL_MINIMUM_POSITION_VALUE
    # メインスレッドで他の処理を実行
    while True:
        # Dynamixelを60度から120度の範囲で動かす
        target_position = DXL_MINIMUM_POSITION_VALUE if target_position == DXL_MAXIMUM_POSITION_VALUE else DXL_MAXIMUM_POSITION_VALUE
        dxl.set_goal_position(target_position)

        # Switch goal position at regular intervals (polling)
        for _ in range(55):  # Polling for 6 seconds (60 x 0.1 seconds)
            event = threading.Event()
            print("Pooling...")
            event.wait(0.1)  # wait for 0.1 seconds

        # Exit main loop condition
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break
        if isExit:
            break

    # Wait for the thread to finish
    thread.join()
    print("Main function ended")

    dxl.disable_torque()
    dxl.close_port()

if __name__ == "__main__":
    main()
