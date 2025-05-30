import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_servokit import ServoKit
from gpiozero import DistanceSensor


from gyro import MPU6050
sensor = DistanceSensor(echo=13, trigger=25, max_distance=2.0)

mpu = MPU6050()
mpu.reset_gyro

kit = ServoKit(channels=16)

i2c = busio.I2C(board.SCL, board.SDA)

ads = ADS.ADS1115(i2c, address=0x48)
ads.gain = 1
chan0 = AnalogIn(ads, ADS.P0)

def map(x, x1, x2, y1, y2):
    return float((x-x1)*(y2-y1)/(x2-x1)+y1)

kit.servo[2].angle=0
time.sleep(1)
servo0 = chan0.voltage
print(f"servo0 = {servo0}")

kit.servo[2].angle=180
time.sleep(1)
servo180 = chan0.voltage
print(f"servo180 = {servo180}")

def getDistance(sensor):
    # time.sleep(0.5)
    # print('sonar start')

    distance = sensor.distance * 100  # convert to cm
    if distance == 0 or distance > 300:
        print('out of range')
        return None
    else:
        print('Distance : %.3f cm' % distance)
        return distance
    # time.sleep(0.1)
    
    

while True:
    if mpu.yaw()*-1+90 > 5 and mpu.yaw()*-1+90 < 175:
        kit.servo[2].angle=mpu.yaw()*1+89
        kit.servo[3].angle=mpu.yaw()*-1+90
    print(getDistance(sensor))
    angle = map(chan0.voltage, servo0, servo180, 0, 180)
    print(f"Gyro Açı: {mpu.yaw()} Servo Açı: {angle}")
    time.sleep(0.05)