from gpiozero import DistanceSensor
from adafruit_servokit import ServoKit
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import time, board, busio
import esc 

from ultrasonic import getDistance
from gyro import MPU6050
from get_blocks import PixyCam

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

        
        
        self.kit = ServoKit(channels=16)
        
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
            time.sleep(delay/100)
            
    def turn(self, target_offset=90):
            target_yaw = (self.defaultYaw + target_offset) % 360
            pid = PID(kp=1.2, ki=0.01, kd=0.2, setpoint=target_yaw)

            while True:
                current_yaw = self.mpu.yaw()

                error = (target_yaw - current_yaw + 540) % 360 - 180
                if abs(error) < 2:
                    break

                correction = pid.compute(current_yaw)

                throttle = max(min(correction / 100, 1), -1)

                self.motor.set_throttle(throttle)
                time.sleep(0.05)

            self.motor.set_throttle(0)
    
    def isAhead(self):
        x = self.cam.get_blocks()[0]["x"]
        
        if getDistance(self.UltraF) < 10 and (150 < x < 250): #10 satısı rastgele| sayılar rasglele verildi amaç ortada olduğnu anlamak
            return True
        else:
            return False
    
    def getUltrasonic(self):

        left = getDistance(self.UltraL)
        right = getDistance(self.UltraL)
        forward = getDistance(self.UltraF)

        return left, right, forward
    
def servo_adjust(self, servo_channels=[0]):
    servo_zero_voltages = []
    servo_full_voltages = []

    # for ch in servo_channels:
    #     self.kit.servo[ch].angle = 0
    # time.sleep(1)
    # for ch in servo_channels:
    #     servo_zero_voltages.append(self.chan[ch].voltage)

    # for ch in servo_channels:
    #     self.kit.servo[ch].angle = 180
    # time.sleep(1)
    # for ch in servo_channels:
    #     servo_full_voltages.append(self.chan[ch].voltage)

    # print("Kalibrasyon tamamlandı.")

    #RÜZGAR yukarısı gerekli mi bilmiyorum sen daha iyi anlarsın ben koydum yine de TODO:

    # Başlangıç yaw açısını referans al
    initial_yaw = self.mpu.yaw()

    while True:
        current_yaw = self.mpu.yaw()
        delta_yaw = current_yaw - initial_yaw  # Robotun ne kadar döndüğünü hesapla

        for i, ch in enumerate(servo_channels):
            target_angle = 90 - delta_yaw
            target_angle = max(0, min(180, target_angle))
            self.kit.servo[ch].angle = round(target_angle)

                # ADC'den açıyı geri oku (debug için)
            measured = self.map(self.chan[ch].voltage, servo_zero_voltages[i], servo_full_voltages[i], 0, 180)

        time.sleep(0.05)