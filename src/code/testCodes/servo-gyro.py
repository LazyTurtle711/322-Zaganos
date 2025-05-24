from adafruit_servokit import ServoKit
import time
from gyro import MPU6050

kit = ServoKit(channels=16)

kit.servo[1].set_pulse_width_range(525, 2475)
kit.servo[2].set_pulse_width_range(525, 2475)

mpu = MPU6050()
mpu.reset_gyro()

REFERENCE_YAW = 90 

def stabilize_yaw():
    while True:
        current_yaw = mpu.yaw()
        yaw_error = (REFERENCE_YAW - current_yaw + 540) % 360 - 180

        angle = 90 + yaw_error  
        angle = max(0, min(180, angle))  
        
        kit.servo[1].angle = angle
        kit.servo[2].angle = angle

        print(f"Yaw: {current_yaw:.2f}  →  Servo Angle: {angle:.2f}")
        time.sleep(0.05)

stabilize_yaw()
