import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_servokit import ServoKit
from gpiozero import DistanceSensor
from gyro import MPU6050
from esc import ESC
from ultrasonic import Ultras
from gpiozero import PWMOutputDevice  # Import PWM output for controlling ESC
from gpiozero import DigitalOutputDevice
from gpiozero import Button
class AutonomousCar:
    def __init__(self):
        self.button = Button(12)
        self.motor = ESC()

        # Ultrasonik sensörler
        ultraPins = { # Echo, Trigger
        "front": [5, 7],
        "left": [6, 24],
        "right": [13, 23],
        "back": [19, 8]
        }
        self.ult = Ultras(ultraPins)


        # Yaw sensörü
        self.last_value = 0
        self.mpu = MPU6050()
        self.mpu.reset_gyro()

        # Servo sürücü
        self.kit = ServoKit(channels=16)

        # ESC motor kontrolü
        self.move_speed = 1.6

        # Başlangıç yönü (0°)
        self.default_yaw    = 0
        self.turn_cooldown = 2.0
        self.last_turn_time = 0

        self.counter = 0
        self.centerOffset = 0

    def setCornerTurningYaw(self):
        now = time.time()
        if now - self.last_turn_time < self.turn_cooldown:
            return self.default_yaw, False

        SIDE_TH  = 115
        FRONT_TH = 170

        dl = self.ult.getDistance("left")  
        dr = self.ult.getDistance("right")
        df = self.ult.getDistance("front")

        print(f"left|{dl} right|{dr} forward|{df}")
        if dl is None or dr is None or df is None:
            return self.default_yaw, False

        if df < FRONT_TH:
            if dl > SIDE_TH and dr <= SIDE_TH:
                self.default_yaw    = (self.default_yaw + 90) % 360
                self.last_turn_time = now
                self.counter += 1
                self.centerOffset = 20
                return self.default_yaw, True
            if dr > SIDE_TH and dl <= SIDE_TH:
                self.default_yaw    = (self.default_yaw - 90) % 360
                self.last_turn_time = now
                self.counter += 1
                self.centerOffset = -20
                return self.default_yaw, True
                

        return self.default_yaw, False

    def turn_to_yaw(self, target_yaw):
        """
        target_yaw’a en kısa yönden dönüp, |error| < TARGET_THRESH olana dek sürer.
        Bu süreçte motor kapatılmaz; sürekli ileri hareket devam eder.
        """
        print(f"🎯 Yaw'a hizalanma başlıyor: hedef = {target_yaw}°")

        def get_error():
            try:
                current = self.mpu.yaw()
                return (target_yaw - current + 540) % 360 - 180
            except:
                time.sleep(0.05)
                current = self.mpu.yaw()
                return (target_yaw - current + 540) % 360 - 180


        K = 4
        MIN_A, MAX_A = 60, 120
        DEAD_BAND = 0.5
        TARGET_THRESH = 1.0

        # Hedefe ulaşana dek servo yönlendirme ve sürekli motor ileri
        while True:
            # Motor desteği
            if self.ult.getDistance("front") < 15:
                break

            self.motor.set_throttle(self.move_speed)

            error = get_error()
            if abs(error) < TARGET_THRESH:
                break

            if abs(error) < DEAD_BAND:
                angle = 90
            else:
                angle = 90 - K * error
                angle = max(MIN_A, min(MAX_A, angle))

            self.kit.servo[0].angle = angle 
            self.kit.servo[1].angle = angle
            time.sleep(0.01)

        # Hizalama sonrası direksiyon düz
        self.kit.servo[0].angle = 90
        self.kit.servo[1].angle = 90

    def alignToUltrasonic(self, offset_cm=0):  # offset_cm > 0 ise sağa, < 0 ise sola hizalan
        right = self.ult.getDistance("right")
        left = self.ult.getDistance("left")

        # İstenen farkı oluştur: sağdan soldan offset kadar fazla olmalı
        target_diff = offset_cm  # örn. 20 cm sağa kaymak istiyorsan sağ > sol olacak

        diff = right - left

        # Gerçek fark ile hedef fark arasındaki hata
        error = diff - target_diff

        if abs(error) < 3:  # yeterince yakınsa hizalı say
            self.turn_to_yaw(self.default_yaw)
        elif error > 0:
            self.turn_to_yaw(self.default_yaw - 20)  # sola düzelt
        else:
            self.turn_to_yaw(self.default_yaw + 20)   


    def run(self):
        print("▶ Sürekli sürüş + koşullu yaw dönüş modunda.")
        while True:
            yaw, turning = self.setCornerTurningYaw()
            self.default_yaw = yaw
            print(turning)

            self.turn_to_yaw(self.default_yaw)
            print(f"DefaultYaw: {self.default_yaw}")
                # Düz git + nötr servo

            if self.counter == 12:
                time.sleep(0.3)
                self.motor.set_throttle(1.5)
                break
    

            time.sleep(0.025)


if __name__ == "__main__":
    car = AutonomousCar()
    while not car.button.is_pressed:
        pass
    car.run()
#(-20 right) + left
