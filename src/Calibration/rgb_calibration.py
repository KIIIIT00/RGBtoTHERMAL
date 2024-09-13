import cv2
import numpy as np
from utils.CameraCalibration import CameraCalibration

CHECKERBOARD = (7,10) 
camera_calibration = CameraCalibration(CHECKERBOARD)

images = '.results/Calibration/chessboard_calibration_data/rgb/*.jpg'
text_files = '.results/Calibration/rgb_re_projection.txt'
save_text = '.results/Calibration/rgb_again_re_projection.txt'
threshold = 0.03
camera_calibration.rgb_re_calibration(images, text_files, threshold, save_text)