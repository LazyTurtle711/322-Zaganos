# Import libraries
from adafruit_servokit import ServoKit
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import time, board, busio
import math
import sys
import signal

#Import our classes
from gyro import MPU6050
from get_blocks import PixyCam

def signal_handler(signal, frame): # ctrl + c -> exit program
        print('You pressed Ctrl+C!')
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

ultraPins = { # Echo, Trigger
    "front": [5, 7],
    "left": [6, 24],
    "right": [13, 23],
    "back": [19, 8]
}

try:
    pass

except (KeyboardInterrupt, SystemExit):
    gpio.cleanup()
    sys.exit(0)