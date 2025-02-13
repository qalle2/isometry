# Draw an isometric image consisting of building blocks (small cubes).
# See README.md.

import itertools, os, sys
try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow module required. See https://python-pillow.org")

# horizontal/vertical margins in output image
MARGIN_HORZ = 8
MARGIN_VERT = 8

# number of colours in block files, including transparent
COLOUR_COUNT = 6

# --- helper functions --------------------------------------------------------

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
    # generate non-empty lines without leading or trailing whitespace
    with open(filename, "rt", encoding="ascii") as handle:
        handle.seek(0)
        for line in handle:
            if line := line.strip():
                yield line

def get_block_filename(coordType, width, depth, height):
    # get name of file to read building blocks from

    return f"block-t{coordType}-w{width}-d{depth}-h{height}.png"

# --- argument parsing --------------------------------------------------------

def parse_args():
    # parse command line arguments; return a dict

    if 7 <= len(sys.argv) <= 9:
        (
            inputFile, outputFile, coordType,
            blkWidth, blkDepth, blkHeight,
        ) = sys.argv[1:7]
        rotateAxes = sys.argv[7].upper() if len(sys.argv) >= 8 else ""
        mirrorAxes = sys.argv[8].upper() if len(sys.argv) == 9 else ""
    else:
        sys.exit(
            "Arguments: inputFile outputFile 3dCoordinateType blkWidth "
            "blkDepth blkHeight [axesToRotate] [axesToReverse]; see "
            "README.md for details."
        )

    coordType = decode_int(coordType, 1,   2)
    blkWidth  = decode_int(blkWidth,  1, 256)
    blkDepth  = decode_int(blkDepth,  0, 256)
    blkHeight = decode_int(blkHeight, 1, 256)

    if not os.path.isfile(inputFile):
        sys.exit(f"{inputFile} not found.")
    blockFile = get_block_filename(coordType, blkWidth, blkDepth, blkHeight)
    if not os.path.isfile(blockFile):
        sys.exit(f"{blockFile} not found.")
    if os.path.exists(outputFile):
        sys.exit(f"{outputFile} already exists.")

    return {
        "inputFile":  inputFile,
        "outputFile": outputFile,
        "coordType":  coordType,
        "blkWidth":   blkWidth,
        "blkDepth":   blkDepth,
        "blkHeight":  blkHeight,
        "rotateAxes": rotateAxes,
        "mirrorAxes": mirrorAxes,
    }

# --- block data --------------------------------------------------------------

def get_object_properties(inputFile):
    # read properties of object from input file;
    # return a dict (width, depth, height are in blocks;
    #         background colour is (red, green, blue))

    width = depth = height = bgColour = None

    for line in get_lines(inputFile):
        if line.upper().startswith("W"):
            width = decode_int(line[1:], 1, 256)
        elif line.upper().startswith("D"):
            depth = decode_int(line[1:], 1, 256)
        elif line.upper().startswith("H"):
            height = decode_int(line[1:], 1, 256)
        elif line.upper().startswith("B"):
            bgColour = decode_colour_code(line[1:])
        elif not line.startswith("|") and not line.startswith("#"):
            sys.exit("Syntax error: " + line)

    if any(v is None for v in (width, depth, height, bgColour)):
        sys.exit("Must define width, depth, height and background colour.")

    return {
        "width"   : width,
        "depth":    depth,
        "height":   height,
        "bgColour": bgColour,
    }

def get_object_data(inputFile):
    # generate colours of building blocks from input file
    # (a tuple of ints per "|" line)

    for line in get_lines(inputFile):
        if line.startswith("|"):
            try:
                yield tuple(int(c, 10) for c in line[1:].replace(" ", "0"))
            except ValueError:
                sys.exit("Only spaces and digits are allowed after '|'.")

def x_rotate(object):
    # rotate object 90 degrees counterclockwise around X axis;
    # object: tuple of tuples of tuples of ints

    width  = len(object[0][0])
    depth  = len(object[0])
    height = len(object)

    # (x, y, z) = (x, z, -y)
    return tuple(
        tuple(
            tuple(
                object[z][y][x]
                for x in range(width)
            ) for z in range(height)
        ) for y in range(depth - 1, -1, -1)
    )

def y_rotate(object):
    # rotate object 90 degrees counterclockwise around Y axis;
    # object: tuple of tuples of tuples of ints

    width  = len(object[0][0])
    depth  = len(object[0])
    height = len(object)

    # (x, y, z) = (-z, y, x)
    return tuple(
        tuple(
            tuple(
                object[z][y][x]
                for z in range(height - 1, -1, -1)
            ) for y in range(depth)
        ) for x in range(width)
    )

def z_rotate(object):
    # rotate object 90 degrees counterclockwise around Z axis;
    # object: tuple of tuples of tuples of ints

    width  = len(object[0][0])
    depth  = len(object[0])
    height = len(object)

    # (x, y, z) = (y, -x, z)
    return tuple(
        tuple(
            tuple(
                object[z][y][x]
                for y in range(depth)
            ) for x in range(width - 1, -1, -1)
        ) for z in range(height)
    )

def transform_object(object, rotateAxes, mirrorAxes):
    # rotate and mirror object if needed;
    # object: tuple of tuples of tuples of ints

    for i in range(rotateAxes.count("X")):
        object = x_rotate(object)
    for i in range(rotateAxes.count("Y")):
        object = y_rotate(object)
    for i in range(rotateAxes.count("Z")):
        object = z_rotate(object)

    if "X" in mirrorAxes:
        object = tuple(tuple(j[::-1] for j in i) for i in object)
    if "Y" in mirrorAxes:
        object = tuple(i[::-1] for i in object)
    if "Z" in mirrorAxes:
        object = object[::-1]

    return object

# --- output image drawing ----------------------------------------------------

def get_type1_coords(width, depth, height):
    # generate 3D coordinates (x, y, z) from rear to front for "type 1" blocks
    # (from smallest to largest y+z)

    for yzSum in range(0, depth + height + 1):
        for (y, z) in itertools.product(range(depth), range(height)):
            if y + z == yzSum:
                yield from ((x, y, z) for x in range(width))

def get_type2_coords(width, depth, height):
    # generate 3D coordinates (x, y, z) from rear to front for "type 2" blocks
    # (from smallest to largest x+y+z)

    for coordSum in range(0, width + depth + height + 1):
        yield from (
            coords for coords
            in itertools.product(range(width), range(depth), range(height))
            if sum(coords) == coordSum
        )

def draw_blocks_type1(object, blkImgs, outImg, blkWidth, blkDepth, blkHeight):
    # draw object on image using "type 1" blocks (see readme);
    # object:  colours of building blocks (tuple of tuples of tuples of ints)
    # blkImgs: list of building blocks (one colour variant/image)
    # outImg:  image to paint to

    # object size in blocks
    objWidth  = len(object[0][0])
    objDepth  = len(object[0])
    objHeight = len(object)

    # 2D origin
    originX = MARGIN_HORZ
    originY = MARGIN_VERT + (objHeight - 1) * blkHeight

    # get 3D coordinates from rear to front and transform them to 2D
    #   Z
    #   |
    #   +--X  -->  +-- X
    #   |          |
    #   Y          Y
    for (x, y, z) in get_type1_coords(objWidth, objDepth, objHeight):
        _2dX = originX + x * blkWidth
        _2dY = originY + y * blkDepth - z * blkHeight
        colour = object[z][y][x]
        outImg.alpha_composite(blkImgs[colour], dest=(_2dX, _2dY))

    return outImg

def draw_blocks_type2(object, blkImgs, outImg, blkWidth, blkDepth, blkHeight):
    # draw object on image using "type 2" blocks (see readme);
    # object:  colours of building blocks (tuple of tuples of tuples of ints)
    # blkImgs: list of building blocks (one colour variant/image)
    # outImg:  image to paint to

    # object size in blocks
    objWidth  = len(object[0][0])
    objDepth  = len(object[0])
    objHeight = len(object)

    # 2D origin
    originX = MARGIN_HORZ + (objDepth  - 1) * blkWidth
    originY = MARGIN_VERT + (objHeight - 1) * blkHeight

    # get 3D coordinates from rear to front and transform them to 2D
    #     Z
    #     |    -->  +-- X
    #    / \        |
    #   Y   X       Y
    for (x, y, z) in get_type2_coords(objWidth, objDepth, objHeight):
        _2dX = originX + (x - y) * blkWidth
        _2dY = originY + (x + y) * blkDepth - z * blkHeight
        colour = object[z][y][x]
        outImg.alpha_composite(blkImgs[colour], dest=(_2dX, _2dY))

    return outImg

# --- main --------------------------------------------------------------------

def main():
    args = parse_args()
    objProps = get_object_properties(args["inputFile"])

    # get colours of building blocks
    objData = list(get_object_data(args["inputFile"]))
    if max(len(l) for l in objData) > objProps["width"]:
        sys.exit(
            f"Can't have more than {objProps['width']} characters after '|'."
        )
    if len(objData) != objProps["height"] * objProps["depth"]:
        sys.exit(
            f"Must have {objProps['height']*objProps['depth']} lines starting "
            f"with '|'."
        )
    if max((max(l) if l else 0) for l in objData) > COLOUR_COUNT - 1:
        sys.exit(f"Can't have colour numbers greater than {COLOUR_COUNT-1}.")

    # pad each line of blocks to (object width) integers
    objData = [l + (objProps["width"] - len(l)) * (0,) for l in objData]
    # wrap each layer in its own tuple to get a tuple of tuples of tuples
    objData = tuple(
        tuple(objData[i:i+objProps["depth"]])
        for i
        in range(0, objProps["height"] * objProps["depth"], objProps["depth"])
    )

    # rotate and mirror object if needed
    objData = transform_object(objData, args["rotateAxes"], args["mirrorAxes"])
    objWidth  = len(objData[0][0])
    objDepth  = len(objData[0])
    objHeight = len(objData)

    # these are no longer valid
    del objProps["width"], objProps["depth"], objProps["height"]

    # get sizes of block and output images
    if args["coordType"] == 1:
        blkImgWidth  = args["blkWidth"]                     + 1
        blkImgHeight = args["blkHeight"] + args["blkDepth"] + 1
        outImgWidth = (
            MARGIN_HORZ * 2
            + objWidth * args["blkWidth"]
            + 1
        )
        outImgHeight = (
            MARGIN_VERT * 2
            + objHeight * args["blkHeight"]
            + objDepth  * args["blkDepth"]
            + 1
        )
    else:
        blkImgWidth  = args["blkWidth"] * 2                     + 1
        blkImgHeight = args["blkDepth"] * 2 + args["blkHeight"] + 1
        outImgWidth = (
            MARGIN_HORZ * 2
            + (objWidth + objDepth) * args["blkWidth"]
            + 1
        )
        outImgHeight = (
            MARGIN_VERT * 2
            + (objWidth + objDepth) * args["blkDepth"]
            + objHeight * args["blkHeight"]
            + 1
        )

    blockFile = get_block_filename(
        args["coordType"], args["blkWidth"], args["blkDepth"],
        args["blkHeight"]
    )

    # draw block images on output image
    try:
        with open(blockFile, "rb") as handle:
            # open and validate block image
            handle.seek(0)
            blkImg = Image.open(handle)
            if blkImg.mode != "RGBA":
                sys.exit("Block image must be in RGBA format.")
            if blkImg.width != blkImgWidth * COLOUR_COUNT:
                sys.exit(
                    f"Block image width must be {blkImgWidth*COLOUR_COUNT}."
                )
            if blkImg.height != blkImgHeight:
                sys.exit(f"Block image height must be {blkImgHeight}.")

            # get each colour variant of block image as separate image
            blkImgs = tuple(
                blkImg.crop(
                    (i * blkImgWidth, 0, (i + 1) * blkImgWidth, blkImgHeight)
                ) for i in range(COLOUR_COUNT)
            )

            # create output image
            outImg = Image.new(
                "RGBA", (outImgWidth, outImgHeight),
                objProps["bgColour"] + (0xff,)
            )

            # draw output image
            func = {
                1: draw_blocks_type1, 2: draw_blocks_type2
            }[args["coordType"]]
            func(
                objData, blkImgs, outImg,
                args["blkWidth"], args["blkDepth"], args["blkHeight"]
            )
    except OSError:
        sys.exit(f"Error reading {blockFile}")

    # remove alpha channel from output image
    outImg = outImg.convert("RGB")

    # save output image
    try:
        with open(args["outputFile"], "wb") as handle:
            handle.seek(0)
            outImg.save(handle, "png")
    except OSError:
        sys.exit(f"Error writing {args['outputFile']}")

    print(f"Wrote {args['outputFile']}")

main()
