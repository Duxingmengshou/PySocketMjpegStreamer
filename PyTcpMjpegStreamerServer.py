import base64

from twisted.internet import reactor, protocol
from twisted.web import server, resource
from twisted.internet import reactor
import datetime
import time
import cv2
import numpy as np
import uuid


class FrameDataServer(protocol.Protocol):
    def __init__(self, httpServer, clientID):
        self.buffer = b''
        self.HTTPServer = httpServer
        self.ClientID = clientID
        self.StartTime = time.time()
        self.EndTime = time.time()
        self.FrameCount = 0

    def dataReceived(self, data):
        self.buffer += data
        while True:
            if len(self.buffer) < 4:
                break
            length = int.from_bytes(self.buffer[:4], byteorder='big')
            # print(f'{len(self.buffer)}/{length}')
            if len(self.buffer) < 4 + length:
                break
            frame_data = self.buffer[4:4 + length]
            self.buffer = self.buffer[4 + length:]

            frame_type = frame_data[0]
            frame_data = frame_data[1:]
            # print(frame_type)

            if frame_type == 1:
                self.EndTime = time.time()
                self.FrameCount += 1
                fps = self.FrameCount / (self.EndTime - self.StartTime)
                frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
                datestr = str(datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S"))
                cv2.putText(frame, datestr, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                cv2.putText(frame, f"fps: {fps:.4}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                self.HTTPServer.frames[self.ClientID] = frame
            elif frame_type == 2:
                self.EndTime = time.time()
                self.FrameCount += 1
                fps = self.FrameCount / (self.EndTime - self.StartTime)
                frame_data = base64.b64decode(frame_data)
                frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
                datestr = str(datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S"))
                cv2.putText(frame, datestr, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                cv2.putText(frame, f"fps: {fps:.4}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                self.HTTPServer.frames[self.ClientID] = frame
            elif frame_type == 3:
                self.EndTime = time.time()
                self.FrameCount += 1
                fps = self.FrameCount / (self.EndTime - self.StartTime)
                frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
                datestr = str(datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S"))
                cv2.putText(frame, datestr, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                cv2.putText(frame, f"fps: {fps:.4}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                self.HTTPServer.frames[self.ClientID] = frame
            elif frame_type == 32:
                self.EndTime = time.time()
                self.FrameCount += 1
                fps = self.FrameCount / (self.EndTime - self.StartTime)
                frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
                datestr = str(datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S"))
                cv2.putText(frame, datestr, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                cv2.putText(frame, f"fps: {fps:.4}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
                self.HTTPServer.frames[self.ClientID] = frame

    def connectionLost(self, reason):
        print(f"Connection lost: {reason.getErrorMessage()}")
        if self.ClientID in self.HTTPServer.frames:
            del self.HTTPServer.frames[self.ClientID]


class FrameDataServerFactory(protocol.Factory):
    def __init__(self, http_server):
        self.http_server = http_server

    def buildProtocol(self, addr):
        client_id = str(uuid.uuid1())  # Generate a unique client ID
        print(f"New connection with ID: {client_id}")
        return FrameDataServer(self.http_server, client_id)


class MJPEGStream(resource.Resource):
    isLeaf = True

    def __init__(self):
        super().__init__()
        self.frames = {}

    def render_GET(self, request):
        client_id = request.path.decode().strip('/')
        if client_id in self.frames:
            request.setHeader(b'Content-Type', b'multipart/x-mixed-replace; boundary=frame')
            self._write_frame(request, client_id)
            return server.NOT_DONE_YET
        elif client_id == "device":
            devices = "<p>Devices</p>"
            for device in self.frames.keys():
                devices += f"<br><a href=\"http://127.0.0.1:8080/{device}\">{device}</a></br>"
            return devices.encode()
        else:
            request.setResponseCode(404)
            return b'Client not found'

    def _write_frame(self, request, client_id):
        if client_id in self.frames:
            _, jpeg = cv2.imencode('.jpg', self.frames[client_id])
            frame = jpeg.tobytes()

            request.write(
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
            )

        reactor.callLater(0.1, self._write_frame, request, client_id)  # Adjust the frame rate as needed


if __name__ == "__main__":
    stream = MJPEGStream()

    site = server.Site(stream)
    reactor.listenTCP(8080, site)

    factory = FrameDataServerFactory(stream)
    reactor.listenTCP(8000, factory)

    reactor.run()
