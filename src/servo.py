from adafruit_servokit import ServoKit
import time
kit = ServoKit(channels=16)
kit.servo[0].angle=0
time.sleep(3)
kit.servo[0].angle=180