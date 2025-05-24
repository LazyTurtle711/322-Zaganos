from get_blocks import PixyCam

cam = PixyCam()

def setServo():
    blocks = cam.get_blocks()
    block = blocks[0]

    block["x"]