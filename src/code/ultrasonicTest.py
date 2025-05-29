import RPi.GPIO as GPIO
import time
import sys
import signal

TRIG = 27  # BCM pin
ECHO = 17  # BCM pin

def signal_handler(sig, frame):
    print('\nÇıkılıyor...')
    GPIO.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def get_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.05)

    # Trigger pulse
    GPIO.output(TRIG, True)
    time.sleep(0.00001)  # 10 µs pulse
    GPIO.output(TRIG, False)

    # Echo start
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    # Echo end
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # cm
    distance = round(distance, 2)

    if 2 <= distance <= 300:
        print("Mesafe: %.2f cm" % distance)
        return distance
    else:
        print("Menzil dışı")
        return None

# Ana döngü
while True:
    get_distance()
    time.sleep(0.5)
