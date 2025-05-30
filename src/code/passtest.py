from get_blocks import PixyCam

rec1 = (0, 100, 316, 200)
rec2 = (280, 140, 318, 235)
rec3 = (0, 140, 25, 235)

cam = PixyCam()

def rectangle_intersection_area(rect1, rect2):
    x_left = max(rect1[0], rect2[0])
    y_top = max(rect1[1], rect2[1])
    x_right = min(rect1[2], rect2[2])
    y_bottom = min(rect1[3], rect2[3])

    if x_right < x_left or y_bottom < y_top:
        return 0

    return (x_right - x_left) * (y_bottom - y_top)

def main():
    blocks = cam.get_blocks()
    if not blocks:
        return

    block = blocks[0]
    block_x = block["x"]
    block_y = block["y"]
    block_w = block["width"]
    block_h = block["height"]
    
    midX = (block_x + block_w) / 2
    midY = (block_y + block_h) / 2
    block_rec = (block_x, block_y, block_x + block_w, block_y + block_h)

    for rect in [rec2, rec3]:
        if ((midX < 40) and (midY > 110)) or ((midX > 165 and (midY > 110))):
            print("kenarında")
        else:
            print("kenarda değil")

        print((block_x + block_w) / 2, (block_y+block_h)/2)
        break
while True:
    main()
