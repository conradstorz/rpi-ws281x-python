import time

from luma.led_matrix.device import ws2812, UNICORN_HAT
from luma.core.render import canvas

device = ws2812(width=8, height=8, mapping=UNICORN_HAT)

for y in range(device.height):
    for x in range(device.width):
        with canvas(device) as draw:
            draw.point((x, y), fill="green")
        time.sleep(0.5)