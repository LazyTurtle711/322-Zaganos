from gpiozero import DistanceSensor
from adafruit_servokit import ServoKit
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import time, board, busio

from ultrasonic import getDistance
from gyro import MPU6050

from get_blocks import PixyCam

# source env/bin/activate
defaultYaw = 0

def map(x, x1, x2, y1, y2):
    return float((x-x1)*(y2-y1)/(x2-x1)+y1)

def getServoAngle(s):
    return map(chan[s], servoV[s, 0], servoV[s, 1], 0, 180)

def moveServo(s, degree, delay):
    angle = getServoAngle(s)
    delta = degree - angle
    if delta == 0:
        return
    sign = delta / abs(delta)
    
    while True:
        angle = getServoAngle(s)
        
        kit.servo[s].angle = round(angle) + sign
        if abs(degree-angle) < 1.5:
            break
        time.sleep(delay/1000)
        
# Gyro
mpu = MPU6050()

# Camera
cam = PixyCam(5)

    
servoV = [
    [0,0],
    [0,0],
    [0,0],
    [0,0],
    [0,0],
]

def orientServos(target=0):
    err = target - mpu.yaw()
    
    kit.servo[3].angle = 0
    kit.servo[4].angle = 0
    

# Ultrasonic
UltraL = DistanceSensor(echo=17, trigger=27, max_distance=2.0)  # max 2 meters
UltraR = DistanceSensor(echo=17, trigger=27, max_distance=2.0)

# Servo driver
kit = ServoKit(channels=16)

# ADC
i2c = busio.I2C(board.SCL, board.SDA)
#Create ADS object and specify the gain
ads0 = ADS.ADS1115(i2c, address=0x48)
ads1 = ADS.ADS1115(i2c, address=0x49)
#Can change based on the voltage signal - Gain of 1 is typically enough for a lot of sensors
ads0.gain = ads1.gain = 1
chan0 = AnalogIn(ads0, ADS.P0)
chan1 = AnalogIn(ads0, ADS.P0)
chan2 = AnalogIn(ads0, ADS.P0)
chan3 = AnalogIn(ads0, ADS.P0)
chan4 = AnalogIn(ads1, ADS.P0)
chan5 = AnalogIn(ads1, ADS.P0)


chan = [chan0, chan1, chan2, chan3, chan4, chan5]

while True:
    getDistance(UltraL)
    
    orientServos(0)
    
    cam.get_blocks()
    if cam.count > 0:
        for i in range(len(cam.block_data)):
            print(f"{i + 1}. block data: {cam.block_data[i]}")
        print()
    else:
        print("No targets detected!")
        time.sleep(1)
        
    time.sleep(0.1)

