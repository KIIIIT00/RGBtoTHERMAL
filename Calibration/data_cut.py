"""
データをカットするプログラム
"""

import cv2
import os

# インプットフォルダ
INPUT_RGB_TRAIN      = './DataSet/Scene2/RGB/train/'
INPUT_RGB_TEST       = './DataSet/Scene2/RGB/test/'
INPUT_THERMAL_TRAIN  = './DataSet/Scene2/THERMAL/train/'
INPUT_THERMAL_TEST   = './DataSet/Scene2/THERMAL/test/'

# アウトプットフォルダ
OUTPUT_RGB_TRAIN     = './DataSet/Scene2ver2/trainA/'
OUTPUT_RGB_TEST      = './DataSet/Scene2ver2/testA/'
OUTPUT_THERMAL_TRAIN = './DataSet/Scene2ver2/trainB/'
OUTPUT_THERMAL_TEST  = './DataSet/Scene2ver2/testB/'

# 写真をカットするリスト
cut_lists = [2, 6, 11, 17, 18, 19, 24, 25, 26, 27, 28, 29, 31, 38, 41, 44, 46, 47, 48, 50, 51, 52,
             53, 57, 60, 61, 80, 92, 93, 95, 96, 97, 100, 115, 120, 132, 134, 154, 157, 159, 168, 
             170, 171, 185, 186, 191, 198, 204, 234, 236, 262, 274, 279, 280, 281, 282, 283, 284, 
             285, 308, 310, 313, 319, 321, 322, 329, 330, 335, 337, 341, 345, 346, 359, 361, 367, 
             401, 425, 431, 433, 442, 451, 470, 480, 520, 521, 523, 525, 541, 544, 560, 580, 583,
             596, 625, 703, 704, 727, 749, 750, 752, 756, 757, 769, 785, 790, 800, 801, 806, 811,
             925, 927, 930, 962, 978, 984, 1003, 1012]


rgb_train_files = os.listdir(INPUT_RGB_TRAIN)
rgb_test_files = os.listdir(INPUT_RGB_TEST)
thermal_train_files = os.listdir(INPUT_THERMAL_TRAIN)
thermal_test_files = os.listdir(INPUT_THERMAL_TEST)

# 番号だけを取り出す
rgb_train_numbers   = [int(file.split('_')[1].split('.')[0]) for file in rgb_train_files]
rgb_test_numbers    = [int(file.split('_')[1].split('.')[0]) for file in rgb_test_files]
thermal_train_numbers = [int(file.split('_')[1].split('.')[0]) for file in thermal_train_files]
thermal_test_numbers  = [int(file.split('_')[1].split('.')[0]) for file in thermal_test_files]

# 番号だけ取り出したリストをソートする
sorted_rgb_train_numbers = sorted(rgb_train_numbers)
sorted_rgb_test_numbers  = sorted(rgb_test_numbers)
sorted_thermal_train_numbers = sorted(thermal_train_numbers)
sorted_thermal_test_numbers = sorted(thermal_test_numbers)

image_cnt = 1
# 訓練用データでぶれているものを除去する
for rgb_num, thermal_num in zip(sorted_rgb_train_numbers, sorted_thermal_train_numbers):
    # カットしたい番号でないとき
    if not rgb_num in cut_lists:
        input_rgb_file_name = os.path.join(INPUT_RGB_TRAIN,''f'rgb_{rgb_num}.jpg')
        input_thermal_file_name = os.path.join(INPUT_THERMAL_TRAIN, ''f'thermal_{rgb_num}.jpg')
        rgb_img = cv2.imread(input_rgb_file_name)
        thermal_img = cv2.imread(input_thermal_file_name)
        rgb_file_name = os.path.join(OUTPUT_RGB_TRAIN,''f'rgb_{image_cnt}.jpg')
        thermal_file_name = os.path.join(OUTPUT_THERMAL_TRAIN, ''f'thermal_{image_cnt}.jpg')
        cv2.imwrite(rgb_file_name, rgb_img)
        cv2.imwrite(thermal_file_name, thermal_img)
        image_cnt += 1

# テスト用データを移動
for rgb_num, thermal_num in zip(sorted_rgb_test_numbers, sorted_thermal_test_numbers):
    input_rgb_name = os.path.join(INPUT_RGB_TEST,''f'rgb_{rgb_num}.jpg')
    input_thermal_name = os.path.join(INPUT_THERMAL_TEST, ''f'thermal_{thermal_num}.jpg')
    output_rgb_name = os.path.join(OUTPUT_RGB_TEST,''f'rgb_{rgb_num}.jpg')
    output_thermal_name = os.path.join(OUTPUT_THERMAL_TEST, ''f'thermal_{thermal_num}.jpg')
    
    # 画像読み込み
    rgb_test_img = cv2.imread(input_rgb_name)
    thermal_test_img = cv2.imread(input_thermal_name)
    
    # 画像保存
    cv2.imwrite(output_rgb_name, rgb_test_img)
    cv2.imwrite(output_thermal_name, thermal_test_img)
    
    
        