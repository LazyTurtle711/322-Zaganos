import time  # For implementing delays
import board  # Adafruit's board library for pinout definitions
import busio  # For I2C communication
import adafruit_ads1x15.ads1115 as ADS  # ADS1115 16-bit ADC library
from adafruit_ads1x15.analog_in import AnalogIn  # Helper class for reading analog signals

# Set up I2C communication protocol
i2c = busio.I2C(board.SCL, board.SDA)

# Create an ADS1115 ADC (analog-to-digital converter) object
ads = ADS.ADS1115(i2c)

# Set the gain of the ADC
# The gain determines the input voltage range:
# gain=1: ±4.096V range
# gain=2: ±2.048V range
# gain=4: ±1.024V range
# gain=8: ±0.512V range
# gain=16: ±0.256V range
ads.gain = 1

# Create analog input channels
chan0 = AnalogIn(ads, ADS.P0)
chan1 = AnalogIn(ads, ADS.P1)
chan2 = AnalogIn(ads, ADS.P2)
chan3 = AnalogIn(ads, ADS.P3)

while True:
    # Print incoming voltage from channels
    print(chan0.voltage)
    print(chan1.voltage)
    print(chan2.voltage)
    print(chan3.voltage)
    time.sleep(0.05)