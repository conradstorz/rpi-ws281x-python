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
from luma.core.legacy.font import TINY_FONT

# from PIL import ImageFont
from random_colors import UseLumaLEDMatrix, color_dict, COLOR_KEYS
from random import choice, shuffle

from tqdm import tqdm
xsize = 32
ysize = 8

# build a pixel mapping for BTF matrix device
MAP_BTF = []
tmp_BTF = []
map_x = xsize
map_y = ysize
xlist = list(range(map_x))

for x in xlist:
    ylist = list(range(x * map_y, x * map_y + map_y))
    if x % 2 == 1:  # invert list to account for serpentine layout
        ylist.reverse()
    tmp_BTF.append(ylist)

for y in range(map_y):
    for l in tmp_BTF:
        MAP_BTF.append(l[y])


# create matrix device
device = neopixel(width=xsize, height=ysize, mapping=MAP_BTF, rotate=0)

local_color_keys = COLOR_KEYS.copy()
shuffle(local_color_keys)

# random dots of color
def glitter(_x, _y, _step):
    """ Take an xy position and return a random color for it
    """
    color = local_color_keys.pop()
    r, g, b = color_dict[color]["rgb"]
    local_color_keys.insert(0, color)
    #time.sleep(step/10000000)
    return (r, g, b)


# twisty swirly goodness
def swirl(x, y, step):

    x -= device.width / 2
    y -= device.height / 2

    dist = math.sqrt(pow(x, 2) + pow(y, 2)) / 2.0
    angle = (step / 10.0) + (dist * 1.5)
    sa = math.sin(angle)
    ca = math.cos(angle)

    xs = x * ca - y * sa
    ys = x * sa + y * ca

    r = abs(xs + ys)
    r = r * 64.0
    r -= 20

    return (r, r + (sa * 130), r + (ca * 130))


# roto-zooming checker board
def checker(x, y, step):

    x -= device.width / 2
    y -= device.height / 2

    angle = step / 10.0
    sa = math.sin(angle)
    ca = math.cos(angle)

    xs = x * ca - y * sa
    ys = x * sa + y * ca

    xs -= math.sin(step / 200.0) * 40.0
    ys -= math.cos(step / 200.0) * 40.0

    scale = step % 20
    scale /= 20
    scale = (math.sin(step / 50.0) / 8.0) + 0.25

    xs *= scale
    ys *= scale

    xo = abs(xs) - int(abs(xs))
    yo = abs(ys) - int(abs(ys))
    xyfloor = math.floor(xs) + math.floor(ys)
    lightness = 0 if xyfloor % 2 else 1 if xo > 0.1 and yo > 0.1 else 0.5

    r, g, b = colorsys.hsv_to_rgb((step % 255) / 255.0, 1, lightness)

    return (r * 255, g * 255, b * 255)


# weeee waaaah
def blues_and_twos(x, y, step):

    x -= device.width / 2
    y -= device.height / 2

    #    xs = (math.sin((x + step) / 10.0) / 2.0) + 1.0
    #    ys = (math.cos((y + step) / 10.0) / 2.0) + 1.0

    scale = math.sin(step / 6.0) / 1.5
    r = math.sin((x * scale) / 1.0) + math.cos((y * scale) / 1.0)
    b = math.sin(x * scale / 2.0) + math.cos(y * scale / 2.0)
    g = r - 0.8
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
    x -= device.width / 2
    y -= device.height / 2

    xo = math.sin(step / 27.0) * 2
    yo = math.cos(step / 18.0) * 2

    x += xo
    y += yo

    if y == 0:
        if x < 0:
            angle = -(math.pi / 2)
        else:
            angle = math.pi / 2
    else:
        angle = math.atan(x / y)

    if y > 0:
        angle += math.pi

    angle /= 2 * math.pi  # convert angle to 0...1 range

    shade = math.sqrt(math.pow(x, 2) + math.pow(y, 2)) / 2.1
    shade = 1 if shade > 1 else shade

    angle += speed
    depth = speed + (math.sqrt(math.pow(x, 2) + math.pow(y, 2)) / 10)

    col1 = colorsys.hsv_to_rgb((step % 255) / 255.0, 1, 0.8)
    col2 = colorsys.hsv_to_rgb((step % 255) / 255.0, 1, 0.3)

    col = col1 if int(abs(angle * 6.0)) % 2 == 0 else col2

    td = 0.3 if int(abs(depth * 3.0)) % 2 == 0 else 0

    col = (col[0] + td, col[1] + td, col[2] + td)

    col = (col[0] * shade, col[1] * shade, col[2] * shade)

    return (col[0] * 255, col[1] * 255, col[2] * 255)


DISPLAY_BUFFER = dict()


def update_display_buffer(point, color):
    """Keep record of all display points.

    point = tuple(x,y)
    color = tuple(r,g,b)
    """
    x, y = point
    if x not in DISPLAY_BUFFER:
        DISPLAY_BUFFER[x] = dict()
    if y not in DISPLAY_BUFFER[x]:
        DISPLAY_BUFFER[x][y] = color
    DISPLAY_BUFFER[x][y] = color
    return True


def blend_into_next_effect(effects, point, incr, color):
    """Blend together 2 function results.

    effects = list of function pointers
    point = tuple(x, y, step)
    incr = current iteration
    color = tuple(r, g, b)
    """
    r, g, b = color  # unpack tuples
    x, y, step = point
    r2, g2, b2 = effects[-1](x, y, step)

    ratio = (500.00 - incr) / 100.0
    r = r * ratio + r2 * (1.0 - ratio)
    g = g * ratio + g2 * (1.0 - ratio)
    b = b * ratio + b2 * (1.0 - ratio)
    return (r, g, b)


def set_bounds_limits(r, g, b):
    r = int(max(0, min(255, r)))
    g = int(max(0, min(255, g)))
    b = int(max(0, min(255, b)))
    return (r, g, b)

FRAMERATE = 0.041666666  # approx 24 frames/second

def gfx(device):
    effects = [glitter, tunnel, rainbow_search, checker, swirl, blues_and_twos]
    shuffle(effects)
    step = 0
    while True:
        print(f"Displaying effect: {effects[0]}")
        for i in tqdm(range(500)):
            if i == 400:
                print(f"blending with {effects[-1]}")
            with canvas(device) as draw:
                for y in range(device.height):
                    for x in range(device.width):
                        r, g, b = effects[0](x, y, step)
                        if i > 400:
                            r, g, b = blend_into_next_effect(
                                effects, (x, y, step), i, (r, g, b)
                            )
                        r, g, b = set_bounds_limits(r, g, b)
                        draw.point((x, y), (r, g, b))
                        update_display_buffer((x, y), (r, g, b))
            step += 1
            # re-adjust delay to maintain framerate across different effects
            time.sleep(FRAMERATE - (time.time() % FRAMERATE))

        effect = effects.pop()
        effects.insert(0, effect)
    return True


# def make_font(name, size):
#   font_path = os.path.abspath(os.path.join(
#       os.path.dirname(__file__), 'fonts', name))
#   return ImageFont.truetype(font_path, size)


def scan_up_down():
    print("scan lines up/down")
    ylist = list(range(device.height))
    for y in range(10):  # repeat scan for multiple
        ylist.reverse()
        for y in ylist:  # scan the line through the list
            rndcolor = choice(COLOR_KEYS)
            clr = color_dict[rndcolor]["hex"]
            with canvas(device) as draw:
                draw.line([(0, y), (device.width, y)], fill=clr)
            time.sleep(0.1)
        time.sleep(0.1)
    time.sleep(2)
    return True


def scan_across():
    print("scan lines across")
    xlist = list(range(device.width))
    for x in range(3):  # repeat scan for multiple
        xlist.reverse()
        for x in xlist:  # scan the line through the list
            rndcolor = choice(COLOR_KEYS)
            clr = color_dict[rndcolor]["hex"]
            with canvas(device) as draw:
                draw.line([(x, 0), (x, device.height)], fill=clr)
            time.sleep(0.1)
        time.sleep(0.1)
    time.sleep(2)


def main():
    msg = "Neopixel WS2812 LED Matrix Demo"
    print(msg)
    # px8font = make_font("pixelmix.ttf", 8)
    rndcolor = choice(COLOR_KEYS)
    clr = color_dict[rndcolor]["hex"]
    show_message(device, msg, y_offset=-1, fill=clr, font=TINY_FONT)
    time.sleep(0.1)

    # call the random pixel effect
    # result = UseLumaLEDMatrix(device, xsize, ysize, 1, 100)

    print('Draw text "A" and "T"')
    with canvas(device) as draw:
        text(draw, (0, -1), txt="A", fill="red", font=TINY_FONT)
        text(draw, (4, -1), txt="T", fill="green", font=TINY_FONT)

    # time.sleep(1)

    # with canvas(device) as draw:
    #    rectangle(draw, device.bounding_box, outline="white", fill="black")
    #    text(draw, (0, -1), "Hello world", fill="white", font=TINY_FONT)

    time.sleep(0)

    print("Draw lines in the rainbow")
    device.contrast(8)
    with canvas(device) as draw:
        draw.line([(0, 0), (device.width, 0)], fill="red")
        draw.line([(0, 1), (device.width, 1)], fill="yellow")
        draw.line([(0, 2), (device.width, 2)], fill="green")
        draw.line([(0, 3), (device.width, 3)], fill="blue")
        draw.line([(0, 4), (device.width, 4)], fill="indigo")
        draw.line([(0, 5), (device.width, 5)], fill="violet")
        draw.line([(0, 6), (device.width, 6)], fill="white")

    # time.sleep(2)

    print("Vary intensity from 0 - 32")
    for _ in range(9):
        for intensity in range(16):
            device.contrast(intensity * 2)
            # time.sleep(0.1)

    print("Set contrast to: 0x80")
    device.contrast(0x80)
    # time.sleep(1)

    scan_across()

    scan_up_down()

    print("Set contrast to: 32")
    device.contrast(32)
    # time.sleep(1)

    print('Start "gfx" routine')
    gfx(device)
    return True


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
