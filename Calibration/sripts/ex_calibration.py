import numpy as np
import cv2
import glob

# Asymmetry-CircleGridのパターン設定
grid_size = (4, 11)  # 内部の点の数 (columns, rows)

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# 画像ファイルのパスを取得
image_paths = glob.glob('./Calibration/calibration_data/*.jpg')  # 画像ファイルのパスを適宜変更

# 3次元のオブジェクト座標と2次元のイメージ座標の配列を作成
object_points = []
image_points = []

# 円形グリッドの3次元座標を生成
objp = np.zeros((np.prod(grid_size), 3), dtype=np.float32)
objp[:, :2] = np.mgrid[0:grid_size[0], 0:grid_size[1]].T.reshape(-1, 2)


for image_path in image_paths:
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    print(img.shape)

    # Asymmetry-CircleGridを検出
    found, corners = cv2.findCirclesGrid(gray, grid_size, flags=cv2.CALIB_CB_ASYMMETRIC_GRID)

    # グリッドが見つかれば追加
    if found:
        objp = np.zeros((np.prod(grid_size), 3), dtype=np.float32)
        objp[:, :2] = np.mgrid[0:grid_size[0], 0:grid_size[1]].T.reshape(-1, 2)
        object_points.append(objp)          # 交点のワールド座標をobjpointsに追加
        # refining pixel coordinates for given 2d points.
        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        
        image_points.append(corners2)
cv2.destroyAllWindows()

# カメラキャリブレーションを実行
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(object_points, image_points, gray.shape[::-1],None,None)    # ここでカメラキャリブレーションを行っている

# キャリブレーション結果を保存
np.savez('calibration_data_asymmetry_circlegrid.npz', mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)

print("Calibration successful.")
print("Camera matrix:\n", mtx)
print("Distortion coefficients:\n", dist)
