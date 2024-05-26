# -*- coding: utf-8 -*-
"""
Created on Mon May 20 12:19:54 2024

@author: Kawahara

参考:https://ito-room.com/python-filedialog/
    https://qiita.com/best_not_best/items/c9497ffb5240622ede01
    https://pystyle.info/opencv-feature-matching/#outline__4_1
    
"""

import cv2
import os
import tkinter as tk
import tkinter.filedialog
from PIL import Image,ImageTk,ImageOps

### 定数
WIDTH  = 640        # 幅
HEIGHT = 512        # 高さ


def tk_dialog():
    
    # ルートウィンドウ作成
    root = tk.Tk()
    
    # ルートウィンドウの非表示
    root.withdraw()
    
    # ファイル選択
    target_file = tkinter.filedialog.askopenfilename(title="ファイル選択", initialdir="./", filetypes=[("Image File","*.png;*.jpg")])
    
    
    feature_detecion(target_file)
    
def feature_detecion(target_file):
    
    TARGET_FILE_PATH = target_file
    TARGET_FILE = os.path.basename(TARGET_FILE_PATH)
    IMG_DIR_PATH =  './images_thermal_train/data/'
    file_names = os.listdir(IMG_DIR_PATH)

    print('TARGET_FILE: %s' % (TARGET_FILE))

    target_img = cv2.imread(TARGET_FILE_PATH, cv2.IMREAD_GRAYSCALE)
    target_img = cv2.resize(target_img, dsize=(640, 512))
    
    # マッチング器
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    detector = cv2.AKAZE_create()
    (target_kp, target_des) = detector.detectAndCompute(target_img, None)
    
    # マッチング率が良いもの
    min_ret = 100000
    min_file = ""
    for file in file_names:
        try:
            comparing_img_path = IMG_DIR_PATH + file
            #print(comparing_img_path)
            comparing_img = cv2.imread(comparing_img_path, cv2.IMREAD_GRAYSCALE)
            (comparing_kp, comparing_des) = detector.detectAndCompute(comparing_img, None)
            matches = bf.match(target_des, comparing_des)
            dist = [m.distance for m in matches]
            ret = sum(dist) / len(dist)
            print("ret:" + str(ret))
            if min_ret > ret:
                min_ret = ret
                min_file = file
        except cv2.error:
            ret = 100000
    print('TARGET_FILE: %s' % (TARGET_FILE))        
    print(min_file, min_ret)
if __name__ == '__main__':
    tk_dialog()