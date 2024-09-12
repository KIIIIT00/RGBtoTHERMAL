"""
画像領域に赤線で範囲を描画する
"""
import os
import cv2

rgbcount = 86
INPUT_RGB = './Calibration/FOV/RGB/'
rgb_filename = os.path.join(INPUT_RGB,''f'rgb_{rgbcount}.jpg')

rgb_img = cv2.imread(rgb_filename)


# 赤色 (BGR形式) の色指定
color = (0, 0, 255)

cv2.rectangle(rgb_img, (71, 29), (571, 420), color, 2)

cv2.imshow("Image with red rect", rgb_img)
cv2.waitKey(0)
cv2.destroyAllWindows()

# 画像を保存
cv2.imwrite('./Calibration/FOV/RGB/rgb_paintrect_86.jpg', rgb_img)