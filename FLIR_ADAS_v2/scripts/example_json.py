# -*- coding: utf-8 -*-
"""
Created on Fri May 17 17:09:59 2024

@author: Kawahara
"""
import json


# RGBとTHEMALの対応した表をもつjsonを読み込む
json_open_rgb = open('./images_rgb_train/index.json', 'r')
json_open_the = open('./images_thermal_train/index.json', 'r')

data_rgb = json.load(json_open_rgb)
data_the = json.load(json_open_the)



print(type(data_rgb))
print(type(data_rgb['frames'][0]))
print(data_rgb['frames'][0])

print(type(data_rgb['datasetId']))
print(len(data_rgb))
