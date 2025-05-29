import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_servokit import ServoKit
from gyro import MPU6050

mpu = MPU6050()
mpu.reset_gyro()

kit = ServoKit(channels=16)
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ads.gain = 1
chan0 = AnalogIn(ads, ADS.P0)

def map(x, x1, x2, y1, y2):
    return float((x-x1)*(y2-y1)/(x2-x1)+y1)

kit.servo[0].angle = 0
time.sleep(1)
servo0 = chan0.voltage
print(f"servo0 = {servo0}")

kit.servo[0].angle = 180
time.sleep(1)
servo180 = chan0.voltage
print(f"servo180 = {servo180}")

while True:
    current_yaw = mpu.yaw()
    angle_input = -current_yaw + 90
    safe_angle = max(5, min(175, angle_input))
    kit.servo[0].angle = safe_angle

    angle_measured = map(chan0.voltage, servo0, servo180, 0, 180)
    print(f"Gyro Açı: {current_yaw:.2f}  → Servo Açı: {angle_measured:.2f}")

    time.sleep(0.05)
