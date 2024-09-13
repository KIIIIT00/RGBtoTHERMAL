import cv2

# ビデオキャプチャオブジェクトを作成する（デフォルトのカメラを使用）
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("カメラを開くことができませんでした")
    exit()

while True:
    # カメラからフレームを読み込む
    ret, frame = cap.read()

    if not ret:
        print("フレームを取得できませんでした")
        break

    # フレームをウィンドウに表示する
    cv2.imshow('Webcam', frame)

    # 'q'キーが押されたらループを終了する
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# リソースを解放する
cap.release()
cv2.destroyAllWindows()
