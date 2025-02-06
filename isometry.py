# Draw an isometric image consisting of cubes.

COORD_TYPE = 2  # 1 or 2; see README.md

# the building block (a single cube); for coordinate type 2,
# width/depth/height = how much X/Y/Z affects 2D coordinates
CUBE_WIDTH  = 10
CUBE_DEPTH  =  5
CUBE_HEIGHT =  8
CUBE_FILE_BASE = (
    f"minicube-t{COORD_TYPE}-w{CUBE_WIDTH}-d{CUBE_DEPTH}-h{CUBE_HEIGHT}"
)
if COORD_TYPE == 1:
    CUBE_IMG_WIDTH  = CUBE_WIDTH  + CUBE_DEPTH + 1
    CUBE_IMG_HEIGHT = CUBE_HEIGHT + CUBE_DEPTH + 1
else:
    CUBE_IMG_WIDTH  = CUBE_WIDTH * 2 + 1
    CUBE_IMG_HEIGHT = CUBE_DEPTH * 2 + CUBE_HEIGHT + 1

# horizontal/vertical margin on each side of the final image, in pixels
HORZ_MARGIN = 8
VERT_MARGIN = 8

# background color of final image (red, green, blue)
BACKGROUND_COLOR = (0xaa, 0xaa, 0xcc)

import itertools, os, sys
try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow module required. See https://python-pillow.org")

def get_lines(filename):
    # generate lines without newlines, leading whitespace or comments
    with open(filename, "rt", encoding="ascii") as handle:
        handle.seek(0)
        for line in handle:
            line = line.lstrip().rstrip("\n")
            if line and not line.startswith("#"):
                yield line

def get_dimensions(inputFile):
    # get dimensions from input file

    width = depth = height = None
    for line in get_lines(inputFile):
        line = line.upper()
        try:
            if line.startswith("W"):
                width = int(line[1:], 10)
            elif line.startswith("D"):
                depth = int(line[1:], 10)
            elif line.startswith("H"):
                height = int(line[1:], 10)
            elif not line.startswith("|"):
                sys.exit("Syntax error: " + line)
        except ValueError:
            sys.exit("Not an integer: " + line[1:])

    for dimension in (width, depth, height):
        if dimension is None:
            sys.exit("Must define all of width, depth and height.")
        if not 1 <= dimension <= 256:
            sys.exit("Each dimension must be 1 to 256.")

    return (width, depth, height)

def get_cube_data(inputFile):
    # generate cube data from input file (a tuple of ints per "|" line)

    for line in get_lines(inputFile):
        if line.startswith("|"):
            try:
                yield tuple(int(c, 10) for c in line[1:].replace(" ", "0"))
            except ValueError:
                sys.exit(
                    "A character other than space or digit after '|': "
                    + line[1:]
                )

def type1_coords_to_2d(x, y, z):
    # Convert "type 1" 3D coordinates into 2D (x, y)
    #       Z
    #       |
    #       +---X  -->  +-- X
    #      /            |
    #     Y             Y
    return (
         x * CUBE_WIDTH  - y * CUBE_DEPTH,
        -z * CUBE_HEIGHT + y * CUBE_DEPTH
    )

def type2_coords_to_2d(x, y, z):
    # Convert "type 2" 3D coordinates into 2D (x, y)
    #       Z
    #       |    -->  +-- X
    #      / \        |
    #     Y   X       Y
    return (
        (x - y) * CUBE_WIDTH,
        (x + y) * CUBE_DEPTH - z * CUBE_HEIGHT
    )

def main():
    if 3 <= len(sys.argv) <= 4:
        (inputFile, outputFile) = sys.argv[1:3]
        reverseAxes = sys.argv[3].upper() if len(sys.argv) == 4 else ""
    else:
        sys.exit(
            "Arguments: inputFile outputFile [axesToReverse]; see README.md "
            "for details"
        )

    (width, depth, height) = get_dimensions(inputFile)

    lines = list(get_cube_data(inputFile))
    if max(len(l) for l in lines) > width:
        sys.exit(
            f"Can't have more than {width} characters plus newline after '|'."
        )
    if len(lines) != height * depth:
        sys.exit(f"There must be {height*depth} lines starting with '|'.")

    # get distinct colors used (except 0 or "non-cube")
    colorsUsed = set(itertools.chain.from_iterable(lines)) - set((0,))
    # pad each line to width integers
    lines = [l + (width - len(l)) * (0,) for l in lines]
    # wrap each layer in its own tuple to get a tuple of tuples of tuples
    lines = tuple(
        tuple(lines[i:i+depth])
        for i in range(0, height * depth, depth)
    )

    # reverse axes if needed
    if "X" in reverseAxes:
        lines = tuple(tuple(j[::-1] for j in i) for i in lines)
    if "Y" in reverseAxes:
        lines = tuple(i[::-1] for i in lines)
    if "Z" in reverseAxes:
        lines = lines[::-1]

    # get 3D-to-2D projection function, size of final image and 2D origin
    if COORD_TYPE == 1:
        project_fn = type1_coords_to_2d
        imgWidth  = width  * CUBE_WIDTH  + depth * CUBE_DEPTH
        imgHeight = height * CUBE_HEIGHT + depth * CUBE_DEPTH
        originX = (depth  - 1) * CUBE_DEPTH
        originY = (height - 1) * CUBE_HEIGHT
    else:
        project_fn = type2_coords_to_2d
        imgWidth  = (width + depth) * CUBE_WIDTH
        imgHeight = (width + depth) * CUBE_DEPTH + height * CUBE_HEIGHT
        originX = (depth  - 1) * CUBE_WIDTH
        originY = (height - 1) * CUBE_HEIGHT
    imgWidth  += HORZ_MARGIN * 2
    imgHeight += VERT_MARGIN * 2
    originX   += HORZ_MARGIN
    originY   += VERT_MARGIN

    # make sure cube files exist
    for color in sorted(colorsUsed):
        cubeFile = CUBE_FILE_BASE + f"-c{color}.png"
        if not os.path.isfile(cubeFile):
            sys.exit(f"{cubeFile} not found.")

    # open cube files (ugly code warning; must be manually closed later)
    cubeFileHandles = dict()
    for color in colorsUsed:
        cubeFile = CUBE_FILE_BASE + f"-c{color}.png"
        cubeFileHandles[color] = open(cubeFile, "rb")

    # open cube files and validate them
    cubeImages = dict()
    for color in cubeFileHandles:
        cubeFileHandles[color].seek(0)
        cubeImages[color] = Image.open(cubeFileHandles[color])
        if (
            cubeImages[color].mode != "RGBA"
            or cubeImages[color].width != CUBE_IMG_WIDTH
            or cubeImages[color].height != CUBE_IMG_HEIGHT
        ):
            # close cube files and exit
            for color in cubeFileHandles:
                cubeFileHandles[color].close()
            sys.exit(
                f"Cube files must be in RGBA format, "
                f"{CUBE_IMG_WIDTH} pixels wide "
                f"and {CUBE_IMG_HEIGHT} pixels tall."
            )

    # create output image
    outImage = Image.new(
        "RGBA", (imgWidth, imgHeight), BACKGROUND_COLOR + (0xff,)
    )

    # draw output image
    for y in range(depth):
        for z in range(height):
            for x in range(width):
                color = lines[z][y][x]
                if color:
                    (_2dX, _2dY) = project_fn(x, y, z)
                    _2dX += originX
                    _2dY += originY
                    outImage.alpha_composite(
                        cubeImages[color], dest=(_2dX, _2dY)
                    )

    # close cube files
    for color in colorsUsed:
        cubeFileHandles[color].close()

    # remove alpha channel
    outImage = outImage.convert("RGB")

    # save output image
    with open(outputFile, "wb") as handle:
        handle.seek(0)
        outImage.save(handle, "png")

main()
