# Draw an isometric image consisting of building blocks (small cubes).
# See README.md.


# Size of "type 2" blocks:
#      /\   ^ depth
#     |\/|  v
#     |  |    ^ height
#      \/     v
#     <--> width

# horizontal/vertical margins in output image
MARGIN_HORZ = 8
MARGIN_VERT = 8

# number of colours in block files, incl. transparent
COLOUR_COUNT = 5

import os, sys
try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow module required. See https://python-pillow.org")

def decode_int(stri, min_, max_):
    # decode an integer
    try:
        i = int(stri, 10)
        if not min_ <= i <= max_:
            raise ValueError
    except ValueError:
        sys.exit(f"Expected an integer between {min_}-{max_}.")
    return i

def decode_colour_code(colour):
    # decode a hexadecimal RRGGBB colour code into (red, green, blue)
    try:
        colour = int(colour, 16)
        if not 0 <= colour <= 0xffffff:
            raise ValueError
    except ValueError:
        sys.exit("Expected a hexadecimal RRGGBB colour code.")
    return tuple((colour >> s) & 0xff for s in (16, 8, 0))

def get_lines(filename):
    # generate lines without newlines, leading whitespace or comments
    with open(filename, "rt", encoding="ascii") as handle:
        handle.seek(0)
        for line in handle:
            line = line.lstrip().rstrip("\n")
            if line and not line.startswith("#"):
                yield line

def get_settings(inputFile):
    # read settings from input file;
    # return: (width, depth, height, background_colour);
    #         width, depth, height are in blocks;
    #         background_colour is (red, green, blue)

    width = depth = height = bgColour = None

    for line in get_lines(inputFile):
        line = line.upper()
        if line.startswith("W"):
            width = decode_int(line[1:], 1, 256)
        elif line.startswith("D"):
            depth = decode_int(line[1:], 1, 256)
        elif line.startswith("H"):
            height = decode_int(line[1:], 1, 256)
        elif line.startswith("B"):
            bgColour = decode_colour_code(line[1:])
        elif not line.startswith("|"):
            sys.exit("Syntax error: " + line)

    if any(v is None for v in (width, depth, height, bgColour)):
        sys.exit("Must define width, depth, height and background colour.")

    return (width, depth, height, bgColour)

def get_object_data(inputFile):
    # generate object data (colours of blocks) from input file
    # (a tuple of ints per "|" line)

    for line in get_lines(inputFile):
        if line.startswith("|"):
            try:
                yield tuple(int(c, 10) for c in line[1:].replace(" ", "0"))
            except ValueError:
                sys.exit(
                    "A character other than space or digit after '|': "
                    + line[1:]
                )

def transform_object(object, rotateAxes, reverseAxes):
    # rotate and mirror object if needed;
    # object: tuple of tuples of tuples of ints

    # rotate axes 90 degrees if needed
    if "X" in rotateAxes:
        object = tuple(
            tuple(
                tuple(
                    object[z][y][x]
                    for x in range(len(object[0][0]))
                ) for z in range(len(object))
            ) for y in range(len(object[0]))
        )
    if "Y" in rotateAxes:
        object = tuple(
            tuple(
                tuple(
                    object[z][y][x]
                    for z in range(len(object))
                ) for y in range(len(object[0]))
            ) for x in range(len(object[0][0]))
        )
    if "Z" in rotateAxes:
        object = tuple(
            tuple(
                tuple(
                    object[z][y][x]
                    for y in range(len(object[0]))
                ) for x in range(len(object[0][0]))
            ) for z in range(len(object))
        )

    # mirror axes if needed
    if "X" in reverseAxes:
        object = tuple(tuple(j[::-1] for j in i) for i in object)
    if "Y" in reverseAxes:
        object = tuple(i[::-1] for i in object)
    if "Z" in reverseAxes:
        object = object[::-1]

    return object

def type1_coords_to_2d(x, y, z, w, d, h):
    # convert "type 1" 3D coordinates into 2D (x, y);
    # w, d, h = block width/depth/height
    #       Z
    #       |
    #       +---X  -->  +-- X
    #       |           |
    #       Y           Y
    return (x * w, y * d - z * h)

def type2_coords_to_2d(x, y, z, w, d, h):
    # convert "type 2" 3D coordinates into 2D (x, y);
    # w, d, h = block width/depth/height
    #       Z
    #       |    -->  +-- X
    #      / \        |
    #     Y   X       Y
    return ((x - y) * w, (x + y) * d - z * h)

def main():
    if 7 <= len(sys.argv) <= 9:
        (
            inputFile, outputFile, coordType,
            blkWidth, blkDepth, blkHeight,
        ) = sys.argv[1:7]
        rotateAxes  = sys.argv[7].upper() if len(sys.argv) >= 8 else ""
        reverseAxes = sys.argv[8].upper() if len(sys.argv) == 9 else ""
    else:
        sys.exit(
            "Arguments: inputFile outputFile 3dCoordinateType blkWidth "
            "blkDepth blkHeight [axesToRotate] [axesToReverse]; see README.md "
            "for details."
        )

    coordType = int(coordType, 10)
    blkWidth  = int(blkWidth,  10)
    blkDepth  = int(blkDepth,  10)
    blkHeight = int(blkHeight, 10)

    (objWidth, objDepth, objHeight, bgColour) = get_settings(inputFile)

    objData = list(get_object_data(inputFile))
    if max(len(l) for l in objData) > objWidth:
        sys.exit(f"Can't have more than {objWidth} characters after '|'.")
    if len(objData) != objHeight * objDepth:
        sys.exit(f"Must have {objHeight*objDepth} lines starting with '|'.")
    if max((max(l) if l else 0) for l in objData) > COLOUR_COUNT - 1:
        sys.exit(f"Can't have colour numbers greater than {COLOUR_COUNT-1}.")

    # pad each line to objWidth integers
    objData = [l + (objWidth - len(l)) * (0,) for l in objData]
    # wrap each layer in its own tuple to get a tuple of tuples of tuples
    objData = tuple(
        tuple(objData[i:i+objDepth])
        for i in range(0, objHeight * objDepth, objDepth)
    )

    # rotate and mirror object if needed
    objData = transform_object(objData, rotateAxes, reverseAxes)
    objWidth  = len(objData[0][0])
    objDepth  = len(objData[0])
    objHeight = len(objData)

    # get size of final image and 2D origin
    if coordType == 1:
        imgWidth  = objWidth  * blkWidth + 1
        imgHeight = objHeight * blkHeight + objDepth * blkDepth + 1
        originX = 0
        originY = (objHeight - 1) * blkHeight
    else:
        imgWidth = (objWidth + objDepth) * blkWidth + 1
        imgHeight = (
            (objWidth + objDepth) * blkDepth + objHeight * blkHeight + 1
        )
        originX = (objDepth  - 1) * blkWidth
        originY = (objHeight - 1) * blkHeight
    imgWidth  += MARGIN_HORZ * 2
    imgHeight += MARGIN_VERT * 2
    originX   += MARGIN_HORZ
    originY   += MARGIN_VERT

    blockFile = (
        f"block-t{coordType}-w{blkWidth}-d{blkDepth}-h{blkHeight}.png"
    )

    if coordType == 1:
        blkImgWidth  = blkWidth  + 1
        blkImgHeight = blkHeight + blkDepth + 1
    else:
        blkImgWidth  = blkWidth * 2 + 1
        blkImgHeight = blkDepth * 2 + blkHeight + 1

    if not os.path.isfile(blockFile):
        sys.exit(f"{blockFile} not found.")
    if os.path.exists(outputFile):
        sys.exit(f"{outputFile} already exists.")

    with open(blockFile, "rb") as handle:
        handle.seek(0)
        blockImage = Image.open(handle)
        if blockImage.mode != "RGBA":
            sys.exit("Block image must be in RGBA format.")
        if blockImage.width != blkImgWidth * COLOUR_COUNT:
            sys.exit(
                f"Block image must be {blkImgWidth*COLOUR_COUNT} pixels wide."
            )
        if blockImage.height != blkImgHeight:
            sys.exit(f"Block image must be {blkImgHeight} pixels tall.")

        blockImages = [
            blockImage.crop((
                i * blkImgWidth, 0,
                (i + 1) * blkImgWidth, blkImgHeight
            )) for i in range(COLOUR_COUNT)
        ]

        # create output image
        outImage = Image.new("RGBA", (imgWidth, imgHeight), bgColour + (0xff,))

        # draw output image
        if coordType == 1:
            # draw blocks from smallest to largest y+z
            for distSum in range(0, objDepth + objHeight + 1):
                for y in range(objDepth):
                    for z in range(objHeight):
                        if y + z == distSum:
                            for x in range(objWidth):
                                colour = objData[z][y][x]
                                (_2dX, _2dY) = type1_coords_to_2d(
                                    x, y, z, blkWidth, blkDepth, blkHeight
                                )
                                _2dX += originX
                                _2dY += originY
                                outImage.alpha_composite(
                                    blockImages[colour], dest=(_2dX, _2dY)
                                )
        else:
            # draw blocks from smallest to largest x+y+z
            for distSum in range(0, objWidth + objDepth + objHeight + 1):
                for z in range(objHeight):
                    for x in range(objWidth):
                        for y in range(objDepth):
                            if x + y + z == distSum:
                                colour = objData[z][y][x]
                                (_2dX, _2dY) = type2_coords_to_2d(
                                    x, y, z, blkWidth, blkDepth, blkHeight
                                )
                                _2dX += originX
                                _2dY += originY
                                outImage.alpha_composite(
                                    blockImages[colour], dest=(_2dX, _2dY)
                                )

    # remove alpha channel from output image
    outImage = outImage.convert("RGB")

    # save output image
    with open(outputFile, "wb") as handle:
        handle.seek(0)
        outImage.save(handle, "png")

    print(f"Wrote {outputFile}")

main()
