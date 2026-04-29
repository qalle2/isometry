# render a voxel file as a PNG file

import os, sys
try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow module required. See https://pypi.org/project/pillow/")

HELP_TEXT = """\
Render a voxel file as a PNG file. Arguments: inputFile outputFile xRotation
yRotation zRotation [axesToMirror]; see README.md for details.\
"""

# --- output file "constants" -------------------------------------------------

MARGIN_HORZ = 8  # horizontal margins
MARGIN_VERT = 8  # vertical   margins

# background colour (red, green, blue, opacity; each 0-255)
BACKGROUND_COLOUR = (255, 255, 255, 255)

# --- building blocks file "constants" ----------------------------------------

# read building blocks from here
BLOCK_FILE = "blocks.png"

# number of colours in block file, excluding colour #0 (transparent)
COLOUR_COUNT = 9

# key:   (fine_Z_rotation, fine_X_rotation)       from command line
# value: (width1, width2, depth1, depth2, height) of a block
FINE_ROTATION_TO_BLOCK_SIZE = {
    (0, 0): (20, 0,  0, 0, 20),
    (1, 0): (18, 8,  0, 0, 20),
    (2, 0): (14,14,  0, 0, 20),
    (3, 0): ( 8,18,  0, 0, 20),
    (0, 2): (20, 0, 14, 0, 14),
    (1, 2): (18, 8, 12, 4, 15),
    (2, 2): (14,14,  8, 8, 16),
    (3, 2): ( 8,18,  4,12, 15),
}

# key:   (width1, width2, depth1, depth2, height) of a block
# value: (column, row)                            in block file
BLOCK_FILE_BLOCKSETS = {
    (20, 0,  0, 0, 20): (0, 1),
    (18, 8,  0, 0, 20): (1, 1),
    (14,14,  0, 0, 20): (2, 1),
    ( 8,18,  0, 0, 20): (3, 1),
    (20, 0, 14, 0, 14): (0, 0),
    (18, 8, 12, 4, 15): (1, 0),
    (14,14,  8, 8, 16): (2, 0),
    ( 8,18,  4,12, 15): (3, 0),
}
assert set(BLOCK_FILE_BLOCKSETS) == set(FINE_ROTATION_TO_BLOCK_SIZE.values())

BLOCK_FILE_COLUMN_WIDTHS = (  # must include the last column
    (20      + 1) * COLOUR_COUNT,
    (18 +  8 + 1) * COLOUR_COUNT,
    (14 + 14 + 1) * COLOUR_COUNT,
    ( 8 + 18 + 1) * COLOUR_COUNT,
)
BLOCK_FILE_ROW_HEIGHTS = (  # must include the last row
    32 + 1,
    20 + 1,
)

# --- helper functions --------------------------------------------------------

def decode_int(stri, min_, max_, descr):
    # decode a string to an integer

    try:
        i = int(stri, 10)
        if not min_ <= i <= max_:
            raise ValueError
    except ValueError:
        sys.exit(f"{descr} must be an integer between {min_} and {max_}")
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
            line = line.strip()
            if line:
                yield line

# --- argument parsing --------------------------------------------------------

def parse_arguments():
    # parse command line arguments

    if not 6 <= len(sys.argv) <= 7:
        sys.exit(HELP_TEXT)

    (inputFile, outputFile, xRot, yRot, zRot) = sys.argv[1:6]
    mirrorAxes = sys.argv[6].upper() if len(sys.argv) == 7 else ""

    xRot = decode_int(xRot, 0, 15, "X rotation")
    yRot = decode_int(yRot, 0, 15, "Y rotation")
    zRot = decode_int(zRot, 0, 15, "Z rotation")
    if xRot % 2 > 0:
        sys.exit("Only X rotations divisible by 2 are supported.")
    if yRot % 4 > 0:
        sys.exit("Only Y rotations divisible by 4 are supported.")

    # split rotations into coarse and fine parts
    (coarseXRot, fineXRot) = divmod(xRot, 4)
    coarseYRot             = yRot // 4
    (coarseZRot, fineZRot) = divmod(zRot, 4)
    del xRot, yRot, zRot

    if not set(mirrorAxes).issubset(set("XYZ")):
        sys.exit("mirrorAxes may only contain letters X, Y and/or Z")

    if not os.path.isfile(inputFile):
        sys.exit(f"{inputFile} not found.")
    if os.path.exists(outputFile):
        sys.exit(f"{outputFile} already exists.")

    blockSize  = FINE_ROTATION_TO_BLOCK_SIZE[(fineZRot, fineXRot)]
    coarseRots = (coarseXRot, coarseYRot, coarseZRot)
    mirrorAxes = ("X" in mirrorAxes, "Y" in mirrorAxes, "Z" in mirrorAxes)

    return (inputFile, outputFile, blockSize, coarseRots, mirrorAxes)

# --- block data --------------------------------------------------------------

def get_object_properties(inputFile):
    # read properties of object from input file;
    # return (width, depth, height) in blocks

    width = depth = height = None

    for line in get_lines(inputFile):
        line = line.upper()
        if line.startswith("W"):
            width = decode_int(line[1:], 1, 256, "object width")
        elif line.startswith("D"):
            depth = decode_int(line[1:], 1, 256, "object depth")
        elif line.startswith("H"):
            height = decode_int(line[1:], 1, 256, "object height")
        elif not (
               line.startswith("C")  # unsupported for now
            or line.startswith("|")
            or line.startswith("#")
        ):
            sys.exit("Syntax error: " + line)

    if width is None or depth is None or height is None:
        sys.exit("Must define width, depth and height in input file.")

    return (width, depth, height)

def get_object_data(inputFile):
    # generate colours of building blocks from input file
    # (a tuple of ints per "|" line)

    for line in get_lines(inputFile):
        if line.startswith("|"):
            try:
                yield tuple(int(c, 10) for c in line[1:].replace(" ", "0"))
            except ValueError:
                sys.exit("Only spaces and digits are allowed after '|'.")

def rotate_object_x(object):
    # rotate object 90 degrees clockwise around X axis;
    # object: tuple of tuples of tuples of ints

    width  = len(object[0][0])
    depth  = len(object[0])
    height = len(object)

    # (x, y, z) = (x, z, -y)
    return tuple(
        tuple(
            tuple(
                object[z][y][x] for x in range(width)
            ) for z in range(height)
        ) for y in range(depth - 1, -1, -1)
    )

def rotate_object_y(object):
    # rotate object 90 degrees clockwise around Y axis;
    # object: tuple of tuples of tuples of ints

    width  = len(object[0][0])
    depth  = len(object[0])
    height = len(object)

    # (x, y, z) = (z, y, -x)
    return tuple(
        tuple(
            tuple(
                object[z][y][x] for z in range(height)
            ) for y in range(depth)
        ) for x in range(width - 1, -1, -1)
    )

def rotate_object_z(object):
    # rotate object 90 degrees clockwise around Z axis;
    # object: tuple of tuples of tuples of ints

    width  = len(object[0][0])
    depth  = len(object[0])
    height = len(object)

    return tuple(
        tuple(
            tuple(
                object[z][y][x] for y in range(depth - 1, -1, -1)
            ) for x in range(width)
        ) for z in range(height)
    )

def transform_object(object, rotations, mirrorAxes):
    # rotate and mirror object if needed;
    # rotations:  coarse (X, Y, Z) rotations (0-3 each);
    # mirrorAxes: mirror along (X, Y, Z)? (booleans)
    # object: tuple of tuples of tuples of ints

    for i in range(rotations[0]):
        object = rotate_object_x(object)
    for i in range(rotations[1]):
        object = rotate_object_y(object)
    for i in range(rotations[2]):
        object = rotate_object_z(object)

    if mirrorAxes[0]:
        object = tuple(tuple(j[::-1] for j in i) for i in object)
    if mirrorAxes[1]:
        object = tuple(i[::-1] for i in object)
    if mirrorAxes[2]:
        object = object[::-1]

    return object

# --- output image drawing ----------------------------------------------------

def get_output_image_size(blockSize, objWidth, objDepth, objHeight):
    # blockSize: (width1, width2, depth1, depth2, height) of blocks;
    # objWidth, objHeight: object size in blocks;
    # return: (image_width, image_height)

    (blkWidth1, blkWidth2, blkDepth1, blkDepth2, blkHeight) = blockSize

    width = (
          objWidth * blkWidth1
        + objDepth * blkWidth2
        + MARGIN_HORZ * 2 + 1
    )
    height = (
          objWidth  * blkDepth2
        + objDepth  * blkDepth1
        + objHeight * blkHeight
        + MARGIN_VERT * 2 + 1
    )
    return (width, height)

def get_image_properties_in_block_file(blockSize):
    # get (x, y, width, height) of one image in block file;
    # blockSize: (width1, width2, depth1, depth2, height) of blocks

    (column, row) = BLOCK_FILE_BLOCKSETS[blockSize]
    x = sum(BLOCK_FILE_COLUMN_WIDTHS[:column])
    y = sum(BLOCK_FILE_ROW_HEIGHTS[:row])
    (blkWidth1, blkWidth2, blkDepth1, blkDepth2, blkHeight) = blockSize
    width  = blkWidth1 + blkWidth2             + 1
    height = blkDepth1 + blkDepth2 + blkHeight + 1
    return (x, y, width, height)

def validate_block_image(img):
    # img: block image in Pillow format

    if img.mode not in ("P", "RGBA"):
        sys.exit(f"Block image must be in 'P' or 'RGBA' format.")
    if img.width != sum(BLOCK_FILE_COLUMN_WIDTHS):
        sys.exit(f"Block image width must be {sum(BLOCK_FILE_COLUMN_WIDTHS)}.")
    if img.height != sum(BLOCK_FILE_ROW_HEIGHTS):
        sys.exit(f"Block image height must be {sum(BLOCK_FILE_ROW_HEIGHTS)}.")

def get_3d_coordinates(width, depth, height):
    # generate 3D coordinates from rear to front (increasing x+y+z)

    for xyzSum in range(0, width + depth + height - 2):
        # x + y + z must equal xyzSum
        for x in range(width):
            for y in range(depth):
                z = xyzSum - x - y
                if 0 <= z < height:
                    yield (x, y, z)

def get_2d_origin(objDepth, objHeight, blockSize):
    # get 2D origin of 3D-to-2D coordinate transform as (x, y)
    # objDepth:  object depth  in blocks
    # objHeight: object height in blocks
    # blockSize: (width1, width2, depth1, depth2, height) of blocks

    (blkWidth2, blkHeight) = (blockSize[1], blockSize[4])
    x = MARGIN_HORZ + (objDepth  - 1) * blkWidth2
    y = MARGIN_VERT + (objHeight - 1) * blkHeight
    return (x, y)

def transform_3d_to_2d(x, y, z, blockSize):
    # transform 3D coordinates to 2D
    # blockSize: (width1, width2, depth1, depth2, height) of blocks

    (blkWidth1, blkWidth2, blkDepth1, blkDepth2, blkHeight) = blockSize
    tx = x * blkWidth1 - y * blkWidth2
    ty = x * blkDepth2 + y * blkDepth1 - z * blkHeight
    return (tx, ty)

def draw_blocks(object, blkImgs, outImg, blockSize):
    # draw object on image
    # object:    colours of building blocks (tuple of tuples of tuples of ints)
    # blkImgs:   list of building blocks (one colour variant/image)
    # outImg:    image to paint to
    # blockSize: (width1, width2, depth1, depth2, height) of blocks

    # object size in blocks
    objWidth  = len(object[0][0])
    objDepth  = len(object[0])
    objHeight = len(object)

    # 2D origin coordinates
    (ox, oy) = get_2d_origin(objDepth, objHeight, blockSize)

    # get 3D coordinates from rear to front
    for (x, y, z) in get_3d_coordinates(objWidth, objDepth, objHeight):
        colour = object[z][y][x]
        if colour:
            # transform coordinates to 2D, add origin coordinates and paint
            # a block there
            (tx, ty) = transform_3d_to_2d(x, y, z, blockSize)
            outImg.alpha_composite(blkImgs[colour-1], dest=(ox+tx, oy+ty))

    return outImg

# --- main --------------------------------------------------------------------

def main():
    if not os.path.isfile(BLOCK_FILE):
        sys.exit(f"{BLOCK_FILE} not found.")
    (
        inputFile, outputFile, blockSize, coarseRots, mirrorAxes
    ) = parse_arguments()
    (width, depth, height) = get_object_properties(inputFile)

    # get object data (colours of building blocks)
    objData = list(get_object_data(inputFile))
    if max(len(l) for l in objData) > width:
        sys.exit(f"Can't have more than {width} characters after '|'.")
    if len(objData) != height * depth:
        sys.exit(f"Must have {height*depth} lines starting with '|'.")
    if max((max(l) if l else 0) for l in objData) > COLOUR_COUNT:
        sys.exit(f"Can't have colour numbers greater than {COLOUR_COUNT}.")

    # pad each line of blocks to object_width integers
    objData = [l + (width - len(l)) * (0,) for l in objData]
    # wrap each layer in its own tuple to get a tuple of tuples of tuples
    objData = tuple(
        tuple(objData[i:i+depth]) for i in range(0, height * depth, depth)
    )

    # rotate and mirror object if needed; recalculate object size
    objData = transform_object(objData, coarseRots, mirrorAxes)
    width  = len(objData[0][0])
    depth  = len(objData[0])
    height = len(objData)

    (outImgWidth, outImgHeight) = get_output_image_size(
        blockSize, width, depth, height
    )

    (
        blkImgX, blkImgY, blkImgWidth, blkImgHeight
    ) = get_image_properties_in_block_file(blockSize)

    # copy blocks from block file to output image
    try:
        with open(BLOCK_FILE, "rb") as handle:
            handle.seek(0)
            blkImg = Image.open(handle)
            validate_block_image(blkImg)
            if blkImg.mode == "P":
                blkImg = blkImg.convert("RGBA")

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
                "RGBA", (outImgWidth, outImgHeight), BACKGROUND_COLOUR
            )

            # draw output image
            draw_blocks(objData, blkImgs, outImg, blockSize)
    except OSError:
        sys.exit(f"Error reading {BLOCK_FILE}")

    # remove alpha channel if image is fully opaque
    if BACKGROUND_COLOUR[3] == 255:
        outImg = outImg.convert("RGB")

    # save output image
    try:
        with open(outputFile, "wb") as handle:
            handle.seek(0)
            outImg.save(handle, "png")
    except OSError:
        sys.exit(f"Error writing {outputFile}")

    print(f"Wrote {outputFile}")

main()
