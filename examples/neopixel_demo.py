#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2017-18 Richard Hull and contributors
# See LICENSE.rst for details.

# Portions of this script were adapted from:
#  https://github.com/pimoroni/unicorn-hat/blob/master/examples/demo.py

from BTF32x8_matrix_device import MAP_BTF32x8, BTF_XSIZE, BTF_YSIZE
from random_colors import color_dict, COLOR_KEYS
from random import choice, shuffle
from tqdm import tqdm

import math
import time
import colorsys

from luma.led_matrix.device import neopixel
from luma.core.render import canvas
from luma.core.legacy import text, show_message
from luma.core.legacy.font import TINY_FONT, SINCLAIR_FONT

from PIL import ImageFont
"""https://pillow.readthedocs.io/en/stable/reference/ImageFont.html
from PIL import ImageFont, ImageDraw

draw = ImageDraw.Draw(image)

# use a bitmap font
font = ImageFont.load("arial.pil")

draw.text((10, 10), "hello", font=font)

from BTF64x8_matrix_device import MAP_BTF, BTF_XSIZE, BTF_YSIZE
# use a truetype font
font = ImageFont.truetype("arial.ttf", 15)

draw.text((10, 25), "world", font=font)
"""
# ARIAL_FONT = ImageFont.truetype("arial")
ARIAL_FONT = ImageFont.load("arial.pil")


# create matrix device
device = neopixel(width=BTF_XSIZE, height=BTF_YSIZE, mapping=MAP_BTF, rotate=0)

LOCAL_COLOR_KEYS = COLOR_KEYS.copy()
shuffle(LOCAL_COLOR_KEYS)

# random dots of color
def glitter(_x, _y, _step, _depth=0):
    """ Take an xy position and return a random color for it

    TODO reduce the number of colors to change the effect
    example: new parameter: depth = 1 to len(COLOR_KEYS)
    if depth = 0: depth = len(COLOR_KEYS)
    CK = subset(COLOR_KEYS, depth) 


        # drop a color from the list periodically    
        if x + y == 0: # only do it once per frame
            print(len(LOCAL_COLOR_KEYS))
            color = LOCAL_COLOR_KEYS.pop()

    """
    color = LOCAL_COLOR_KEYS.pop()    
    r, g, b = color_dict[color]["rgb"]
    LOCAL_COLOR_KEYS.insert(0, color)
    return (r, g, b)


# twisty swirly goodness
def swirl(x, y, step):
    """Returns RGB color tuple
    """
    x -= device.width / 2
    y -= device.height / 2
    dist = math.sqrt(pow(x, 2) + pow(y, 2)) / 2.0
    angle = (step / 10.0) + (dist * 1.5)
    xs = x * math.cos(angle) - y * math.sin(angle)
    ys = x * math.sin(angle) + y * math.cos(angle)
    r = (abs(xs + ys) * 64.0) - 20
    return (r, r + (math.sin(angle) * 130), r + (math.cos(angle) * 130))


# roto-zooming checker board
def checkerboard(x, y, step):
    """Returns RGB color tuple
    """
    x -= device.width / 2
    y -= device.height / 2
    angle = step / 10.0
    xs = (x * math.cos(angle) - y * math.sin(angle)) - math.sin(step / 200.0) * 40.0
    ys = (x * math.sin(angle) + y * math.cos(angle)) - math.cos(step / 200.0) * 40.0
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
    """Returns RGB color tuple
    """    
    x -= device.width / 2
    y -= device.height / 2
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
    """Returns RGB color tuple
    """    
    xs = math.sin((step) / 100.0) * 20.0
    ys = math.cos((step) / 100.0) * 20.0
    scale = ((math.sin(step / 60.0) + 1.0) / 5.0) + 0.2
    r = math.sin((x + xs) * scale) + math.cos((y + xs) * scale)
    g = math.sin((x + xs) * scale) + math.cos((y + ys) * scale)
    b = math.sin((x + ys) * scale) + math.cos((y + ys) * scale)
    return (r * 255, g * 255, b * 255)


# zoom tunnel
def tunnel(x, y, step):
    """Returns RGB color tuple
    """    
    speed = step / 100.0
    x -= device.width / 2
    y -= device.height / 2
    x += math.sin(step / 27.0) * 2
    y += math.cos(step / 18.0) * 2
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


SIX_FRAMES_SEC = 0.166666666
EIGHT_FRAMES_SEC = 0.125
TEN_FRAMES_SEC = 0.1
x24_FRAMES_SEC = 0.041666666
x60_FRAMES_SEC = 0.016666666
UNLIMTED_FRAMES_SEC = 0.000000001

FRAMERATE = UNLIMTED_FRAMES_SEC
EFFECT_ITERATIONS = 500
BLEND_POINT = 400

def gfx(device):
    effects = [glitter, tunnel, rainbow_search, checkerboard, swirl, blues_and_twos]
    shuffle(effects)
    step = 0
    while True:
        print(f"Displaying effect: {effects[0]}")
        for i in tqdm(range(EFFECT_ITERATIONS)):
            if i == BLEND_POINT:
                print(f"blending with {effects[-1]}")
            with canvas(device) as draw:
                for y in range(device.height):
                    for x in range(device.width):
                        r, g, b = effects[0](x, y, step)
                        if i > BLEND_POINT:
                            r, g, b = blend_into_next_effect(
                                effects, (x, y, step), i, (r, g, b)
                            )
                        r, g, b = set_bounds_limits(r, g, b)
                        draw.point((x, y), (r, g, b))
                        update_display_buffer((x, y), (r, g, b))
            step += 1
            # re-adjust delay to maintain framerate across different effects
            time.sleep(FRAMERATE - (time.time() % FRAMERATE))
        # rotate the queue of effects
        """
        effect = effects.pop()
        effects.insert(0, effect)
        """
        shuffle(effects)
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
    return True




def display_scroll_text(msg, speed=0.1):
    """Place msg onto LED mtrix in a scroll
    """
    print(msg)
    # px8font = make_font("pixelmix.ttf", 8)
    rndcolor = choice(COLOR_KEYS)
    clr = color_dict[rndcolor]["hex"]
    show_message(device, msg, y_offset=-1, fill=clr, font=ARIAL_FONT, scroll_delay=speed)



def main():
    display_scroll_text("NEOPIXEL WS2812 LED MATRIX DEMO", speed=0.05)
    time.sleep(0.5)

    print('Draw text "R" "G" and "B"')
    with canvas(device) as draw:
        text(draw, (0, -1), txt="R", fill="red", font=SINCLAIR_FONT)
        text(draw, (8, -1), txt="G", fill="green", font=TINY_FONT)
        text(draw, (16, -1), txt="B", fill="blue", font=SINCLAIR_FONT)

    time.sleep(3)

    # with canvas(device) as draw:
    #    rectangle(draw, device.bounding_box, outline="white", fill="black")
    #    text(draw, (0, -1), "Hello world", fill="white", font=TINY_FONT)

    time.sleep(0)

    print("Draw lines in the rainbow")
    color = ['red', 'orange','yellow', 'green', 'blue', 'indigo', 'violet', 'white']
    device.contrast(8)
    with canvas(device) as draw:
        for line in range(8):
            draw.line([(0, line), (device.width, line)], fill=color[line])
    time.sleep(2)

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
