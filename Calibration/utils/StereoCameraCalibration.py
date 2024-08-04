"""
ステレオカメラのキャリブレーションを行うクラス
"""

import cv2
import numpy as np
from tqdm import tqdm    # ��り返し処理の進��を表示するためもの
import glob # ��り返し処理の進�
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class StereoCameraCalibration:
    def __init__(self, chessboard_size, mtx_rgb, dist_rgb, mtx_thermal, dist_thermal):
        """
        コンストラクタ

        Parameters
        ----------
        chessboard_size (tuple): チェスボードのサイズ (width, height)
        """
        self.chessboard_size = chessboard_size
        self.square_size = 42.5            # チェスボードの格子点の間隔(mm)
        self.objpoints = []                # 3Dオブジェクトのポイント
        self.imgpoints_rgb = []            # RGBカメラの2Dポイント
        self.imgpoints_thermal = []        # 赤外線カメラの2Dポイント
        self.mtx_rgb = mtx_rgb             # RGBカメラの内部パラメータ
        self.dist_rgb = dist_rgb           # RGBカメラの歪み係数
        self.mtx_thermal = mtx_thermal     # 赤外線カメラの内部パラメータ
        self.dist_thermal = dist_thermal   # 赤外線カメラの歪み係数
        
        objp = np.zeros((self.chessboard_size[0] * self.chessboard_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:self.chessboard_size[0], 0:self.chessboard_size[1]].T.reshape(-1, 2)
        objp *= self.square_size  # 格子点間隔を設定
        self.objp = objp

        self.corners_rgb = []             # RGBカメラのコーナーの点を格納するリスト       
        self.corners_thermal = []         # 赤外線カメラの点を格納するリスト

        self.R = []                       # RGBカメラと赤外線カメラの座標系間の回転行列
        self.T = []                       # RGBカメラと赤外線カメラの座標系間の並進ベクトル 

    def add_corners(self, rgb_img_path, corners_rgb_list, thermal_img_path, corners_thermal_list):
        """
        RGBカメラと赤外線カメラの画像において,コーナー検出を追加する
        """
        # カメラの読み込み
        rgb_img = cv2.imread(rgb_img_path)
        gray_rgb = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2GRAY)
        thermal_img = cv2.imread(thermal_img_path)
        gray_thermal = cv2.cvtColor(thermal_img, cv2.COLOR_BGR2GRAY)

        self.objpoints.append(self.objp)

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners_rgb = np.array(corners_rgb_list,dtype = 'float32').reshape(-1, 1, 2)
        corners_thermal = np.array(corners_thermal_list ,dtype = 'float32').reshape(-1, 1, 2)

        corners2_rgb = cv2.cornerSubPix(gray_rgb, corners_rgb, (11, 11), (-1,-1), criteria)
        corners2_thermal = cv2.cornerSubPix(gray_thermal, corners_thermal, (11, 11), (-1,-1), criteria)
        self.imgpoints_rgb.append(corners2_rgb)
        self.imgpoints_thermal.append(corners2_thermal)
        self.corners_rgb = corners2_rgb
        self.corners_thermal = corners2_thermal
    
    def stereo_calibration(self):
        """
        ステレオカメラのキャリブレーション

        Parameters
        ----------
        gray_rgb : RGBカメラのグレー画像

        """
        flags = cv2.CALIB_FIX_INTRINSIC
        criteria_stereo = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6)
        retval, thermalMatrix, distCoeffs_tehrmal, rgbMatrix, distCoeffs_thermal, R, T, E, F = cv2.stereoCalibrate(
        self.objpoints, self.imgpoints_thermal,  self.imgpoints_rgb, self.mtx_thermal, self.dist_thermal, self.mtx_rgb, self.dist_rgb, (640, 512), criteria=criteria_stereo, flags=flags
        )
        self.R = R
        self.T = T
        print("回転行列 R:", R)
        print("並進ベクトル T:", T)
    
    def plot_cameras(self):
        """
        カメラの関係をプロットする
        """
        # 赤外線カメラは原点におく
        thermal_position = np.array([0, 0, 0])

        # RGBカメラの位置を計算
        rgb_position = -np.dot(self.R.T, self.T).flatten()

        # プロット
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # カメラの位置をプロット
        ax.scatter(rgb_position[0], rgb_position[1], rgb_position[2], color='r', marker='o', label = 'RGB Camera')
        ax.scatter(thermal_position[0], thermal_position[1], thermal_position[2], color='b', marker='o', label = 'Thermal Camera')

        # ラベル
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.legend()

        # 原点からカメラまで線を引く
        ax.plot([0, rgb_position[0]], [0, rgb_position[1]], [0, rgb_position[2]], color='g')

        print("RGB Camera x:"+str(rgb_position[0])+ " y:" + str(rgb_position[1])+ " z:"+str(rgb_position[2]))

        plt.show()
    
    def plot_cameras_pos(self):
        thermal_center = np.array([0, 0, 0])
        rgb_center = self.T

        print("赤外線カメラの位置:", thermal_center)
        print("RGBカメラの位置:", rgb_center)

        thermal_axes = np.eye(3)
        rgb_axes = self.R @ thermal_axes

        print("赤外線カメラの向き:")
        print(thermal_axes)
        print("RGBカメラの向き:")
        print(rgb_axes)

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # カメラの位置をプロット
        ax.scatter(thermal_center[0], thermal_center[1], thermal_center[2], color='r', label="Thermal Camera")
        ax.scatter(rgb_center[0], rgb_center[1], rgb_center[2], color='b', label="RGB Camera")

        # カメラの向きをプロット
        def plot_axes(ax, origin, axes, color):
            for i in range(3):
                ax.quiver(origin[0], origin[1], origin[2], axes[0, i], axes[1, i], axes[2, i], color=color)
            
        plot_axes(ax, thermal_center, thermal_axes, 'r')
        plot_axes(ax, rgb_center, rgb_axes, 'b')

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.legend()
        plt.show()

