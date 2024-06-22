"""
非同期関数でwebカメラを動作中に,あるPosに到達したとき,
設定されたディレクトリに写真を格納する

サーマルとRGB画像を格納する
この時に，視野の位置，画像サイズ，画像の向きを合わせる
"""

# インポート
import cv2
import threading
from dynamixel_sdk import *                    # Uses Dynamixel SDK library
from Dxl import Dxl

# Default setting
DXL_MINIMUM_POSITION_VALUE = Dxl.deg_2_pos(-90)       
DXL_MAXIMUM_POSITION_VALUE = Dxl.deg_2_pos(90)        
DXL_ID = 12                                   # Dynamixel ID: 1
DEVICENAME = "COM3"                   # Check which port is being used on your controller
                                               # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"
DXL_MOVING_STATUS_THRESHOLD = 20               # Dynamixel moving status threshold

framecount = 0
#xl = Dxl(DXL_ID, DEVICENAME)

def save_rgb_image(frame):
    """
    rgb_frameの写真を保存する

    Parameters

    """
    global framecount
    filename = 'rgb' + f'{framecount}' + '.jpg'
    cv2.imwrite(filename, frame)
    print(f"Image saved as {filename}")
    framecount += 1

def save_thermal_image(frame):
    """
    thermal_frameの写真を保存する

    Parameters

    """
    global framecount
    filename = 'thermal' + f'{framecount}' + '.jpg'
    cv2.imwrite(filename, frame)
    print(f"Image saved as {filename}")
    framecount += 1


def Match_Size(img_rgb, img_thermal):
    h_rgb, w_rgb, _ = img_rgb.shape
    h_thermal, w_thermal, _ = img_thermal.shape
    h_max = max([h_rgb, h_thermal])
    w_max = max([w_rgb, w_thermal])
    img_rgb = cv2.resize(img_rgb, dsize=(w_max, h_max))
    img_thermal = cv2.resize(img_thermal, dsize=(w_max, h_max))
    return img_rgb, img_thermal

def process(dxl):
    cap_rgb = cv2.VideoCapture(0)  # 0 is the default camera
    cap_thermal = cv2.VideoCapture(1)
    if not cap_rgb.isOpened():
        print("Cannot open RGB camera")
        return
    if not cap_thermal.isOpened():
        print("Cannot open Thermal camera")

    print("Process started")
    # Set speed in joint mode
    dxl.set_speed(350)
    moving = False
    while True:
        dxl_present_position = dxl.print_present_position()
        moving = dxl.print_moving_state()

        ret_rgb, frame_rgb = cap_rgb.read()
        ret_thermal, frame_thermal = cap_thermal.read()
        if ret_rgb and ret_thermal:
            cv2.imshow('Camera', frame_rgb)
            cv2.imshow('Thermal', frame_thermal)

        # Check if motor is moving
        #if abs(dxl_present_position - target_position) <= DXL_MOVING_STATUS_THRESHOLD:
        if moving == 0:
            # ブレをなくす
            stop_for_seconds(1)
            save_rgb_image(frame_rgb)
            save_thermal_image(frame_thermal)
            stop_for_seconds(3)
            #moving = False
        #else:
            #moving = True

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("Process resumed")
    cap_rgb.release()
    cap_thermal.release()
    cv2.destroyAllWindows()

def stop_for_seconds(seconds):
    """
    seconds秒停止

    Parameters
    
    """
    print("Waiting for " + f'{seconds}' + " seconds...")
    event = threading.Event()
    event.wait(seconds)  # wait for specified seconds

def main():
    # dynamixel_moduleのDXLクラスの呼び出し
    dxl = Dxl(DXL_ID, DEVICENAME)

    dxl.enable_torque()

    dxl.set_goal_position(DXL_MINIMUM_POSITION_VALUE)

    # process関数を別のスレッドで実行
    thread = threading.Thread(target=process, args=(dxl,))
    thread.start()

    global target_position
    target_position = DXL_MINIMUM_POSITION_VALUE
    # メインスレッドで他の処理を実行
    while True:
        # Dynamixelを60度から120度の範囲で動かす
        target_position = DXL_MINIMUM_POSITION_VALUE if target_position == DXL_MAXIMUM_POSITION_VALUE else DXL_MAXIMUM_POSITION_VALUE
        dxl.set_goal_position(target_position)

        # Switch goal position at regular intervals (polling)
        for _ in range(40):  # Polling for 2 seconds (20 x 0.1 seconds)
            event = threading.Event()
            event.wait(0.1)  # wait for 0.1 seconds

        # Exit main loop condition
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Wait for the thread to finish
    thread.join()
    print("Main function ended")

    dxl.disable_torque()
    dxl.close_port()

if __name__ == "__main__":
    main()
