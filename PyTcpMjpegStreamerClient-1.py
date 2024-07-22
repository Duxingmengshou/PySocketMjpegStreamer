import cv2
from twisted.internet import reactor, protocol


class FrameDataClient(protocol.Protocol):
    def connectionMade(self):
        self.ColorImg = cv2.imread("check-1.png")
        self.cap = cv2.VideoCapture(0)
        self.sendFrames()

    def sendFrames(self):

        _, self.ColorImg = self.cap.read()
        _, encoded_frame = cv2.imencode('.jpeg', self.ColorImg)
        encoded_frame = int(1).to_bytes(1, byteorder='big') + encoded_frame.tobytes()
        frame_data = len(encoded_frame).to_bytes(4, byteorder='big') + encoded_frame
        self.transport.write(frame_data)
        reactor.callLater(0.02, self.sendFrames)  # Send frames every 0.1 seconds

    def dataReceived(self, data):
        print(f"Received data from server: {data}")


class FrameDataClientFactory(protocol.ClientFactory):
    def buildProtocol(self, addr):
        return FrameDataClient()

    def clientConnectionFailed(self, connector, reason):
        print(f"Connection failed: {reason.getErrorMessage()}")
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print(f"Connection lost: {reason.getErrorMessage()}")
        reactor.stop()


if __name__ == "__main__":
    factory = FrameDataClientFactory()
    reactor.connectTCP('localhost', 8000, factory)
    reactor.run()
