from gpiozero import DistanceSensor
from adafruit_servokit import ServoKit
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import time, board, busio
import esc 

from ultrasonic import getDistance
from gyro import MPU6050
from get_blocks import PixyCam
import math

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



class Robot():
    def __init__(self):
        self.defaultYaw = 0
        self.mpu = MPU6050()
        self.mpu.reset_gyro()
        
        self.motor = esc.ESC()
        self.motor.calibrate()
        
        self.UltraL = DistanceSensor(echo=17, trigger=27, max_distance=2.0)  # max 2 meters
        self.UltraR = DistanceSensor(echo=17, trigger=27, max_distance=2.0)
        self.UltraF = DistanceSensor(echo=17, trigger=27, max_distance=2.0)

        self.turnCount = 0
        
        self.kit = ServoKit(channels=16)

        self.kit.servo[1].set_pulse_width_range(525, 2475)
        self.kit.servo[2].set_pulse_width_range(525, 2475)

        
        self.cam = PixyCam(5)

        # ADC
        self.i2c = busio.I2C(board.SCL, board.SDA)
        #Create ADS object and specify the gain
        self.ads0 = ADS.ADS1115(self.i2c, address=0x48)
        self.ads1 = ADS.ADS1115(self.i2c, address=0x49)
        #Can change based on the voltage signal - Gain of 1 is typically enough for a lot of sensors
        self.ads0.gain = self.ads1.gain = 1
        self.chan0 = AnalogIn(self.ads0, ADS.P0)
        self.chan1 = AnalogIn(self.ads0, ADS.P0)
        self.chan2 = AnalogIn(self.ads0, ADS.P0)
        self.chan3 = AnalogIn(self.ads0, ADS.P0)
        self.chan4 = AnalogIn(self.ads1, ADS.P0)
        self.chan5 = AnalogIn(self.ads1, ADS.P0)
        
        self.chan = [self.chan0, self.chan1, self.chan2, self.chan3, self.chan4, self.chan5]
        
        self.servoV = [
            [0,0],
            [0,0],
            [0,0],
            [0,0],
            [0,0],
        ]

        self.colors = [
            "red",
            "blue",
            "pink",
        ]
        
        self.pid = PID(kp=1.2, ki=0.01, kd=0.2)
        #pid.reset() yapılabilir

    def map(self, x, x1, x2, y1, y2):
        return float((x-x1)*(y2-y1)/(x2-x1)+y1)

    def getServoAngle(self, s):
        return map(self.chan[s], self.servoV[s, 0], self.servoV[s, 1], 0, 180)

    def moveServo(self, s, degree, delay):
        while True:
            angle = self.getServoAngle(s)
            self.kit.servo[s].angle = round(angle+1)
            if abs(degree-angle) < 1.5:
                break
            time.sleep(delay/1000)
            
    def turn(self, target_offset = 90, isCorner=True):
        """
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

    # def isAhead(self):
    #     x = self.cam.get_blocks()[0]["x"]
        
    #     if getDistance(self.UltraF) < 10 and (150 < x < 250): #10 satısı rastgele| sayılar rasglele verildi amaç ortada olduğnu anlamak
    #         return True
    #     else:
    #         return False
    
    def getUltrasonic(self):
        left = getDistance(self.UltraL)
        right = getDistance(self.UltraR)
        forward = getDistance(self.UltraF)

        return left, right, forward
    
    def servo_adjust(self, servo_channels=[0]):
        initial_yaw = self.mpu.yaw()

        current_yaw = self.mpu.yaw()
        delta_yaw = current_yaw - initial_yaw  

        for i, ch in enumerate(servo_channels):
            target_angle = 90 - delta_yaw
            target_angle = max(0, min(180, target_angle))
            self.kit.servo[ch].angle = round(target_angle)

            # measured = self.map(self.chan[ch].voltage, servo_zero_voltages[i], servo_full_voltages[i], 0, 180)

            time.sleep(0.05)

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

    def passBarrier(self, block):
        pass

    
    def centerCorridor(self):
        if self.isCentered():
            return True
        else:
            diffrence = (getDistance(self.UltraL) - getDistance(self.UltraR))

            if diffrence > 0:
                self.set_heading(135)#sayılar rasgele
            else:
                self.set_heading(70)#sayılar rastgele


        #çalıştığını farz et

    def isCentered(self):
        diffrence = abs(getDistance(self.UltraL) - getDistance(self.UltraR))

        if diffrence < 1:
            return True, 
        
        return False
    
    def isCorner(self):
        if getDistance(self.UltraF) < 10 and getDistance(self.UltraL) > 30:#sayılar rasgele verilmiştir
            return True
        else:
            return False

