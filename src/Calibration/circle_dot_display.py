import cv2
import numpy as np
import glob

# グリッドサイズ (行, 列) (例: 4行, 11列)
pattern_size = (4, 9)

# 世界座標系の点を準備する
objp = np.zeros((np.prod(pattern_size), 3), np.float32)
objp[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
objp[:,0] *= 2  # 非対称グリッドの補正

# 画像座標系の点を格納するリスト
objpoints = []
imgpoints = []

# 画像の読み込み
images = glob.glob('./Calibration/asymetric_calibration_data/rgb/*.jpg')

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # ドットの中心を検出
    ret, centers = cv2.findCirclesGrid(gray, pattern_size, flags=cv2.CALIB_CB_ASYMMETRIC_GRID)

    if ret:
        objpoints.append(objp)
        imgpoints.append(centers)

        # 検出したドットを描画して確認
        cv2.drawChessboardCorners(img, pattern_size, centers, ret)
        cv2.imshow('Corners', img)
        cv2.waitKey(500)

cv2.destroyAllWindows()

# カメラキャリブレーション
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

# 結果を表示
print("カメラ行列:\n", mtx)
print("歪み係数:\n", dist)

img = cv2.imread('./Calibration/circle_grid.jpg')
h, w = img.shape[:2]
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

# 歪み補正
dst = cv2.undistort(img, mtx, dist, None, newcameramtx)

# 結果を表示
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]
cv2.imshow('Undistorted Image', dst)
cv2.waitKey(0)
cv2.destroyAllWindows()
