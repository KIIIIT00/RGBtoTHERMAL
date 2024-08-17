"""
クリックしてキャリブレーションをし，検出したコーナーや再投影誤差などを保存する
"""
import cv2
import numpy as np
import glob
import re
from utils.EllipseFinder import EllipseFinder
class SaveCameraCalibration():
    def __init__(self):
        """
        コンストラクタ
        """
        self.chessboard_size = (5, 5)
        self.objpoints = [] # ワールド座標を格納する配列
        self.imgpoints = [] # 二次元座標を格納する配列
        
        objp = np.zeros((self.chessboard_size[0] * self.chessboard_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:self.chessboard_size[0], 0:self.chessboard_size[1]].T.reshape(-1, 2)
        self.objp = objp
        
    def add_corners(self, image_path, corners_list):
        """
        コーナー検出をする
        """
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        self.objpoints.append(self.objp)
        corners = np.array(corners_list, dtype='float32').reshape(-1, 1, 2)
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        self.imgpoints.append(corners2)
        return corners2
    
    def calibrate(self, image_size = (640, 480)):
        """
        カメラキャリブレーションを行う
        """
        print("\nカメラキャリブレーションを行っています")
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(self.objpoints, self.imgpoints, image_size, None, None)
        self.ret = ret
        self.mtx = mtx
        self.dist = dist
        self.revcs = rvecs
        self.tvecs = tvecs
        return ret, mtx, dist, rvecs, tvecs
    
    def save_imagepoints_npy(self, file_path, corners2):
        """
        二次元座標をnpyファイルに保存する
        """
        np.save(file_path, corners2)
    
    def projection_error(self):
        """
        再投影誤差を計算する
        """
        mean_error = 0
        for i in range(len(self.objpoints)):
            imgpoints2, _ = cv2.projectPoints(self.objpoints[i], self.revcs[i], self.tvecs[i], self.mtx, self.dist)
            error = cv2.norm(self.imgpoints[i], imgpoints2, cv2.NORM_L2) / len(self.imgpoints[i])
            print("picnum", pic_list[i])
            print(":", error)
            mean_error += error
        return mean_error / len(self.objpoints)

if __name__ == "__main__":
    # 画像のファイルパス
    images = glob.glob('./Calibration/chessboard_calibration_data/thermal/*.jpg')
    save_folder = './Calibration/chessboard_calibration_data/thermal_data/'
    calibration = SaveCameraCalibration()
    calibration_cnt = 0
    pic_list = [] # 写真の番号を格納するリスト
    for fname in images:
        print(f"-----start add corners-----\n")
        finder = EllipseFinder(fname)
        corners = finder.run()
        if corners is not False:
            # 正規表現で数字を抽出
            numbers = re.findall(r'\d+', fname)
            pic_num = numbers[0]
            pic_list.append(pic_num)
            # コーナー検出
            corners2 = calibration.add_corners(fname, corners)
            save_npy = f'./Calibration/chessboard_calibration_data/thermal_data/imagpoints_{str(pic_num)}.npy'
            # コーナーをnpyファイルに保存する
            calibration.save_imagepoints_npy(save_npy, corners2)
            # キャリブレーションカウントを加算
            calibration_cnt += 1
        
        print(f'-----end add corners-----\n')
    
    image_size = (640, 480)
    ret, mtx, dist, rvecs, tvecs = calibration.calibrate(image_size)
    print("キャリブレーション結果:")
    print("リプロジェクションエラー:", ret)
    print("カメラ行列:\n", mtx)
    print("歪み係数:\n", dist)
    
    projection_error = calibration.projection_error()
    
    
    