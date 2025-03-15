# Convert a voxel file into an OpenSCAD file.

import os, random, sys, time

# colours of blocks in "blocks-small.png", excluding transparent;
# format: (red, green, blue, name)
BLOCK_COLOURS = [
    (0x55, 0x55, 0x55, "BLK"),
    (0x00, 0x40, 0xff, "BLU"),
    (0xff, 0x00, 0x55, "RED"),
    (0xff, 0xc0, 0x00, "YEL"),
    (0xff, 0xff, 0xff, "WHT"),
]

# make all nontransparent cubes the same colour?
# (will reduce the number of cuboids needed)
COMBINE_CUBE_COLOURS = 0  # 0=no, 1=yes

# assign each cuboid a random colour instead of the original colour?
RANDOM_CUBOID_COLOURS = 0  # 0=no, 1=yes

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

def get_largest_solid_cuboid_here(x, y, z, cubes):
    # find the largest unassigned non-transparent one-colour cuboid starting
    # from the specified location
    # cubes:  {(x, y, z): colourIndex, ...}
    # return: (width, depth, height) of cuboid

    totalWidth  = max(c[0] for c in cubes) + 1
    totalDepth  = max(c[1] for c in cubes) + 1
    totalHeight = max(c[2] for c in cubes) + 1

    largestVolume = 0
    bestWidth     = 0
    bestDepth     = 0
    bestHeight    = 0

    for height in range(1, totalHeight - z + 1):
        for depth in range(1, totalDepth - y + 1):
            for width in range(1, totalWidth - x + 1):
                isSolid = True
                for z2 in range(z, z + height):
                    for y2 in range(y, y + depth):
                        for x2 in range(x, x + width):
                            if cubes.get((x2, y2, z2), 0) != cubes[(x, y, z)]:
                                isSolid = False
                                break
                        if not isSolid:
                            break
                    if not isSolid:
                        break
                if isSolid:
                    volume = width * depth * height
                    if volume > largestVolume:
                        largestVolume = volume
                        bestWidth  = width
                        bestDepth  = depth
                        bestHeight = height

    return (bestWidth, bestDepth, bestHeight)

def get_largest_solid_cuboid(cubes):
    # find the largest unassigned non-transparent one-colour cuboid anywhere
    # cubes:  {(x, y, z): colourIndex, ...}
    # return: (x, y, z)

    totalWidth  = max(c[0] for c in cubes) + 1
    totalDepth  = max(c[1] for c in cubes) + 1
    totalHeight = max(c[2] for c in cubes) + 1
    largestVolume = 0

    for z in range(totalHeight):
        for y in range(totalDepth):
            for x in range(totalWidth):
                thisColour = cubes.get((x, y, z), 0)
                if thisColour != 0:
                    (width, depth, height) = get_largest_solid_cuboid_here(
                        x, y, z, cubes
                    )
                    volume = width * depth * height
                    if volume > largestVolume:
                        largestVolume = volume
                        bestX         = x
                        bestY         = y
                        bestZ         = z

    return (bestX, bestY, bestZ)

def cubes_to_cuboids(cubes):
    # combine unit cubes into larger rectangular cuboids
    # cubes:    {(x, y, z): colourIndex, ...}; modified in-place
    # generate: (x, y, z, width, depth, height, colourIndex) per call

    # total time: 6.1 s

    while len(cubes) > 0:
        # find the largest unassigned non-transparent one-colour cuboid
        (x, y, z) = get_largest_solid_cuboid(cubes)
        (width, depth, height) = get_largest_solid_cuboid_here(x, y, z, cubes)

        # output the cuboid
        yield (
            x + (width  - 1) / 2,
            y + (depth  - 1) / 2,
            z + (height - 1) / 2,
            width,
            depth,
            height,
            cubes[(x, y, z)]  # colour index
        )

        # free the cubes that were in the cuboid
        for z2 in range(z, z + height):
            for y2 in range(y, y + depth):
                for x2 in range(x, x + width):
                    cubes.pop((x2, y2, z2))

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

    # center everything
    xOffset = -(totalWidth  - 1) / 2
    yOffset = -(totalDepth  - 1) / 2
    zOffset = -(totalHeight - 1) / 2
    print(f"translate([{xOffset},{yOffset},{zOffset}]) {{")

    for (x, y, z, w, d, h, colourIndex) in cuboids:
        if RANDOM_CUBOID_COLOURS:
            colourName = "[{},{},{}]".format(
                random.randrange(0, 100) / 100,
                random.randrange(0, 100) / 100,
                random.randrange(0, 100) / 100
            )
        else:
            colourName = BLOCK_COLOURS[colourIndex-1][3]
        #
        print(
            f"{'':4}color({colourName}) "
            f"translate([{x:4},{y:4},{z:4}]) "
            f"cube([{w:2},{d:2},{h:2}], center=true);"
        )

    print("}")  # end translate

def main():
    startTime = time.time()

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

    if COMBINE_CUBE_COLOURS:
        objData = [tuple(1 if c > 0 else 0 for c in row) for row in objData]

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
    print("// volume:", len(usedCubes), "unit cubes")

    cuboids = list(cubes_to_cuboids(usedCubes))
    maxCuboidVol = max(c[3] * c[4] * c[5] for c in cuboids)
    print(f"// cuboids:", len(cuboids))
    print(f"// max cuboid volume:", maxCuboidVol, "unit cubes")
    print()

    if not RANDOM_CUBOID_COLOURS:
        print("// colours")
        print_colour_definitions(set(c[6] for c in cuboids))
        print()
    print_cube_data(cuboids, width, depth, height)
    print()
    print("// time:", format(time.time() - startTime, ".1f"), "s")

main()
