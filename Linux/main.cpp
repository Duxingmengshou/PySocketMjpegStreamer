//编译：g++ -o camera_client main.cpp `pkg-config --cflags --libs opencv4` -lpthread
#include <iostream>
#include <opencv2/opencv.hpp>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>
#include <vector>

int main() {
    // 创建 socket 客户端
    int client_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (client_socket < 0) {
        std::cerr << "Error: Unable to create socket." << std::endl;
        return -1;
    }

    struct sockaddr_in server_address;
    const char *host_addr = "192.168.11.136"; // 替换为服务器的 IP 地址
    server_address.sin_family = AF_INET;
    server_address.sin_port = htons(8000);    // 替换为服务器的端口号
    if (inet_pton(AF_INET, host_addr, &server_address.sin_addr) <= 0) {
        std::cerr << "Error: Invalid address/ Address not supported." << std::endl;
        close(client_socket);
        return -1;
    }

    // 连接到服务器
    if (connect(client_socket, (struct sockaddr *)&server_address, sizeof(server_address)) < 0) {
        std::cerr << "Error: Unable to connect to the server." << std::endl;
        close(client_socket);
        return -1;
    }

    // 从摄像头读取视频流
    cv::VideoCapture cap(0, cv::CAP_V4L2);
    cap.set(cv::CAP_PROP_FOURCC, cv::VideoWriter::fourcc('M', 'J', 'P', 'G'));



    // 检查摄像头是否成功打开
    if (!cap.isOpened()) {
        std::cerr << "Error: Unable to open camera." << std::endl;
        close(client_socket);
        return -1;
    }

    // 逐帧读取视频并发送到服务器
    cv::Mat frame;
    int frame_count = 0;
    while (true) {
        cap.read(frame);
        if (frame.empty()) {
            std::cerr << "Error: Failed to capture frame." << std::endl;
            break;
        }

        // 将帧转换为二进制流数据
        std::vector<uchar> buffer;
        cv::imencode(".jpg", frame, buffer);
        int buffer_size = buffer.size()+1;

        // 构建包头部信息（帧大小 + 帧数据）
        uint32_t size = htonl(buffer_size); // 转换为网络字节序（大端）
        std::vector<uchar> packet;
        packet.insert(packet.end(), reinterpret_cast<uchar*>(&size), reinterpret_cast<uchar*>(&size) + sizeof(size));
        packet.push_back(static_cast<uchar>(1));
        packet.insert(packet.end(), buffer.begin(), buffer.end());

        // 发送帧数据
        if (send(client_socket, packet.data(), packet.size(), 0) < 0) {
            std::cerr << "Error: Failed to send frame data." << std::endl;
            break;
        }



        // 控制帧率
    }

    // 关闭连接
    close(client_socket);
    cap.release();
    cv::destroyAllWindows();

    return 0;
}