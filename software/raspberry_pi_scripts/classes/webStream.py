import io
import logging
import socketserver
from http import server
from threading import Condition
import threading
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

PAGE = """\
<html>
<head>
<title>picamera2 MJPEG streaming demo</title>
</head>
<body>
<h1>Picamera2 MJPEG Streaming Demo</h1>
<img src="stream.mjpg" width="640" height="480" />
</body>
</html>
"""

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

class StreamingHandler(server.BaseHTTPRequestHandler):
    output = None  # Class variable to hold the streaming output

    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with self.output.condition:
                        self.output.condition.wait()
                        frame = self.output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, output):
        super().__init__(server_address, RequestHandlerClass)
        self.RequestHandlerClass.output = output  # Assign the shared output to all handlers

    allow_reuse_address = True
    daemon_threads = True

class startStream():
    def __init__(self):
        self.output = StreamingOutput()  # Instance variable to hold the streaming output
        server_thread = threading.Thread(target=self.__startStream)
        server_thread.daemon = True
        server_thread.start()

    def __startStream(self):
        picam2 = Picamera2()
        picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
        picam2.start_recording(JpegEncoder(), FileOutput(self.output))  # Pass the output instance
        try:
            address = ('', 8000)
            server = StreamingServer(address, StreamingHandler, self.output)  # Pass the output instance to the server
            server.serve_forever()
        finally:
            picam2.stop_recording()

