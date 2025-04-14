import RPi.GPIO as GPIO  # Library for controlling Raspberry Pi GPIO pins
import time  # For timing and delays

# GPIO pin assignments for the TCS3200 color sensor
s2 = 23  # S2 pin controls which color filter is active (with S3)
s3 = 24  # S3 pin controls which color filter is active (with S2)
signal = 25  # Signal pin outputs the frequency proportional to light intensity

# Number of cycles to sample for more accurate readings
# Higher values give more accurate results but take longer
NUM_CYCLES = 10


def setup():
    """
    Set up the GPIO pins for the TCS3200 color sensor.
    Must be called before any other functions.
    """
    # Set the GPIO pin numbering mode to BCM (Broadcom SOC channel numbers)
    # This uses the GPIO numbers rather than physical pin numbers
    GPIO.setmode(GPIO.BCM)

    # Configure the signal pin as an input with pull-up resistor
    # The sensor outputs a square wave, and we'll measure its frequency
    GPIO.setup(signal, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Configure S2 and S3 pins as outputs to select color filters
    GPIO.setup(s2, GPIO.OUT)
    GPIO.setup(s3, GPIO.OUT)


def get_color_value(s2_state, s3_state):
    """
    Measure the frequency output for a specific color filter setting.

    Parameters:
    - s2_state: GPIO.LOW or GPIO.HIGH to select color filter with S2 pin
    - s3_state: GPIO.LOW or GPIO.HIGH to select color filter with S3 pin

    S2    S3    Photodiode Type
    LOW   LOW   Red
    LOW   HIGH  Blue
    HIGH  HIGH  Green
    HIGH  LOW   Clear (no filter)

    Returns:
    - Frequency in Hz, which corresponds to the color intensity
    """
    # Set the S2 and S3 pins to select the desired color filter
    GPIO.output(s2, s2_state)
    GPIO.output(s3, s3_state)

    # Wait for the sensor to stabilize after changing the filter
    time.sleep(0.3)

    # Record the start time for frequency calculation
    start = time.time()

    # Count NUM_CYCLES of the square wave from the sensor
    # Each falling edge represents one cycle of the frequency
    for _ in range(NUM_CYCLES):
        GPIO.wait_for_edge(signal, GPIO.FALLING)

    # Calculate the elapsed time for NUM_CYCLES
    duration = time.time() - start

    # Return the frequency (cycles per second, Hz)
    # Higher frequency means higher intensity of that color
    return NUM_CYCLES / duration


def loop():
    """
    Main loop that continuously reads color values and detects colors.
    This function runs indefinitely until interrupted.
    """
    while True:
        # Read the intensity of each primary color
        # Lower values indicate higher color intensity (due to sensor characteristics)
        red = get_color_value(GPIO.LOW, GPIO.LOW)  # Read red intensity
        blue = get_color_value(GPIO.LOW, GPIO.HIGH)  # Read blue intensity
        green = get_color_value(GPIO.HIGH, GPIO.HIGH)  # Read green intensity

        print()  # Print a blank line between readings

        # f"RGB Values: Red={red:.2f}, Green={green:.2f}, Blue={blue:.2f}"

        # Color detection based on calibrated threshold values
        # These thresholds may need adjustment for different lighting conditions
        if green < 7000 and blue < 7000 and red > 12000:
            # Red is dominant when red value is high and others are low
            print("Red detected")
        elif red < 12000 and blue < 12000 and green > 12000:
            # Green is dominant when green value is high and others are low
            print("Green detected")
        elif green < 7000 and red < 7000 and blue > 12000:
            # Blue is dominant when blue value is high and others are low
            print("Blue detected")


def endprogram():
    """
    Clean up GPIO resources before exiting.
    Should be called when the program is terminating.
    """
    GPIO.cleanup()  # Release GPIO resources to prevent warnings in future programs


# Main program entry point
if __name__ == '__main__':
    setup()  # Initialize GPIO pins
    try:
        loop()  # Start the main detection loop
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully by cleaning up GPIO
        endprogram()