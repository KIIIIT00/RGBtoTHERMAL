import numpy as np
import cv2

tate = 7    # 縦の交点の個数
yoko = 10   # 横の交点の個数

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

# 内部パラメータと歪み係数
#mtx = np.array(["""***************ここにあらかじめ求めておいた内部パラメータを書く***************"""]).reshape(3,3)
mtx = np.array([679.96806785, 0, 346.1742875, 0, 680.07309494, 223.11864346, 0, 0, 1]).reshape(3,3)
#dist = np.array(["""***************ここにあらかじめ求めておいた歪み係数を書く***************"""])
dist = np.array([-4.65322788e-01, 3.88192556e-01, -2.58061414e-03, -1.69216070e-04, -3.97886096e-01])

#繰り返しのためのwhile文
while True:
    #カメラからの画像取得
    ret1, frame = cap.read()
    if ret1:
        #カメラの画像の出力
        cv2.imshow('camera' , frame)

        img = frame.copy()
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        # Find the chess board corners　交点を見つける
        ret2, corners = cv2.findChessboardCorners(gray, (yoko,tate),None)
        # If found, add object points, image points (after refining them)　交点が見つかったなら描画
        if ret2:
            rvecs = []
            tvecs = []
            objpoints.append(objp)      # object point

            corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
            imgpoints.append(corners2)

            # パラメータの表示
            # Draw and display the corners
            img = cv2.drawChessboardCorners(img, (yoko,tate), corners2,ret2)     # 交点を見つけて印を付ける
            cv2.imshow('drawChessboardCorners',img)     # 印の付いた画像を出力

            ret3, rvecs, tvecs, _ = cv2.solvePnPRansac(objp, corners2, mtx, dist)      # ここで外部パラメータを求めている

            """
            mtx：camera matrix，内部パラメータ
            dist：distortion coefficients，歪み係数
            rvecs：rotation vectors，外部パラメータの回転行列
            tvecs：translation vectors，外部パラメータの並進ベクトル
            """
            if ret3:
                # 歪み補正の準備
                img2 = frame.copy()
                h, w = img2.shape[:2]
                newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))     # 周りの画像の欠損を考慮した内部パラメータと，トリミング範囲を作成

                dst = cv2.undistort(img2, mtx, dist, None, newcameramtx)        # ここで歪み補正を行っている
                before_undistort = dst.copy()
                cv2.imshow('before undistort' , before_undistort)  
                # crop the image
                x,y,w,h = roi
                dst = dst[y:y+h, x:x+w]     # 画像の端が黒くなっているのでトリミング

                #カメラの画像の出力
                cv2.imshow('undistort' , dst)   # 歪み補正された画像を出力

    #繰り返し分から抜けるためのif文
    key =cv2.waitKey(1)
    if key == 27:   #Escで終了
        break

#cv2.imwrite('frame.png',frame)      # そのままの画像を保存
#cv2.imwrite('undistort.png',dst)    # 歪み補正された画像を保存
#メモリを解放して終了するためのコマンド
cap.release()
cv2.destroyAllWindows()


#【参考】
# http://labs.eecs.tottori-u.ac.jp/sd/Member/oyamada/OpenCV/html/py_tutorials/py_calib3d/py_calibration/py_calibration.html
# https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
