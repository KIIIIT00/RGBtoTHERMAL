"""
再投影誤差を考慮して外部パラメータを求める
"""
import numpy as np
import cv2
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class ProjectionExternalParameter():
    def __init__(self, thermal_npy, rgb_npy):
        self.chessboard_size = (5, 5) # チェスボードの格子点
        self.square_size = 42.5 # チェスボードの格子点の間隔[mm]
        self.thermal_objpoints = [] # 赤外線カメラの3次元点格納リスト
        self.thermal_imgpoints = [] # 赤外線カメラの画像座標格納リスト
        self.rgb_objpoints = [] # RGBカメラの3次元点格点格納リスト
        self.rgb_imgpoints = [] # RGBカメラの画像座標格納リスト
        objp = np.zeros((self.chessboard_size[0] * self.chessboard_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:self.chessboard_size[0], 0:self.chessboard_size[1]].T.reshape(-1, 2)
        objp *= self.square_size
        self.thermal_objp = objp
        self.rgb_objp = objp
        
        # 赤外線カメラの内部パラメータ
        self.thermal_mtx = np.array([773.41392054, 0, 329.198468,
                        0, 776.32513558, 208.53439152,
                        0 ,0 ,1]).reshape(3, 3)
        self.thermal_dist = np.array([1.67262996e-01, -2.94477097e+00, -2.30689758e-02, -1.33138573e-03, 1.02082943e+01])
        
        # RGBカメラの内部パラメータ
        self.rgb_mtx = np.array([621.80090236, 0, 309.61717191, 0, 624.22815912, 234.27475688, 0, 0, 1]).reshape(3,3)
        self.rgb_dist = np.array([ 0.1311874, -0.21356334, -0.00798234,  -0.00648277, 0.10214072])
        
        # npyファイル
        self.thermal_npy = thermal_npy
        self.rgb_npy = rgb_npy
        
    def read_npy(self):
        """
        npyファイルをロードし，imgpointsに格納する
        """
        thermal_array = np.load(self.thermal_npy)
        thermal_float32 = thermal_array.astype(np.float32)
        rgb_array = np.load(self.rgb_npy)
        rgb_float32 = rgb_array.astype(np.float32)
        print(thermal_array)
        self.thermal_imgpoints.append(thermal_float32)
        self.rgb_imgpoints.append(rgb_float32)
    
    def calculate_external_parameters(self, objp, imgpoints, mtx, dist):
        """
        カメラの外部パラメータを求める
        """
        ret, rvecs, tvecs = cv2.solvePnP(objp, imgpoints[0], mtx, dist)
        return ret, rvecs, tvecs
        
        
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
    
    def undistort_points(self, image_point, mtx, dist):
        """
        画像座標をカメラ座標に変換する
        """
        print("image_point:", image_point.shape)
        image_point = image_point.T.reshape(1, 1, 2)
        print("image_point reshape:", image_point)
        normalized_image_point = cv2.undistortPoints(image_point, mtx, dist)
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
    
    def world_in_camerapoint(self, rotation_matrix, translation_vector):
        """
        チェスボードの原点に対してワールド座標におけるカメラの原点と視点方向を求める

        """
        R, _ = cv2.Rodrigues(rotation_matrix)
        t = translation_vector
        # カメラのワールド座標系における位置
        camera_position = -np.dot(np.linalg.inv(R), t)

        # カメラの視点方向を計算
        camera_direction = np.dot(np.linalg.inv(R), np.array([[0], [0], [1]]))
        return camera_position, camera_direction
    
    def get_projection_errors(self, objp, rvecs, tvecs, mtx, dist, imgpoints):
        """
        再投影誤差を求める
        """
        imgpoints2, _ = cv2.projectPoints(objp, rvecs, tvecs, mtx, dist)
        projection_error = cv2.norm(imgpoints[0], imgpoints2, cv2.NORM_L2) / len(imgpoints[0])
        return projection_error, imgpoints2
    
    def projection_corners_draw(self, imgpoints, imgpoints2, img):
        """
        再投影されたポイントと元のコーナーを画像に描画する
        """
        for i in range(len(imgpoints[0])):
            # 検出されたコーナーを緑で描画
            imgpoint = tuple(imgpoints[0][i].ravel().astype(int))
            cv2.circle(img, imgpoint, 5, (0, 255, 0), -1) # 緑色
            
            # 再投影されたポイントを赤で描画
            imgpoint2 = tuple(imgpoints2[i].ravel().astype(int))
            cv2.circle(img, imgpoint2, 5, (0, 0, 255), -1)  # 赤色
        
        cv2.imshow('Detected Corners (Green) and Reprojected Points (Red)', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    def plot_cameras_pos_direction(self, thermal_pos, rgb_pos, thermal_direction, rgb_direction):
        """
        赤外線カメラとRGBカメラの位置と視点方向をプロットする
        """
        # カメラの位置を表示
        print("Thermal Camera Position: x:{x}, y:{y}, z:{z}".format(x = thermal_pos[0], y = thermal_pos[1], z=thermal_pos[2]))
        print("RGB Camera Position: x:{x}, y:{y}, z:{z}".format(x =rgb_pos[0], y = rgb_pos[1], z = rgb_pos[2]))

        # カメラの視線方向を表示
        print("Thermal Camera Direction: x:{x}, y:{y}, z:{z}".format(x = thermal_direction[0], y = thermal_direction[1], z = thermal_direction[2]))
        print("RGB Camera Direction: x:{x}, y:{y}, z:{z}".format(x = rgb_direction[0], y = rgb_direction[1], z = rgb_direction[2]))
        
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        # カメラの位置をプロット
        # 赤外線カメラは，青色
        ax.scatter(thermal_pos[0], thermal_pos[1], thermal_pos[2], c='b', marker='x', label = 'Thermal Position')
        # RGBカメラは，赤色
        ax.scatter(rgb_pos[0], rgb_pos[1], rgb_pos[2], c='r', marker='o', label='RGB Position')

        # カメラの視線方向をプロット
        ax.quiver(thermal_pos[0], thermal_pos[1], thermal_pos[2], 
                  thermal_direction[0], thermal_direction[1], thermal_direction[2], 
                  length=5.0, color='b', label=' Thermal Direction')
        
        ax.quiver(rgb_pos[0], rgb_pos[1], rgb_pos[2], 
                  rgb_direction[0], rgb_direction[1], rgb_direction[2], 
                  length=5.0, color='r', label=' RGB Direction')
        
        # ラベルを設定
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.legend()
        
        # 表示
        plt.show()
        
    def run(self, thermal_img, rgb_img):
        # npyファイルをロード
        self.read_npy()
        
        # 外部パラメータを求める
        thermal_ret, thermal_rvecs, thermal_tvecs = self.calculate_external_parameters(self.thermal_objp, self.thermal_imgpoints, self.thermal_mtx, self.thermal_dist)
        rgb_ret, rgb_rvecs, rgb_tvecs = self.calculate_external_parameters(self.rgb_objp, self.rgb_imgpoints, self.rgb_mtx, self.rgb_dist)
        
        # カメラ座標系をワールド座標に変換する
        thermal_pos, thermal_direction = self.world_in_camerapoint(thermal_rvecs, thermal_tvecs)
        rgb_pos, rgb_direction = self.world_in_camerapoint(rgb_rvecs, rgb_tvecs)
        
        # 赤外線カメラとRGBカメラの位置と視点方向をプロット
        self.plot_cameras_pos_direction(thermal_pos, rgb_pos, thermal_direction, rgb_direction)
        
        # 再投影誤差を求める
        thermal_projection, thermal_imgpoints2 = self.get_projection_errors(self.thermal_objp, thermal_rvecs, thermal_tvecs, self.thermal_mtx, self.thermal_dist, self.thermal_imgpoints)
        rgb_projection, rgb_imgpoints2 = self.get_projection_errors(self.rgb_objp, rgb_rvecs, rgb_tvecs, self.rgb_mtx, self.rgb_dist, self.rgb_imgpoints)
        
        print(f"Thermal Projection:\n")
        print(f"{str(thermal_projection)} \n")
        print(f"RGB Projection:\n")
        print(f"{str(rgb_projection)} \n")
        
        # 再投影されたポイントと元のコーナーを画像に描画する
        self.projection_corners_draw(self.thermal_imgpoints, thermal_imgpoints2, thermal_img)
        self.projection_corners_draw(self.rgb_imgpoints, rgb_imgpoints2, rgb_img)

if __name__ == '__main__':
    image_count = 34  # FOVは，30か34がいいかも
    # 画像のパス
    # thermal_img_path = './Calibration/ExternalParameter_Chessboard/THERMAL/thermal_'+str(image_count) + '.jpg'
    # rgb_img_path = './Calibration/ExternalParameter_Chessboard/RGB/rgb_'+str(image_count)+'.jpg'
    thermal_img_path = './Calibration/FOV/THERMAL/thermal_'+str(image_count) + '.jpg'
    rgb_img_path = './Calibration/FOV/RGB/rgb_'+str(image_count)+'.jpg'
    thermal_img = cv2.imread(thermal_img_path)
    rgb_img = cv2.imread(rgb_img_path)
    # thermal_imgpoints2_npy = './Calibration/Calibration_result/external/thermal_imgpoints2_'+str(image_count) + '.npy'
    # thermal_corners_npy = './Calibration/Calibration_result/external/thermal_corners_'+str(image_count) + '.npy'
    # rgb_imgpoints2_npy = './Calibration/Calibration_result/external/rgb_imgpoints2_'+str(image_count) + '.npy'
    # rgb_corners_npy = './Calibration/Calibration_result/external/rgb_corners_'+str(image_count) + '.npy'
    thermal_imgpoints2_npy = './Calibration/FOV/external/thermal_imgpoints2_'+str(image_count) + '.npy'
    thermal_corners_npy = './Calibration/FOV/external/thermal_corners_'+str(image_count) + '.npy'
    rgb_imgpoints2_npy = './Calibration/FOV/external/rgb_imgpoints2_'+str(image_count) + '.npy'
    rgb_corners_npy = './Calibration/FOV/external/rgb_corners_'+str(image_count) + '.npy'
    external_para = ProjectionExternalParameter(thermal_imgpoints2_npy, rgb_imgpoints2_npy)
    #external_para = ProjectionExternalParameter(thermal_corners_npy, rgb_corners_npy)
    external_para.run(thermal_img, rgb_img)    