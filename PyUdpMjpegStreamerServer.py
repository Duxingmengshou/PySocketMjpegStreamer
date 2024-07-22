import copy
import uuid
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
from twisted.web import server, resource
from twisted.web.server import Site
from twisted.web.resource import Resource

# Global dictionary to store the frames for each UUID
streams = {}


class UDPMjpegPackage:
    def __init__(self):
        self.count = None
        self.bufferMap = {}
        self.category = None
        self.buffer = None
        self.maxIndex = 0

    def isReady(self):
        return (self.maxIndex == self.count and len(self.bufferMap) == self.count)

    def parsingPackage(self):
        if self.isReady():
            sorted_keys = sorted(self.bufferMap.keys())
            self.buffer = bytearray()
            for key in sorted_keys:
                self.buffer.extend(self.bufferMap[key])
            self.count = None
            self.bufferMap = {}
            self.category = None
            self.maxIndex = 0
            return bytes(self.buffer)
        else:
            return None

    def pushBuffer(self, bufferSlice):
        bufferNum = bufferSlice[4]
        # print(bufferNum)
        if bufferNum in self.bufferMap.keys():
            print("Packet loss, discarding")
            self.buffer = None
            self.count = None
            self.bufferMap = {}
            self.category = None
            self.maxIndex = 0

        self.buffer = None
        self.count = int.from_bytes(bufferSlice[:4], byteorder='big')
        if bufferNum > self.maxIndex:
            self.maxIndex = bufferNum
        self.category = bufferSlice[5]
        self.bufferMap[bufferNum] = bufferSlice[6:]


class UDPMjpegStreamerProtocol(DatagramProtocol):
    def __init__(self):
        self.message = {}

    def datagramReceived(self, data, addr):
        if addr not in self.message:
            uid = str(uuid.uuid4())
            self.message[addr] = (uid, UDPMjpegPackage())
            streams[uid] = None
        uid, package = self.message[addr]
        package.pushBuffer(data)
        if package.isReady():
            frame_data = package.parsingPackage()
            streams[uid] = frame_data


class MJPEGStream(Resource):
    isLeaf = True

    def render_GET(self, request):
        client_id = request.path.decode().strip('/')
        if client_id in streams:
            request.setHeader(b'Content-Type', b'multipart/x-mixed-replace; boundary=frame')
            self._write_frame(request, client_id)
            return server.NOT_DONE_YET
        elif client_id == "device":
            devices = ""
            for device in streams.keys():
                devices += f"http://127.0.0.1:8080/{device}\n"
            return devices.encode()
        else:
            request.setResponseCode(404)
            return b'Client not found'

    def _write_frame(self, request, client_id):
        if client_id in streams and streams[client_id] is not None:
            frame = streams[client_id]
            request.write(
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
            )

        reactor.callLater(0.1, self._write_frame, request, client_id)  # Adjust the frame rate as needed


# Start the UDP server
reactor.listenUDP(9999, UDPMjpegStreamerProtocol())

# Create the MJPEG stream resource
root = MJPEGStream()

# Start the Twisted web server
site = Site(root)
reactor.listenTCP(8080, site)

# Run the reactor
reactor.run()
