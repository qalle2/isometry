# Draw an isometric image consisting of building blocks (small cubes).
# See README.md.

import os, sys
try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow module required. See https://python-pillow.org")

# horizontal/vertical margins in output image
MARGIN_HORZ = 8
MARGIN_VERT = 8

# number of colours in block files, excluding colour #0 (transparent)
COLOUR_COUNT = 5

# key:   (fine_Z_rotation, fine_X_rotation)       from command line
# value: (width1, width2, depth1, depth2, height) of a block
FINE_ROTATION_TO_BLOCK_SIZE = {
    (0, 0): (8, 0, 0, 0, 8),
    (1, 0): (7, 3, 0, 0, 8),
    (2, 0): (6, 6, 0, 0, 8),
    (3, 0): (3, 7, 0, 0, 8),
    (0, 2): (8, 0, 6, 0, 6),
    (1, 2): (7, 3, 4, 2, 6),
    (2, 2): (6, 6, 3, 3, 6),
    (3, 2): (3, 7, 2, 4, 6),
    # for "blocks-large.png"
    #(0, 0): (20, 0,  0, 0, 20),
    #(1, 0): (18, 8,  0, 0, 20),
    #(2, 0): (14,14,  0, 0, 20),
    #(3, 0): ( 8,18,  0, 0, 20),
    #(0, 2): (20, 0, 14, 0, 14),
    #(1, 2): (18, 8, 12, 4, 15),
    #(2, 2): (14,14,  8, 9, 17),
    #(3, 2): ( 8,18,  4,12, 15),
}

# key:   (width1, width2, depth1, depth2, height) of a block
# value: (column, row)                            in block file
BLOCK_FILE_BLOCKSETS = {
    (8, 0, 0, 0, 8): (0, 1),
    (7, 3, 0, 0, 8): (1, 1),
    (6, 6, 0, 0, 8): (2, 1),
    (3, 7, 0, 0, 8): (3, 1),
    (8, 0, 6, 0, 6): (0, 0),
    (7, 3, 4, 2, 6): (1, 0),
    (6, 6, 3, 3, 6): (2, 0),
    (3, 7, 2, 4, 6): (3, 0),
    # for "blocks-large.png"
    #(20, 0,  0, 0, 20): (0, 1),
    #(18, 8,  0, 0, 20): (1, 1),
    #(14,14,  0, 0, 20): (2, 1),
    #( 8,18,  0, 0, 20): (3, 1),
    #(20, 0, 14, 0, 14): (0, 0),
    #(18, 8, 12, 4, 15): (1, 0),
    #(14,14,  8, 9, 17): (2, 0),
    #( 8,18,  4,12, 15): (3, 0),
}
assert set(BLOCK_FILE_BLOCKSETS) == set(FINE_ROTATION_TO_BLOCK_SIZE.values())

BLOCK_FILE_COLUMN_WIDTHS = (  # must include the last column
     8      * COLOUR_COUNT,
    (7 + 3) * COLOUR_COUNT,
    (6 + 6) * COLOUR_COUNT,
    (3 + 7) * COLOUR_COUNT,
    # for "blocks-large.png"
    #(20      + 1) * COLOUR_COUNT,
    #(18 +  8 + 1) * COLOUR_COUNT,
    #(14 + 14 + 1) * COLOUR_COUNT,
    #( 8 + 18 + 1) * COLOUR_COUNT,
)
BLOCK_FILE_ROW_HEIGHTS = (  # must include the last row
    6 + 6,
    8,
    # for "blocks-large.png"
    #34 + 1,
    #20 + 1,
)

# read building blocks from here
BLOCK_FILE = "blocks-small.png"
#BLOCK_FILE = "blocks-large.png"

# --- helper functions --------------------------------------------------------

def decode_int(stri, min_, max_, name):
    # decode an integer
    try:
        i = int(stri, 10)
        if not min_ <= i <= max_:
            raise ValueError
    except ValueError:
        sys.exit(f"{name} must be an integer between {min_} and {max_}")
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

# --- argument parsing --------------------------------------------------------

def parse_args():
    # parse command line arguments; return a dict

    if 6 <= len(sys.argv) <= 7:
        (inputFile, outputFile, xRot, yRot, zRot) = sys.argv[1:6]
        mirrorAxes = sys.argv[6].upper() if len(sys.argv) == 7 else ""
    else:
        sys.exit(
            "Arguments: inputFile outputFile xRotation yRotation zRotation "
            "[axesToMirror]; see README.md for details"
        )

    xRot = decode_int(xRot, 0, 15, "X rotation")
    yRot = decode_int(yRot, 0, 15, "Y rotation")
    zRot = decode_int(zRot, 0, 15, "Z rotation")
    if xRot % 2 > 0:
        sys.exit("Only X rotations divisible by 2 are supported.")
    if yRot % 4 > 0:
        sys.exit("Only Y rotations divisible by 4 are supported.")

    # split rotations into coarse and fine parts
    # (note: fineYRot is always 0 and unused)
    (coarseXRot, fineXRot) = divmod(xRot, 4)
    (coarseYRot, fineYRot) = divmod(yRot, 4)
    (coarseZRot, fineZRot) = divmod(zRot, 4)
    del xRot, yRot, zRot

    # get block width, depth, height from fine rotations
    try:
        (blkWidth1, blkWidth2, blkDepth1, blkDepth2, blkHeight) = (
            FINE_ROTATION_TO_BLOCK_SIZE[(fineZRot, fineXRot)]
        )
    except KeyError:
        # this error should always be caught earlier
        sys.exit("This combination of fine rotations is not supported.")

    if not set(mirrorAxes).issubset(set("XYZ")):
        sys.exit("the mirrorAxes argument may only contain letters X Y Z")

    if not os.path.isfile(inputFile):
        sys.exit(f"{inputFile} not found.")
    if os.path.exists(outputFile):
        sys.exit(f"{outputFile} already exists.")

    coarseRots = (coarseXRot, coarseYRot, coarseZRot)
    mirrorAxes = ("X" in mirrorAxes, "Y" in mirrorAxes, "Z" in mirrorAxes)

    return {
        "inputFile":  inputFile,
        "outputFile": outputFile,
        "blkWidth1":  blkWidth1,
        "blkWidth2":  blkWidth2,
        "blkDepth1":  blkDepth1,
        "blkDepth2":  blkDepth2,
        "blkHeight":  blkHeight,
        "coarseRots": coarseRots,
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
            width = decode_int(line[1:], 1, 256, "object width")
        elif line.upper().startswith("D"):
            depth = decode_int(line[1:], 1, 256, "object depth")
        elif line.upper().startswith("H"):
            height = decode_int(line[1:], 1, 256, "object height")
        elif line.upper().startswith("B"):
            bgColour = decode_colour_code(line[1:])
        elif not line.startswith("|") and not line.startswith("#"):
            sys.exit("Syntax error: " + line)

    if any(v is None for v in (width, depth, height, bgColour)):
        sys.exit("Must define width, depth, height and background colour.")

    return {
        "width":    width,
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
    # rotate object 90 degrees clockwise around X axis;
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
    # rotate object 90 degrees clockwise around Y axis;
    # object: tuple of tuples of tuples of ints

    width  = len(object[0][0])
    depth  = len(object[0])
    height = len(object)

    # (x, y, z) = (z, y, -x)
    return tuple(
        tuple(
            tuple(
                object[z][y][x]
                for z in range(height)
            ) for y in range(depth)
        ) for x in range(width - 1, -1, -1)
    )

def z_rotate(object):
    # rotate object 90 degrees clockwise around Z axis;
    # object: tuple of tuples of tuples of ints

    width  = len(object[0][0])
    depth  = len(object[0])
    height = len(object)

    return tuple(
        tuple(
            tuple(
                object[z][y][x]
                for y in range(depth - 1, -1, -1)
            ) for x in range(width)
        ) for z in range(height)
    )

def transform_object(object, rotations, mirrorAxes):
    # rotate and mirror object if needed;
    # rotations:  coarse (X, Y, Z) rotations (0-3 each);
    # mirrorAxes: mirror along (X, Y, Z)? (booleans)
    # object: tuple of tuples of tuples of ints

    for i in range(rotations[0]):
        object = x_rotate(object)
    for i in range(rotations[1]):
        object = y_rotate(object)
    for i in range(rotations[2]):
        object = z_rotate(object)

    if mirrorAxes[0]:
        object = tuple(tuple(j[::-1] for j in i) for i in object)
    if mirrorAxes[1]:
        object = tuple(i[::-1] for i in object)
    if mirrorAxes[2]:
        object = object[::-1]

    return object

# --- output image drawing ----------------------------------------------------

def get_output_image_size(args, objWidth, objDepth, objHeight):
    # args:   command line arguments;
    # obj*:   object size in blocks;
    # return: (width, height)

    imgWidth = (
          objWidth * args["blkWidth1"]
        + objDepth * args["blkWidth2"]
        + MARGIN_HORZ * 2 + 1
    )
    imgHeight = (
          objWidth  * args["blkDepth2"]
        + objDepth  * args["blkDepth1"]
        + objHeight * args["blkHeight"]
        + MARGIN_VERT * 2 + 1
    )
    return (imgWidth, imgHeight)

def get_coords_type1(width, depth, height):
    # generate 3D coordinates from rear to front for "type 1" blocks
    # (from smallest to largest y+z)

    for yzSum in range(0, depth + height + 1):
        # y + z must equal yzSum
        for y in range(depth):
            if 0 <= (z := yzSum - y) < height:
                yield from ((x, y, z) for x in range(width))

def get_coords_type2(width, depth, height):
    # generate 3D coordinates from rear to front for "type 2" blocks
    # (from smallest to largest x+y+z)

    for xyzSum in range(0, width + depth + height + 1):
        # x + y + z must equal xyzSum
        for x in range(width):
            for y in range(depth):
                if 0 <= (z := xyzSum - x - y) < height:
                    yield (x, y, z)

def draw_blocks(object, blkImgs, outImg, args):
    # draw object on image
    # object:  colours of building blocks (tuple of tuples of tuples of ints)
    # blkImgs: list of building blocks (one colour variant/image)
    # outImg:  image to paint to
    # args:    command line arguments

    # object size in blocks
    objWidth  = len(object[0][0])
    objDepth  = len(object[0])
    objHeight = len(object)

    # 3D coordinate generator, 2D origin
    if args["blkWidth2"] == 0:
        coord_gen = get_coords_type1
        originX   = MARGIN_HORZ
    else:
        coord_gen = get_coords_type2
        originX   = MARGIN_HORZ + (objDepth - 1) * args["blkWidth2"]
    originY = MARGIN_VERT + (objHeight - 1) * args["blkHeight"]

    # get 3D coordinates from rear to front
    for (x, y, z) in coord_gen(objWidth, objDepth, objHeight):
        colour = object[z][y][x]
        if colour:
            # transform coordinates to 2D and paint a block there
            _2dX = (
                originX
                + x * args["blkWidth1"]
                - y * args["blkWidth2"]
            )
            _2dY = (
                originY
                + x * args["blkDepth2"]
                + y * args["blkDepth1"]
                - z * args["blkHeight"]
            )
            outImg.alpha_composite(blkImgs[colour-1], dest=(_2dX, _2dY))

    return outImg

# --- main --------------------------------------------------------------------

def main():
    if not os.path.isfile(BLOCK_FILE):
        sys.exit(f"{BLOCK_FILE} not found.")
    args = parse_args()
    objProps = get_object_properties(args["inputFile"])

    # get object data (colours of building blocks)
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
    if max((max(l) if l else 0) for l in objData) > COLOUR_COUNT:
        sys.exit(f"Can't have colour numbers greater than {COLOUR_COUNT}.")

    # pad each line of blocks to (object width) integers
    objData = [l + (objProps["width"] - len(l)) * (0,) for l in objData]
    # wrap each layer in its own tuple to get a tuple of tuples of tuples
    objData = tuple(
        tuple(objData[i:i+objProps["depth"]])
        for i
        in range(0, objProps["height"] * objProps["depth"], objProps["depth"])
    )

    # rotate and mirror object if needed
    objData = transform_object(objData, args["coarseRots"], args["mirrorAxes"])
    objWidth  = len(objData[0][0])
    objDepth  = len(objData[0])
    objHeight = len(objData)

    # these are no longer valid
    del objProps["width"], objProps["depth"], objProps["height"]

    (outImgWidth, outImgHeight) = get_output_image_size(
        args, objWidth, objDepth, objHeight
    )

    # get properties of one block image (coordinates in block file and size)
    (col, row) = BLOCK_FILE_BLOCKSETS[(
        args["blkWidth1"],
        args["blkWidth2"],
        args["blkDepth1"],
        args["blkDepth2"],
        args["blkHeight"]
    )]
    blkImgX = sum(BLOCK_FILE_COLUMN_WIDTHS[:col])
    blkImgY = sum(BLOCK_FILE_ROW_HEIGHTS[:row])
    # note: add 1 to these if using "blocks-large.png"
    blkImgWidth  = args["blkWidth1"] + args["blkWidth2"]
    blkImgHeight = args["blkDepth1"] + args["blkDepth2"] + args["blkHeight"]

    # copy block images from block file to output image
    try:
        with open(BLOCK_FILE, "rb") as handle:
            handle.seek(0)
            blkImg = Image.open(handle)
            if blkImg.mode != "RGBA":
                sys.exit("Block image must be in RGBA format.")
            if blkImg.width != sum(BLOCK_FILE_COLUMN_WIDTHS):
                sys.exit("Incorrect width of block file.")
            if blkImg.height != sum(BLOCK_FILE_ROW_HEIGHTS):
                sys.exit("Incorrect height of block file.")

            # get each colour variant of block image as separate image
            # (does not include colour #0 (transparency))
            blkImgs = tuple(
                blkImg.crop((
                    blkImgX +  i      * blkImgWidth, blkImgY,
                    blkImgX + (i + 1) * blkImgWidth, blkImgY + blkImgHeight
                )) for i in range(COLOUR_COUNT)
            )

            # create output image
            outImg = Image.new(
                "RGBA", (outImgWidth, outImgHeight),
                objProps["bgColour"] + (0xff,)
            )

            # draw output image
            draw_blocks(objData, blkImgs, outImg, args)
    except OSError:
        sys.exit(f"Error reading {BLOCK_FILE}")

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
