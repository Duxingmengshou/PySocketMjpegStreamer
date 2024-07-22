cmake_minimum_required(VERSION 3.26)
project(BoostClient)

set(CMAKE_CXX_STANDARD 17)
set(OpenCV_DIR "H:/Programming/C++/OpenCV/OpenCV490/opencv/build/x64/vc16/lib")
find_package(OpenCV REQUIRED)

# 设置boost库lib的路径
link_directories("D:/boost/msvc_bin_complete/lib")

# 设置头文件路径
include_directories("D:/boost/msvc_bin/include/boost-1_84")

add_executable(BoostClient
        main.cpp
)

target_link_libraries(BoostClient ${OpenCV_LIBS})
