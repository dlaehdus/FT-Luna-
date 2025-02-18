import serial

#Appendix II Serial communication protocol

#1. Version information ID_GET_VERSION=0x01
def ID_GET_VERSION(ser):
    # 버전 조회 명령 (ID_GET_VERSION = 0x01)
    command = [0x5A, 0x04, 0x40, 0x00]
    print(f"전송된 패킷: {' '.join([hex(b) for b in command])}")
    # 응답 읽기 (최대 10바이트 예상)
    response = ser.read(7)
    print(f"수신된 응답: {' '.join([hex(b) for b in response])}")
    # 응답 최소 길이 확인 (헤더, 길이, ID, 버전 3바이트, 체크섬)
    if len(response) != 7:
        print("응답 데이터가 부족합니다!")
        return None
    # 응답 패킷 검증 0은 헤드, 2는 아이디
    if response[0] != 0x5A:
            print("잘못된 헤더:", response[0])
            return None
    # ID 검증 (바이트 2는 0x01여야 함)
    if response[2] != 0x01:
            print("잘못된 명령 ID:", response[2])
            return None
    # 체크섬 검증
    if (sum(response[:-1]) & 0xFF) != response[-1]:
        print("체크섬 오류")
        return None
    ver_bytes = response[3:6]
    version_str = f"{ver_bytes[2]}.{ver_bytes[1]}.{ver_bytes[0]}"
    return version_str
    
#2. System software restore ID_SOFT_RESET=0x02
def ID_SOFT_RESET(port):
    ID_SOFT_RESET = 0x02
    header = 0x5A
    length = 4  # 헤더, 길이, ID, 체크섬의 총 길이
    
    # 명령 생성: 초기 명령 리스트 구성
    command = [header, length, ID_SOFT_RESET, 0x00]
    
    # 체크섬 계산: 모든 바이트의 합을 1바이트로 제한
    checksum = sum(command) & 0xFF
    command.append(checksum)
    
    # 직렬 포트로 명령 전송 (serial 모듈은 이미 임포트된 상태)
    ser = serial.Serial(port, 115200, timeout=1)
    ser.write(bytearray(command))
    
    # 응답은 5바이트로 예상: 헤더, 길이, ID, 상태, 체크섬
    response = ser.read(5)
    ser.close()
    
    # 응답 처리
    if response and len(response) == 5:
        resp_header = response[0]
        resp_length = response[1]
        resp_id = response[2]
        resp_status = response[3]
        resp_checksum = response[4]
        
        # 응답 체크섬 재계산 (헤더, 길이, ID, 상태)
        calc_checksum = (resp_header + resp_length + resp_id + resp_status) & 0xFF
        
        if resp_header == header and resp_id == ID_SOFT_RESET and resp_checksum == calc_checksum:
            return "Success" if resp_status == 0 else "Fail (Status: {})".format(resp_status)
        else:
            return "Invalid response format"
    else:
        return "No response or incorrect length"

#3. Output frequency ID_SAMPLE_FREQ=0x03
def ID_SAMPLE_FREQ(ser, samp_rate=100):
    #헤더바이트, 패킷길이 6바이트. 명령어 아이디, 설정할 샘플링 속도,샘플링 속도의 LSB, 체크섬
    packet = [0x5A, 0x06, 0x03, samp_rate, 0x00, 0x00]
    # 체크섬 계산 (0~4번 바이트 합의 하위 8비트)
    # 마지막 바이트에 체크섬 저장
    packet[-1] = sum(packet[:-1]) & 0xFF
    # 명령어 전송
    ser.write(bytes(packet))
    print(f"샘플링 속도를 {samp_rate}Hz로 설정하는 명령을 전송했습니다.")



#시리얼 포트 설정하고 열기 FT Luna는 패리티 비트 없음, 8데이터 비트, 1스톱 비트
ser = serial.Serial(
    port = "/dev/ttyUSB0",
    baudrate = 115200,
    bytesize = 8,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1)


#입력 버퍼를 삭제하는 함수 (이전에 수신된 데이터가 남아 있으면 모두 삭제)
ser.reset_input_buffer()
#출력 버퍼를 삭제하는 함수 (전송 대기중인 데이터를 삭제함)
ser.reset_output_buffer()
#샘플링 속도를 변경하는 명령을 전송하는 함수 루나는 10HZ~250HZ 까지 가능함 자동으로 체크섬 계산시 16진수로 변홤
ID_SAMPLE_FREQ(ser, 250)
#루나 버전 정보 가져오기(실패)
ID_GET_VERSION(ser) 