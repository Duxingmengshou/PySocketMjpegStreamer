#include <Arduino.h>
#include <WiFi.h>
#include "esp_camera.h"
#include <vector>



const char *ssid = "609Cam";
const char *password = "12345678";
const IPAddress serverIP(192, 168, 11, 136);  // 欲访问的地址
uint16_t serverPort = 8000;                   // 服务器端口号

#define maxcache 1430

WiFiClient client;  // 声明一个客户端对象，用于与服务器进行连接

// CAMERA_MODEL_AI_THINKER类型摄像头的引脚定义
#define PWDN_GPIO_NUM 32
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM 0
#define SIOD_GPIO_NUM 26
#define SIOC_GPIO_NUM 27

#define Y9_GPIO_NUM 35
#define Y8_GPIO_NUM 34
#define Y7_GPIO_NUM 39
#define Y6_GPIO_NUM 36
#define Y5_GPIO_NUM 21
#define Y4_GPIO_NUM 19
#define Y3_GPIO_NUM 18
#define Y2_GPIO_NUM 5
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM 23
#define PCLK_GPIO_NUM 22

static camera_config_t camera_config = {
  .pin_pwdn = PWDN_GPIO_NUM,
  .pin_reset = RESET_GPIO_NUM,
  .pin_xclk = XCLK_GPIO_NUM,
  .pin_sscb_sda = SIOD_GPIO_NUM,
  .pin_sscb_scl = SIOC_GPIO_NUM,

  .pin_d7 = Y9_GPIO_NUM,
  .pin_d6 = Y8_GPIO_NUM,
  .pin_d5 = Y7_GPIO_NUM,
  .pin_d4 = Y6_GPIO_NUM,
  .pin_d3 = Y5_GPIO_NUM,
  .pin_d2 = Y4_GPIO_NUM,
  .pin_d1 = Y3_GPIO_NUM,
  .pin_d0 = Y2_GPIO_NUM,
  .pin_vsync = VSYNC_GPIO_NUM,
  .pin_href = HREF_GPIO_NUM,
  .pin_pclk = PCLK_GPIO_NUM,

  .xclk_freq_hz = 20000000,  // 帧率
  .ledc_timer = LEDC_TIMER_0,
  .ledc_channel = LEDC_CHANNEL_0,

  .pixel_format = PIXFORMAT_JPEG,
  .frame_size = FRAMESIZE_VGA,  // 图片格式
  .jpeg_quality = 12,           // PEG图片质量（jpeg_quality），0-63，数字越小质量越高
  .fb_count = 1,
};
void wifi_init() {
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);  // 关闭STA模式下wifi休眠，提高响应速度
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi Connected!");
  Serial.print("IP Address:");
  Serial.println(WiFi.localIP());
}

void tcp_init() {
  client.connect(serverIP, serverPort);
  Serial.println("TCP Connected!");
}

esp_err_t camera_init() {
  // initialize the camera
  esp_err_t err = esp_camera_init(&camera_config);
  if (err != ESP_OK) {
    Serial.println("Camera Init Failed");
    return err;
  }
  sensor_t *s = esp_camera_sensor_get();
  // initial sensors are flipped vertically and colors are a bit saturated
  if (s->id.PID == OV2640_PID) {
    //        s->set_vflip(s, 1);//flip it back
    //        s->set_brightness(s, 1);//up the blightness just a bit
    //        s->set_contrast(s, 1);
  }
  Serial.println("Camera Init OK!");
  return ESP_OK;
}

void setup() {
  Serial.begin(115200);
  wifi_init();
  tcp_init();
  camera_init();
  Serial.println("okkkkkk");
}
uint32_t length = 0;
uint8_t category = 32;
camera_fb_t *fb = nullptr;
uint8_t *temp = nullptr;
void loop() {
  fb = esp_camera_fb_get();
  temp = fb->buf;  //这个是为了保存一个地址，在摄像头数据发送完毕后需要返回，否则会出现板子发送一段时间后自动重启，不断重复
  if (!fb) {
    Serial.println("Camera Capture Failed");
  } else {
    length = fb->len + 1;
    length = htonl(length);
    client.write(reinterpret_cast<uint8_t *>(&length), sizeof(length));
    client.write(&category, sizeof(category));
    client.write(fb->buf, fb->len);
    fb->buf = temp;            //将当时保存的指针重新返还
    esp_camera_fb_return(fb);  //这一步在发送完毕后要执行，具体作用还未可知。
  }
}
