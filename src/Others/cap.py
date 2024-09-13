import cv2
import os

# ビデオキャプチャオブジェクトを作成する（デフォルトのカメラを使用）
#cap = cv2.VideoCapture(1)
cam = cv2.VideoCapture(0)

imgpath = './Calibration/'
framecount = 1
#if not cap.isOpened():
#    print("カメラを開くことができませんでした")
#    exit()

while True:
    # カメラからフレームを読み込む
    #ret, frame = cap.read()
    ret1, Frame = cam.read()

    #if not ret:
    #    print("フレームを取得できませんでした")
    #    break

    # フレームをウィンドウに表示する
   # cv2.imshow('Webcam', frame)
    cv2.imshow('Webcam2', Frame)
    # キャプチャ
    if cv2.waitKey(1) == ord('c'):
        print('capture')
        rgb_filename = 'chessboard_check_'f'{framecount}''.png'
        print(rgb_filename)
        thermal_filename = 'cold_thermal_'f'{framecount}''.png'
        #cv2.imwrite(os.path.join(imgpath, rgb_filename), frame)
        cv2.imwrite(os.path.join(imgpath, rgb_filename), Frame)
        framecount += 1
    # 'q'キーが押されたらループを終了する
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# リソースを解放する
#cap.release()
cam.release()
cv2.destroyAllWindows()
