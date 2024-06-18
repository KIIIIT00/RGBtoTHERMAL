import cv2

# ビデオキャプチャオブジェクトを2つ作成する（カメラ0とカメラ1を使用）
cap1 = cv2.VideoCapture(1, cv2.CAP_DSHOW)
cap2 = cv2.VideoCapture(0)

if not cap1.isOpened():
    print("カメラ1を開くことができませんでした")
    exit()

if not cap2.isOpened():
    print("カメラ2を開くことができませんでした")
    exit()

while True:
    # カメラ1からフレームを読み込む
    ret1, frame1 = cap1.read()
    if not ret1:
        print("カメラ1のフレームを取得できませんでした")
        break

    # カメラ2からフレームを読み込む
    ret2, frame2 = cap2.read()
    if not ret2:
        print("カメラ2のフレームを取得できませんでした")
        break

    # カメラ1のフレームをウィンドウに表示する
    cv2.imshow('Webcam 1', frame1)

    # カメラ2のフレームをウィンドウに表示する
    cv2.imshow('Webcam 2', frame2)

    # 'q'キーが押されたらループを終了する
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# リソースを解放する
cap1.release()
cap2.release()
cv2.destroyAllWindows()
