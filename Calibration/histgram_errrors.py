"""
再投影誤差のヒストグラムを作成する
"""

import matplotlib.pyplot as plt
import re
import japanize_matplotlib

def read_file(file_name):
    """
    テキストファイルから，写真の数と再投影誤差が格納されたリストを返す
    """
    pic_num_list =[]
    error_num_list = []
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            for line in file:
                sentences = re.split(r'[,]', line.strip())
                for sentence in sentences:
                    # 正規表現を使用して，数値を抽出
                    match_pic = re.search(r'picnum:\s*(\d+)', sentence)
                    match_error = re.search(r'error:\s*([\d\.]+)', sentence)
                    if match_pic:
                        pic_num = int(match_pic.group(1))
                        pic_num_list.append(pic_num)
                    
                    if match_error:
                        error_num = float(match_error.group(1))
                        error_num_list.append(error_num)
            return error_num_list       

    except FileNotFoundError as e:
        # ファイルが存在しないとき
        print(f"The file {file_name} was not found.")
    except Exception as e:
        # その他のエラー
        print(f"An error occurred: {e}")

#file_name = './Calibration/re_projection_error_text.txt'
rgb_file_name = './Calibration/rgb_re_projection.txt'

errors = read_file(rgb_file_name)

# ヒストグラムの作成
plt.figure(figsize=(10, 6))
plt.hist(errors, bins='auto', edgecolor='black')
plt.xlabel('再投影誤差値[pixels]')
plt.ylabel('頻度')
plt.title('RGBカメラの再投影誤差の頻度分布')
plt.grid(True)
plt.show()