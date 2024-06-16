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

# Protocol version
PROTOCOL_VERSION        = 1  # See which protocol version is used in the Dynamixel

# Default setting
DXL_ID                  = 10    # Dynamixel ID
BAUDRATE                = 1000000
DEVICENAME              = "COM4"  # Check which port is being used on your controller

TORQUE_ENABLE           = 1    # Value for enabling the torque
TORQUE_DISABLE          = 0    # Value for disabling the torque
DXL_MINIMUM_POSITION_VALUE  = 100  # Dynamixel will rotate between this value
DXL_MAXIMUM_POSITION_VALUE  = 4000  # and this value
DXL_MOVING_STATUS_THRESHOLD = 10  # Dynamixel moving status threshold

portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

# 150度基準から-90度の場所にあるとき，0
rotate_flag = 0

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

    # ジョイントモードの現在値を読み取る
    def GetPresentPos(self):
        dxl_present_position, dxl_comm_result, dxl_error = packetHandler.read2ByteTxRx(portHandler, DXL_ID, ADDR_PRESENT_POSITION)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))
        else:
            print("Present Position: %d" % dxl_present_position)
    
    # 90か-90度からPositionに変換する
    @staticmethod
    def DeqToPos(self,deq):
        return (int)(512 + 1024/300 * deq)
    
    # 関節モードを動かす
    def moveJoint(self):
        global rotate_flag
        # 関節モードの速度
        dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, DXL_ID, ADDR_GOAL_POSITION_SPEED, 50)

        # 150度基準から-90度の時
        if rotate_flag == 0:
            dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, DXL_ID, ADDR_GOAL_POSITION, DXL.DeqToPos(90))
            rotate_flag = 1
        # 150度基準から90度の時
        else:
            dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, DXL_ID, ADDR_GOAL_POSITION, DXL.DeqToPos(-90))
            rotate_flag = 0
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))
        
        # 後から，現在の位置がわかるように，状態の変数を返す
        return rotate_flag
    

"""
if __name__ == "__main__":
# Write goal position
    dx = DXL()
    while True:
        if cv2.waitKey(1) & 0xff == 27:
            break
   
        dx.moveJoint()

    # Write goal position
    #dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, DXL_ID, ADDR_GOAL_POSITION, DXL_MINIMUM_POSITION_VALUE)
    #if dxl_comm_result != COMM_SUCCESS:
    #    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    #elif dxl_error != 0:
    #    print("%s" % packetHandler.getRxPacketError(dxl_error))

    time.sleep(2)

    # Write goal position
    #dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, DXL_ID, ADDR_GOAL_POSITION, DXL_MAXIMUM_POSITION_VALUE)
    #if dxl_comm_result != COMM_SUCCESS:
    #    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    #elif dxl_error != 0:
    #    print("%s" % packetHandler.getRxPacketError(dxl_error))

    #time.sleep(2)

# Disable Dynamixel torque
#dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
#if dxl_comm_result != COMM_SUCCESS:
#    print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
#elif dxl_error != 0:
#    print("%s" % packetHandler.getRxPacketError(dxl_error))

cv2.destroyAllWindows()
# Close port
portHandler.closePort()
"""
