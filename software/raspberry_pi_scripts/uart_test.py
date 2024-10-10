import serial
import time

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1) # Open serial port at 9600 baud
ser.reset_input_buffer()
while True:
    motor1_speed = input("motor1_speed: ")
    motor2_speed = input("motor2_speed: ")
    command = "{},{}\n".format(motor1_speed, motor2_speed)
    ser.write(command.encode('utf-8'))
    line = ser.readline().decode('utf-8').rstrip()
    print(line)
    time.sleep(1)  # Delay between commands