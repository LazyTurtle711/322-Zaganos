from main import Robot

robot = Robot()

while True:
    robot.motor.set_throttle(1.6)
    robot.servo_adjust(1,2,3,4,5,6,7)
    if robot.isCorner():
        robot.turn()
    elif not robot.isCentered():
        robot.centerCorridor()
    else:
        robot.robot.keep_heading_straight()



    

