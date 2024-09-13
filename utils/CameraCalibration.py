"""
カメラキャリブレーションを行うクラス
"""

import cv2
import numpy as np
from tqdm import tqdm   
import glob # 繰り返し処理の進捗を表示するためもの
import re

class CameraCalibration:
    def __init__(self, chessboard_size=(6, 6)):
        self.chessboard_size = chessboard_size
        self.objpoints = []          # 三次元座標(ワールド座標)を格納する配列
        self.imgpoints = []          # 二次元座標(画像座標)を格納する配列

        objp = np.zeros((self.chessboard_size[0] * self.chessboard_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:self.chessboard_size[0], 0:self.chessboard_size[1]].T.reshape(-1, 2)
        self.objp = objp
    
    def rgb_re_projection_errors(self, pic_nums, filename):
        """
        RGBカメラの再投影誤差を算出する

        Parameters
        ----------
        pic_nums : list
            RGB画像の番号を格納しているリスト
        filename : str
            RGB画像の番号と再投影誤差を格納するテキストのファイルパス
        """
        mean_error = 0
        error_list = []
        for i in range(len(self.objpoints)):
            imgpoints2, _ = cv2.projectPoints(self.objpoints[i], self.rvecs[i], self.tvecs[i], self.mtx, self.dist)
            error = cv2.norm(self.imgpoints[i], imgpoints2, cv2.NORM_L2) / len(self.imgpoints[i])
            error_list.append(error)
            print("picnum", pic_nums[i])
            print(":", error)
            mean_error += error

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for i, error in enumerate(error_list):
                    f.write(f"picnum: {pic_nums[i]}, error: {error}\n")
            print(f"再投影誤差を記録しました: {filename}")
        except Exception as e:
            print(f"再投影誤差記録に失敗しました: {e}")
        print("projetion_error", mean_error/ len(self.objpoints))
    
    def get_data_from_text(self, text_path, threshold):
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

    def rgb_re_calibration(self, images_path, text_path, threshold, save_text):
        """
        再投影誤差の値を考慮したカメラキャリブレーションを行う

        Parameters
        ----------
        images_path : str
            画像のファイルパス
        text_path : str
            画像の番号と再投影誤差が格納されているファイルパス
        threshold : float
            再投影誤差の閾値
        save_text : str
                再投影誤差を保存するテキストファイルパス
        """

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        # 画像パスの取得
        images = glob.glob(images_path)
        pic_nums, errors = self.get_data_from_text(text_path, threshold)
        calibration_count = 0
        print(pic_nums)

        print("全ての画像の交点の画像座標を求めています")
        for filepath in tqdm(images):       # ※tqdmは繰り返し処理の進捗を表示するためのもの
            #print(filepath)
            pic_num = re.findall(r'\d+', filepath)[0]
            pic_num = int(pic_num)
            #print("pic_num", int(pic_num))
            if pic_num in pic_nums: # pic_numsにpic_numが含まれているとき
                print('contatins')
                img = cv2.imread(filepath)                      # 変数filepathが持っている名前の画像を開く
                gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)     # 白黒画像にする
                #print(gray.shape[::-1])
                # Find the chess board corners
                ret, corners = cv2.findChessboardCorners(gray, self.chessboard_size, cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE)
            
                # If found, add object points, image points (after refining them)
                if ret:
                    self.objpoints.append(self.objp)
                    corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                    self.imgpoints.append(corners2)
                    calibration_count += 1

        print("\nカメラキャリブレーションを行っています")
        print(f"\n{calibration_count}枚の画像でカメラキャリブレーションを行いました")

        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(self.objpoints, self.imgpoints, gray.shape[::-1],None,None)    # ここでカメラキャリブレーションを行っている
        self.ret = ret
        self.mtx = mtx
        self.dist = dist
        self.rvecs = rvecs
        self.tvecs = tvecs
        print(f'\n内部パラメータ: \n{mtx}')
        print(f'\n歪み係数: \n{dist}')

        # 再投影誤差を記録する
        self.rgb_re_projection_errors(pic_nums, save_text)

    def rgb_calibration(self, images_path, text_file_path):
        """
        RGBカメラのカメラキャリブレーションをする

        Parameters
        ----------
        images_path : str
            画像のファイルパス
        text_file_path : str
            再投影誤差を保存するファイルパス
        """
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        # 画像パスの取得
        images = glob.glob(images_path)
        # 画像の番号を格納するリスト
        rgb_pic_nums = []

        print("全ての画像の交点の画像座標を求めています")
        for filepath in tqdm(images):       # tqdmは繰り返し処理の進捗を表示するためのもの
            print(filepath)
            pic_num = re.findall(r'\d+', filepath)[0]
            print("pic_num", int(pic_num))
            rgb_pic_nums.append(int(pic_num)) # 写真の番号を格納
            img = cv2.imread(filepath)                      # 変数filepathが持っている名前の画像を開く
            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)     # 白黒画像にする

            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(gray, self.chessboard_size, cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE)
            
            # If found, add object points, image points (after refining them)
            if ret:
                self.objpoints.append(self.objp)
                corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                self.imgpoints.append(corners2)
        print("\nカメラキャリブレーションを行っています")
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(self.objpoints, self.imgpoints, gray.shape[::-1],None,None)    # ここでカメラキャリブレーションを行っている
        self.ret = ret
        self.mtx = mtx
        self.dist = dist
        self.rvecs = rvecs
        self.tvecs = tvecs
        print(f'\n内部パラメータ: \n{mtx}')
        print(f'\n歪み係数: \n{dist}')
        #print(f'\n外部パラメータの回転行列:\n{rvecs}')
        #print(f'\n外部パラメータの並進ベクトル:\n{tvecs}')

        # 再投影誤差を記録する
        self.rgb_re_projection_errors(rgb_pic_nums, text_file_path)


    def add_image(self, image_path):
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, self.chessboard_size, None)
        
        # If found, add object points, image points (after refining them)
        if ret:
            self.objpoints.append(self.objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            self.imgpoints.append(corners2)
            return True
        return False
    
    def add_corners(self, image_path, corners_list):
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        self.objpoints.append(self.objp)
        corners = np.array(corners_list, dtype='float32').reshape(-1, 1, 2)
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        self.imgpoints.append(corners2)
        return True
    
    def calibrate(self, image_size):
        print("\nカメラキャリブレーションを行っています")
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(self.objpoints, self.imgpoints, image_size, None, None)
        self.ret = ret
        self.mtx = mtx
        self.dist = dist
        self.revcs = rvecs
        self.tvecs = tvecs
        return ret, mtx, dist, rvecs, tvecs
    
    def undistort(self, img, mtx, dist):
        h, w = img.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
        dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
        x, y, w, h = roi
        dst = dst[y:y+h, x:x+w]
        return dst
    
    
    def re_projection_error_and_save_file(self, pic_list):
        """
        再投影誤差を算出し，テキストファイルに書き込みをする
        """
        mean_error = 0
        error_list = []
        for i in range(len(self.objpoints)):
            imgpoints2, _ = cv2.projectPoints(self.objpoints[i], self.revcs[i], self.tvecs[i], self.mtx, self.dist)
            error = cv2.norm(self.imgpoints[i], imgpoints2, cv2.NORM_L2) / len(self.imgpoints[i])
            error_list.append(error)
            print("picnum", pic_list[i])
            print(":", error)
            mean_error += error
        
        filename = './Calibration/again2_re_projection_error_text.txt'
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for i, error in enumerate(error_list):
                    f.write(f"picnum: {pic_list[i]}, error: {error}\n")
            print(f"再投影誤差を記録しました: {filename}")
        except Exception as e:
            print(f"再投影誤差記録に失敗しました: {e}")
        
        # imagpointsの保存
        for num, ererror in enumerate(error_list):
            numpy_filename = './Calibration/projection_imgpoints'+str(pic_list[num])+'.npy'
            np.save(numpy_filename,self.imgpoints[num])
        return mean_error / len(self.objpoints)

    


