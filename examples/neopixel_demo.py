#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

# Portions of this script were adapted from:
#  https://github.com/pimoroni/unicorn-hat/blob/master/examples/demo.py

import math
import time
import colorsys

from luma.led_matrix.device import neopixel
from luma.core.render import canvas
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, TINY_FONT
from PIL import ImageFont

xsize = 32
ysize = 8


MAP_BTF = []
tmp_BTF = []
map_x = 32
map_y = 8
xlist = list(range(map_x))
for x in xlist:
    ylist = list(range(x*map_y,x*map_y+map_y))
    if x%2 == 1: # invert list to account for serpentine layout
        ylist.reverse()
    tmp_BTF.append(ylist)


for y in range(map_y):
    for l in tmp_BTF:
        MAP_BTF.append(l[y])

print(MAP_BTF)

# create matrix device
device = neopixel(width=xsize, height=ysize, mapping=MAP_BTF, rotate=0)

# call the random pixel effect
from random_colors import UseLumaLEDMatrix
#result = UseLumaLEDMatrix(device, xsize, ysize, 1, 100)

# twisty swirly goodness
def swirl(x, y, step):
    x -= (device.width / 2)
    y -= (device.height / 2)

    dist = math.sqrt(pow(x, 2) + pow(y, 2)) / 2.0
    angle = (step / 10.0) + (dist * 1.5)
    s = math.sin(angle)
    c = math.cos(angle)

    xs = x * c - y * s
    ys = x * s + y * c

    r = abs(xs + ys)
    r = r * 64.0
    r -= 20

    return (r, r + (s * 130), r + (c * 130))


# roto-zooming checker board
def checker(x, y, step):
    x -= (device.width / 2)
    y -= (device.height / 2)

    angle = (step / 10.0)
    s = math.sin(angle)
    c = math.cos(angle)

    xs = x * c - y * s
    ys = x * s + y * c

    xs -= math.sin(step / 200.0) * 40.0
    ys -= math.cos(step / 200.0) * 40.0

    scale = step % 20
    scale /= 20
    scale = (math.sin(step / 50.0) / 8.0) + 0.25

    xs *= scale
    ys *= scale

    xo = abs(xs) - int(abs(xs))
    yo = abs(ys) - int(abs(ys))
    l = 0 if (math.floor(xs) + math.floor(ys)) % 2 else 1 if xo > .1 and yo > .1 else .5

    r, g, b = colorsys.hsv_to_rgb((step % 255) / 255.0, 1, l)

    return (r * 255, g * 255, b * 255)


# weeee waaaah
def blues_and_twos(x, y, step):
    x -= (device.width / 2)
    y -= (device.height / 2)

#    xs = (math.sin((x + step) / 10.0) / 2.0) + 1.0
#    ys = (math.cos((y + step) / 10.0) / 2.0) + 1.0

    scale = math.sin(step / 6.0) / 1.5
    r = math.sin((x * scale) / 1.0) + math.cos((y * scale) / 1.0)
    b = math.sin(x * scale / 2.0) + math.cos(y * scale / 2.0)
    g = r - .8
    g = 0 if g < 0 else g

    b -= r
    b /= 1.4

    return (r * 255, (b + g) * 255, g * 255)


# rainbow search spotlights
def rainbow_search(x, y, step):
    xs = math.sin((step) / 100.0) * 20.0
    ys = math.cos((step) / 100.0) * 20.0

    scale = ((math.sin(step / 60.0) + 1.0) / 5.0) + 0.2
    r = math.sin((x + xs) * scale) + math.cos((y + xs) * scale)
    g = math.sin((x + xs) * scale) + math.cos((y + ys) * scale)
    b = math.sin((x + ys) * scale) + math.cos((y + ys) * scale)

    return (r * 255, g * 255, b * 255)


# zoom tunnel
def tunnel(x, y, step):

    speed = step / 100.0
    x -= (device.width / 2)
    y -= (device.height / 2)

    xo = math.sin(step / 27.0) * 2
    yo = math.cos(step / 18.0) * 2

    x += xo
    y += yo

    if y == 0:
        if x < 0:
            angle = -(math.pi / 2)
        else:
            angle = (math.pi / 2)
    else:
        angle = math.atan(x / y)

    if y > 0:
        angle += math.pi

    angle /= 2 * math.pi  # convert angle to 0...1 range

    shade = math.sqrt(math.pow(x, 2) + math.pow(y, 2)) / 2.1
    shade = 1 if shade > 1 else shade

    angle += speed
    depth = speed + (math.sqrt(math.pow(x, 2) + math.pow(y, 2)) / 10)

    col1 = colorsys.hsv_to_rgb((step % 255) / 255.0, 1, .8)
    col2 = colorsys.hsv_to_rgb((step % 255) / 255.0, 1, .3)

    col = col1 if int(abs(angle * 6.0)) % 2 == 0 else col2

    td = .3 if int(abs(depth * 3.0)) % 2 == 0 else 0

    col = (col[0] + td, col[1] + td, col[2] + td)

    col = (col[0] * shade, col[1] * shade, col[2] * shade)

    return (col[0] * 255, col[1] * 255, col[2] * 255)


def gfx(device):
    effects = [tunnel, rainbow_search, checker, swirl]

    step = 0
    while True:
        for i in range(500):
            with canvas(device) as draw:
                for y in range(device.height):
                    for x in range(device.width):
                        r, g, b = effects[0](x, y, step)
                        if i > 400:
                            r2, g2, b2 = effects[-1](x, y, step)

                            ratio = (500.00 - i) / 100.0
                            r = r * ratio + r2 * (1.0 - ratio)
                            g = g * ratio + g2 * (1.0 - ratio)
                            b = b * ratio + b2 * (1.0 - ratio)
                        r = int(max(0, min(255, r)))
                        g = int(max(0, min(255, g)))
                        b = int(max(0, min(255, b)))
                        draw.point((x, y), (r, g, b))

            step += 1

            time.sleep(0.01)

        effect = effects.pop()
        effects.insert(0, effect)
    return True


#def make_font(name, size):
#   font_path = os.path.abspath(os.path.join(
#       os.path.dirname(__file__), 'fonts', name))
#   return ImageFont.truetype(font_path, size)


def main():
    msg = "Neopixel WS2812 LED Matrix Demo"
    print(msg)
    #px8font = make_font("pixelmix.ttf", 8)
    show_message(device, msg, y_offset=-1, fill="green", font = TINY_FONT)
    time.sleep(1)

    print('Draw text "A" and "T"')
    with canvas(device) as draw:
        text(draw, (0, -1), txt="A", fill="red", font=TINY_FONT)
        text(draw, (4, -1), txt="T", fill="green", font=TINY_FONT)

    time.sleep(1)

    with canvas(device) as draw:
        #rectangle(draw, device.bounding_box, outline="white", fill="black")
        text(draw, (0, -1), "Hello world", fill="white", font=TINY_FONT)

    time.sleep(2)

    print('Draw lines in the rainbow')
    with canvas(device) as draw:
        draw.line((0, 0, 0, device.height), fill="red")
        draw.line((1, 0, 1, device.height), fill="orange")
        draw.line((2, 0, 2, device.height), fill="yellow")
        draw.line((3, 0, 3, device.height), fill="green")
        draw.line((4, 0, 4, device.height), fill="blue")
        draw.line((5, 0, 5, device.height), fill="indigo")
        draw.line((6, 0, 6, device.height), fill="violet")
        draw.line((7, 0, 7, device.height), fill="white")

    time.sleep(4)


    print('Vary intensity from 0 - 255')
    for _ in range(5):
        for intensity in range(16):
            device.contrast(intensity * 16)
            time.sleep(0.1)

    print('Set contrast to: 0x80')
    device.contrast(0x80)
    time.sleep(1)


    print('scan lines across')
    #x&y are reversed for some reason
    ylist = list(range(device.width))
    print(ylist)
    for x in range(device.height): #repeat scan for multiple
        print(x)
        if x%2 == 0: ylist.reverse()
        for y in ylist: #scan the line through the list
            with canvas(device) as draw:
                draw.line([(y, 0), (y, device.width)], fill="red")
            time.sleep(0.1)

    time.sleep(2)

    print('scan lines up/down')
    #x&y are reversed for some reason
    xlist = list(range(device.height))
    print(xlist)
    for y in range(device.width): #repeat scan for multiple
        print(y)
        if y%2 == 0: xlist.reverse()
        for x in xlist: #scan the line through the list
            with canvas(device) as draw:
                draw.line([(x, 0), (x, device.height)], fill="red")
            time.sleep(0.1)

    time.sleep(2)


    print('Set contrast to: 0x80')
    device.contrast(0x80)
    time.sleep(1)

    print('Start "gfx" routine')
    #gfx(device)
    return True


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
