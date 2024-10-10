import serial
import time
import threading
import queue
import json

class uartCom():
    def __init__(self, path, baud, timeDelay):
        self.que = queue.Queue()
        self.commandToArduino = queue.Queue()
        uart_thread = threading.Thread(target=self.__attemptConnection, args=(path, baud, timeDelay))
        uart_thread.daemon = True
        uart_thread.start()

    def sendCommand(self, command):
        #ADD feature to check if the comand is valid
        self.commandToArduino.put(command)

    def getCommand(self):
        if not self.que.empty():
            item = self.que.get()
            return item
        return None

    def __communicate(self, timeDelay):
        while(1):
            command = self.commandToArduino.get() 
            if command is not None:
                print("Received command:", command)
                speeds = json.loads(command)
                motor1_speed = speeds["Motor1"]
                motor2_speed = speeds["Motor2"] 
                arduinoCommand = "{},{}\n".format(motor1_speed, motor2_speed)
                self.com.write(arduinoCommand.encode('utf-8'))
                time.sleep(timeDelay)

            line = self.com.readline().decode('utf-8').rstrip()
            # Check if there's incoming data
            if line is not '':  
                self.que.put(line)

    def __attemptConnection(self, path, baud, timeDelay):
        self.com = None
        while(1):
            try:
                self.com = serial.Serial(path, baud, timeout=1)
                self.com.flush()
                break
            except:
                print("Serial Connection attempt failed")
                time.sleep(3)
        self.__communicate(timeDelay)