"""
環境構築は，以下のURLを参考にしていただきたい
https://github.com/ais-lab/sotsuken1/wiki/%E3%83%AD%E3%83%9C%E3%83%83%E3%83%88-%E7%94%BB%E5%83%8F%E5%87%A6%E7%90%86

関節モードでモータを180度の範囲を動かす
"""

import os
import time
from dynamixel_sdk import *  # Uses Dynamixel SDK library
import cv2

# Control table address
ADDR_TORQUE_ENABLE       = 24
ADDR_GOAL_POSITION       = 30
ADDR_PRESENT_POSITION    = 36
ADDR_GOAL_POSITION_SPEED = 32
ADDR_MOVING_STATE        = 46

# Protocol version
PROTOCOL_VERSION        = 1  # See which protocol version is used in the Dynamixel

# Default setting
DXL_ID                  = 12    # Dynamixel ID
BAUDRATE                = 1000000
DEVICENAME              = "COM3"  # Check which port is being used on your controller

TORQUE_ENABLE           = 1    # Value for enabling the torque
TORQUE_DISABLE          = 0    # Value for disabling the torque
DXL_MINIMUM_POSITION_VALUE  = 100  # Dynamixel will rotate between this value
DXL_MAXIMUM_POSITION_VALUE  = 4000  # and this value
DXL_MOVING_STATUS_THRESHOLD = 10  # Dynamixel moving status threshold
DXL_MINIMUM_POSITION_VALUE = 205       # 60 degrees
DXL_MAXIMUM_POSITION_VALUE = 817

portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

# 150度基準から-90度の場所にあるとき，False
rotate_flag = False

class DXL():
    def __init__(self):
        # Open port
        if portHandler.openPort():
            print("Succeeded to open the port")
        else:
            print("Failed to open the port")
            print("Press any key to terminate...")
            quit()

        # Set port baudrate
        if portHandler.setBaudRate(BAUDRATE):
            print("Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate")
            print("Press any key to terminate...")
            quit()

        # Enable Dynamixel torque
        dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))
        else:
            print("Dynamixel has been successfully connected")
        
        # Move Dynamixel to initial position
    packetHandler.write2ByteTxRx(portHandler, DXL_ID, ADDR_GOAL_POSITION, DXL_MINIMUM_POSITION_VALUE)

    # ジョイントモードの現在値を読み取る
    def get_present_pos(self):
        dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(portHandler, DXL_ID, ADDR_PRESENT_POSITION)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))
        else:
            print("Present Position: %d" % dxl_present_position)
        return dxl_present_position
    
    # 90か-90度からPositionに変換する
    @staticmethod
    def deg_to_pos(deq):
        return (int)(512 + 1024/300 * deq)
    
    # 関節モードにおいて，モータが動いているか
    # 動いているとき，1，動いていないとき，0を返す
    def get_moving_state(self):
        dxl_moving, dxl_comm_result, dxl_error = packetHandler.read1ByteTxRx(portHandler, DXL_ID, ADDR_MOVING_STATE)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))

        print(f"Moving status: {dxl_moving}")
        return dxl_moving
    
    # Dynamixelのトルクを無効にし，ポートを閉じる
    def finish_dynamixel(self):
        # Disable Dynamixel Torque
        packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)

        # Close port
        portHandler.closePort()
   
"""
if __name__ == "__main__":
# Write goal position
    dx = DXL()
    while True:
        if cv2.waitKey(1) & 0xff == 27:
            break
   
        dx.move_joint(-90)
        dx.get_present_pos()
        dx.get_moving_state()
        time.sleep(5)
        dx.get_moving_state()
        dx.move_joint(90)
        dx.get_present_pos()
        time.sleep(5)

cv2.destroyAllWindows()
# Close port
dx.finish_dynamixel()
"""

