import numpy as np
import cv2

class TakePics:
    def __init__(self, rgb_id, thermal_id ,folder_path, count):
        self.rgb_id = rgb_id
        self.thermal_id = thermal_id
        self.folder_path = folder_path
        self.rgb_cap = cv2.VideoCapture(self.rgb_id)
        self.thermal_cap = cv2.VideoCapture(self.thermal_id)
        self.count = count

        # カメラの解像度を設定
        self.rgb_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.rgb_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 512)
        self.thermal_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.thermal_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 512)

        