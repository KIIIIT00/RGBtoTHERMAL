"""
RGB画像をグレースケールにする
"""

import cv2

image_count = 22
INPUT_FILENAME = './Calibration/FOV/RGB/rgb_'+str(image_count)+'.jpg'
OUTPUT_FILENAME = './Calibration/FOV/RGB/gray_'+str(image_count)+'.jpg'
# 画像を読み込む（RGB画像）
image = cv2.imread(INPUT_FILENAME)

# RGBからグレースケールに変換
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# グレースケール画像を保存する
cv2.imwrite(OUTPUT_FILENAME, gray_image)
