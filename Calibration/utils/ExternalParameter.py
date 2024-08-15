"""
外部パラメータを算出するクラス
"""

import numpy as np
import cv2

class ExternalParameterCalculator:
    def __init__(self, chessboard_size, mtx, dist):
        self.chessboard_size = chessboard_size
        self.square_size = 42.5
        self.mtx = mtx
        self.dist = dist
        self.objpoints = []
        self.imgpoints = []

        objp = np.zeros((self.chessboard_size[0] * self.chessboard_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:self.chessboard_size[0], 0:self.chessboard_size[1]].T.reshape(-1, 2)
        objp *= self.square_size
        self.objp = objp
        self.corners2 = []
        print("mtx:", self.mtx)
        print("dist:", self.dist)
        print("objpoints:", self.objp)


    def add_corners(self, image_path, corners_list):
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        self.objpoints.append(self.objp)
        corners = np.array(corners_list, dtype='float32').reshape(-1, 1, 2)
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        self.imgpoints.append(corners2)
        self.corners2 = corners2
        print(self.corners2)
        return corners2
    
    def get_projection_errors(self):
        """
        再投影誤差を計算する
        
        Returns
        -------
        procjection_error : float
            再投影誤差
        """
        print(len(self.objpoints))
        imgpoints2, _ = cv2.projectPoints(self.objp, self.rvecs, self.tvecs, self.mtx, self.dist)
        self.imgpoints2 = imgpoints2
        projection_error = cv2.norm(self.corners2, imgpoints2, cv2.NORM_L2) / len(self.imgpoints)
        return projection_error
    
    def re_draw(self, img):
        """
        再投影されたポイントと元のコーナーを画像に描画して確認
        """
        for i in range(len(self.corners2)):
            # 検出されたコーナーを緑で描画
            corner = tuple(self.corners2[i].ravel().astype(int))
            cv2.circle(img, corner, 5, (0, 255, 0), -1)  # 緑色
            
            # 再投影されたポイントを赤で描画
            imgpoint = tuple(self.imgpoints2[i].ravel().astype(int))
            cv2.circle(img, imgpoint, 5, (0, 0, 255), -1)  # 赤色
        
        cv2.imshow('Detected Corners (Green) and Reprojected Points (Red)', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    def calculate_external_parameters(self, corners2):
        print("objpoints:", self.objp)
        print("object points shape:", self.objp.shape)
        print("corners2:", corners2)
        print("corners2 shape:", corners2.shape)
        print("mtx:", self.mtx)
        print("dist:", self.dist)
        print("Calculating external parameters...")
        ret3, rvecs, tvecs = cv2.solvePnP(self.objp, corners2, self.mtx, self.dist)
        self.rvecs = rvecs
        self.tvecs = tvecs
        return ret3, rvecs, tvecs
    
    def write_to_txt(self, filename, rvecs, tvecs):
        with open(filename, 'w') as f:
            f.write("Camera Matrix:\n")
            np.savetxt(f, self.mtx, delimiter=',')
            f.write("\nDistortion Coefficients:\n")
            np.savetxt(f, self.dist, delimiter=',')
            f.write("\nRotation Vectors:\n")
            np.savetxt(f, rvecs, delimiter=',')
            f.write("\nTranslation Vectors:\n")
            np.savetxt(f, tvecs, delimiter=',')
    
    def image_to_camera(self, image_point):
        """
        画像座標をカメラ座標に変換する。

        Parameters:
        - image_point: 画像座標系における2次元点 (u, v)。
        - camera_matrix: カメラ行列 (3x3)

        Returns:
        - camera_point: カメラ座標系における3次元点 (x, y, z)
        """
        fx = self.mtx[0, 0]
        fy = self.mtx[1, 1]
        cx = self.mtx[0, 2]
        cy = self.mtx[1, 2]
    
        u, v = image_point
        z = 1  # 仮のz値
        x = (u - cx) * z / fx
        y = (v - cy) * z / fy
        return np.array([x, y, z])

    def camera_to_world(self, camera_point, rotation_matrix, translation_vector):
        """
        カメラ座標の点をワールド座標に変換する
        """
        camera_point_homogeneous = np.append(camera_point, 1)

        # 外部パラメータ行列を作成
        extrinsic_matrix = np.hstack((rotation_matrix, translation_vector))

        # カメラ座標からワールド座標への変換を計算
        world_point_homogeneous = rotation_matrix @ camera_point + translation_vector.ravel()

        # 同次座標を通常の3次元座標に変換
        world_point = world_point_homogeneous[:3] / world_point_homogeneous[3]

        return world_point
    
    def undistort_points(self, image_point):
        """
        画像座標をカメラ座標に変換する
        """
        print("image_point:", image_point.shape)
        image_point = image_point.T.reshape(1, 1, 2)
        print("image_point reshape:", image_point)
        normalized_image_point = cv2.undistortPoints(image_point, self.mtx, self.dist)
        print("normalized_image_point:", normalized_image_point.shape)
        normalized_image_point = np.append(normalized_image_point[0, 0], 1)
        return normalized_image_point

    def camerapoint_to_worldpoint(self, camera_point, rotation_matrix, translation_vector):
        """
        カメラ座標をワールド座標に変換する
        """
        R, _ = cv2.Rodrigues(rotation_matrix)
        t = translation_vector
        world_point = np.dot(np.linalg.inv(R), camera_point - t)
        return world_point
    
    def world_in_camerapoint(self, image_point, rotation_matrix, translation_vector):
        """
        チェスボードの原点に対してワールド座標におけるカメラの原点と視点方向を求める

        """
        undistorted_ponts_homogeneous = self.undistort_points(image_point)
        R, _ = cv2.Rodrigues(rotation_matrix)
        t = translation_vector
        world_point = np.dot(np.linalg.inv(R), undistorted_ponts_homogeneous - t)
        # カメラのワールド座標系における位置
        camera_position = -np.dot(np.linalg.inv(R), t)

        # カメラの視点方向を計算
        camera_direction = np.dot(np.linalg.inv(R), np.array([[0], [0], [1]]))
        return camera_position, camera_direction
    
    
    
