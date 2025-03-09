import os
from uudagong.soundModule import record_audio, convert_speech_to_text
from uudagong.thinkingModule import get_model_response
from uudagong.lightingModule import adjust_lighting, restore_lighting


def main():
    while True:
        # 录制音频
        audio_file = record_audio()
        
        # 将音频转换为文字
        user_input = convert_speech_to_text(audio_file)
        
        # 获取模型响应
        response = get_model_response(user_input，system_prompt='You are a helpful assistant.')
        
        # 调整灯光
        adjust_lighting()
        
        # 播放响应音频
        os.system(f'play {response.audio_file}')
        
        # 恢复灯光
        restore_lighting()
        
        # 删除临时音频文件
        os.remove(audio_file)
        os.remove(response.audio_file)

if __name__ == '__main__':
    main()