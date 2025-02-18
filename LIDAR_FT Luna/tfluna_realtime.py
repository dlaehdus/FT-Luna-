import serial, time

# TF-Luna 데이터 읽기
def read_tfluna_data():
    while True:
        counter = ser.in_waiting  # 읽을 데이터 개수 확인
        bytes_to_read = 9
        if counter > bytes_to_read - 1:
            bytes_serial = ser.read(bytes_to_read)  # 9바이트 읽기
            ser.reset_input_buffer()  # 입력 버퍼 초기화

            if bytes_serial[0] == 0x59 and bytes_serial[1] == 0x59:  # 첫 번째 두 바이트 체크
                distance = bytes_serial[2] + bytes_serial[3] * 256  # 거리 계산
                strength = bytes_serial[4] + bytes_serial[5] * 256  # 신호 세기 계산
                temperature = bytes_serial[6] + bytes_serial[7] * 256  # 온도 계산
                temperature = (temperature / 8) - 256  # 온도 보정
                return distance / 100.0, strength, temperature

# 샘플링 속도 설정
def set_samp_rate(samp_rate=100):
    samp_rate_packet = [0x5a, 0x06, 0x03, samp_rate, 0x00, 0x00]  # 샘플링 속도 패킷
    ser.write(samp_rate_packet)  # 샘플링 속도 명령 전송
    return

# 버전 정보 조회
def get_version():
    info_packet = [0x5a, 0x04, 0x14, 0x00]
    ser.write(info_packet)  # 버전 조회 명령 전송
    time.sleep(0.1)  # 읽을 시간을 기다림
    bytes_to_read = 30  # 매뉴얼에 지정된 대로 30바이트
    t0 = time.time()
    while (time.time() - t0) < 5:
        counter = ser.in_waiting
        if counter > bytes_to_read:
            bytes_data = ser.read(bytes_to_read)
            ser.reset_input_buffer()
            if bytes_data[0] == 0x5a:
                version = bytes_data[3:-1].decode('utf-8')
                print('Version - ' + version)  # 버전 정보 출력
                return
            else:
                ser.write(info_packet)  # 잘못된 데이터가 오면 재전송
                time.sleep(0.1)

# 새로운 baudrate 설정
def set_baudrate(baud_indx=4):
    baud_hex = [
        [0x80, 0x25, 0x00],  # 9600
        [0x00, 0x4b, 0x00],  # 19200
        [0x00, 0x96, 0x00],  # 38400
        [0x00, 0xe1, 0x00],  # 57600
        [0x00, 0xc2, 0x01],  # 115200
        [0x00, 0x84, 0x03],  # 230400
        [0x00, 0x08, 0x07],  # 460800
        [0x00, 0x10, 0x0e]   # 921600
    ]
    
    # 인덱스가 범위를 벗어나지 않는지 체크
    if baud_indx < 0 or baud_indx >= len(baud_hex):
        print(f"Invalid baud index: {baud_indx}. Using default (115200).")
        baud_indx = 4  # 기본값을 115200으로 설정

    # baudrate 설정 패킷
    info_packet = [0x5a, 0x08, 0x06, baud_hex[baud_indx][0], baud_hex[baud_indx][1],
                   baud_hex[baud_indx][2], 0x00, 0x00]

    prev_ser.write(info_packet)  # 기존 baudrate 변경 명령 전송
    time.sleep(0.1)  # 잠시 대기
    prev_ser.close()  # 기존 시리얼 포트 닫기
    time.sleep(0.1)  # 잠시 대기

    # 새로운 시리얼 포트 열기
    ser_new = serial.Serial("/dev/ttyUSB0", baudrates[baud_indx], timeout=0)
    if not ser_new.isOpen():
        ser_new.open()
    bytes_to_read = 8
    t0 = time.time()
    while (time.time() - t0) < 5:
        counter = ser_new.in_waiting
        if counter > bytes_to_read:
            bytes_data = ser_new.read(bytes_to_read)
            ser_new.reset_input_buffer()
            if bytes_data[0] == 0x5a:
                indx = [ii for ii in range(0, len(baud_hex)) if
                        baud_hex[ii][0] == bytes_data[3] and
                        baud_hex[ii][1] == bytes_data[4] and
                        baud_hex[ii][2] == bytes_data[5]]
                if indx:
                    print('Set Baud Rate = {0}'.format(baudrates[indx[0]]))
                    time.sleep(0.1)
                    return ser_new
                else:
                    print("Baud rate match failed, retrying...")
            else:
                ser_new.write(info_packet)  # 잘못된 데이터 수신 시 재전송
                time.sleep(0.1)
                continue

# 전역 설정
baudrates = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]  # 지원되는 baudrate
prev_indx = 5  # 현재 baudrate 인덱스 (115200)
prev_ser = serial.Serial("/dev/ttyUSB0", baudrates[prev_indx], timeout=0)  # 기존 시리얼 포트
if not prev_ser.isOpen():
    prev_ser.open()  # 시리얼 포트 열기

baud_indx = 4  # 변경할 baudrate 인덱스 (115200)
ser = set_baudrate(baud_indx)  # 새로운 baudrate로 변경
set_samp_rate(100)  # 샘플링 속도 설정
get_version()  # TF-Luna 버전 정보 출력

# 실시간 데이터 출력 루프
print('Starting Ranging...')
while True:
    distance, strength, temperature = read_tfluna_data()  # TF-Luna 데이터 읽기
    print(distance, strength, temperature)

ser.close()  # 시리얼 포트 닫기
