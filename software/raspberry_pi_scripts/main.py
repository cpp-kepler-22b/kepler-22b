from classes.serverThread import parallelServer
from classes.vidClient import vidClient
from classes.uartCom import uartCom
from classes.streamVideo import streamVideo
import time
import json

def main():
    startServer = parallelServer('', 65432)
    starVideo = streamVideo("47.148.234.28", 6789)
    arduinoCom = uartCom('/dev/ttyACM0', 9600, 0.1)
    while(1):
        command = startServer.getCommand()
        if command is not None:
            print("Command is:", command)
            arduinoCom.sendCommand(command)


if __name__ == "__main__":
    main()