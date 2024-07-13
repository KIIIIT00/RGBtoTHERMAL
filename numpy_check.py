import numpy as np
corner = [581, 274, 685, 276, 786, 278, 884, 280, 579, 340, 691, 342, 801, 342, 905, 344, 579, 417, 700, 418, 820, 418, 933, 417, 578, 512, 711, 509, 841, 508, 961, 501, 576, 620, 721, 619, 864, 613, 994, 602]
change_co = np.array(corner, dtype=np.float32).reshape(-1, 1, 2)
print(len(corner))
print(change_co.shape)
arr = [[4, 5], [5,5]]
print([4,5] in arr)
chessboard_size = (5, 5)
objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
print(objp.shape)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
print(objp.shape)