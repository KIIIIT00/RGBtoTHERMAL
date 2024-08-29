"""
RGB画像と赤外線画像で特徴点マッチングをする
"""
# インポート
import numpy as np
import cv2
from utils.DynamixelEX106 import DynamixelEX106
from utils.SerialSetting import SerialSetting
import os
import time

class FeatureDetection():
    def __init__(self, rgb_image_path, thermal_image_path, rgb_corners_npy, thermal_corners_npy):
        self.rgb_image_path = rgb_image_path
        self.thermal_image_path = thermal_image_path
        self.rgb_corners_npy = rgb_corners_npy
        self.thermal_corners_npy = thermal_corners_npy
    
    def imread(self):
        """
        画像の読み込み
        """
        self.rgb_image = cv2.imread(self.rgb_image_path)
        self.thermal_image = cv2.imread(self.thermal_image_path)
    
    def get_corners_bynpy(self):
        """
        npyファイルからコーナーを取得する
        """
        thermal_array = np.load(self.thermal_corners_npy)
        thermal_float32 = thermal_array.astype(np.float32)
        rgb_array = np.load(self.rgb_corners_npy)
        rgb_float32 = rgb_array.astype(np.float32)
        self.corners_thermal = thermal_float32[:25]
        self.corners_rgb = rgb_float32[:25]
    
    def image_imread(self):
        """
        RGB画像と赤外線画像を読み込む
        """
        self.rgb_image = cv2.imread(self.rgb_image_path)
        self.thermal_image = cv2.imread(self.thermal_image_path, cv2.IMREAD_GRAYSCALE)
        gray_rgb_image = cv2.cvtColor(self.rgb_image, cv2.COLOR_BGR2GRAY)
        cv2.imshow("GRAY RGB", gray_rgb_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        cv2.imshow("GRAY THERMAL", self.thermal_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        # ヒストグラム平坦化
        self.equalized_rgb_image = cv2.equalizeHist(gray_rgb_image)
        self.equalized_thermal_image = cv2.equalizeHist(self.thermal_image)
        
    def feature_matching_sift(self):
        """
        SIFTを使用して特徴点の検出をする
        """ 
        self.image_imread()
        sift = cv2.SIFT_create()
        kp_rgb, des_rgb = sift.detectAndCompute(self.equalized_rgb_image, None)
        kp_thermal, des_thermal = sift.detectAndCompute(self.equalized_thermal_image, None)
        
        cv2.imshow("DETECT RGB", des_rgb)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        cv2.imshow("DETECT THERMAL", des_thermal)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        # 特徴点のマッチング
        bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
        matches = bf.match(des_rgb, des_thermal)
        
        # 特徴点の距離順に並べる
        matches = sorted(matches, key=lambda x: x.distance)
        
        # 10. マッチングされた特徴点を取得
        src_pts = np.float32([kp_rgb[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp_thermal[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
        
        # 11. ホモグラフィー行列を計算
        H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        height, width = self.thermal_image.shape
        aligned_rgb_image = cv2.warpPerspective(self.rgb_image, H, (width, height))
        
        self.side_by_side = np.hstack((aligned_rgb_image, cv2.cvtColor(self.thermal_image, cv2.COLOR_GRAY2BGR)))
        
    def feature_matching(self):
        """
        特徴点マッチングをする
        """
        self.imread()
        self.get_corners_bynpy()
        
        # 5. ホモグラフィー行列を計算
        H, status = cv2.findHomography(self.corners_rgb, self.corners_thermal, cv2.RANSAC, 5.0)

        # 6. RGB画像を赤外線画像にアライメント      
        height, width = self.thermal_image.shape[:2]
        aligned_rgb_image = cv2.warpPerspective(self.rgb_image, H, (width, height))
        resize_rgb_image = cv2.resize(self.rgb_image, dsize=(width, height))
        cv2.imshow("Resize Image", resize_rgb_image)

        # 7. RGB画像と赤外線画像を横並びに結合
        side_by_side = np.hstack((aligned_rgb_image, self.thermal_image))

        self.side_by_side = side_by_side

        # 結果の表示（オプション）
        cv2.imshow('Aligned RGB Image', aligned_rgb_image)
        cv2.imshow('Side by Side', side_by_side)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    def save_side_by_side(self, OUTPUT, pic_cnt):
        """
        横並びの写真を保存する
        """
        output_file = os.path.join(OUTPUT, 'side_by_side' + str(pic_cnt) + '.jpg')
        cv2.imwrite(output_file, self.side_by_side)

if __name__ == "__main__":
    image_count = 34
    thermal_img_path = './Calibration/FOV/THERMAL/thermal_'+str(image_count) + '.jpg'
    rgb_img_path = './Calibration/FOV/RGB/rgb_'+str(image_count)+'.jpg'
    thermal_imgpoints2_npy = './Calibration/FOV/external/thermal_imgpoints2_'+str(image_count) + '.npy'
    rgb_imgpoints2_npy = './Calibration/FOV/external/rgb_imgpoints2_'+str(image_count) + '.npy'
    
    OUTPUT = './Calibration/FOV/Feature/'
    
    feature_detection = FeatureDetection(rgb_img_path, thermal_img_path, rgb_imgpoints2_npy, thermal_imgpoints2_npy)
    feature_detection.feature_matching()
    #feature_detection.feature_matching_sift()
    feature_detection.save_side_by_side(OUTPUT, image_count)