from adafruit_servokit import ServoKit
import time
kit = ServoKit(channels=16)

kit.servo[1].set_pulse_width_range(525, 2475)
kit.servo[2].set_pulse_width_range(525, 2475)

kit.servo[1].angle=120
kit.servo[2].angle=120

time.sleep(3)

kit.servo[1].angle=90
kit.servo[2].angle=90