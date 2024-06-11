"""
RGBとTHERMALを結合する
参考:
    参考:
    https://qiita.com/katsudon_qiita/items/452958eda6505bb371a1
"""

import os
import cv2
import numpy as np
from PIL import Image

# 参照元のフォルダ
RGB_DIR_PNG_PATH = './Data/rgb_img/png/'
THERMAL_DIR_PNG_PATH = './Data/thermal_img/png/'
RGB_DIR_JPG_PATH = './Data/rgb_img/jpg/'
THERMAL_DIR_JPG_PATH = './Data/thermal_img/jpg/'

# 移動後のフォルダ
#COMBINE_DIR_PATH = './Combine/Scene1/'
COMBINE_DIR_PATH = "/Users/Kawahara/pix2pix/datasets/datasets/facades/combine/"

"""
関数定義
"""
################################################
# RGBとサーモグラフィの画像の結合
# INPUT_PATH：RGBのファイル
# OUTPUT_PATH：THERMALのファイル
def image_write(OUTPUT_PATH, INPUT_PATH, COMBINE_PATH):
  thermal_files = os.listdir(OUTPUT_PATH)
  rgb_files = os.listdir(INPUT_PATH)
  for thermal_file, rgb_file in zip(thermal_files, rgb_files):
    thermal_path = os.path.join(OUTPUT_PATH, thermal_file)
    rgb_path = os.path.join(INPUT_PATH, rgb_file)
    combint_file = thermal_file
    img_THERMAL = cv2.imread(thermal_path, cv2.IMREAD_COLOR)
    img_THERMAL = cv2.resize(img_THERMAL, dsize=(256, 256))
    img_RGB = cv2.imread(rgb_path, cv2.IMREAD_COLOR)
    img_RGB = cv2.resize(img_RGB, dsize=(256, 256))
    img_THERMAL_RGB = np.concatenate([img_THERMAL,img_RGB],1)
    combine_path = os.path.join(COMBINE_PATH, combint_file)
    cv2.imwrite(combine_path, img_THERMAL_RGB)

# ファルダ内のpng画像をjpg画像に変化
def convert_png_to_jpg(png_dir_path, jpg_dir_path):
  # 入力フォルダ内のPNG画像をリストアップ
  png_files = [f for f in os.listdir(png_dir_path) if f.endswith('.png')]
  
  # 出力フォルダがないとき作成
  os.makedirs(jpg_dir_path, exist_ok=True)

  count = 1
  # 各PNG画像をJPGに変換
  for png_file in png_files:
    png_path = os.path.join(png_dir_path, png_file)
    # JPGの出力パスを生成
    jpg_path = os.path.join(jpg_dir_path, count + '.jpg')

    # 画像の変換
    img = Image.open(png_path)
    img.save(jpg_path, 'JPEG')
    count += 1

################################################

if __name__ == '__main__':
  image_write(THERMAL_DIR_JPG_PATH, RGB_DIR_JPG_PATH, COMBINE_DIR_PATH)