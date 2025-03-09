from machine import Pin, PWM
from config import RGB_R_PIN, RGB_G_PIN, RGB_B_PIN, COLORS

class RGBLED:
    def __init__(self):
        self.r_pwm = PWM(Pin(RGB_R_PIN), freq=1000, duty=0)
        self.g_pwm = PWM(Pin(RGB_G_PIN), freq=1000, duty=0)
        self.b_pwm = PWM(Pin(RGB_B_PIN), freq=1000, duty=0)

    def set_color(self, color_name):
        if color_name in COLORS:
            r, g, b = COLORS[color_name]
            self.r_pwm.duty(r)
            self.g_pwm.duty(g)
            self.b_pwm.duty(b)
        else:
            raise ValueError(f'无效的颜色名称，请使用以下颜色之一：{list(COLORS.keys())}')

    def off(self):
        self.r_pwm.duty(0)
        self.g_pwm.duty(0)
        self.b_pwm.duty(0)