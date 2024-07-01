import numpy as np
import cv2

# 3次元座標を描画
def draw(img, corners, imgpts):
    #corner = tuple(corners[0].ravel())
    img = cv2.line(img, (int(corners[0][0][0]), int(corners[0][0][1])), (int(imgpts[0][0][0]), int(imgpts[0][0][1])), (255,0,0), 5)   # x
    img = cv2.line(img, (int(corners[0][0][0]), int(corners[0][0][1])), (int(imgpts[1][0][0]), int(imgpts[1][0][1])), (0,255,0), 5)   # y
    img = cv2.line(img, (int(corners[0][0][0]), int(corners[0][0][1])), (int(imgpts[2][0][0]), int(imgpts[2][0][1])), (0,0,255), 5)   # z
    return img

tate = 7
yoko = 10
ret2 = False    # 交点を見つけたかどうか

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((tate*yoko,3), np.float32)
objp[:,:2] = np.mgrid[0:yoko,0:tate].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.
#カメラの設定
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # 幅の設定
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # 高さの設定

#内部パラメータと歪み係数
#mtx = np.array(["""***************ここにあらかじめ求めておいた内部パラメータを書く***************"""]).reshape(3,3)
mtx = np.array([622.56592404, 0, 318.24063181, 0, 623.20968839, 245.37576884, 0, 0, 1]).reshape(3,3)
#dist = np.array(["""***************ここにあらかじめ求めておいた歪み係数を書く***************"""])
dist = np.array([ 0.14621503, -0.26374155, -0.00065967,  -0.00055428, 0.25360545])
#繰り返しのためのwhile文
while True:
    #カメラからの画像取得
    ret1, frame = cap.read()

    img = frame.copy()
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    #ret, img_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
    cv2.imshow('frame',frame)

    # Find the chess board corners　交点を見つける
    ret2, corners = cv2.findChessboardCorners(gray, (yoko,tate),None)
    # If found, add object points, image points (after refining them)　交点が見つかったなら、描画
    if ret2 == True:
        objpoints.append(objp)      # object point

        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria) # 精度を上げている
        imgpoints.append(corners2)

        # パラメータの表示
        # Draw and display the corners
        #img = cv2.drawChessboardCorners(img, (yoko,tate), corners2,ret2)
        #cv2.imshow('drawChessboardCorners',img)

        ret3, rvecs, tvecs, _ = cv2.solvePnPRansac(objp, corners2, mtx, dist)      # ここで外部パラメータを求めている
        """
        ret：
        mtx：camera matrix，カメラ行列(内部パラメータ)
        dist：distortion coefficients，レンズ歪みパラメータ
        rvecs：rotation vectors，回転ベクトル
        tvecs：translation vectors，並進ベクトル
        """

        img_dots = img.copy()

        # ワールド座標軸
        axis = np.float32([[3,0,0], [0,3,0], [0,0,-3]]).reshape(-1,3)       # [0,0,0]からどこまで線を伸ばしたいか
        axis_imgpts, _ = cv2.projectPoints(axis, rvecs, tvecs, mtx, dist)      # axisで定義したワールド座標を画像座標に変換
        img_dots = draw(img_dots,corners2,axis_imgpts)

        # 点の定義
        dots = np.float32([[3,3,0], [0,0,-4]]).reshape(-1,3)       # 点群のワールド座標
        # project 3D points to image plane

        imgpts, jac = cv2.projectPoints(dots, rvecs, tvecs, mtx, dist)      # dotsのワールド座標を画像座標に変換
        print(imgpts)

        for i in imgpts:
            img_dots = cv2.circle(img_dots, (int(i[0][0]),int(i[0][1])), 5, (255, 0, 255), thickness=5)

        cv2.imshow('dots',img_dots)             # 点が描画された画像を出力


    #繰り返し分から抜けるためのif文
    key =cv2.waitKey(1)
    if key == 27:   #Escで終了
        break

cv2.imwrite('dots.png',img_dots)        # 点が描画された画像を保存
#メモリを解放して終了するためのコマンド
cap.release()
cv2.destroyAllWindows()



"""
【参考】
カメラキャリブレーション
http://labs.eecs.tottori-u.ac.jp/sd/Member/oyamada/OpenCV/html/py_tutorials/py_calib3d/py_calibration/py_calibration.html
https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html

姿勢推定
http://labs.eecs.tottori-u.ac.jp/sd/Member/oyamada/OpenCV/html/py_tutorials/py_calib3d/py_pose/py_pose.html#pose-estimation
https://docs.opencv.org/4.x/d7/d53/tutorial_py_pose.html
"""