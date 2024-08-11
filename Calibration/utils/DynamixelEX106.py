"""
DynamixelのEX-106+の設定を行うクラス
"""
from dynamixel_sdk import *

class DynamixelEX106:

  def __init__(self, port_name, baudrate, dxl_id):
    """
    コンストラクタ
    
    Parameters
    ------------
    port_name : str
      ポート番号
    baudrate : int
      ボートレート
    dxl_id : int
      モータのid
    """
    self.ADDR_TORQUE_ENABLE = 24
    self.ADDR_GOAL_POSITION = 30
    self.ADDR_PRESENT_POSITION = 36
    self.ADDR_MOVING_SPEED = 32
    self.ADDR_MOVING = 46
    self.ADDR_CW_ANGLE_LIMIT = 6
    self.ADDR_CCW_ANGLE_LIMIT = 8

    self.TORQUE_ENABLE = 1
    self.TORQUE_DISABLE = 0


    # プロトコルバージョン
    self.PROTOCOL_VERSION = 1.0

    # デフォルト設定
    self.DXL_ID = dxl_id
    self.BAUDRATE = baudrate
    self.PORT_NAME = port_name

    # portHandler
    self.port_handler = PortHandler(self.PORT_NAME)

    # PacketHandler
    self.packet_handler = PacketHandler(self.PROTOCOL_VERSION)

    # Open port
    if not self.port_handler.openPort():
      raise Exception("Faled to open the port")
    
    # Set port baudrate
    if not self.port_handler.setBaudRate(self.BAUDRATE):
      raise Exception("Failed to chang the baudrate")
    
    # Enable Dynamixel Torque
    self.enable_torque(self)
  
  def enable_torque(self):
    dxl_comm_result, dxl_error = self.packet_handler.write1ByteTxRx(self.port_handler, self.DXL_ID, self.ADDR_TORQUE_ENABLE, self.TORQUE_ENABLE)
    if dxl_comm_result != COMM_SUCCESS:
        raise Exception(f"Failed to enable torque: {self.packet_handler.getTxRxResult(dxl_comm_result)}")
    elif dxl_error != 0:
        raise Exception(f"Dynamixel error: {self.packet_handler.getRxPacketError(dxl_error)}")
  
  def disable_torque(self):
    dxl_comm_result, dxl_error = self.packet_handler.write1ByteTxRx(self.port_handler, self.DXL_ID, self.ADDR_TORQUE_ENABLE, self.TORQUE_DISABLE)
    if dxl_comm_result != COMM_SUCCESS:
        raise Exception(f"Failed to disable torque: {self.packet_handler.getTxRxResult(dxl_comm_result)}")
    elif dxl_error != 0:
        raise Exception(f"Dynamixel error: {self.packet_handler.getRxPacketError(dxl_error)}")
  
  def set_goal_position(self, position):
     """
     関節モードでの目標位置を設定
     """
     result, error = self.packet_handler.write2BytwTxRx(self.port_handler, self.DXL_ID, self.ADDR_GOAL_POSITION, position)
     if result != COMM_SUCCESS:
      print(f"Failed to set goal position: {self.packetHandler.getTxRxResult(result)}")
     elif error != 0:
      print(f"Error: {self.packetHandler.getRxPacketError(error)}")
  
  def read_position(self):
     """
     現在の位置を読み取り
     """
     position, result, error = self.packet_handler.read2ByteTxRx(self.port_handler, self.DXL_ID, self.ADDR_PRESENT_POSITION)
     if result != COMM_SUCCESS:
        print(f"Failed to read position: {self.packetHandler.getTxRxResult(result)}")
     elif error != 0:
        print(f"Error: {self.packetHandler.getRxPacketError(error)}")
     return position
  
  def set_speed(self, speed):
     """
     モータの移動速度を設定する
     """
     result, error = self.packet_handler.write2ByteTxRx(self.port_handler, self.DXL_ID, self.ADDR_MOVING_SPEED, speed)
     if result != COMM_SUCCESS:
        print(f"Failed to set speed: {self.packetHandler.getTxRxResult(result)}")
     elif error != 0:
        print(f"Error: {self.packetHandler.getRxPacketError(error)}")
  
  def is_moving(self):
     """
     モータが動いているどうか
     """
     moving, result, error = self.packet_handler.read1ByteTxRx(self.port_handler, self.DXL_ID, self.ADDR_MOVING)
     if result != COMM_SUCCESS:
        print("%s" % self.packet_handler.getTxRxResult(result))
        return False
     elif error != 0:
        print("%s" % self.packet_handler.getRxPacketError(error))
        return False
     return moving == 1
  
  def init_position(self):
     """
     初期位置(2048)にする
     """
     self.set_goal_position(2048)
  
  def cw_rotate_45(self):
     """
     CW方向に45度回転する
     """
     self.set_goal_position(1313)

  
  def ccw_rotate_45(self):
     """
     CCW方向に45度回転する
     """
     self.set_goal_position(2783)
  
  def close_port(self):
     self.port_handler.closePort()
