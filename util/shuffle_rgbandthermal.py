"""
Data/rgb_imgとData/thermal_imgの写真をランダムで7:3にtest，train，valueに分ける
"""

import os
from sklearn.model_selection import train_test_split
# 参照元のフォルダ
RGB_FILE_PATH = './Data/rgb_img/'
THERMAL_FILE_PATH = './Data/thermal_img/'

# 移動後のフォルダ
MOVE_RGB_FILE_PATH = './datasets/Scene1/train'
MOVE_THERMAL_FILE_PATH = './datasets/Scene1/test'

"""
関数定義
"""
################################################

# フォルダの存在確認する関数
def check_exists_dir(DIR_PATH):
  return os.path.exists(DIR_PATH)

# フォルダの作成する関数
# フォルダの存在があるときは，作成しない
def make_dir():
  if not check_exists_dir(MOVE_RGB_FILE_PATH):
    os.makedirs(MOVE_RGB_FILE_PATH)
  
  if not check_exists_dir(MOVE_THERMAL_FILE_PATH):
    os.makedirs(MOVE_THERMAL_FILE_PATH)

# Dataフォルダに入っているRGB画像とサーモグラフィのファイル数を配列にいれる
# 配列を返す
# ただし，rgb_imgとthermal_imgに入っているファイル数が一緒であると仮定
def get_Data_filenum_list():
  if len(os.listdir(RGB_FILE_PATH)) == len(os.listdir(THERMAL_FILE_PATH)):
    filenumlist = []
    filenum = len(os.listdir(RGB_FILE_PATH))
    for i in range(filenum):
      filenumlist.append(i)
    return filenumlist
  else:
    print("[Error]ファイル数が一致しません")
    return None

# ファイルの番号を格納したリストを分割する
def data_split():
  list = get_Data_filenum_list()
  if list is not None:



################################################