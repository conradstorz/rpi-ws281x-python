import time

from luma.led_matrix.device import ws2812
from luma.core.render import canvas

BTF_MATRIX = []

map_x = 32
map_y = 8

# HAT = [x for x in range(map_x), y for y in range(map_y)]

for x in range(map_x):
    ylist = list(range(x*map_y,x*map_y+map_y))
    if x%2 == 0: # invert list to account for serpentine layout
        ylist.reverse()
    for y in ylist:
        BTF_MATRIX.append(y)


device = ws2812(width=map_x, height=map_y, mapping=BTF_MATRIX)

for x in range(device.width):
    for y in range(device.height):
        with canvas(device) as draw:
            draw.point((x, y), fill="blue")
        time.sleep(0.05)
