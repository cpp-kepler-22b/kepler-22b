import cv2
import numpy as np
import base64
from websocket_server import WebsocketServer
import threading
import queue
import time

class vidServer():
    def __init__(self, port):
        self.que = queue.Queue()
        self.startTime = time.time()
        server_thread = threading.Thread(target=self.__startServer, args=(self.que, port))
        server_thread.daemon = True
        server_thread.start()

    def __startServer(self, que, port):
        server = WebsocketServer(host='', port=port)
        server.set_fn_new_client(self.new_client)
        server.set_fn_client_left(self.client_left)
        server.set_fn_message_received(self.message_received)
        server.run_forever()

    def getImg(self):
        # Image from client
        elapsedWaitTime = time.time() - self.startTime
        if not self.que.empty():
            self.startTime = time.time()
            item = self.que.get()
            self.recent_message = item
            return item
        # Stalk image to prevent the crash of lack of data
        elif elapsedWaitTime > 3:
            image = cv2.imread('imgs/disconnected.png')
            return image
        return None
    
    def new_client(self, client, server):
        print(f"New client connected and was given id {client['id']}")

    def client_left(self, client, server):
        print(f"Client({client['id']}) disconnected")

    def message_received(self, client, server, message):
        img_data = base64.b64decode(message)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is not None:
            self.que.put(img)