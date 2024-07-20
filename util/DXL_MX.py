"""
Dynamixel MX-106の制御を行うクラス
"""

from dynamixel_sdk import *

ADDR_TORQUE_ENABLE           = 64
ADDR_GOAL_POSITION           = 116
ADDR_PRESENT_POSITION        = 132
ADDR_GOAL_POSITION_SPEED     = 128
ADDR_MOING_STATE             = 123

TORQUE_ENABLE = 1
TORQUE_DISABLE = 0

class DynamixelMX106:
    def __init__(self, port_name, baud_rate, motor_id):
        self.port_name = port_name
        self.baud_rate = baud_rate
        self.motor_id = motor_id
        
        # Initialize PortHandler and PacketHandler
        self.port_handler = PortHandler(self.port_name)
        self.packet_handler = PacketHandler(2.0)  # Using protocol 2.0
        
        # Open port
        if not self.port_handler.openPort():
            raise Exception("Failed to open the port")
        
        # Set port baudrate
        if not self.port_handler.setBaudRate(self.baud_rate):
            raise Exception("Failed to change the baudrate")
    
    def enable_torque(self):
        # Enable Dynamixel Torque
        dxl_comm_result, dxl_error = self.packet_handler.write1ByteTxRx(self.port_handler, self.motor_id, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
        if dxl_comm_result != COMM_SUCCESS:
            raise Exception(f"Failed to enable torque: {self.packet_handler.getTxRxResult(dxl_comm_result)}")
        elif dxl_error != 0:
            raise Exception(f"Dynamixel error: {self.packet_handler.getRxPacketError(dxl_error)}")
    
    def disable_torque(self):
        # Disable Dynamixel Torque
        dxl_comm_result, dxl_error = self.packet_handler.write1ByteTxRx(self.port_handler, self.motor_id, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
        if dxl_comm_result != COMM_SUCCESS:
            raise Exception(f"Failed to disable torque: {self.packet_handler.getTxRxResult(dxl_comm_result)}")
        elif dxl_error != 0:
            raise Exception(f"Dynamixel error: {self.packet_handler.getRxPacketError(dxl_error)}")
    
    def set_goal_position(self, position):
        # Write goal position
        dxl_comm_result, dxl_error = self.packet_handler.write4ByteTxRx(self.port_handler, self.motor_id, ADDR_GOAL_POSITION, position)
        if dxl_comm_result != COMM_SUCCESS:
            raise Exception(f"Failed to set goal position: {self.packet_handler.getTxRxResult(dxl_comm_result)}")
        elif dxl_error != 0:
            raise Exception(f"Dynamixel error: {self.packet_handler.getRxPacketError(dxl_error)}")
    
    def get_present_position(self):
        # Read present position
        dxl_present_position, dxl_comm_result, dxl_error = self.packet_handler.read4ByteTxRx(self.port_handler, self.motor_id, ADDR_PRESENT_POSITION)
        if dxl_comm_result != COMM_SUCCESS:
            raise Exception(f"Failed to read present position: {self.packet_handler.getTxRxResult(dxl_comm_result)}")
        elif dxl_error != 0:
            raise Exception(f"Dynamixel error: {self.packet_handler.getRxPacketError(dxl_error)}")
        
        return dxl_present_position
    
    def rotate_to_minus_180(self):
        # Rotate to -90 degrees
        self.set_goal_position(0)
    
    def init_position(self):
        self.set_goal_position(2048)
    def rotate_to_180(self):
        # Rotate to +90 degrees
        self.set_goal_position(4095)

    def close_port(self):
        # Close port
        self.port_handler.closePort()

# Example usage
if __name__ == "__main__":
    motor = DynamixelMX106(port_name='COM3', baud_rate=57600, motor_id=1)
    
    
    try:
        motor.enable_torque()
        motor.init_position()
        time.sleep(2)  # Wait for 2 seconds
        motor.rotate_to_180()
        time.sleep(2)  # Wait for 2 seconds
        motor.init_position()
        time.sleep(2)  # Wait for 2 seconds
        motor.disable_torque()
    finally:
        motor.close_port()