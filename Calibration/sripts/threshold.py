"""
2値化する
"""

import cv2

# 閾値を調整するためのコールバック関数
def update_threshold(val):
    global threshold, img_gray, img_binary
    threshold = val
    _, img_binary = cv2.threshold(img_gray, threshold, 255, cv2.THRESH_BINARY)
    cv2.imshow('Binary Image', img_binary)

# 画像を読み込み、グレースケールに変換
img = cv2.imread('./Calibration/demo/cold_rgb_38.png')
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 初期閾値
threshold = 128

# 初期の2値化画像を生成
_, img_binary = cv2.threshold(img_gray, threshold, 255, cv2.THRESH_BINARY)

# ウィンドウを作成
cv2.namedWindow('Binary Image')
cv2.imshow('Binary Image', img_binary)

# トラックバーを作成
cv2.createTrackbar('Threshold', 'Binary Image', threshold, 255, update_threshold)


# 'ESC'キーが押されるまで待機
while True:
    if cv2.waitKey(1) & 0xFF == 27:  # ESCキーで終了
        break

    if cv2.waitKey(1) == 99: # cキー
        cv2.imwrite(f'./Calibration/thermal_threshold{threshold}.jpg', img_binary)
cv2.destroyAllWindows()
