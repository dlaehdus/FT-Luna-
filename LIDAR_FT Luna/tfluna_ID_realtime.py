import serial,time

############################
# Serial Functions
############################         
def read_tfluna_data():
    while True:
        counter = ser.in_waiting # count the number of bytes waiting to be read
        bytes_to_read = 13
        if counter > bytes_to_read-1:
            bytes_serial = ser.read(bytes_to_read) # read 9 bytes
            ser.reset_input_buffer() # reset buffer
            # print(hex(bytes_serial[0]), hex(bytes_serial[1]), hex(bytes_serial[2]))
            if bytes_serial[0] == 0x5A and bytes_serial[1] == 0x0D and bytes_serial[2] == 0x00: # check first three bytes
                distance = bytes_serial[3] + bytes_serial[4]*256 # distance in next two bytes
                dev_id = bytes_serial[-2]
                return distance/100.0, hex(dev_id)

def set_samp_rate(samp_rate=100):
    ##########################
    # change the sample rate
    samp_rate_packet = [0x5A,0x06,0x03,samp_rate,00,00] # sample rate byte array
    ser.write(samp_rate_packet) # send sample rate instruction
    return

def set_output_format(command):
    ##########################
    # change the sample rate
    samp_rate_packet = [0x5A,0x05,0x05,command,00] # sample rate byte array
    ser.write(samp_rate_packet) # send sample rate instruction
    return

def set_Dev_ID(command):
    ##########################
    # change the sample rate
    samp_rate_packet = [0x5A,0x05,0x0B,command,00] # sample rate byte array
    ser.write(samp_rate_packet) # send sample rate instruction
    return

def save_setting():
    samp_rate_packet= [0x5A,0x04,0x11,0x00]
    ser.write(samp_rate_packet) # send sample rate instruction

def get_version():
    ##########################
    # get version info
    info_packet = [0x5A,0x04,0x40,0x00]

    ser.write(info_packet) # write packet
    time.sleep(0.1) # wait to read
    bytes_to_read = 30 # prescribed in the product manual
    t0 = time.time()
    while (time.time()-t0)<5:
        counter = ser.in_waiting
        if counter > bytes_to_read:
            bytes_data = ser.read(bytes_to_read)
            ser.reset_input_buffer()
            if bytes_data[0] == 0x5a:
                version = bytes_data[3:-1].decode('utf-8')
                print('Version -'+version) # print version details
                return
            else:
                ser.write(info_packet) # if fails, re-write packet
                time.sleep(0.1) # wait

############################
# Configurations
############################
ser = serial.Serial("/dev/ttyUSB0", 115200,timeout=0)
ser.reset_input_buffer()
ser.reset_output_buffer()
# get_version() # print version info for TF-Luna
set_samp_rate(100) # set sample rate 1-250

# set_output_format(0x0A)
# set_Dev_ID(0x40)
# save_setting()

############################
# Real-Time Plotter Loop
############################
print('Starting Ranging...')
while True:
    distance, dev_id = read_tfluna_data() # read values
    print(distance,dev_id)

# ser.close() # close serial port

