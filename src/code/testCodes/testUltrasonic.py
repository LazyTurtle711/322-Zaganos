from ultrasonic import getDistance
from gpiozero import DistanceSensor

UltraL = DistanceSensor(echo=17, trigger=27, max_distance=2.0)
print(getDistance(UltraL))