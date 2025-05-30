from adafruit_servokit import ServoKit
import time
kit = ServoKit(channels=16)

kit.servo[1].set_pulse_width_range(525, 2475)
kit.servo[0].set_pulse_width_range(525, 2475)

kit.servo[1].angle=90
kit.servo[0].angle=90

# kit.servo[2].set_pulse_width_range(525, 2475)
# kit.servo[3].set_pulse_width_range(525, 2475)

# kit.servo[2].angle=125
# kit.servo[3].angle=55