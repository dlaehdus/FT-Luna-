#include <Wire.h>

#define SENSOR1_ADDR 0x10  // 첫 번째 센서 주소
#define SENSOR2_ADDR 0x11  // 두 번째 센서 주소

// 지정한 센서의 레지스터에서 1바이트 읽어오기
uint8_t readRegister(uint8_t sensorAddr, uint8_t reg) {
  Wire.beginTransmission(sensorAddr);
  Wire.write(reg);
  if (Wire.endTransmission() != 0) {
    Serial.print("I2C 통신 에러 (센서 0x");
    Serial.print(sensorAddr, HEX);
    Serial.println(")");
    return 0;
  }
  Wire.requestFrom(sensorAddr, (uint8_t)1);
  if (Wire.available()) {
    return Wire.read();
  }
  return 0;
}

// 센서 데이터 읽기
void readSensorData(uint8_t sensorAddr) {
  uint8_t distLow = readRegister(sensorAddr, 0x00);
  uint8_t distHigh = readRegister(sensorAddr, 0x01);
  uint16_t distance = ((uint16_t)distHigh << 8) | distLow;

  Serial.print("센서 0x");
  Serial.print(sensorAddr, HEX);
  Serial.print(" - 거리: ");
  Serial.print(distance);
  Serial.println(" cm");
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
}

void loop() {
  readSensorData(SENSOR1_ADDR);
  delay(1000); // 센서 간 지연 시간
  readSensorData(SENSOR2_ADDR);
  delay(1000); // 주기적 지연 시간
}
