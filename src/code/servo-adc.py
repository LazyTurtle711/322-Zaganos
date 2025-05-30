import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_servokit import ServoKit
from gpiozero import DistanceSensor
from gyro import MPU6050
from esc import ESC

class AutonomousCar:
    def __init__(self):
        self.left_ultrasonic = DistanceSensor(echo=13, trigger=25, max_distance=2.0)
        self.right_ultrasonic = DistanceSensor(echo=19, trigger=8, max_distance=2.0)
        self.forward_ultrasonic = DistanceSensor(echo=5, trigger=24, max_distance=2.0)

# TODO: u dönüşünden sonra onUltrasonic değişecek
        self.mpu = MPU6050()
        self.mpu.reset_gyro()

        self.kit = ServoKit(channels=16)
        self.kit.servo[2].angle = 0
        time.sleep(1)

        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(self.i2c, address=0x48)
        self.ads.gain = 1
        self.chan0 = AnalogIn(self.ads, ADS.P0)

        self.servo0_voltage = self.chan0.voltage
        print(f"servo0 = {self.servo0_voltage}")

        self.kit.servo[2].angle = 90
        time.sleep(1)

        self.servo180_voltage = self.chan0.voltage
        print(f"servo180 = {self.servo180_voltage}")

        self.motor = ESC()
        self.move_speed = 1.6
        self.default_yaw = 0

        self.last_turn_time = 0
        self.turn_cooldown  = 2.0

    
    def map(self, x, x1, x2, y1, y2):
        return float((x-x1)*(y2-y1)/(x2-x1)+y1)


    def get_distance(self, sensor):
        distance = sensor.distance * 100  # cm
        if distance == 0 or distance > 300:
            print("Out of range")
            return None
        else:
            return distance

    def ultrasonic_balance(self, threshold_cm=5):
        """
        Sol ve sağ ultrasonik arasındaki fark |fark| <= threshold_cm 
        olana kadar servo[0] ve [1] açılarını kaydırarak aracı ortalar.
        """
        print("🔁 Ultrasonik ortalama başlıyor...")
        while True:
            left  = self.get_distance(self.left_ultrasonic)
            right = self.get_distance(self.right_ultrasonic)
            if left is None or right is None:
                continue

            diff = right - left
            if abs(diff) <= threshold_cm:
                print("✅ Araç ortalandı.")
                break

            # bias: farkın %40’ı, ±10° ile sınırla
            bias = max(min(diff * 0.4, 10), -10)
            angle = max(60, min(120, 90 + bias))
            self.kit.servo[0].angle = angle
            self.kit.servo[1].angle = angle

            print(f"Sol: {left:.1f} cm | Sağ: {right:.1f} cm | Fark: {diff:.1f} → Servo: {angle:.1f}")
            time.sleep(0.1)

    # ───── 4. Yaw’a göre hizalama ─────────────────────────────────────────────

    def turn_to_yaw(self, target_yaw):
        """
        target_yaw’a en kısa yönden dönerken servo[0] ve [1] açılarını
        error’a göre kaydırır. |error| < 2° olunca hizalama biter.
        """
        print(f"🎯 Yaw'a hizalanma başlıyor: hedef = {target_yaw}°")

        def get_error():
            # MPU’dan okunan current_yaw
            current_yaw = self.mpu.yaw()
            # (target–current +540)%360–180 ile error’ü –180…+180 aralığına al
            return (target_yaw - current_yaw + 540) % 360 - 180

        while True:
            error = get_error()
            if abs(error) < 25:
                print("✅ Yaw hizalama tamamlandı.")
                break

            # error kadar ± açı kaydır, 60–120° aralığına sınırla
            angle = max(60, min(120, 90 + error))
            self.kit.servo[0].angle = angle
            self.kit.servo[1].angle = angle
            print(f"Yaw Hata: {error:.2f}° → Servo Açısı: {angle:.2f}°")
            time.sleep(0.05)

        # hizalama sonunda düz konum
        self.kit.servo[0].angle = 90
        self.kit.servo[1].angle = 90

    def setCornerTurningYaw(self):
        """
        Eğer önde dar geçiş varsa ve yalnızca bir yan yol açıksa,
        self.default_yaw’ı ±90° kaydırır ve (self.default_yaw, True) döner.
        Aksi halde (self.default_yaw, False).
        Aynı anda birden fazla rapid algılamayı önlemek için cooldown var.
        """
        now = time.time()
        # Cooldown'daysa hiç algılama yapma
        if now - self.last_turn_time < self.turn_cooldown:
            return self.default_yaw, False

        SIDE_TH  = 150
        FRONT_TH = 78

        dl = self.get_distance(self.left_ultrasonic)
        dr = self.get_distance(self.right_ultrasonic)
        df = self.get_distance(self.forward_ultrasonic)

        print(f"left: {dl} | right: {dr} | forward: {df}")

        # Geçersiz ölçüm varsa vazgeç
        if dl is None or dr is None or df is None:
            return self.default_yaw, False

        # Önde daralmışsa yanları kontrol et
        if df < FRONT_TH:
            # Sola dönme koşulu
            if dl  > SIDE_TH and dr <= SIDE_TH:
                self.default_yaw = (self.default_yaw - 90) % 360
                self.last_turn_time = now
                return self.default_yaw, True

            # Sağa dönme koşulu
            if dr  > SIDE_TH and dl <= SIDE_TH:
                self.default_yaw = (self.default_yaw + 90) % 360
                self.last_turn_time = now
                return self.default_yaw, True

        return self.default_yaw, False


    def run(self):
        while True:
            # self.motor.set_throttle(self.move_speed)
            time.sleep(0.01)
            self.default_yaw, isTurning = self.setCornerTurningYaw()
            print(isTurning)
            print(self.default_yaw)
            if isTurning:
                print("burada")
                time.sleep(3)
if __name__ == "__main__":
    car = AutonomousCar()
    car.run()