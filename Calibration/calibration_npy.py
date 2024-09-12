"""
npyファイルからnumpyを取り出して，そのimgpointsでキャリブレーションをする
"""
import numpy as np
import cv2
from tqdm import tqdm
import glob
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

def read_npy(file_name):
    """
    npyファイルを読み取る
    """
    load_array = np.load(file_name)
    return load_array

def re_projection_error_and_save_file(pic_list, objpoints, imgpoints, revcs, tvecs, mtx, dist):
        """
        再投影誤差を算出し，テキストファイルに書き込みをする
        """
        mean_error = 0
        error_list = []
        for i in range(len(objpoints)):
            imgpoints2, _ = cv2.projectPoints(objpoints[i], revcs[i], tvecs[i], mtx, dist)
            error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints[i])
            error_list.append(error)
            print("picnum", pic_list[i])
            print(":", error)
            mean_error += error
        
        filename = './Calibration/again3_re_projection_error_text.txt'
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for i, error in enumerate(error_list):
                    f.write(f"picnum: {pic_list[i]}, error: {error}\n")
            print(f"再投影誤差を記録しました: {filename}")
        except Exception as e:
            print(f"再投影誤差記録に失敗しました: {e}")
        return mean_error / len(objpoints)
            
def calirabration(chessboard_size, threshold, file_name):
    objpoints = []
    imgpoints = []
    
    objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
    
    
    pic_num_list, error_num_list = read_file(file_name)
    img = cv2.imread('./Calibration/chessboard_calibration_data/thermal/pic'+str(pic_num_list[0])+'.jpg')
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    image_size = gray.shape[::-1]
    
    # 閾値以下の写真と再投影誤差を格納するリスト
    threshold_pics = []
    threshold_errors = []
    
    calibration_cnt = 0
    for i in range(len(pic_num_list)):
        if error_num_list[i] <= threshold:
            threshold_pics.append(pic_num_list[i])
            threshold_errors.append(error_num_list[i])
            npy_file = './Calibration/projection_imgpoints'+str(pic_num_list[i])+'.npy'
            objpoints.append(objp)
            corners = read_npy(npy_file)
            imgpoints.append(corners)
            calibration_cnt += 1
    
    
    print("\nカメラキャリブレーションを行っています")
    ret, mtx, dist, revcs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, image_size, None, None)
    print(f'\n内部パラメータ: \n{mtx}')
    print(f'\n歪み係数: \n{dist}')
    print(f'\nキャリブレーションカウント: \n{calibration_cnt}')
    projection_error = re_projection_error_and_save_file(threshold_pics, objpoints, imgpoints, revcs, tvecs, mtx, dist)
    print(f'\n平均再投影誤差: \n{projection_error}')
    
projection_txt = './Calibration/again2_re_projection_error_text.txt'

chessboard_size = (5, 5)
images = glob.glob('./Calibration/chessboard_calibration_data/thermal/*.jpg')
threshold = 0.30

calirabration(chessboard_size, threshold, projection_txt)