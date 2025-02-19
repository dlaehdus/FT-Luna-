#include <Wire.h>  //SENSOR1_ADDR와 SENSOR2_ADDR 매크로를 정의하여, 각각 I2C 통신에서 사용될 센서의 주소를 지정합니다.

#define SENSOR1_ADDR 0x10  // 첫 번째 센서 주소 (기본값)
#define SENSOR2_ADDR 0x11  // 두 번째 센서 주소

// 지정한 센서의 레지스터 주소(reg)에서 1바이트 읽어오기
uint8_t readRegister(uint8_t sensorAddr, uint8_t reg) {  //함수 목적: 지정된 센서 주소(sensorAddr)의 특정 레지스터(reg)에서 1바이트 데이터를 읽어옵니다.
  Wire.beginTransmission(sensorAddr);   //센서와의 I2C 통신을 시작합니다
  Wire.write(reg);    //읽고자 하는 레지스터의 주소를 센서에 전송합니다.
  if (Wire.endTransmission() != 0) {    //전송 종료 후 에러가 발생하면 에러 메시지를 시리얼 모니터에 출력하고, 0을 반환합니다.
    Serial.print("I2C 통신 에러 (센서 0x");
    Serial.print(sensorAddr, HEX);
    Serial.println(")");
    return 0;
  }
  Wire.requestFrom(sensorAddr, (uint8_t)1);    //센서에서 1바이트의 데이터를 요청합니다.
  if (Wire.available()) {    //데이터가 도착하면 읽어서 반환합니다.
    return Wire.read();
  }
  return 0;
}

// 하나의 센서에서 데이터 읽어오기 (레지스터 0x00~0x05)
// 0x00: DIST_LOW, 0x01: DIST_HIGH, 0x02: AMP_LOW, 0x03: AMP_HIGH, 0x04: TEMP_LOW, 0x05: TEMP_HIGH
void readSensorData(uint8_t sensorAddr) {    //readRegister 함수를 이용해 각 레지스터의 값을 읽습니다
  uint8_t distLow = readRegister(sensorAddr, 0x00);
  uint8_t distHigh = readRegister(sensorAddr, 0x01);
  uint8_t ampLow = readRegister(sensorAddr, 0x02);
  uint8_t ampHigh = readRegister(sensorAddr, 0x03);
  uint8_t tempLow = readRegister(sensorAddr, 0x04);
  uint8_t tempHigh = readRegister(sensorAddr, 0x05);
  
  // 두 바이트를 결합하여 16비트 값으로 구성 (상위 바이트 << 8 | 하위 바이트)
  uint16_t distance = ((uint16_t)distHigh << 8) | distLow;
  uint16_t amplitude = ((uint16_t)ampHigh << 8) | ampLow;
  
  // 온도는 메뉴얼 공식: 온도(C) = (Temp/8) - 256
  int16_t tempRaw = ((int16_t)tempHigh << 8) | tempLow;
  float temperature = tempRaw / 8.0 - 256.0;
  
  Serial.print("센서 0x");
  Serial.print(sensorAddr, HEX);
  Serial.print(" - 거리: ");
  Serial.print(distance);
  Serial.print(" cm, 신호 강도: ");
  Serial.print(amplitude);
  Serial.print(", 온도: ");
  Serial.print(temperature);
  Serial.println(" C");
}

void setup() {
  Serial.begin(115200);   // 시리얼 모니터 초기화
  Wire.begin();           // I2C 통신 시작
  
  // TF-Luna가 I2C 모드로 동작하려면 핀 5를 반드시 GND에 연결해야 합니다.
  // 회로 연결: 
  // - 센서의 핀 1 → +5V
  // - 센서의 핀 4, 5 → GND
  // - 센서의 핀 2 → SDA (아두이노 MEGA 핀 20)
  // - 센서의 핀 3 → SCL (아두이노 MEGA 핀 21)
}

void loop() {
  // 첫 번째 센서 데이터 읽기
  readSensorData(SENSOR1_ADDR);
  delay(20); // 약 200ms 주기로 데이터 갱신
  // 두 번째 센서 데이터 읽기
  readSensorData(SENSOR2_ADDR);
  delay(20); // 약 200ms 주기로 데이터 갱신
}
