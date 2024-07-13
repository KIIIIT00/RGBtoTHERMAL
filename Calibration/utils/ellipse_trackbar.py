"""
楕円検出のトラックバーを作成するクラス
"""

import cv2
import numpy as np

class EllipseFinder():
    
    def __init__(self, image_path):
        self.image = cv2.imread(image_path) #画像を読み込む
        self.image = cv2.bitwise_not(self.image)
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.threshold = 93 # 初期閾値
        self.min_axis_length = 35 # 最小軸長
        self.max_axis_length = 80 # 最大軸長
        self.max_value = 255 # 最大値
        self.point_list = [] # 円の中心を入れる配列
        cv2.namedWindow('Parameters')
        # トラックバーを作成
        cv2.createTrackbar('Threshold', 'Parameters', self.threshold, self.max_value, self.update_display)
        cv2.createTrackbar('Min Axis Length', 'Parameters',  self.min_axis_length, 100, self.update_display)
        cv2.createTrackbar('Max Axis Length', 'Parameters', self.max_axis_length, 200, self.update_display)

        self.update_display(None) # 初期状態での表示


    
    def update_display(self, _):
        # トラックバーの値を取得
        threshold = cv2.getTrackbarPos('Threshold', 'Parameters')
        min_axis_length = cv2.getTrackbarPos('Min Axis Length', 'Parameters')
        max_axis_length = cv2.getTrackbarPos('Max Axis Length', 'Parameters')

        _, binary_image = cv2.threshold(self.gray, threshold, self.max_value, cv2.THRESH_BINARY)
        contours, _ =  cv2.findContours(binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contour_image = cv2.cvtColor(self.gray, cv2.COLOR_GRAY2BGR)

        for contour in contours:
            if len(contour) >= 5:  # 楕円フィッティングには最低5つの点が必要
                ellipse = cv2.fitEllipse(contour)
                (center, axes, angle) = ellipse
                (major_axis, minor_axis) = (max(axes), min(axes))  # 長軸と短軸

                # 楕円の大きさを制限
            if min_axis_length <= major_axis <= max_axis_length and min_axis_length <= minor_axis <= max_axis_length:
                center = (int(center[0]), int(center[1]))  # 楕円の中心
                print(f'x:{center[0]}, y:{center[1]}')
                self.point_list.append([int(center[0]), int(center[1])])
                cv2.ellipse(contour_image, ellipse, (0, 255, 0), 2)  # 楕円を描画
                cv2.circle(contour_image, center, 5, (0, 0, 255), -1)  # 中心を描画
            
        cv2.imshow('Ellipse Finder', contour_image)
        # y座標でソート
        self.point_list = sorted(self.point_list, key=lambda coord: coord[1])
        print("----------sorted-----------")
        for point in self.point_list:
            x, y = point
            print(f'x:{x}, y:{y}')
    
    def run(self):
        while True:
            if cv2.waitKey(1) & 0xFF == 27:  # 'ESC'キーを押すと終了
                break
        cv2.destroyAllWindows()

if __name__ == "__main__":
    image_path = './Calibration/chessboard_calibration_data/thermal/pic62.jpg'
    finder = EllipseFinder(image_path)
    finder.run()


