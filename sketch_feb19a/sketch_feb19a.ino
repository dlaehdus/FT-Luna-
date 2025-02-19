#include <Wire.h>  //설명: I2C 통신을 위해 필요한 Wire 라이브러리를 포함합니다.

#define TF_LUNA_ADDR 0x10  // TF‑Luna의 기본 7비트 I2C 주소 (0x10 = 16)

void setup() {
  Serial.begin(115200);  // 시리얼 모니터 초기화
  Wire.begin();          // I2C 통신 시작
  
  // TF-Luna가 I2C 모드로 동작하려면 핀 5를 반드시 GND에 연결해야 함을 확인
  // (핀 1: +5V, 핀 4,5: GND; 핀 2: SDA -> 아두이노 핀 20, 핀 3: SCL -> 아두이노 핀 21)
}

uint8_t readRegister(uint8_t reg) {
  Wire.beginTransmission(TF_LUNA_ADDR);
  Wire.write(reg);              // 읽고자 하는 레지스터 주소 전송
  if(Wire.endTransmission() != 0) {
    Serial.println("I2C 통신 에러 발생");
    return 0;
  }
  
  Wire.requestFrom(TF_LUNA_ADDR, (uint8_t)1);
  if(Wire.available()) {
    return Wire.read();
  }
  return 0;
}

void loop() {
  // 0x00: DIST_LOW, 0x01: DIST_HIGH → 거리 (cm)
  uint8_t distLow = readRegister(0x00);
  uint8_t distHigh = readRegister(0x01);
  uint16_t distance = ((uint16_t)distHigh << 8) | distLow;  
  // 위 표현은 distHigh를 16비트로 캐스팅한 후 왼쪽으로 8비트 시프트하여 상위 바이트로 만들고,
  // 하위 바이트인 distLow와 OR 연산하여 하나의 16비트 값(distance)을 구성하는 과정입니다.

  // 0x02: AMP_LOW, 0x03: AMP_HIGH → 신호 강도
  uint8_t ampLow = readRegister(0x02);
  uint8_t ampHigh = readRegister(0x03);
  uint16_t amplitude = ((uint16_t)ampHigh << 8) | ampLow;
  
  // 0x04: TEMP_LOW, 0x05: TEMP_HIGH → 온도 (온도 변환 공식: 온도 = (Temp/8) - 256)
  uint8_t tempLow = readRegister(0x04);
  uint8_t tempHigh = readRegister(0x05);
  int16_t tempRaw = ((int16_t)tempHigh << 8) | tempLow;
  float temperature = tempRaw / 8.0 - 256.0;
  
  Serial.print("거리: ");
  Serial.print(distance);
  Serial.print(" cm, 신호 강도: ");
  Serial.print(amplitude);
  Serial.print(", 온도: ");
  Serial.print(temperature);
  Serial.println(" C");
  
  delay(10);  // 100ms 간격으로 데이터 갱신
}

