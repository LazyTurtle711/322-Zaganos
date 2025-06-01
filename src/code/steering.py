from adafruit_servokit import ServoKit
import time
import math
from gyro import MPU6050
from ultrasonic import getDistance

class PID:
    def __init__(self, kp, ki, kd, setpoint=0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.prev_error = 0
        self.integral = 0

    def compute(self, current_value):
        error = self.setpoint - current_value
        self.integral += error
        derivative = error - self.prev_error
        self.prev_error = error
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        return output

class Steering:
    def __init__(self):
        self.kit = ServoKit(channels=16)
        self.kit.servo[1].set_pulse_width_range(525, 2475)
        self.kit.servo[0].set_pulse_width_range(525, 2475)

        self.mpu = MPU6050()
        self.defaultYaw = 0
        self.pid = PID(kp=1.2, ki=0.01, kd=0.2)
        self.turnCount = 0

        # Initialize ultrasonic sensors if needed
        self.UltraL = None
        self.UltraR = None
        self.UltraF = None

    def steer(self, angle):
        self.kit.servo[0].angle = angle
        self.kit.servo[1].angle = angle

    def map(self, x, x1, x2, y1, y2):
        return float((x-x1)*(y2-y1)/(x2-x1)+y1)

    def set_heading(self, servo_angle):
        self.kit.servo[1].angle = servo_angle
        self.kit.servo[2].angle = servo_angle

    def keep_heading_straight(self, throttle_pulse=1.7, tolerance=2):
        """
        SetPoint vermeyi unutma
        """
        NEUTRAL_ANGLE = 90
        MAX_STEER = 30

        current_yaw = self.mpu.yaw()

        error = (self.defaultYaw - current_yaw + 540) % 360 - 180

        if abs(error) <= tolerance:
            self.set_heading(NEUTRAL_ANGLE)

        correction = self.pid.compute(error)
        steer = max(min(correction, MAX_STEER), -MAX_STEER)
        angle = NEUTRAL_ANGLE + steer

        self.set_heading(angle)

        time.sleep(0.05)

    def turn(self, target_offset = 90, isCorner=True):
        """
        Turn the robot by a specified angle offset
        """
        target_yaw = (self.defaultYaw + target_offset) % 360
        pid = PID(0.15, 0.1, 0.5, setpoint=target_yaw)

        NEUTRAL_ANGLE = 90
        MAX_STEER = 30  

        while True:
            current_yaw = self.mpu.yaw()

            error = (target_yaw - current_yaw + 540) % 360 - 180
            if abs(error) < 2:
                self.set_heading(NEUTRAL_ANGLE)

                if isCorner:
                    self.turnCount += 1
                    self.defaultYaw = target_yaw % 360
                return True

            correction = pid.compute(error)
            steer_offset = max(min(correction,  MAX_STEER), -MAX_STEER)
            angle = NEUTRAL_ANGLE + steer_offset

            self.set_heading(angle)

            time.sleep(0.005)

    def centerCorridor(self):
        if self.isCentered():
            return True
        else:
            diffrence = (getDistance(self.UltraL) - getDistance(self.UltraR))

            if diffrence > 0:
                self.set_heading(135)  # sayılar rasgele
            else:
                self.set_heading(70)  # sayılar rastgele

    def isCentered(self):
        diffrence = abs(getDistance(self.UltraL) - getDistance(self.UltraR))

        if diffrence < 1:
            return True

        return False

    def servo_adjust(self, servo_channels=[0]):
        initial_yaw = self.mpu.yaw()

        current_yaw = self.mpu.yaw()
        delta_yaw = current_yaw - initial_yaw  

        for i, ch in enumerate(servo_channels):
            target_angle = 90 - delta_yaw
            target_angle = max(0, min(180, target_angle))
            self.kit.servo[ch].angle = round(target_angle)

            time.sleep(0.05)

    def set_ultrasonic_sensors(self, UltraL, UltraR, UltraF):
        """
        Set the ultrasonic sensors for the steering class
        """
        self.UltraL = UltraL
        self.UltraR = UltraR
        self.UltraF = UltraF

    def isCorner(self):
        if getDistance(self.UltraF) < 10 and getDistance(self.UltraL) > 30:  # sayılar rasgele verilmiştir
            return True
        else:
            return False
