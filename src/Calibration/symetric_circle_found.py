import numpy as np
import cv2
import glob

# グリッドサイズ (行, 列) (例: 4行, 11列)
pattern_size = (7, 7)
images = glob.glob('./Calibration/circlegrid_calibration_data/rgb/*.jpg')
count = 0
for image_path in images:
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # ドットの中心を検出
    ret, centers = cv2.findCirclesGrid(gray, pattern_size, flags=cv2.CALIB_CB_SYMMETRIC_GRID)

    if ret:
        # 検出したドットを描画して確認
        cv2.drawChessboardCorners(img, pattern_size, centers, ret)
        cv2.imshow('Detected Circles Grid', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("円グリッドが検出されませんでした。")
        print(count)
    count += 1