import threading
import socket
import queue
import time

class receiveMessage():
    def __init__(self, host, port):
        self.que = queue.Queue()
        self.recent_message = None
        self.host = host
        self.port = port

        server_thread = threading.Thread(target=self.__getServerInfo, args=(self.que,))
        # Without setting to daemon to true the thread will never close application
        server_thread.daemon = True
        server_thread.start()
        print("Server Thread started.\n")

    def getMessage(self):
        if not self.que.empty():
            item = self.que.get()
            self.recent_message = item
            return item
        return None

    def getRecentMsg(self):
        return self.recent_message

    # Recieve info from server
    def __getServerInfo(self, que):
        # Set the host and port
        HOST = self.host
        PORT = self.port 

        # Create a socket object
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Bind the socket to the address and port
            s.bind((HOST, PORT))
            # Start listening for incoming connections
            s.listen()

            print(f"Server listening on {HOST}:{PORT}")
            while True:
                # Accept a new connection
                conn, addr = s.accept()
                with conn:
                    print('Connected by', addr)
                    while True:
                        # Receive data from the client
                        data = conn.recv(1024)
                        if not data:
                            break  # Break the loop if no more data is received
                        print('Received', repr(data))
                        message = data.decode('utf-8')

                        # Todo: Add filtering for useless messages
                        que.put(message)
                        # Echo the received data back to the client
                        conn.sendall(b'Data received')