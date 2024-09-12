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
        self.click_nearest_point = [] # クリックしたところから一番近い円の中心を入れる配列
        self.click_count = 0 # クリックされた回数
        cv2.namedWindow('Ellipse Finder')
        cv2.namedWindow('Parameters')
        # トラックバーを作成
        cv2.createTrackbar('Threshold', 'Parameters', self.threshold, self.max_value, self.update_display)
        cv2.createTrackbar('Min Axis Length', 'Parameters',  self.min_axis_length, 100, self.update_display)
        cv2.createTrackbar('Max Axis Length', 'Parameters', self.max_axis_length, 200, self.update_display)
        cv2.setMouseCallback('Ellipse Finder', self.on_mouse_click)
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
                    #print(f'x:{center[0]}, y:{center[1]}')
                    self.point_list.append(center) # y座標も追加
                    cv2.ellipse(contour_image, ellipse, (0, 255, 0), 2)  # 楕円を描画
                    cv2.circle(contour_image, center, 5, (0, 0, 255), -1)  # 中心を描画
            
        cv2.imshow('Ellipse Finder', contour_image)
        # y座標でソート
        self.point_list = sorted(self.point_list, key=lambda coord: coord[1])
        #print("----------sorted-----------")
        #for point in self.point_list:
        #    x, y = point
        #    print(f'x:{x}, y:{y}')
    
    def get_point_liust(self):
        return self.point_list
    
    def on_mouse_click(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            closest_center = self.find_closest_center(x, y)
            if closest_center:
                print(f'Closest center to ({x}, {y}): {closest_center}')
                if not self.click_check(x, y):
                    # クリックしたとこ座標から一番近い円の中心を記録
                    self.click_nearest_point.append(closest_center[0])
                    self.click_nearest_point.append(closest_center[1])
                    print(self.click_nearest_point)
                    print(self.click_check(x, y))
                    self.click_count += 1
                    print(f"クリックされた回数: {self.click_count}")
                else:
                    print("[Error] 同じ座標がクリックされています")

    def click_check(self, center_x, center_y):
        if not self.click_nearest_point:
            return False
        else:
            size = len(self.click_nearest_point) // 2  # 配列の要素数を2で割った商がクリックされた回数
            # 記録��みのクリックしたとこ��との距��を比��して一番近い��の中心を返す
            # 同じ座標が記録されていたらFalseを返す
            # ループで記録��みのクリックしたとこ��との距��を比��し、一番近い��の中心を返す
        for i in range(0, size):
            if self.click_nearest_point[i*2] == center_x and self.click_nearest_point[i*2+1] == center_y:
                return True
        return False
    
    def get_click_nearest_point(self):
        return self.click_nearest_point
    
    def find_closest_center(self, x, y):
        if not self.point_list:
            return None
        closest_center = min(self.point_list, key=lambda point: (point[0] - x)**2 + (point[1] - y)**2)
        return closest_center
    
    def run(self):
        while True:
            if cv2.waitKey(1) & 0xFF == 9:  # 'Tab'キーを押すと終了
                cv2.destroyAllWindows()
                return False
            if cv2.waitKey(1) & 0xFF == 103:  # 'g'キーを押すとclick_nearest_pointを取得 
                cv2.destroyAllWindows() 
                return self.get_click_nearest_point()
        cv2.destroyAllWindows()




