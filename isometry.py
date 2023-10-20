# create a PNG with an isometric drawing

CUBE_IMAGE = "minicube.png"  # RGBA, 25*25 pixels

import re, sys
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
    # space = 0, non-space = 1, pad to width with zeros;
    # e.g. (" ab", 5) -> 0b01100
    return int(re.sub(r"[^ ]", r"1", stri).ljust(width).replace(" ", "0"), 2)

def main():
    if len(sys.argv) != 3:
        sys.exit("Args: inputFile outputFile")
    (inputFile, outputFile) = sys.argv[1:]

    # parse input file
    lines = []
    for line in get_lines(inputFile):
        line = line.upper()
        try:
            if line.startswith("W"):
                width = int(line[1:])
            elif line.startswith("L"):
                length = int(line[1:])
            elif line.startswith("H"):
                height = int(line[1:])
            elif line.startswith("|"):
                lines.append(line[1:])
            else:
                sys.exit("Syntax error: " + line)
        except ValueError:
            sys.exit("Not an integer: " + line[1:])

    if min(width, length, height) < 1:
        sys.exit("Each dimension must be 1 or greater.")
    if len(lines) != height * length:
        sys.exit("There must be {height*length} lines starting with '|'.")
    if max(len(l) for l in lines) > width:
        sys.exit("There must be no lines longer than {width}.")

    # encode lines as integers (one bit per cube)
    lines = [string_to_int(l, width) for l in lines]

    # convert into a tuple of tuples of ints
    lines = tuple(
        tuple(lines[i:i+length])
        for i in range(0, height * length, length)
    )

    #print(f"{width=}, {length=}, {height=}")
    #print("Lines:", lines)

    imgWidth  = width  * 16 + length * 8 + 2 * 8
    imgHeight = height * 16 + length * 8 + 2 * 8

    # read cube image (RGBA, 25*25 pixels)
    with open(CUBE_IMAGE, "rb") as handle:
        handle.seek(0)
        cubeImage = Image.open(handle)

        # create image
        image = Image.new("RGBA", (imgWidth, imgHeight))

        for y in range(length):         # +Y = towards viewer
            for z in range(height):     # +Z = up
                for x in range(width):  # +X = right
                    if lines[z][y] & (1 << (width - 1 - x)):
                        imgX = 8 + x * 16 + (length - 1 - y) * 8
                        imgY = 8 + (height - 1 - z) * 16 + y * 8
                        image.alpha_composite(cubeImage, dest=(imgX, imgY))

    # save image
    with open(outputFile, "wb") as handle:
        handle.seek(0)
        image.save(handle, "png")

main()
