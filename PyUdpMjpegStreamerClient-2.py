from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
import cv2
import struct


class VideoClientProtocol(DatagramProtocol):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        # self.capture = cv2.VideoCapture(0)
        self.frame=cv2.imread("check-1.png")
        self.MAX_DATAGRAM_SIZE = 8192 - 6  # 65507 is the max UDP payload size minus the header size ########################################################################################################Confused here

    def startProtocol(self):
        self.send_frame()

    def send_frame(self):
        # ret, frame = self.capture.read()
        # if not ret:
        #     return

        # Encode frame to bytes
        ret, frame_encoded = cv2.imencode('.jpg', self.frame)
        frame_data = frame_encoded.tobytes()

        count = (len(frame_data) + self.MAX_DATAGRAM_SIZE - 1) // self.MAX_DATAGRAM_SIZE
        # print(count)
        for i in range(count):
            start = i * self.MAX_DATAGRAM_SIZE
            end = min((i + 1) * self.MAX_DATAGRAM_SIZE, len(frame_data))
            data = frame_data[start:end]
            header = struct.pack('>I', count) + bytes([i+1]) + bytes([0])  # class_id = 0 for video frame
            self.transport.write(header + data, (self.host, self.port))

        reactor.callLater(0.1, self.send_frame)  # approximately 30 frames per second


def main():
    host = '127.0.0.1'
    port = 9999
    reactor.listenUDP(0, VideoClientProtocol(host, port))
    reactor.run()


if __name__ == "__main__":
    main()