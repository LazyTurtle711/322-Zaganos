from gpiozero import Button
import time

# GPIO 12 pinine bağlı buton
button = Button(12)

while True:
    if button.is_pressed:
        print("Butona basıldı!")
    else:
        print("Butona basılmıyor.")
    time.sleep(0.1)
