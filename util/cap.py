import cv2

# ビデオキャプチャオブジェクトを作成する（デフォルトのカメラを使用）
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("カメラを開くことができませんでした")
    exit()

while True:
    # カメラからフレームを読み込む
    ret, frame = cap.read()
    ret1, Frame = cam.read()

    if not ret:
        print("フレームを取得できませんでした")
        break

    # フレームをウィンドウに表示する
    cv2.imshow('Webcam', frame)
    cv2.imshow('Webcam2', Frame)

    # 'q'キーが押されたらループを終了する
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# リソースを解放する
cap.release()
cam.release()
cv2.destroyAllWindows()
