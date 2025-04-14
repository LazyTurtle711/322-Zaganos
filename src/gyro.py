# Import required libraries
import mpu6050  # Library for interfacing with MPU6050 sensor
import math  # For mathematical calculations like square root and trigonometry
import time  # For tracking time between readings


class MPU6050:
    def __init__(self, address=0x68, alpha=0.96):
        """
        Initialize the MPU6050 helper class.

        Parameters:
        - address: I2C address of the MPU6050 (default 0x68)
        - alpha: Complementary filter coefficient (default 0.96)
                 Higher alpha values give more weight to gyroscope data
                 Lower alpha values give more weight to accelerometer data
        """
        # Create an instance of the MPU6050 sensor at the specified I2C address
        self.sensor = mpu6050.mpu6050(address)

        # Store the filter coefficient for later use
        self.alpha = alpha

        # Initialize angles and timing
        self.reset_gyro()

        # Set initial timestamp for calculating time differences
        self.previous_time = time.time()

    def reset_gyro(self):
        """
        Resets the gyro-based yaw, pitch, and roll angles to zero.
        Reads the current accelerometer and gyroscope data to recalibrate.
        This can be used to establish a new reference orientation.
        """
        # Get current accelerometer readings
        accel_data = self.sensor.get_accel_data()

        # Reset yaw to zero (yaw can't be calculated from accelerometer alone)
        self.yaw_angle = 0

        # Calculate initial pitch angle from accelerometer data
        # Convert from radians to degrees using the factor (180.0 / math.pi)
        # The arctangent calculation gives the angle between the x-axis and the ground plane
        self.pitch_angle = math.atan2(accel_data['x'], math.sqrt(accel_data['y'] ** 2 + accel_data['z'] ** 2)) * (180.0 / math.pi)

        # Calculate initial roll angle from accelerometer data
        # Similar to pitch, but using the y-axis instead of x-axis
        self.roll_angle = math.atan2(accel_data['y'], math.sqrt(accel_data['x'] ** 2 + accel_data['z'] ** 2)) * (180.0 / math.pi)

        # Reset the time tracker to the current time
        self.previous_time = time.time()

    def _update_angles(self):
        """
        Updates the yaw, pitch, and roll angles using the gyroscope and accelerometer data.
        This method implements a complementary filter to combine data from both sensors.
        It's called internally before returning any angle values.
        """
        # Calculate time elapsed since the last update
        current_time = time.time()
        delta_time = current_time - self.previous_time
        self.previous_time = current_time  # Update the timestamp for next calculation

        # Get fresh sensor data
        accel_data = self.sensor.get_accel_data()  # Accelerometer data in g forces
        gyro_data = self.sensor.get_gyro_data()  # Gyroscope data in degrees per second

        # --- Update pitch angle ---
        # 1. Calculate pitch from accelerometer (absolute but noisy)
        accel_pitch = math.atan2(accel_data['x'], math.sqrt(accel_data['y'] ** 2 + accel_data['z'] ** 2)) * (180.0 / math.pi)

        # 2. Calculate pitch from gyroscope (relative but smooth)
        # Integrate gyro rate to get change in angle
        gyro_pitch = self.pitch_angle + gyro_data['x'] * delta_time

        # 3. Combine both using complementary filter
        # alpha controls how much we trust each sensor
        self.pitch_angle = self.alpha * gyro_pitch + (1 - self.alpha) * accel_pitch

        # --- Update roll angle ---
        # Similar process to pitch, but for the roll axis
        accel_roll = math.atan2(accel_data['y'], math.sqrt(accel_data['x'] ** 2 + accel_data['z'] ** 2)) * (180.0 / math.pi)
        gyro_roll = self.roll_angle + gyro_data['y'] * delta_time
        self.roll_angle = self.alpha * gyro_roll + (1 - self.alpha) * accel_roll

        # --- Update yaw angle ---
        # Yaw can only be calculated from gyroscope data because the accelerometer
        # can't detect rotation around the gravity vector
        # Subtract 1 from z-axis reading to compensate for sensor bias/drift
        self.yaw_angle += (gyro_data['z'] - 1) * delta_time

    def yaw(self):
        """
        Calculate and return the current yaw angle (rotation around z-axis).
        Yaw is the "heading" or compass direction.
        """
        self._update_angles()  # Refresh all angle calculations
        return self.yaw_angle

    def pitch(self):
        """
        Calculate and return the current pitch angle (rotation around x-axis).
        Pitch is the nose up/down motion.
        """
        self._update_angles()  # Refresh all angle calculations
        return self.pitch_angle

    def roll(self):
        """
        Calculate and return the current roll angle (rotation around y-axis).
        Roll is the side-to-side tilting motion.
        """
        self._update_angles()  # Refresh all angle calculations
        return self.roll_angle

if __name__ == '__main__':
    import time

    mpu = MPU6050()
    mpu.reset_gyro()

    # Start an infinite loop to continuously read and display sensor data
    while True:
        # Get the current yaw angle from the MPU6050 sensor and print it
        print(mpu.yaw())
        time.sleep(0.05)