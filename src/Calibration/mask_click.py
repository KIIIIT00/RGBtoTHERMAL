import matplotlib.pyplot as plt
import numpy as np
import cv2

# サンプル画像を生成する関数（今回はランダムなデータを用いる）
def generate_sample_image():
    return np.random.rand(500, 500, 3)

# クリックイベントのハンドラ
clicks = []
def onclick(event):
    if len(clicks) < 2:
        clicks.append((int(event.xdata), int(event.ydata)))
        if len(clicks) == 2:
            plt.close()

# サンプル画像を取得
filePath = './Calibration/demo/cold_thermal_10.png'
image = cv2.imread(filePath,1 )

# 画像を表示し、クリックイベントを待つ
fig, ax = plt.subplots()
ax.imshow(image)
cid = fig.canvas.mpl_connect('button_press_event', onclick)
plt.show()

if len(clicks) == 4:
    # クリックした4点の座標
    print(f"Clicked points: {clicks}")
    
    # クリックした4点を多角形として使用してマスクを作成
    mask = np.zeros_like(image, dtype=np.uint8)
    polygon = np.array([clicks], dtype=np.int32)
    cv2.fillPoly(mask, polygon, (1, 1, 1))
    
    # マスクを適用する
    masked_image = image * mask
    
    # 元画像とマスク画像を表示する
    fig, ax = plt.subplots(1, 2)
    ax[0].imshow(image)
    ax[0].set_title("Original Image")
    ax[1].imshow(masked_image)
    ax[1].set_title("Masked Image")
    plt.show()
else:
    print("4点をクリックしてください")