"""
Dynamixelの設定を行うDxlクラス
"""

from dynamixel_sdk import *

# Control table address
ADDR_TORQUE_ENABLE       = 24
ADDR_GOAL_POSITION       = 30
ADDR_PRESENT_POSITION    = 36
ADDR_GOAL_POSITION_SPEED = 32
ADDR_MOVING_STATE        = 46

TORQUE_ENABLE           = 1    # Value for enabling the torque
TORQUE_DISABLE          = 0    # Value for disabling the torque
DXL_MOVING_STATUS_THRESHOLD = 10  # Dynamixel moving status threshold




class Dxl:
    """
    Dynamixelの設定を行う
    """
    def __init__(self, dxl_id, device_name, baudrate= 1000000, protocol_version=1.0):
        """
        Parameters
        --------------
        dxl_id : int
            DynamixelのID
        device_name : str 
            ポート番号
        baudrate : int
            データ通信速度(デフォルト:1000000)
        protoclo_version : float 
            Dynamixelのプロトコルversion(デフォルト:1.0)
        """
        self.dxl_id = dxl_id
        self.device_name = device_name
        self.baudrate = baudrate
        self.protocol_version = protocol_version
        self.port_handler = PortHandler(device_name)
        self.packet_handler = PacketHandler(protocol_version)
        self.open_port()
        self.set_baudrate()
    
    def open_port(self):
        """
        ポートを開ける
        """
        if self.port_handler.openPort():
            print("Succeeded to open the port")
        else:
            print("Failed to open the port")
            raise Exception("Failed to open the port")

    def close_port(self):
        """
        ポートを閉める
        """
        self.port_handler.closePort()
    
    def set_baudrate(self):
        """
        通信速度を設定する
        """
        if self.port_handler.setBaudRate(self.baudrate):
            print("Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate")
            raise Exception("Failed to change the baudrate")
    
    def enable_torque(self):
        """
        Dynamixelのトルクを有効化する 
        """
        self.packet_handler.write1ByteTxRx(self.port_handler, self.dxl_id, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
    
    def disable_torque(self):
        """
        Dynamixelのトルクを無効化する
        """
        self.packet_handler.write1ByteTxRx(self.port_handler, self.dxl_id, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)

    def set_goal_position(self, goal_position):
        """
        関節モードのgoal_positionに移動する

        Parameters
        --------------
        gaol_position : int
            目標位置(0-1023)
        """
        self.packet_handler.write2ByteTxRx(self.port_handler, self.dxl_id, ADDR_GOAL_POSITION, goal_position)

    @staticmethod
    def deg_2_pos(degree):
        """
        150度を基準としたときの角度をpositionに変換する

        Parammeters
        --------------
        degree : int
            150度を基準としたときの角度(-150~150)

        Returns 
        --------------
        pos : int
            関節モードのポジション(0-1023)
        
        """
        pos = (int)(512 + 1024/300 * degree)
        return pos
    
    def get_present_position(self):
        """
        関節モードにおける現在の位置を取得

        Returns
        --------------
        dxl_present_position : int
            dynamixelの現在の位置(0-1023)
        dxl_comm_result: int
            COM_SUCCESSかどうか COM_SUCCESSの場合,1
        dxl_error : int
            dynamixelのエラー
        """
        return self.packet_handler.read2ByteTxRx(self.port_handler, self.dxl_id, ADDR_PRESENT_POSITION)
    
    def set_speed(self, speed):
        """
        Dynamixelの関節モードにおける速度をセットする
        
        Parameters
        --------------
        speed : int
            設定する速度(0-1023)
            1-23のとき,最大
        """
        self.packet_handler.write2ByteTxRx(self.port_handler, self.dxl_id, ADDR_GOAL_POSITION_SPEED, speed)
    
    def get_moving_state(self):
        """
        Dynamixelの現在動いているかどうかを取得する

        Returns 
        --------------
        dxl_moving : int
            dynamixelの現在,動いているか
            動いているとき,1動いていないとき,0
        dxl_comm_result: int
            COM_SUCCESSかどうか COM_SUCCESSの場合,1
        dxl_error : int
            dynamixelのエラー
        """
        return self.packet_handler.read1ByteTxRx(self.port_handler, self.dxl_id, ADDR_MOVING_STATE)

    def print_moving_state(self):
        """
        Dynamixelが関節モードにおいて,動いているかどうかをpirntし,取得する

        Returns
        --------------
        dxl_moving : int
            Dynamixelが動いているとき,1
            Dynamixelが動いていないとき,0
        """
        dxl_moving, dxl_comm_result, dxl_error = self.get_moving_state()
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packet_handler.getRxPacketError(dxl_error))

        print(f"Moving status: {dxl_moving}")
        return dxl_moving
    
    def print_present_position(self):
        """
        関節モードにおけるDynamixelの現在の位置をprintとし,取得

        Returns
        --------------
        dxl_present_position : int
            Dynamixelの現在の位置(0-1023)
        """
        dxl_present_position, dxl_comm_result, dxl_error = self.get_present_position()
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packet_handler.getRxPacketError(dxl_error))
        print("[ID:%03d] PresPos:%03d" % (self.dxl_id, dxl_present_position))
        return dxl_present_position

