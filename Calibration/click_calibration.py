"""
画像をクリックしたところでカメラキャリブレーションを行う
"""

import cv2
import numpy as np
import glob
from utils.cameracalibration import CameraCalibration
from utils.EllipseFinder import EllipseFinder
import re

def read_file(file_name):
    """
    テキストファイルから，写真の数と再投影誤差が格納されたリストを返す
    """
    pic_num_list =[]
    error_num_list = []
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            for line in file:
                sentences = re.split(r'[,]', line.strip())
                for sentence in sentences:
                    # 正規表現を使用して，数値を抽出
                    match_pic = re.search(r'picnum:\s*(\d+)', sentence)
                    match_error = re.search(r'error:\s*([\d\.]+)', sentence)
                    if match_pic:
                        pic_num = int(match_pic.group(1))
                        pic_num_list.append(pic_num)
                    
                    if match_error:
                        error_num = float(match_error.group(1))
                        error_num_list.append(error_num)
            return pic_num_list, error_num_list       

    except FileNotFoundError as e:
        # ファイルが存在しないとき
        print(f"The file {file_name} was not found.")
    except Exception as e:
        # その他のエラー
        print(f"An error occurred: {e}")

def get_data_from_text(text_path, threshold):
        """
        テキストファイルから，写真の番号と再投影誤差が格納されたリストを返す

        Parameters
        ----------
        text_path : str
            テキストファイルのパス
        threshold : float
            再投影誤差の閾値

        Returns
        ----------
        pic_nums : list
            写真の番号が格納されたリスト
        errors : list
            再投影誤差が格納されたリスト
        """
        pic_nums = []
        errors = []
        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                for line in f:
                    sentences = re.split(r'[,]', line.strip())
                    for sentence in sentences:
                        # 正規表現を使用して，数値を抽出
                        match_pic = re.search(r'picnum:\s*(\d+)', sentence)
                        match_error = re.search(r'error:\s*([\d\.]+)', sentence)
                        if match_pic:
                            pic_num = int(match_pic.group(1))
                        if match_error:
                            error = float(match_error.group(1))
                            if error <= threshold:  # 再投影誤差が閾値以下のとき
                                pic_nums.append(pic_num)
                                errors.append(error)
            return pic_nums, errors

        except FileNotFoundError as e: # ファイルが存在しないとき
            print(f"The file {text_path} was not found.")

        except Exception as e: #その他のエラー
            print(f"An error occurred: {e}") 
                 
def contatins_digit(file_path, pic_num_list):
    """
    file_pathにpic_numが含まれるかどうか

    Parameters
    ----------
    file_path : str 
        画像のファイルパス
    pic_num_list : list
        写真の番号が格納されているリスト

    Returns
    -------
    boolean
    """
    # 正規表現を使用して，file_pathから数値を抽出する
    file_contains_numbers = re.findall(r'\d+', file_path)
    for contains_num in file_contains_numbers:
        contains_num = int(contains_num)
        if contains_num in pic_num_list:
            return True
        else:
            return False


file_name = './Calibration/re_projection_error_text.txt'
chessboard_size = (5, 5)
calibration = CameraCalibration(chessboard_size)
images = glob.glob('./Calibration/chessboard_calibration_data/thermal/*.jpg')
cal_count = 1
pic_count = 62
threshold = 0.25
#pic_num_list, error_num_list = read_file(file_name) 
pic_num_list, error_num_list = get_data_from_text(file_name, threshold)
print(len(pic_num_list))
index = 0 # pic_num_listとerror_numlistの添え字
pic_list = [] # 再投影誤差用の写真番号を格納するリスト
for fname in images:
    contains_bool = contatins_digit(fname, pic_num_list)
    # ファイルパスにpic_num_list[index]が含まれる, かつ
    # error_num_list[index]が0.5より小さいとき
    if contains_bool:
        print("-----start add corners-----")
        finder = EllipseFinder(fname)
        corners = finder.run()
        if corners is not False:
            print(len(corners))
            calibration.add_corners(fname, corners)
            print(f'calibration count:', cal_count)
            #pic_num = re.findall(r'\d+', fname)[0]
            #pic_list.append(int(pic_num)) #　該当するファイルパスの写真の番号を格納する
            cal_count += 1

    index += 1 # pic_num_listとerror_num_listの添え字を進める
    pic_count += 1
    print("-----finish add corners-----")

image_size = (640, 512)
ret, mtx, dist, rvecs, tvecs = calibration.calibrate(image_size)

print("キャリブレーション結果:")
print("リプロジェクションエラー:", ret)
print("カメラ行列:\n", mtx)
print("歪み係数:\n", dist)

preojection_error = calibration.re_projection_error_and_save_file(pic_num_list)
print("preojection error:", preojection_error)                                                          