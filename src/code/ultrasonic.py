import RPi.GPIO as gpio
import time

class Ultras:
    def __init__(self, pins):
        self.pins = pins
        gpio.setmode(gpio.BCM)
        
        self.frontEcho = self.pins["front"][0]
        self.frontTrig = self.pins["front"][1]
        gpio.setup(self.frontEcho, gpio.IN)
        gpio.setup(self.frontTrig, gpio.OUT)
        
        self.leftEcho = self.pins["left"][0]
        self.leftTrig = self.pins["left"][1]
        gpio.setup(self.leftEcho, gpio.IN)
        gpio.setup(self.leftTrig, gpio.OUT)
        
        self.rightEcho = self.pins["right"][0]
        self.rightTrig = self.pins["right"][1]
        gpio.setup(self.rightEcho, gpio.IN)
        gpio.setup(self.rightTrig, gpio.OUT)
        
        self.backEcho = self.pins["back"][0]
        self.backTrig = self.pins["back"][1]
        gpio.setup(self.backEcho, gpio.IN)
        gpio.setup(self.backTrig, gpio.OUT)

        # time.sleep(0.5)
        
    def getDistance(self, ultra):
        pulse_start = pulse_end = 0
        
        echo = self.pins[ultra][0]
        trig = self.pins[ultra][1]
        
        gpio.output(trig, False)
        time.sleep(0.1)
        gpio.output(trig, True)
        time.sleep(0.00001)
        gpio.output(trig, False)
        while gpio.input(echo) == 0 :
            pulse_start = time.time()
        while gpio.input(echo) == 1 :
            pulse_end = time.time()
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17000
        if pulse_duration >=0.01746:
            print("timeout")
            return None
        elif distance > 200 or distance==0:
            print("out of range")
            return 200
        distance = round(distance, 3)
        print (f"{ultra} distance: {distance}")
        return distance
        
    def exit(self):
        gpio.cleanup()
        # sys.exit(0)
        

if __name__ == "__main__":
    ultraPins = { # Echo, Trigger
        "front": [5, 7],
        "left": [6, 24],
        "right": [13, 23],
        "back": [19, 8]
    }
    
    ult = Ultras(ultraPins)
    try:
        while True:
            ult.getDistance("left")
    except KeyboardInterrupt:
        ult.exit()