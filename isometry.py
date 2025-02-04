# Draw an isometric image consisting of cubes.

# the building block (a single cube)
CUBE_WIDTH  = 16  # width  minus one
CUBE_HEIGHT = 16  # height minus one
CUBE_DEPTH  =  8  # depth  minus one
CUBE_FILE = f"minicube-{CUBE_WIDTH}x{CUBE_HEIGHT}x{CUBE_DEPTH}.png"
CUBE_IMG_WIDTH  = CUBE_WIDTH  + CUBE_DEPTH + 1  # image width
CUBE_IMG_HEIGHT = CUBE_HEIGHT + CUBE_DEPTH + 1  # image height

# horizontal/vertical margin on each side of the final image, in pixels
HORZ_MARGIN = 8
VERT_MARGIN = 8

# background color of final image (red, green, blue)
BACKGROUND_COLOR = (255, 255, 255)

import os, re, sys
try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow module required. See https://python-pillow.org")

def get_lines(filename):
    # generate lines without newlines
    with open(filename, "rt", encoding="ascii") as handle:
        handle.seek(0)
        for line in handle:
            line = line.rstrip("\n")
            if line:
                yield line

def string_to_int(stri, width):
    # interpret string as binary number;
    # space = 0, non-space = 1, pad to width with trailing zeros;
    # e.g. (" ab", 5) -> 0b01100
    return int(re.sub(r"[^ ]", r"1", stri).ljust(width).replace(" ", "0"), 2)

def reverse_int(n, width):
    # reverse order of bits; e.g. (0b10, 4) -> 0b0100
    return sum(
        ((n >> i) & 1) << (width - 1 - i) for i in range(width)
    )

def three_d_to_two_d(x, y, z, depth, height):
    # x, y, z = 3D coordinates;
    # return: (x, y) in 2D coordinates
    _2dX = HORZ_MARGIN + x * CUBE_WIDTH + (depth - 1 - y) * CUBE_DEPTH
    _2dY = VERT_MARGIN + (height - 1 - z) * CUBE_HEIGHT + y * CUBE_DEPTH
    return (_2dX, _2dY)

def main():
    if 3 <= len(sys.argv) <= 4:
        (inputFile, outputFile) = sys.argv[1:3]
        reverseAxes = sys.argv[3].upper() if len(sys.argv) == 4 else ""
    else:
        sys.exit(
            "Arguments: inputFile outputFile [axesToReverse]; see README.md "
            "for details"
        )

    # parse input file
    width = depth = height = None
    lines = []
    for line in get_lines(inputFile):
        line = line.upper()
        try:
            if line.startswith("W"):
                width = int(line[1:])
            elif line.startswith("D"):
                depth = int(line[1:])
            elif line.startswith("H"):
                height = int(line[1:])
            elif line.startswith("|"):
                lines.append(line[1:])
            else:
                sys.exit("Syntax error: " + line)
        except ValueError:
            sys.exit("Not an integer: " + line[1:])

    if any(d is None for d in (width, depth, height)):
        sys.exit("Must define all of width, depth and height.")
    if min(width, depth, height) < 1:
        sys.exit("Each dimension must be 1 or greater.")
    if len(lines) != height * depth:
        sys.exit(f"There must be {height*depth} lines starting with '|'.")
    if max(len(l) for l in lines) > width:
        sys.exit(
            f"Can't have more than {width} characters plus newline after '|'."
        )

    # encode lines as integers (one bit per cube)
    lines = [string_to_int(l, width) for l in lines]

    # convert into a tuple of tuples of ints
    lines = tuple(
        tuple(lines[i:i+depth])
        for i in range(0, height * depth, depth)
    )

    # reverse axes if needed
    if "X" in reverseAxes:
        lines = tuple(tuple(reverse_int(n, width) for n in i) for i in lines)
    if "Y" in reverseAxes:
        lines = tuple(i[::-1] for i in lines)
    if "Z" in reverseAxes:
        lines = lines[::-1]

    # dimensions of final image
    imgWidth  = width  * CUBE_WIDTH  + depth * CUBE_DEPTH + 2 * HORZ_MARGIN
    imgHeight = height * CUBE_HEIGHT + depth * CUBE_DEPTH + 2 * VERT_MARGIN

    if not os.path.isfile(CUBE_FILE):
        sys.exit(f"{CUBE_FILE} not found.")

    # read the image of the building block
    with open(CUBE_FILE, "rb") as handle:
        handle.seek(0)
        cubeImage = Image.open(handle)
        if cubeImage.mode != "RGBA":
            sys.exit(f"{CUBE_FILE} must be in RGBA format.")
        if cubeImage.width != CUBE_IMG_WIDTH:
            sys.exit(f"{CUBE_FILE} must be {CUBE_IMG_WIDTH} pixels wide.")
        if cubeImage.height != CUBE_IMG_HEIGHT:
            sys.exit(f"{CUBE_FILE} must be {CUBE_IMG_HEIGHT} pixels tall.")

        # create image
        image = Image.new(
            "RGBA", (imgWidth, imgHeight), BACKGROUND_COLOR + (255,)
        )

        # draw image
        for y in range(depth):
            for z in range(height):
                for x in range(width):
                    bitPos = width - 1 - x
                    if lines[z][y] & (1 << bitPos):
                        coords = three_d_to_two_d(x, y, z, depth, height)
                        image.alpha_composite(cubeImage, dest=coords)

    # remove alpha channel
    image = image.convert("RGB")

    # save image
    with open(outputFile, "wb") as handle:
        handle.seek(0)
        image.save(handle, "png")

main()
