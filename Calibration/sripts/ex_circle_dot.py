import numpy as np
import cv2

def draw(img, corners, imgpts):
    corner = tuple(corners[0].ravel())
    img = cv2.line(img, (int(corners[0][0][0]), int(corners[0][0][1])), (int(imgpts[0][0][0]), int(imgpts[0][0][1])), (255,0,0), 5)   # x
    img = cv2.line(img, (int(corners[0][0][0]), int(corners[0][0][1])), (int(imgpts[1][0][0]), int(imgpts[1][0][1])), (0,255,0), 5)   # y
    img = cv2.line(img, (int(corners[0][0][0]), int(corners[0][0][1])), (int(imgpts[2][0][0]), int(imgpts[2][0][1])), (0,0,255), 5)   # z
    return img
# 円グリッドのサイズを指定
grid_size = (4, 9)  # 例として (rows, cols)

# 3Dオブジェクトポイント（ワールド座標系の座標）
objp = np.zeros((np.prod(grid_size), 3), dtype=np.float32)
objp[:, :2] = np.mgrid[0:grid_size[0], 0:grid_size[1]].T.reshape(-1, 2)
axis = np.float32([[3,0,0], [0,3,0], [0,0,-3]]).reshape(-1,3)
# 画像座標系における検出した点のリスト
imgpoints = []

# 画像の読み込み
img = cv2.imread('./Calibration/circle_grid.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# 円グリッドの検出
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
found, corners = cv2.findCirclesGrid(gray, grid_size, flags=cv2.CALIB_CB_ASYMMETRIC_GRID)

if found:
    imgpoints.append(corners)

    # 円グリッドを描画
    cv2.drawChessboardCorners(img, grid_size, corners, found)

    # カメラキャリブレーション
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera([objp], imgpoints, gray.shape[::-1], None, None)

    # 外部パラメータの取得
    rotation_vector = rvecs[0]  # 回転ベクトル
    translation_vector = tvecs[0]  # 並進ベクトル

    print("Rotation Vector:")
    print(rotation_vector)
    print("Translation Vector:")
    print(translation_vector)

    corners2 = cv2.cornerSubPix(gray,corners,grid_size,(-1,-1),criteria)
    ret3, rvecs, tvecs, _ = cv2.solvePnPRansac(objp, corners2, mtx, dist)

    # 外部パラメータを使用してワールド座標系の原点を画像座標系に描画する
    origin = np.array([[0, 0, 0]], dtype=np.float32)
    axis_points, _ = cv2.projectPoints(axis, rvecs, tvecs, mtx, dist)
    

    # project 3D points to image plane
    imgpts, jac = cv2.projectPoints(axis, rvecs, tvecs, mtx, dist)

    img = draw(img,corners2,imgpts)
    cv2.imshow('Image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

else:
    print("円グリッドが見つかりませんでした。")
