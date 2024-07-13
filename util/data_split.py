"""
サーマルとrgb画像が結合しているのを別々にする
"""

import os
from PIL import Image
import cv2

# フォルダのパス
INPUT_COMBINE_TRAIN   = './datasets/Scene1/test/'
INPUT_COMBINE_TEST    = './datasets/Scene1/train/'
INPUT_COMBINE_VAL     = './datasets/Scene1/val/'

OUTPUT_RGB_TRAIN      = './DataSet/Scene1/RGB/train/'
OUTPUT_RGB_TEST       = './DataSet/Scene1/RGB/test/'
OUTPUT_RGB_VAL        = './DataSet/Scene1/RGB/val/'
OUTPUT_THERMAL_TRAIN  = './DataSet/Scene1/THERMAL/train/'
OUTPUT_THERMAL_TEST   = './DataSet/Scene1/THERMAL/test/'
OUTPUT_THERMAL_VAL    = './DataSet/Scene1/THERMAL/val/'

def split_rgb_thermal(image_path, output_thermal_folder, output_rgb_folder):
    """
    image_pathの画像を幅で2分割し、output_thermal_folderとoutput_rgb_folderにそれぞれ入れる

    Parameters
    ----------
    image_path : str
        分割対象の画像のパス
    output_thermal_folder : str
        出力対象のサーマル画像を保存するフォルダのパス
    output_rgb_folder : str
        出力対象のrgb画像を保存するフォルダのパス
     """
    # 画像を開く
    image = cv2.imread(image_path)
    _,width, _ = image.shape

    # 分割の幅を計算
    split_width = width // 2

    # 元画像のファイル名を取得
    base_name = os.path.basename(image_path)
    name, ext = os.path.splitext(base_name)

    thermal = image[:,0:split_width]
    rgb = image[:, split_width + 1:width]
    split_thermal_path = os.path.join(output_thermal_folder, name+ext)
    split_rgb_path = os.path.join(output_rgb_folder, name+ext)
    # 画像を保存
    cv2.imwrite(split_thermal_path, thermal)
    cv2.imwrite(split_rgb_path, rgb)
    print('Saved split image')

def process_images_folder(input_folder, output_thermal_folder, output_rgb_folder):
    """
    フォルダ内の画像に対して分割を行う

    Parameters
    -----------
    input_folder : str
        分割対象の画像が入ったフォルダ
    output_thermal_folder : str
        サーマルの画像を格納するフォルダ
    output_rgb_folder : str
        rgbの画像を格納するフォルダ
    """

    # 入力フォルダ内のすべてのファイルを取得
    files = os.listdir(input_folder)
    
    # 出力フォルダが存在しない場合は作成
    os.makedirs(output_thermal_folder, exist_ok=True)
    os.makedirs(output_rgb_folder, exist_ok=True)
    # 各画像ファイルに対して分割処理を実行
    for file in files:
        image_path = os.path.join(input_folder, file)
        # 画像ファイルのみ処理
        if os.path.isfile(image_path) and image_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            split_rgb_thermal(image_path, output_thermal_folder, output_rgb_folder)


process_images_folder(INPUT_COMBINE_TRAIN, OUTPUT_THERMAL_TRAIN, OUTPUT_RGB_TRAIN)
process_images_folder(INPUT_COMBINE_TEST, OUTPUT_THERMAL_TEST, OUTPUT_RGB_TEST)
process_images_folder(INPUT_COMBINE_VAL, OUTPUT_THERMAL_VAL, OUTPUT_RGB_VAL)