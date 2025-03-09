#API配置
ACCESS_KEY_ID = '<your-access-key-id>'
ACCESS_KEY_SECRET = '<your-access-key-secret>'
API_ENDPOINT = 'https://nlp-api.cn-hangzhou.aliyuncs.com'

# WiFi配置
WIFI_SSID = '<your-wifi-ssid>'
WIFI_PASSWORD = '<your-wifi-password>'

# I2S配置
I2S_SCK_PIN = 14
I2S_WS_PIN = 15
I2S_SD_PIN = 13
I2S_SAMPLE_RATE = 16000
I2S_BUFFER_SIZE = 20000

# 声音检测配置
SILENCE_THRESHOLD = 100  # 静音阈值
SILENCE_DURATION = 3  # 静音检测时间（秒）

# 语音合成配置
DASHSCOPE_API_KEY = '<your-dashscope-api-key>'
TTS_MODEL = 'cosyvoice-v1'
TTS_VOICE = 'longxiaochun'

# RGB LED引脚配置
RGB_R_PIN = 16
RGB_G_PIN = 17
RGB_B_PIN = 18

# 颜色配置
COLORS = {
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'cyan': (0, 255, 255),
    'magenta': (255, 0, 255),
    'white': (255, 255, 255),
    'orange': (255, 165, 0)
}