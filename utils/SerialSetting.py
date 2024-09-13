"""
Arudinoからシリアル通信をするように設定するクラス
"""
import serial
import time

class SerialSetting:
    
    def __init__(self, port_name, baud_rate):
        """
        初期設定

        Parameters
        ----------
        port_name : str
            ポート番号
        baud_rate : int
            ボートレート
        """
        self.serial = serial.Serial(
            port = port_name,
            baudrate= baud_rate,
            timeout = 1
        )
    
    def read_accelerometer(self):
        """
        加速度センサのデータを読み取る
        """
        line = self.serial.readline().decode().strip()
        if line.startswith("Accelerometer"):
            _ , data = line.split(":")
            x, y, z = data.split(",")
            return float(x), float(y), float(z)
        return None


