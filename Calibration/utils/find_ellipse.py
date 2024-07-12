"""
赤外線画像の格子状に並べたアルミ円板に対して，円の中心をとる
"""
import cv2
import numpy as np
import matplotlib.pyplot as plt
def image_load_gray(image_path):
    """
    画像を読み込み，グレースケール画像に変換
    Parameters
    ----------
    iamge_path : str
          iamgeのパス
    Returns
    -------
    gray : ndarray
    """
    global gray
    image = cv2.imread(image_path)
    image = cv2.bitwise_not(image)
    # グレースケールに変換
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image, gray
# 閾値を調整するためのコールバック関数
def update_threshold(val):
    global threshold, image, gray, thresh
    threshold = val
    _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    cv2.imshow('Binary Image', thresh)
def update_find_contours(image, min_axis_length, max_axis_length, contours):
    global point_list
    point_list = []
    # 楕円をフィット
    for contour in contours:
        if len(contour) >= 5:  # 楕円フィッティングには最低5つの点が必要
            ellipse = cv2.fitEllipse(contour)
            (center, axes, angle) = ellipse
            (major_axis, minor_axis) = (max(axes), min(axes))  # 長軸と短軸
            # 楕円の大きさを制限
            if min_axis_length <= major_axis <= max_axis_length and min_axis_length <= minor_axis <= max_axis_length:
                center = (int(center[0]), int(center[1]))  # 楕円の中心
                print(f'x:{center[0]}, y:{center[1]}')
                point_list.append([int(center[0]), int(center[1])])
                cv2.ellipse(image, ellipse, (0, 255, 0), 2)  # 楕円を描画
                cv2.circle(image, center, 5, (0, 0, 255), -1)  # 中心を描画
    # y座標でソート
    point_list_sorted = sorted(point_list, key=lambda coord: coord[1])
    print("----------sorted-----------")
    for point in point_list_sorted:
        x, y = point
        print(f'x:{x}, y:{y}')
    # 画像を表示
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
def empty(x):
    pass
def find_circles(image_path):
    """
    グレースケール画像から楕円の中心を取得
    Parameters
    ----------
    image_path : str
    Returns
    -------
    point_list : list
    """
    # 初期閾値
    threshold = 93
    min_axis_length = 35 # 最小軸長
    max_axis_length = 80  # 最大軸長
    cv2.namedWindow('Parameters')
    cv2.resizeWindow('Parameters', width = 600, height = 200)
    # トラックバーを作成
    cv2.createTrackbar('Threshold', 'Parameters', threshold, 255, update_threshold)
    cv2.createTrackbar('min_axis_length', 'Parameters', 0, 100, empty)
    cv2.createTrackbar('max_axis_length', 'Parameters', 0, 100, empty)
    image, gray = image_load_gray(image_path)
    # 初期閾値
    #threshold = 93
    # 閾値処理
    # 赤外線のとき
    _, thresh = cv2.threshold(gray,threshold, 255, cv2.THRESH_BINARY)
    cv2.namedWindow('Binary Image')
    cv2.imshow('Binary Image', thresh)
    # トラックバーを作成
    #cv2.createTrackbar('Threshold', 'Binary Image', threshold, 255, update_threshold)
    min_axis_length = cv2.getTrackbarPos('min_axis_length', 'Parameters')
    max_axis_length = cv2.getTrackbarPos('max_axis_length', 'Parameters')
    # 輪郭を検出
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    update_find_contours(image, min_axis_length, max_axis_length, contours)
    # 赤外線のとき
    #min_axis_length = 35 # 最小軸長
    #max_axis_length = 80  # 最大軸長
    """
    # 楕円の中心(x,y)を格納する辞書
    point_list = []
    # 楕円をフィット
    for contour in contours:
        if len(contour) >= 5:  # 楕円フィッティングには最低5つの点が必要
            ellipse = cv2.fitEllipse(contour)
            (center, axes, angle) = ellipse
            (major_axis, minor_axis) = (max(axes), min(axes))  # 長軸と短軸
            # 楕円の大きさを制限
            if min_axis_length <= major_axis <= max_axis_length and min_axis_length <= minor_axis <= max_axis_length:
                center = (int(center[0]), int(center[1]))  # 楕円の中心
                print(f'x:{center[0]}, y:{center[1]}')
                point_list.append([int(center[0]), int(center[1])])
                cv2.ellipse(image, ellipse, (0, 255, 0), 2)  # 楕円を描画
                cv2.circle(image, center, 5, (0, 0, 255), -1)  # 中心を描画
    # y座標でソート
    point_list_sorted = sorted(point_list, key=lambda coord: coord[1])
    print("----------sorted-----------")
    for point in point_list_sorted:
        x, y = point
        print(f'x:{x}, y:{y}')
    # 画像を表示
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    """
    plt.show()
    #return point_list_sorted
while True:
    find_circles('./Calibration/chessboard_calibration_data/thermal/pic62.jpg')