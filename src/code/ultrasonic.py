from gpiozero import DistanceSensor
from adafruit_servokit import ServoKit
import time

class Ultras:
    def __init__(self, pins):
        self.prevDistance = 0
        self.pins = pins
        self.kit = ServoKit(channels=16)

        self.sensors = {
            "front": DistanceSensor(echo=pins["front"][0], trigger=pins["front"][1], max_distance=2.0),
            "left": DistanceSensor(echo=pins["left"][0], trigger=pins["left"][1], max_distance=2.0),
            "right": DistanceSensor(echo=pins["right"][0], trigger=pins["right"][1], max_distance=2.0),
            "back": DistanceSensor(echo=pins["back"][0], trigger=pins["back"][1], max_distance=2.0),
        }

    def getDistance(self, ultra):
        distance = self.sensors[ultra].distance * 100  # convert to cm
        if distance == 0 or distance > 200:
            print(f"{ultra} out of range")
            return 200
        distance = round(distance, 3)
        print(f"{ultra} distance: {distance} cm")
        self.prevDistance = distance
        return distance

    def exit(self):
        # gpiozero cleans up automatically, but you can define this if needed
        pass

    def getAvgDistance(self, ultra, times=3):
        distances = []
        for _ in range(times):
            distances.append(self.getDistance(ultra))
            time.sleep(0.05)
        return sum(distances) / len(distances)

    def getPos(self):
        return self.getAvgDistance("left") - self.getAvgDistance("right")

    def goto(self, pos):
        error = pos - self.getPos()
        # implement control logic here

if __name__ == "__main__":
    ultraPins = {  # echo, trigger
        "front": (5, 7),
        "left": (6, 24),
        "right": (13, 23),
        "back": (19, 8)
    }

    ult = Ultras(ultraPins)
    try:
        while True:
            ult.getDistance("left")
    except KeyboardInterrupt:
        ult.exit()
