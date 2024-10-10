import cv2
import base64
import websocket
import threading
import time

class vidClient():
    def __init__(self, ip, port):
        server_thread = threading.Thread(target=self.__startClient, args=(ip, port))
        server_thread.daemon = True
        server_thread.start()

    def __startClient(self, ip, port):
        destination = f"ws://{ip}:{port}"
        retry_interval = 3  # Time to wait between connection attempts, in seconds
        while True:
            print("test")
            try:
                print("destination:", destination)
                ws = websocket.WebSocketApp(destination,
                                            on_open=self.on_open)
                ws.run_forever()
            except:
                print(f"Connection failed")
                time.sleep(retry_interval)  

    def on_open(self, ws):
        while True:
            try:
                cap = cv2.VideoCapture(0)
                print("capture cam")
                frame_check = 10  # Number of consecutive frames to check for
                invalid_frames = 0  # Counter for consecutive invalid frames
                
                while cap.isOpened():
                    ret, frame = cap.read()

                    if not ret or frame is None:
                        invalid_frames += 1
                    
                    if invalid_frames >= frame_check:
                        print("Camera may have been disconnected.")
                        raise Exception

                    if ret:
                        _, buffer = cv2.imencode('.jpg', frame)
                        ws.send(base64.b64encode(buffer).decode('utf-8'))
                    cv2.waitKey(10) 
            except:
                print("Cam failed")
            finally:
                print("released camera")
                cap.release()
                time.sleep(3)
