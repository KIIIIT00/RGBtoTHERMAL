"""
再投影誤差など格納されたテキストを読み取って，比較する
"""

import os
import glob

def read_txt(filename):
    """
    テキストファイルを読み取る
    """
    with open(filename, 'r') as file:
        lines = file.readlines()
        
    # Thermal ProjectionとRGB Projectionの値を格納する変数
    thermal_projection = None
    rgb_projection = None
    thermal_flag = False
    rgb_flag = False
    # 1行ごと読み取る
    for line in lines:
        if thermal_flag:
            thermal_projection = float(line.strip())
            thermal_flag = False
        # Thermal Projectionの行を見つける
        if 'Thermal Projection' in line:
            thermal_flag = True
        
        if rgb_flag :
            rgb_projection = float(line.strip())
            rgb_flag = False
        # RGB Projectionの行を見つける
        if 'RGB Projection' in line:
            rgb_flag = True
    
    
    return thermal_projection, rgb_projection

# 走査対象のファイルパス
txt_files = './Calibration/Calibration_result/external/*.txt'

# 最小値を格納する変数
min_thermal_projection = float('inf')
min_rgb_projection = float('inf')
min_thermal_file = None
min_rgb_file = None

for filename in glob.glob(txt_files):
    thermal_projection, rgb_projection = read_txt(filename)
    print(thermal_projection, rgb_projection)
    # Thermal Projectionの最小値を更新
    if thermal_projection is not None and thermal_projection < min_thermal_projection:
        min_thermal_projection = thermal_projection
        min_thermal_file = filename

    # RGB Projectionの最小値を更新
    if rgb_projection is not None and rgb_projection < min_rgb_projection:
        min_rgb_projection = rgb_projection
        min_rgb_file = filename

# 結果を表示
print(f"Minimum Thermal Projection: {min_thermal_projection} in file {min_thermal_file}")
print(f"Minimum RGB Projection: {min_rgb_projection} in file {min_rgb_file}")
