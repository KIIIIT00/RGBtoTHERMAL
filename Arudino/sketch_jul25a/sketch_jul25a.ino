#include <Arduino_LSM9DS1.h>

void setup() {
  // put your setup code here, to run once:
  //シリアル通信の設定
  Serial.begin(9600);
  while(!Serial);

  if(!IMU.begin()){
    Serial.println("Failed to intialize IMU");
    while(1);
  }
  Serial.println("IMU initialized");
}

void loop() {
  // put your main code here, to run repeatedly:
  float x, y, z;

  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(x, y, z);
    Serial.print("Accelerometer: ");
    Serial.print(x);
    Serial.print(", ");
    Serial.print(y);
    Serial.print(", ");
    Serial.println(z);
  }

  //データ取得の間隔を調整
   delay(100);
}
