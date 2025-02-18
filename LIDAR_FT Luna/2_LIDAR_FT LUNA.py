import serial,time,sys

# APPENDIX I SERIAL PORT OUTPUT FORMAT 
# 7. Output with Device ID
def OUTPUT():
    while True:
        counter = ser.in_waiting
        if counter > 12:
            bytes_serial = ser.read(13)
            ser.reset_input_buffer()
            if bytes_serial[0] == 90 and bytes_serial[1] == 13 and bytes_serial[2] == 0:
                dis = (bytes_serial[3] + bytes_serial[4]*256)/100.0
                amp = bytes_serial[5] + bytes_serial[6]*256
                id = bytes_serial[11]
                sys.stdout.write(f"\r거리:{dis}m  신호 강도:{amp} 아이디:{hex(id)}")
                sys.stdout.flush()
        time.sleep(0.01)

# Appendix II Serial communication protocol
# 2. System software restore ID_SOFT_RESET=0x02
def ID_SOFT_RESET():
    packet= [0x5A,0x04,0x02,0x00]
    ser.write(packet)
    time.sleep(0.1)
    bytes_to_read = 5
    t = time.time()
    while (time.time()-t)<5:
    # 5초 이상 걸릴시 프로그램 종료
        counter = ser.in_waiting
        if counter > bytes_to_read:
            bytes_data = ser.read(bytes_to_read)
            ser.reset_input_buffer() 
            if bytes_data[0] == 0x5A:
                IDID = bytes_data[3]
                print("상태(0정상) :",IDID)
                return
            else:
                ser.write(packet)
                time.sleep(0.1)

# 5. Output format setting ID_OUTPUT_FORMAT=0x05
def ID_OUTPUT_FORMAT(FORMAT):
    packet= [0x5A,0x05,0x05,FORMAT,0x00]
    # 3번째 바이트가 포멧 지정
    # 0x01 = 9-byte/cm
    # 0x02 = PIX
    # 0x06 = 9-byte/mm
    # 0x07 = 32-byte with timestamp
    # 0x08 = ID-0
    # 0x09 = 8-byte/cm
    # 0x0A = Output with device ID
    ser.write(packet)
    time.sleep(0.1)
    bytes_to_read = 5
    t = time.time()
    while (time.time()-t)<5:
    # 5초 이상 걸릴시 프로그램 종료
        counter = ser.in_waiting
        if counter > bytes_to_read:
            bytes_data = ser.read(bytes_to_read)
            ser.reset_input_buffer() 
            if bytes_data[0] == 0x5A:
                IDID = bytes_data[3]
                print("FORMAT:",hex(IDID))
                return
            else:
                ser.write(packet)
                time.sleep(0.1)

# 6. Baud rate setting ID_BAUD_RATE=0x06
def ID_BAUD_RATE(new_baud):
    # 지원하는 보드레이트 목록과 해당하는 3바이트 HEX 값
    baudrates = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
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
    if new_baud not in baudrates:
        print("지원하지 않는 보드레이트입니다!")
        return None
    baud_indx = baudrates.index(new_baud)
    # 보드레이트 변경 명령어 패킷 구성
    info_packet = [0x5A, 0x08, 0x06,
                   baud_hex[baud_indx][0],
                   baud_hex[baud_indx][1],
                   baud_hex[baud_indx][2],
                   0x00,0x00]
    # 기존 시리얼 포트(예: ser)가 이미 열려 있다고 가정하고 사용
    # 보드레이트 변경 명령 전송
    ser.write(bytes(info_packet))
    time.sleep(0.1)  # 잠시 대기 후
    ser.close()      # 기존 포트를 닫음
    time.sleep(0.1)
    # 새로운 보드레이트로 시리얼 포트를 다시 엶 (포트 이름은 환경에 맞게 수정)
    ser_new = serial.Serial("/dev/ttyUSB0", new_baud, timeout=0)
    if not ser_new.isOpen():
        ser_new.open()
    # 응답 데이터(8바이트)를 읽어 변경 성공 여부 확인 (최대 5초 대기)
    bytes_to_read = 8
    t0 = time.time()
    while (time.time() - t0) < 5:
        counter = ser_new.in_waiting
        if counter >= bytes_to_read:
            bytes_data = ser_new.read(bytes_to_read)
            ser_new.reset_input_buffer()
            if bytes_data[0] == 0x5A:
                # 응답에서 보드레이트 관련 3바이트를 비교하여 인덱스 찾기
                indx = [ii for ii in range(len(baud_hex))
                        if baud_hex[ii][0] == bytes_data[3] and
                           baud_hex[ii][1] == bytes_data[4] and
                           baud_hex[ii][2] == bytes_data[5]]
                if indx:
                    print('Baud Rate = {0:d}'.format(baudrates[indx[0]]))
                    time.sleep(0.1)
                    return ser_new
            else:
                # 올바른 응답이 아니라면 명령 재전송
                ser_new.write(bytes(info_packet))
                time.sleep(0.1)
    print("보드레이트 변경 응답을 받지 못했습니다.")
    return None

# 9. I2C slave machine address configurationID_I2C_SLAVE_ADDR=0x0B
def ID_I2C_SLAVE_ADDR(ID):
    packet = [0x5A,0x05,0x0B,ID,00]
    ser.write(packet)
    time.sleep(0.1)
    bytes_to_read = 5
    t = time.time()
    while (time.time()-t)<5:
    # 5초 이상 걸릴시 프로그램 종료
        counter = ser.in_waiting
        if counter > bytes_to_read:
            bytes_data = ser.read(bytes_to_read)
            ser.reset_input_buffer() 
            if bytes_data[0] == 0x5A:
                IDID = bytes_data[3]
                print("ID:",hex(IDID))
                return
            else:
                ser.write(packet)
                time.sleep(0.1)

#10. Restore default setting ID_RESTORE_DEFAULT=0x10
def ID_RESTORE_DEFAULT():
    packet= [0x5A,0x04,0x10,0x00]
    ser.write(packet)
    time.sleep(0.1)
    bytes_to_read = 5
    t = time.time()
    while (time.time()-t)<5:
    # 5초 이상 걸릴시 프로그램 종료
        counter = ser.in_waiting
        if counter > bytes_to_read:
            bytes_data = ser.read(bytes_to_read)
            ser.reset_input_buffer() 
            if bytes_data[0] == 0x5A:
                IDID = bytes_data[3]
                print("상태(0정상) :",IDID)
                return
            else:
                ser.write(packet)
                time.sleep(0.1)

#11. Save current setting ID_SAVE_SETTINGS=0x11
def ID_SAVE_SETTINGS():
    packet= [0x5A,0x04,0x11,0x00]
    ser.write(packet)
    time.sleep(0.1)
    bytes_to_read = 5
    t = time.time()
    while (time.time()-t)<5:
    # 5초 이상 걸릴시 프로그램 종료
        counter = ser.in_waiting
        if counter > bytes_to_read:
            bytes_data = ser.read(bytes_to_read)
            ser.reset_input_buffer() 
            if bytes_data[0] == 0x5A:
                IDID = bytes_data[3]
                print("상태(0정상) :",IDID)
                return
            else:
                ser.write(packet)
                time.sleep(0.1)

# 13. Get full-length version number ID_GET_FULL_VERSION=0x14
def ID_GET_FULL_VERSION():
    packet = [0x5a,0x04,0x14,0x00]
    ser.write(packet)
    time.sleep(0.1)
    bytes_to_read = 30
    t = time.time()
    while (time.time()-t)<5:
    # 5초 이상 걸릴시 프로그램 종료
        counter = ser.in_waiting
        if counter > bytes_to_read:
            bytes_data = ser.read(bytes_to_read)
            ser.reset_input_buffer() 
            if bytes_data[0] == 0x5A:
                version = bytes_data[3:-1].decode('utf-8')
                # bytes_data[3:-1]은 버전 정보가 들어있는 부분으로, 이 데이터를 utf-8 형식으로 디코딩하여 문자열로 변환합니다.
                # 3부터 10까지는 32,84,70,45,76,117,110,97 로 아스키코드값이며 문자로 변환하면 공백 TF-Luna, 
                # 12부터 19까지는 32,32,32,32,32,83,84,68로 공백이 이어지가다 STD를 출력함 
                # 21부터 28까지는 48,51,46,48,50,46,48,48로 03.02.00
                print('Version -'+version)
                return
            else:
                ser.write(packet)
                time.sleep(0.1)




ser = serial.Serial(
    port = "/dev/ttyUSB0",
    baudrate = 115200,
    bytesize = 8,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1)
ser.reset_input_buffer()
ser.reset_output_buffer()



# 최종 정보 출력
OUTPUT()




# 2. 소프트웨어 리셋
# ID_SOFT_RESET()

# 5. APPENDIX I SERIAL PORT OUTPUT FORMAT 모드 변경
# ID_OUTPUT_FORMAT(0x0A)

# 6. 통신속도 설정하기
# ID_BAUD_RATE(115200)

# 9. 아이디 설정하기 range [0x08, 0x77]
# ID_I2C_SLAVE_ADDR(0x11)

# 10. 기본 설정 복원
# ID_RESTORE_DEFAULT()

# 11. 세팅 저장
# ID_SAVE_SETTINGS()

# 13. 전체 버전 정보 읽기
# ID_GET_FULL_VERSION()



#시리얼 통신에 대해 대략적으로 이해함, APPENDIX I SERIAL PORT OUTPUT FORMAT의 모드를 변환하는 방법에 대해 알아야함
#5. Output format setting ID_OUTPUT_FORMAT=0x05를 사용하면 바꿀수 있다는 것을 깨달음
# 기본 설정 복원후 소프트웨어 리셋후 통신속도 후 모드 변경 아이디 설정후 세팅저장