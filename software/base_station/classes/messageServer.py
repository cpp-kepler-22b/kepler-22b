import socket
import threading
import queue
import time

class sendCommand():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.msgQueue = queue.Queue()
        self.threadRunning = False
        self.msgThread = threading.Thread(target=self.__atemptConnection, args=())
        self.msgThread.daemon = True
        self.msgThread.start()


    def __atemptConnection(self):
        while True:
            try: 
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((self.host, self.port))
                    #convert the msg string into bytes
                    self.threadRunning = True
                    while True:
                        msg = self.msgQueue.get()
                        if msg is not None:
                            info = msg.encode('utf-8')
                            s.sendall(info)
                        data = s.recv(1024)
                        print(data)
                print('Confirmation from server', repr(data))
            except:
                self.threadRunning = False
                print("connection issue. IP could be incorrect")
                time.sleep(10)
        print("sendCommand thread disconnected")

    def sendMsg(self, msg):
        self.msgQueue.put(msg)
        if not self.threadRunning:
            print("Unable to send message currently...")