"""
2024/05/17
2つのペア画像を連結させて、あらたなフォルダに入れる
参考:https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix/blob/master/datasets/combine_A_and_B.py
"""

import os
import numpy as np
import cv2
import argparse
from multiprocessing import Pool
import json

"""
path_RGB:RGB画像が入っているフォルダのパス
path_THEMAL:サーモグラフィが入っているフォルダのパス
path_Combine:RGB画像とサーモグラフィを連結させた画像を格納するフォルダのパス
"""
def image_write(path_RGB, path_THEMAL, path_Combine):
    img_RGB = cv2.imread(path_RGB, 1)
    img_THEMAL = cv2.imread(path_THEMAL, 1)
    img_RGB_THEMAL = np.concatenate([img_RGB, img_THEMAL], 1)
    cv2.imrwrite(path_Combine, img_RGB_THEMAL)

parser = argparse.ArgumentParser('create image pairs')
parser.add_argument('--fold_RGB', dest='fold_RGB', help='input directory for image A', type=str, default='../Data/video_rgb_test/data/')
parser.add_argument('--fold_THERMAL', dest='fold_THERMAL', help='input directory for image B', type=str, default='../Data/video_thermal_test/data/')
parser.add_argument('--fold_RGB_THERMAL', dest='fold_RGB_THERMAL', help='output directory', type=str, default='../Data/video_rgb_thermal_combine_train/')
#parser.add_argument('--no_multiprocessing', dest='no_multiprocessing', help='If used, chooses single CPU execution instead of parallel execution', action='store_true',default=False)
args = parser.parse_args()

for arg in vars(args):
    print('[%s] = ' % arg, getattr(args, arg))

# 各フォルダ内にファイル内の最小値をnum_imgsに格納
num_imgs = min(len(os.listdir(args.fold_RGB)), len(os.listdir(args.fold_THERMAL)))
print(num_imgs)

splits = os.listdir(args.fold_RGB)

# RGBとTHEMALの対応した表をもつjsonを読み込む
json_open = open('../rgb_to_thermal_vid_map.json', 'r')
# map_dataのkey:RGB画像のファイル名
# map_dataのvalue:サーマルカメラの画像のファイル名
map_data = json.load(json_open)
map_data_RGB = map_data.keys()
map_data_THERMAL = map_data.values()
#print(type(map_data))

#if not args.no_multiprocessing:
#    pool = Pool()

count = 0
# RGBのパスとサーマルのパスをsp_RGBとsp_THERMALに順番に格納
for (sp_RGB, sp_THERMAL) in zip(map_data_RGB, map_data_THERMAL):
    img_fold_RGB = os.path.join(args.fold_RGB, sp_RGB)
    #(img_fold_RGB)
    img_fold_THERMAL = os.path.join(args.fold_THERMAL, sp_THERMAL)
    #print(img_fold_THERMAL)
    #print('split = %s, use %d/%d images' % (sp_RGB, num_imgs))
    
    # 2つの画像を結合させた画像のパス
    img_fold_RGB_THERMAL = os.path.join(args.fold_RGB_THERMAL, sp_RGB)
    
    # 結合する画像が格納されるフォルダがあるかどうか
    if not os.path.isdir(args.fold_RGB_THERMAL):
        os.makedirs(args.fold_RGB_THERMAL)
    #print(os.path.isfile(img_fold_RGB))
    #2つのファイルが存在するかどうか
    if os.path.isfile(img_fold_RGB) and os.path.isfile(img_fold_THERMAL):
        print("Yes")
        # 2つの画像を結合した画像のファイル名とパス
        name_RGB_THERMAL = "RGB_THERMAL_Combine_" + str(count)+".jpg"
        print(name_RGB_THERMAL)
        path_RGB_THERMAL = os.path.join(args.fold_RGB_THERMAL, name_RGB_THERMAL)
        print(path_RGB_THERMAL)
        
        # 並列処理をするかどうか
#        if not args.no_multiprocessing:
#                pool.apply_async(image_write, args=(img_fold_RGB, img_fold_THERMAL, img_fold_RGB_THERMAL))
#        else:
    
        im_RGB = cv2.resize(cv2.imread(img_fold_RGB, cv2.IMREAD_COLOR), dsize=(640,512)) # python2: cv2.CV_LOAD_IMAGE_COLOR; python3: cv2.IMREAD_COLOR
        print(im_RGB.shape)
        im_THERMAL = cv2.imread(img_fold_THERMAL, 1) # python2: cv2.CV_LOAD_IMAGE_COLOR; python3: cv2.IMREAD_COLOR
        print(im_THERMAL.shape)
        im_RGB_THERMAL = np.concatenate([im_RGB, im_THERMAL], 1)
        cv2.imwrite(path_RGB_THERMAL, im_RGB_THERMAL)
    count = count + 1
#if not args.no_multiprocessing:
#    pool.close()
#    pool.join()