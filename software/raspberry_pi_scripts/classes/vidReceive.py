from picamera2 import Picamera2
import time
import threading
import io
import numpy as np
import cv2
import base64
import websocket

class vidClient():
    def __init__(self, ip, port):
        
        server_thread = threading.Thread(target=self.__startClient, args=(ip, port))
        server_thread.daemon = True
        server_thread.start()

    def __startClient(self, ip, port):
        destination = f"ws://{ip}:{port}"
        retry_interval = 3  # Time to wait between connection attempts, in seconds
        while True:
            try:
                print("destination:", destination)

                ws = websocket.WebSocketApp(destination,
                                        on_open=self.on_open)
                ws.run_forever()
            except:
                print(f"Connection failed")
                time.sleep(retry_interval)  # Wait before retrying
                continue  # Retry connection
    
    def on_open(self, ws):
        cap = cv2.VideoCapture('http://000.00.00.0:8000/stream.mjpg')
        while True:
            ret, frame = cap.read()
            if ret:
                _, buffer = cv2.imencode('.jpg', frame)
                ws.send(base64.b64encode(buffer).decode('utf-8'))
