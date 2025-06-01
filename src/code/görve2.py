from get_blocks import PixyCam
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
from gpiozero import PWMOutputDevice
from gpiozero import DigitalOutputDevice

class Car:
    def __init__(self):
        self.cam = PixyCam(5)
        self.motor = ESC()

        ultraPins = {
            "front": [5, 7],
            "left": [6, 24],
            "right": [13, 23],
            "back": [19, 8]
        }
        self.ult = Ultras(ultraPins)

        self.mpu = MPU6050()
        self.mpu.reset_gyro()

        self.kit = ServoKit(channels=16)
        self.move_speed = 1.6

        self.default_yaw = 0
        self.turn_cooldown = 2.0
        self.last_turn_time = 0

        self.counter = 0
        self.centerOffset = 0

        self.turnOffset = 0

    def isBlock(self):
        blocks = self.cam.get_blocks()
        return bool(blocks)

    def setCornerTurningYaw(self):
        now = time.time()
        if now - self.last_turn_time < self.turn_cooldown:
            return self.default_yaw, False

        SIDE_TH = 130
        FRONT_TH = 130

        dl = self.ult.getDistance("left")
        dr = self.ult.getDistance("right")
        df = self.ult.getDistance("front")

        print(f"left|{dl} right|{dr} forward|{df}")
        if dl is None or dr is None or df is None:
            return self.default_yaw, False

        if df < FRONT_TH:
            if dl > SIDE_TH and dr <= SIDE_TH:
                self.default_yaw = (self.default_yaw + 90) % 360
                self.last_turn_time = now
                self.counter += 1
                self.centerOffset = 20
                self.turnOffset = 0

                return self.default_yaw, True
            if dr > SIDE_TH and dl <= SIDE_TH:
                self.default_yaw = (self.default_yaw - 90) % 360
                self.last_turn_time = now
                self.counter += 1
                self.centerOffset = -20
                self.turnOffset = 0

                return self.default_yaw, True

        return self.default_yaw, False

    def turn_to_yaw(self, target_yaw, interrupt_on_corner=False):
        print(f"🎯 Yaw'a hizalanma başlıyor: hedef = {target_yaw}°")

        def get_error():
            current = self.mpu.yaw()
            return (target_yaw - current + 540) % 360 - 180

        K = 2.0
        MIN_A, MAX_A = 60, 120
        DEAD_BAND = 0.5
        TARGET_THRESH = 1.0

        while True:
            if interrupt_on_corner:
                _, turning = self.setCornerTurningYaw()
                if turning:
                    print("⚠️ Yaw hizalama sırasında köşe algılandı, iptal.")
                    return False

            if self.ult.getDistance("front") < 15:
                self.motor.set_throttle(1.5)
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

        self.kit.servo[0].angle = 90
        self.kit.servo[1].angle = 90
        return True

    def perform_corner_turn_with_interrupt(self):
        print(f"🔁 Köşe dönüşü başlatıldı: hedef yaw = {self.default_yaw}")

        def get_error():
            current = self.mpu.yaw()
            return (self.default_yaw - current + 540) % 360 - 180

        K = 3.4
        MIN_A, MAX_A = 60, 120
        DEAD_BAND = 0.5
        TARGET_THRESH = 1.0

        while True:
            if self.isBlock():
                print("🟥 Dönüş sırasında blok algılandı! Dönüş iptal.")
                return False

            if self.ult.getDistance("front") < 15:
                self.motor.set_throttle(1.5)
                break

            self.motor.set_throttle(self.move_speed)

            error = get_error()
            if abs(error) < TARGET_THRESH:
                print("✅ Dönüş tamamlandı.")
                break

            if abs(error) < DEAD_BAND:
                angle = 90
            else:
                angle = 90 - K * error
                angle = max(MIN_A, min(MAX_A, angle + self.turnOffset))
 
            self.kit.servo[0].angle = angle 
            self.kit.servo[1].angle = angle
            time.sleep(0.01)

        self.kit.servo[0].angle = 90
        self.kit.servo[1].angle = 90
        return True

    def calculate_dynamic_yaw(self, x, signature, current_yaw, frame_width=316, max_yaw_offset=30):
        center_x = frame_width / 2
        distance_from_center = abs(x - center_x)
        inverse_weight = 1 - (distance_from_center / center_x)

        direction = 1 if signature == 2 else -1
        yaw_offset = direction * inverse_weight * max_yaw_offset
        target_yaw = (current_yaw + yaw_offset) % 360
        return target_yaw

    def run(self):
        while True:
            blocks = self.cam.get_blocks()

            yaw, turning = self.setCornerTurningYaw()
            self.default_yaw = yaw

            if turning:
                success = self.perform_corner_turn_with_interrupt()
                if not success:
                    continue

            if self.isBlock():
                x = blocks[0]['x']
                sig = blocks[0]['signature']
                target = self.calculate_dynamic_yaw(x, sig, self.mpu.yaw())
                print(f"🎯 Hedef yaw: {target}")
                self.turn_to_yaw(target)

                while self.isBlock():
                    self.motor.set_throttle(self.move_speed)
                    time.sleep(0.05)

                print("✅ Blok geçildi, eski yönüne dönülüyor...")
                time.sleep(0.15)

                alignment_done = self.turn_to_yaw(self.default_yaw, interrupt_on_corner=True)
                if not alignment_done:
                    print("➡️ Hizalama iptal edildi, köşe dönüşüne geçiliyor.")
                    self.perform_corner_turn_with_interrupt()

            else:
                self.motor.set_throttle(1.6)
                print("⛔ Blok yok.")
            time.sleep(0.1)


if __name__ == "__main__":
    car = Car()
    car.run()