# Convert a voxel file into an OpenSCAD file.

import os, sys

# colours of blocks in "blocks-small.png", excluding transparent;
# format: (red, green, blue, name)
BLOCK_COLOURS = [
    (0x55, 0x55, 0x55, "BLK"),
    (0x00, 0x40, 0xff, "BLU"),
    (0xff, 0x00, 0x55, "RED"),
    (0xff, 0xc0, 0x00, "YEL"),
    (0xff, 0xff, 0xff, "WHT"),
]

def get_lines(filename):
    # generate non-empty lines without leading or trailing whitespace
    with open(filename, "rt", encoding="ascii") as handle:
        handle.seek(0)
        for line in handle:
            if line := line.strip():
                yield line

def decode_int(stri, min_, max_, name):
    # decode an integer
    try:
        i = int(stri, 10)
        if not min_ <= i <= max_:
            raise ValueError
    except ValueError:
        sys.exit(f"{name} must be an integer between {min_} and {max_}")
    return i

def get_object_properties(inputFile):
    # read properties of object from input file;
    # return (width, depth, height) in blocks

    width = depth = height = None

    for line in get_lines(inputFile):
        if line.upper().startswith("W"):
            width = decode_int(line[1:], 1, 256, "object width")
        elif line.upper().startswith("D"):
            depth = decode_int(line[1:], 1, 256, "object depth")
        elif line.upper().startswith("H"):
            height = decode_int(line[1:], 1, 256, "object height")
        elif (
                not line.startswith("B")  # background colour
            and not line.startswith("|")
            and not line.startswith("#")
        ):
            sys.exit("Syntax error: " + line)

    if any(v is None for v in (width, depth, height)):
        sys.exit("Must define width, depth and height.")

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

def cubes_to_cuboids(cubes):
    # cubes:    {(x, y, z): colourIndex, ...}
    # generate: {(x, y, z, width, depth, height, colourIndex), ...}

    # TODO: this should actually optimise the data

    cubesLeft = cubes.copy()
    for (x, y, z) in cubes:
        colour = cubes[(x, y, z)]
        yield (x, y, z, 1, 1, 1, colour)
        cubesLeft.pop((x, y, z))

def print_colour_definitions(colours):
    # colours: set of colour indexes in object data
    for (ind, (red, green, blue, name)) in enumerate(BLOCK_COLOURS):
        if ind + 1 in colours:
            print("{} = [{:<4},{:<4},{:<4}];  // was index {}".format(
                name,
                round(red   / 255, 2),
                round(green / 255, 2),
                round(blue  / 255, 2),
                ind + 1
            ))

def print_cube_data(cuboids, totalWidth, totalDepth, totalHeight):
    # cuboids: [(x, y, z, width, depth, height, colourIndex), ...]

    # order: primary = Z, secondary = Y, tertiary = X
    cuboids.sort(key=lambda c: c[0])
    cuboids.sort(key=lambda c: c[1])
    cuboids.sort(key=lambda c: c[2])

    # print cube data
    prevZ = -1
    xOffset = -(totalWidth  - 1) / 2
    yOffset = -(totalDepth  - 1) / 2
    zOffset = -(totalHeight - 1) / 2
    for (x, y, z, w, d, h, colourIndex) in cuboids:
        # make coordinates centered
        colourName = BLOCK_COLOURS[colourIndex-1][3]
        print(
            f"color({colourName}) "
            f"translate([{x+xOffset:5},{y+yOffset:5},{z+zOffset:5}]) "
            f"cube([{w:2},{d:2},{h:2}], center=true);"
        )
        if z != prevZ:
            if prevZ != -1:
                print()
            prevZ = z

def main():
    if len(sys.argv) != 2:
        sys.exit(
            "Convert a voxel file into an OpenSCAD file. Argument: input "
            "file. See README.md for details."
        )
    inputFile = sys.argv[1]
    if not os.path.isfile(inputFile):
        sys.exit("Input file not found.")

    (width, depth, height) = get_object_properties(inputFile)

    # get object data (colours of building blocks)
    objData = list(get_object_data(inputFile))
    if max(len(l) for l in objData) > width:
        sys.exit(f"Can't have more than {width} characters after '|'.")
    if len(objData) != height * depth:
        sys.exit(f"Must have {height*depth} lines starting with '|'.")
    if max((max(l) if l else 0) for l in objData) > len(BLOCK_COLOURS):
        sys.exit(
            f"Can't have colour numbers greater than {len(BLOCK_COLOURS)}."
        )

    print(f"// {os.path.basename(inputFile)}, {width=}, {depth=}, {height=}")

    # wrap each layer in its own tuple to get a tuple of tuples of tuples
    objData = tuple(
        tuple(objData[i:i+depth]) for i in range(0, height * depth, depth)
    )

    # convert object data into a dict
    usedCubes = dict()  # {(x, y, z): colour, ...}
    for (z, layer) in enumerate(objData):
        for (y, row) in enumerate(layer):
            for (x, colour) in enumerate(row):
                if colour > 0:
                    usedCubes[(x, y, z)] = colour
    del objData

    print(f"// non-transparent unit cubes: {len(usedCubes)}")

    cuboids = list(cubes_to_cuboids(usedCubes))
    print(f"// cuboids: {len(cuboids)}")
    print()

    print("// colours")
    print_colour_definitions(set(c[6] for c in cuboids))
    print()
    print_cube_data(cuboids, width, depth, height)

main()
