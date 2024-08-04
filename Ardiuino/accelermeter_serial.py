import serial
import time

# シリアルポートの設定
serial = serial.Serial(
    port = 'COM5',
    baudrate = 57600,
    timeout = 1
)

def read_accelerometer():
    # 加速度センサの値を読み取る
    line = serial.readline().decode().strip()
    if line.startswith("Accelerometer"):
        _ , data = line.split(":")
        x, y, z = data.split(",")
        return float(x), float(y), float(z)
    return None

try:
    while True:
        
        accelerometer_data = read_accelerometer()
        if accelerometer_data:
            x, y, z = accelerometer_data
            print(f"加速度: x={x} [g], y={y} [g], z={z} [g]")
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Ctrl+Cで終了しました")
finally:
    serial.close()