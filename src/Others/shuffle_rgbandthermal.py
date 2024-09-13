"""
Data/rgb_imgとData/thermal_imgの写真をランダムで7:3にtest，train，valueに分ける
また，分けるときに，RGB画像とサーモグラフィをくっつけて表示する

参考:
    https://qiita.com/katsudon_qiita/items/452958eda6505bb371a1
"""

import os
from sklearn.model_selection import train_test_split
import numpy as np
import cv2
import argparse
from multiprocessing import Pool
import combine_RGBandTHERMAL 

# 参照元のフォルダ
RGB_DIR_PNG_PATH = './Data/rgb_img/png/'
THERMAL_DIR_PNG_PATH = './Data/thermal_img/png/'
RGB_DIR_JPG_PATH = './Data/rgb_img/jpg/'
THERMAL_DIR_JPG_PATH = './Data/thermal_img/jpg/'

# 移動後のフォルダ
COMBINE_DIR_PATH = './Combine/Scene1/'
# COMBINE_DIR_PATH = "/Users/Kawahara/pix2pix/datasets/datasets/facades/combine/"
MOVE_TRAIN_DIR_PATH = './datasets/Scene1/train/'
MOVE_TEST_DIR_PATH = './datasets/Scene1/test/'
MOVE_VAL_DIR_PATH = './datasets/Scene1/val/'

# MOVE_TEST_DIR_PATH = "/Users/Kawahara/pix2pix/datasets/datasets/facades/test/"
# MOVE_VAL_DIR_PATH = "/Users/Kawahara/pix2pix/datasets/datasets/facades/val/"
# MOVE_TRAIN_DIR_PATH = "/Users/Kawahara/pix2pix/datasets/datasets/facades/train/"
"""
関数定義
"""
################################################

# フォルダの存在確認する関数
def check_exists_dir(DIR_PATH):
  return os.path.exists(DIR_PATH)

# フォルダの作成する関数
# フォルダの存在があるときは，作成しない
def make_dir(TRAIN_DIR_PATH, TEST_DIR_PATH, VAL_DIR_PATH):
  if not check_exists_dir(TRAIN_DIR_PATH):
    os.makedirs(TRAIN_DIR_PATH)
  
  if not check_exists_dir(TEST_DIR_PATH):
    os.makedirs(TEST_DIR_PATH)
  
  if not check_exists_dir(VAL_DIR_PATH):
    os.makedirs(VAL_DIR_PATH)

# Dataフォルダに入っているRGB画像とサーモグラフィのファイル数を配列にいれる
# 配列を返す
# ただし，rgb_imgとthermal_imgに入っているファイル数が一緒であると仮定
def get_Data_filenum_list(RGB_DIR_PATH, THERMAL_DIR_PATH):
  if len(os.listdir(RGB_DIR_PATH)) == len(os.listdir(THERMAL_DIR_PATH)):
    filenumlist = []
    filenum = len(os.listdir(RGB_DIR_PATH))
    for i in range(filenum):
      filenumlist.append(i)
    return filenumlist
  else:
    print("[Error]ファイル数が一致しません")
    return None
# COMBINEフォルダのファイル番号を格納するリストを返す
def get_filenum_list(COMBINE_PATH):
  filenumlist = []
  filenum = len(os.listdir(COMBINE_PATH))
  for num in range(filenum):
    filenumlist.append(num)
  return filenumlist
# ファイルの番号を格納したリストを分割する
# フォルダが存在するときは，train,test,valの番号を格納したリストを返す
# フォルダが存在しないとき，はNoneを返す
def data_split(COMBINE_PATH):
  list = get_filenum_list(COMBINE_PATH)
  if list is not None:
    # train用データを70%,乱数を固定
    train, other = train_test_split(list, test_size= 0.3, random_state=5)
    # test用データを27%，val用データを3%
    test, val = train_test_split(other, test_size=0.1, random_state=5)
    return train, test, val
  else:
    print("[Error]リストが見つかりません")
    return None

# train,test,valのフォルダに分ける
# listの番号に該当するファイルをフォルダにわける
# 引数:
# list:ファイル番号を格納
# input_dir:参照するフォルダ
# move_dir_path:移動させるフォルダ
def move_dir(list,input_dir, move_dir_path):
  # フォルダ内のファイルを配列に格納する
  file_list = os.listdir(input_dir)
  count = 1
  for name in list:
    for filename in file_list:
      # listの中の番号とfilenameが一致したとき
      if str(name) + '.jpg' == filename:
        file_path = os.path.join(input_dir, filename)
        #print(file_path)
        img = cv2.imread(file_path, cv2.IMREAD_COLOR)
        cv2.imwrite(move_dir_path+str(count)+'.jpg', img)
        count+= 1

  
# RGBとサーモグラフィの画像の結合
# INPUT_PATH：RGBのファイル
# OUTPUT_PATH：THERMALのファイル
def image_write(OUTPUT_PATH, INPUT_PATH, COMBINE_PATH):
  img_THERMAL = cv2.imread(OUTPUT_PATH, cv2.IMREAD_COLOR)
  img_THERMAL = cv2.resize(img_THERMAL, dtype=(256, 256))
  img_RGB = cv2.imread(INPUT_PATH, cv2.IMREAD_COLOR)
  img_RGB = cv2.resize(img_RGB, dtype=(256, 256))
  print(img_RGB.size)
  img_THERMAL_RGB = np.concatenate([img_THERMAL,img_RGB],1)
  cv2.imwrite(COMBINE_PATH, img_THERMAL_RGB)


################################################

if __name__ == '__main__':
  train, test, val = data_split(COMBINE_DIR_PATH)
  # 実行済み
  move_dir(train, COMBINE_DIR_PATH, MOVE_TRAIN_DIR_PATH)
  move_dir(test, COMBINE_DIR_PATH, MOVE_TEST_DIR_PATH)
  move_dir(val, COMBINE_DIR_PATH, MOVE_VAL_DIR_PATH)