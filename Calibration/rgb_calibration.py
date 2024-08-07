import cv2
import numpy as np
from utils.cameracalibration import CameraCalibration

CHECKERBOARD = (7,10) 
camera_calibration = CameraCalibration(CHECKERBOARD)

images = './Calibration/chessboard_calibration_data/rgb/*.jpg'
text_files = './Calibration/rgb_re_projection.txt'
save_text = './Calibration/rgb_again_re_projection.txt'
threshold = 0.03
camera_calibration.rgb_re_calibration(images, text_files, threshold, save_text)