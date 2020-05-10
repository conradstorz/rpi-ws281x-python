"""Device specific details for BTF manufactured LED NeoPixel matrix
"""

# matrix size
BTF_XSIZE = 64
BTF_YSIZE = 8

# build a pixel mapping for BTF matrix device
MAP_BTF = []
_tmp_BTF = []

xlist = list(range(BTF_XSIZE))

for x in xlist:
    ylist = list(range(x * BTF_YSIZE, x * BTF_YSIZE + BTF_YSIZE))
    if x % 2 == 1:  # invert list to account for serpentine layout
        ylist.reverse()
    _tmp_BTF.append(ylist)

for y in range(BTF_YSIZE):
    for l in _tmp_BTF:
        MAP_BTF.append(l[y])
