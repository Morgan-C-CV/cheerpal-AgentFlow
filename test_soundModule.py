import unittest
from unittest.mock import MagicMock, patch
import time
from soundModule import *

class TestSoundModule(unittest.TestCase):
    def setUp(self):
        self.test_audio_data = bytearray([0x00, 0x80] * 1024)

    def test_wifi_connection(self):
        with patch('network.WLAN') as mock_wlan:
            mock_wlan_instance = MagicMock()
            mock_wlan.return_value = mock_wlan_instance
            mock_wlan_instance.isconnected.return_value = True
            mock_wlan_instance.ifconfig.return_value = ('192.168.1.1', '255.255.255.0', '192.168.1.1', '8.8.8.8')
            connect_wifi('test_ssid', 'test_password')

            mock_wlan.assert_called_once_with(network.STA_IF)
            mock_wlan_instance.active.assert_called_once_with(True)
            mock_wlan_instance.connect.assert_called_once_with('test_ssid', 'test_password')

    def test_calculate_amplitude(self):
        amplitude = calculate_amplitude(self.test_audio_data)
        self.assertIsInstance(amplitude, float)
        self.assertGreaterEqual(amplitude, 0)

    @patch('machine.I2S')
    def test_record_audio(self, mock_i2s):
        mock_i2s_instance = MagicMock()
        mock_i2s.return_value = mock_i2s_instance

        def mock_readinto(buf):
            for i in range(len(buf)):
                buf[i] = i % 256
            return None
        mock_i2s_instance.readinto.side_effect = mock_readinto

        recorded_data = record_audio()
        self.assertIsInstance(recorded_data, bytearray)
        self.assertEqual(len(recorded_data), I2S_BUFFER_SIZE)

    @patch('wave.open')
    @patch('machine.I2S')
    def test_play_mp3(self, mock_i2s, mock_wave):
        mock_wave_file = MagicMock()
        mock_wave.return_value.__enter__.return_value = mock_wave_file
        mock_wave_file.readframes.side_effect = [b'test_data', b'']
        mock_i2s_instance = MagicMock()
        mock_i2s.return_value = mock_i2s_instance

        play_mp3('test.mp3')

        mock_i2s_instance.write.assert_called_with(b'test_data')
        mock_i2s_instance.deinit.assert_called_once()

    def test_hardware_recording(self):
        """实际硬件录音测试"""
        print("\n开始硬件录音测试...")
        print("请确保麦克风已正确连接到以下引脚：")
        print(f"SCK: {I2S_SCK_PIN}")
        print(f"WS: {I2S_WS_PIN}")
        print(f"SD: {I2S_SD_PIN}")

        try:
            print("\n开始录音（3秒）...")
            start_time = time.time()
            recorded_chunks = []
            while time.time() - start_time < 3:
                chunk = record_audio()
                recorded_chunks.append(chunk)
                amplitude = calculate_amplitude(chunk)
                print(f"当前音频振幅: {amplitude}")
                time.sleep(0.1)

            print("录音完成！")
            
            self.assertTrue(len(recorded_chunks) > 0)
            for chunk in recorded_chunks:
                self.assertEqual(len(chunk), I2S_BUFFER_SIZE)

            print("\n尝试播放录音...")
            for chunk in recorded_chunks:
                i2s.write(chunk)
            print("播放完成！")

        except Exception as e:
            self.fail(f"硬件测试失败: {str(e)}")

if __name__ == '__main__':
    unittest.main()