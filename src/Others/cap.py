import cv2
import os

# ビデオキャプチャオブジェクトを作成する（デフォルトのカメラを使用）
thermal = cv2.VideoCapture(0)
rgb = cv2.VideoCapture(1)

imgpath = './results/Calibration/beforeAfter/'
framecount = 1
#if not cap.isOpened():
#    print("カメラを開くことができませんでした")
#    exit()
rgb.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
rgb.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
thermal.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
thermal.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    # カメラからフレームを読み込む
    _, rgb_frame = rgb.read()
    _, thermal_frame =thermal.read()

    #if not ret:
    #    print("フレームを取得できませんでした")
    #    break

    # フレームをウィンドウに表示する
    cv2.imshow('Webcam', rgb_frame)
    cv2.imshow('Webcam2', thermal_frame)
    
    # キャプチャ
    if cv2.waitKey(1) == ord('c'):
        print('capture')
        rgb_filename = 'after_rgb_'f'{framecount}''.png'
        print(rgb_filename)
        thermal_filename = 'after_thermal_'f'{framecount}''.png'
        cv2.imwrite(os.path.join(imgpath, rgb_filename), rgb_frame)
        cv2.imwrite(os.path.join(imgpath, thermal_filename), thermal_frame)
        framecount += 1
    # 'q'キーが押されたらループを終了する
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# リソースを解放する
rgb.release()
thermal.release()
cv2.destroyAllWindows()
