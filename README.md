# PySocketMjpegStreamer

### A middleware that receives TCP image streams and converts them into MJPEG video streams.

This is a simple middleware, which receives the image stream (packet) transmitted by TCP or UDP according to the rules, and then converts it into MJPEG stream that can be displayed by HTTP. This does not consume the performance of the device, and you can use OpenCV in this middle layer to do some detection or other tasks. The information transmitted by TCP is not necessarily an image. Sometimes we need to transmit some information accompanying each frame of the image. This is the original purpose of this work (I want to process the depth map and the original image at the same time). After all, there are already many projects to directly generate MJPEG streams (for example: ustreamer).

![](./image/PySocketMjpegStreamer.drawio.png)
