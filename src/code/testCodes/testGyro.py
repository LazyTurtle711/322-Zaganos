from gyro import MPU6050

gyro = MPU6050()
gyro.reset_gyro()
print(gyro.yaw())