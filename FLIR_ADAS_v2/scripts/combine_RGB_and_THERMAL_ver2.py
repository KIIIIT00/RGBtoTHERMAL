# -*- coding: utf-8 -*-
"""
Created on Wed May 22 19:17:05 2024

@author: Kawahara
"""

import os
import numpy as np
import cv2
import argparse
from multiprocessing import Pool

## rgb_trainとthermal_trainのパス
RGB_TRAIN_PATH = './images_rgb_test/data/'
THERMAL_TRAIN_PATH = './images_thermal_test/data/'
RGB_THHERMAL_PATH = './video_rgb_thermal_combine_train/'

