"""
カメラキャリブレーションを行うクラス
"""

import cv2
import numpy as np
from tqdm import tqdm   
import glob # ��り返し処理の進��を表示するためもの

class CameraCalibration:
    def __init__(self, chessboard_size=(6, 6)):
        self.chessboard_size = chessboard_size
        self.objpoints = []          # �������� ��������
        self.imgpoints = []          # �������� ��������

        objp = np.zeros((self.chessboard_size[0] * self.chessboard_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:self.chessboard_size[0], 0:self.chessboard_size[1]].T.reshape(-1, 2)
        self.objp = objp
        

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
        return ret, mtx, dist, rvecs, tvecs
    
    def undistort(self, img, mtx, dist):
        h, w = img.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
        dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
        x, y, w, h = roi
        dst = dst[y:y+h, x:x+w]
        return dst

    