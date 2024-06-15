import os
import time
from dynamixel_sdk import *  # Uses Dynamixel SDK library
import cv2

# Control table address
ADDR_TORQUE_ENABLE      = 24
ADDR_GOAL_POSITION      = 30
ADDR_PRESENT_POSITION   = 36

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

joint_flag = 0

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
    
    # 角度入力からPosition変換
    def Deq2Pos(self,deq):
        return (int)(1023/300 * deq)
    
    # 関節モードを動かす
    def moveJoint(self):
        global joint_flag
        dxl_comm_result, dxl_error = packetHandler.write2ByteTxRx(portHandler, DXL_ID, ADDR_GOAL_POSITION, DXL_MAXIMUM_POSITION_VALUE)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))
    

if __name__ == "__main__":
# Write goal position
    dx = DXL()
    while True:
        if cv2.waitKey(1) & 0xff == 27:
            break
   
        dx.GetPresentPos()

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
