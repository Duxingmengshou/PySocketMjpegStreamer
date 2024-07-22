#include <boost/asio.hpp>
#include <boost/endian/conversion.hpp>
#include <opencv2/opencv.hpp>
#include <iostream>
#include <vector>
#include <thread>
#include <chrono>

void sendFrames(boost::asio::ip::tcp::socket& socket) {
    cv::VideoCapture capture(0);
    cv::Mat frame;
    capture>>frame;
    if (frame.empty()) {
        std::cerr << "Error: frame is empty." << std::endl;
        return;
    }
    while (true) {
        capture>>frame;
        std::vector<unsigned char> encoded_frame;
        cv::imencode(".jpg", frame, encoded_frame);
        uint32_t size = encoded_frame.size() + 1;
        size = boost::endian::native_to_big(size); // Convert to big-endian
        std::vector<unsigned char> buf;
        buf.insert(buf.end(), reinterpret_cast<unsigned char*>(&size), reinterpret_cast<unsigned char*>(&size) + sizeof(size));
        buf.push_back(static_cast<unsigned char>(1));
        buf.insert(buf.end(), encoded_frame.begin(), encoded_frame.end());
        boost::system::error_code error;
        boost::asio::write(socket, boost::asio::buffer(buf), error);
        if (error) {
            std::cerr << "Error sending frame: " << error.message() << std::endl;
            break;
        }
        // Sleep for 20 milliseconds (0.02 seconds)
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
    }
}

void sendSomething(const std::string& host, int port) {
    try {
        boost::asio::io_service io_service;
        boost::asio::ip::tcp::endpoint endpoint(boost::asio::ip::address::from_string(host), port);
        boost::asio::ip::tcp::socket socket(io_service);
        socket.connect(endpoint);
        sendFrames(socket);
        socket.close();
    } catch (std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
    }
}

int main() {
    sendSomething("127.0.0.1", 8000);
    return 0;
}
