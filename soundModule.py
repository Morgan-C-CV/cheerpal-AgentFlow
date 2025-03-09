from machine import I2S, Pin
import time
import network
import urequests
import json
import ubinascii
import hmac
import hashlib
from ucollections import OrderedDict
from config import *  

# 连接到Wi-Fi
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    while not wlan.isconnected():
        time.sleep(1)

    print('Network config:', wlan.ifconfig())

# 配置I2S录音参数
i2s = I2S(
    I2S.NUM0,
    sck=Pin(I2S_SCK_PIN), ws=Pin(I2S_WS_PIN), sd=Pin(I2S_SD_PIN),  # 使用配置文件中的引脚设置
    mode=I2S.RX,
    bits=16,
    format=I2S.MONO,
    rate=I2S_SAMPLE_RATE,
    ibuf=I2S_BUFFER_SIZE
)

# 创建buffer用于存储录音数据
audio_buf = bytearray(I2S_BUFFER_SIZE)

def calculate_amplitude(audio_data):
    # 将字节数组转换为16位整数数组并计算振幅
    samples = []
    for i in range(0, len(audio_data), 2):
        sample = (audio_data[i+1] << 8) | audio_data[i]
        if sample & 0x8000:
            sample -= 0x10000
        samples.append(abs(sample))
    return sum(samples) / len(samples)

def record_audio():
    i2s.readinto(audio_buf)
    return audio_buf

def generate_signature(params):
    sorted_params = OrderedDict(sorted(params.items()))
    canonicalized_query_string = '&'.join(['%s=%s' % (k, v) for k, v in sorted_params.items()])
    string_to_sign = 'POST&%2F&' + ubinascii.b2a_base64(canonicalized_query_string.encode()).decode().strip()

    key = ACCESS_KEY_SECRET + '&'
    signature = hmac.new(key.encode(), string_to_sign.encode(), hashlib.sha1).digest()
    return ubinascii.b2a_base64(signature).decode().strip()

def send_to_speech_recognition(audio_data):
    params = {
        'Action': 'RecognizeRealTimeStream',
        'Format': 'JSON',
        'Version': '2020-12-08',
        'AccessKeyId': ACCESS_KEY_ID,
        'SignatureMethod': 'HMAC-SHA1',
        'Timestamp': str(time.time()),
        'SignatureVersion': '1.0',
        'AudioFormat': 'PCM',
        'SampleRate': I2S_SAMPLE_RATE,
        'Channel': 1
    }
    
    # 添加签名
    params['Signature'] = generate_signature(params)
    
    # 发送请求
    headers = {
        'Content-Type': 'application/octet-stream',
        'X-NLS-Token': ACCESS_KEY_ID
    }
    
    try:
        response = urequests.post(
            API_ENDPOINT,
            data=audio_data,
            headers=headers,
            params=params
        )
        
        if response.status_code == 200:
            result = json.loads(response.text)
            if 'Result' in result:
                print('识别结果:', result['Result'])
                return result['Result']
        else:
            print('请求失败:', response.status_code)
            return None
    except Exception as e:
        print('发送请求时出错:', e)
        return None

def play_mp3(file_path):
    from machine import I2S, Pin
    import wave

    # 配置I2S播放参数
    i2s_out = I2S(
        I2S.NUM1,
        sck=Pin(I2S_SCK_PIN), ws=Pin(I2S_WS_PIN), sd=Pin(I2S_SD_PIN),
        mode=I2S.TX,
        bits=16,
        format=I2S.MONO,
        rate=16000,
        ibuf=4096
    )

    # 打开MP3文件
    with wave.open(file_path, 'rb') as f:
        # 读取并播放音频数据
        data = f.readframes(1024)
        while data:
            i2s_out.write(data)
            data = f.readframes(1024)

        # 关闭I2S
        i2s_out.deinit()


def text_to_speech(text):
    import dashscope
    from dashscope.audio.tts_v2 import SpeechSynthesizer
    from dashscope.audio.asr import Recognition, RecognitionCallback, RecognitionResult

    dashscope.api_key = DASHSCOPE_API_KEY
    model = TTS_MODEL
    voice = TTS_VOICE

    synthesizer = SpeechSynthesizer(model=model, voice=voice)
    audio = synthesizer.call(text)
    print('requestId: ', synthesizer.get_last_request_id())
    with open('output.mp3', 'wb') as f:
        f.write(audio)
    return 'output.mp3'

class SpeechRecognitionCallback(RecognitionCallback):
    def __init__(self):
        self.result = None

    def on_open(self) -> None:
        print('语音识别已启动')

    def on_close(self) -> None:
        print('语音识别已关闭')

    def on_complete(self) -> None:
        print('语音识别完成')

    def on_error(self, message) -> None:
        print('语音识别错误:', message.message)

    def on_event(self, result: RecognitionResult) -> None:
        sentence = result.get_sentence()
        if 'text' in sentence:
            self.result = sentence['text']
            print('识别结果:', self.result)
            if RecognitionResult.is_sentence_end(sentence):
                print('句子结束')

recognition = Recognition(
    model='paraformer-realtime-v2',
    format='pcm',
    sample_rate=I2S_SAMPLE_RATE,
    callback=SpeechRecognitionCallback()
)

if __name__ == '__main__':
    ssid = WIFI_SSID
    password = WIFI_PASSWORD
    connect_wifi(ssid, password)

    silence_duration = 0
    last_sound_time = time.time()
    is_recording = False

    while True:
        try:
            recorded_data = record_audio()
            amplitude = calculate_amplitude(recorded_data)

            if amplitude > SILENCE_THRESHOLD:
                if not is_recording:
                    print('开始录音...')
                    recognition.start()
                    is_recording = True
                last_sound_time = time.time()
                recognition.send_audio_frame(recorded_data)
                result = recognition.callback.result
                if result:
                    print('识别完成:', result)
            else:
                silence_duration = time.time() - last_sound_time
                if is_recording and silence_duration >= SILENCE_DURATION:
                    print('检测到3秒静音，停止录音')
                    is_recording = False

            time.sleep(0.1)
        except KeyboardInterrupt:
            print('程序已停止')
            break
        except Exception as e:
            print('发生错误:', e)
            time.sleep(1)