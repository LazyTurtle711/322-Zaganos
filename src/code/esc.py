from gpiozero import PWMOutputDevice  # Import PWM output for controlling ESC
from gpiozero import DigitalOutputDevice
from time import sleep  # For implementing delays


class ESC:
    def __init__(self, esc_pin=26, freq=50):
        """
        Initialize an Electronic Speed Controller (ESC) interface.

        Parameters:
        - esc_pin: GPIO pin number connected to the ESC signal wire (default: 26)
        - freq: PWM frequency in Hz (default: 50Hz - standard for most RC ESCs)
               Most ESCs expect a 50Hz signal (20ms period)
        """
        # Create a PWM output device on the specified pin with the specified frequency
        # This will generate the control signal for the ESC
        self.device = PWMOutputDevice(esc_pin, frequency=freq)
        self.set_throttle(1.5)
        mosfet = DigitalOutputDevice(14)
        mosfet.on()
        
        print(f"ESC initialized! Pin: {esc_pin} Frequency: {freq}")
        # Short delay after initialization

    def set_throttle(self, pulse_ms, out=True):
        """
        Set throttle based on pulse width (1 ms to 2 ms).

        Parameters:
        - pulse_ms: Pulse width in milliseconds:
            - 1 ms = Full forward
            - 1.5 ms = Neutral (stop)
            - 2 ms = Full reverse
          Values between these provide proportional control.

        - out: Whether to print the duty cycle value (default: True)

        Note: The actual direction (forward vs reverse) may vary depending on
        ESC settings and motor wiring. You may need to swap directions in your code.
        """
        # Convert pulse width (ms) to duty cycle (percentage of 20 ms period)
        # e.g., 1ms pulse = 1/20 = 0.05 = 5% duty cycle
        #       2ms pulse = 2/20 = 0.10 = 10% duty cycle
        duty_cycle = pulse_ms / 20.0

        # Set the PWM output to the calculated duty cycle
        self.device.value = duty_cycle

        # Optionally print the current duty cycle
        if out:
            print(f"Set duty cycle to {duty_cycle * 100}%")

    def calibrate(self):
        """
        Run an ESC calibration sequence.

        This helps the ESC learn the pulse range of your controller.
        Follow the specific instructions for your ESC model as
        calibration sequences can vary between manufacturers.

        This is a generic sequence that works with many ESCs:
        1. Set neutral position
        2. Set full reverse/brake
        3. Set full forward
        """
        # Step 1: Set to neutral position (1.5ms pulse)
        self.set_throttle(1.5)
        print("1")
        sleep(3)  # Wait for ESC to register neutral position

        # Step 2: Set to full forward (2ms pulse)
        self.set_throttle(1.6)
        print("2")
        sleep(3)  # Wait for ESC to register full forward

        # Step 3: Set to full reverse/brake (1ms pulse)
       # self.set_throttle(1)
        #print("3")
        #sleep(3)  # Wait for ESC to register full reverse/brake

if __name__ == '__main__':
    # Create a new ESC object
    esc = ESC(esc_pin=26, freq=50)

    # Start the ESC calibration
    esc.calibrate()

