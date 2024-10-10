from classes.uartCom import uartCom
from classes.serverThread import parallelServer
import time

def main():
    startServer = parallelServer('', 65432)
    coms = uartCom('/dev/serial0', 9600, 0.1)
    print("Doing some work in the background..")
    while True:
        # Get command that is sent from gui
        motorCommand = startServer.getCommand()
        if motorCommand is not None:
            print("Command is:", motorCommand)
            coms.sendCommand(motorCommand)


        command = coms.getCommand()
        if command is not None:
            print("Command is:", command)
        else:
            print("waiting for command")

        time.sleep(1)

if __name__ == "__main__":
    main()