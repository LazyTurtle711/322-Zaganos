from gpiozero import DistanceSensor


class Ultrasonic:
    def __init__(self):
        self.UltraL = DistanceSensor(echo=6, trigger=24, max_distance=2.0)  # sol ultrasonik
        self.UltraR = DistanceSensor(echo=13, trigger=23, max_distance=2.0)  # sol ultrasonik
        self.UltraF = DistanceSensor(echo=5, trigger=7, max_distance=2.0)  # sol ultrasonik


    def getDistance(self, sensor):
        distance = sensor.distance * 100  # convert to cm
        if distance < 0 or distance > 300:
            print('out of range')
            return None
        else:
            return distance
        # time.sleep(0.1)
    
    def getAllUltarsonics(self):
        distanceL, distanceR, distanceF = self.getDistance(self.UltraL), self.getDistance(self.UltraR), self.getDistance(self.UltraF) 
        print(f"left|{distanceL} right|{distanceR} front|{distanceF}")
        return self.getDistance(self.UltraL), self.getDistance(self.UltraR), self.getDistance(self.UltraF)
    

if __name__ == "__main__":
    ultrasonics = Ultrasonic()
    l, r, f = ultrasonics.getAllUltarsonics()