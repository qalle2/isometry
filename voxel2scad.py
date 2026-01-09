# Convert a voxel file into an OpenSCAD file.

import os, sys, time

DEFAULT_PALETTE = [
    ( 85,  85,  85),  # 1: dark grey
    (255,   0,   0),  # 2: red
    (255, 128,   0),  # 3: orange
    (255, 255,   0),  # 4: yellow
    (  0, 255,   0),  # 5: green
    (  0, 255, 255),  # 6: cyan
    (  0,   0, 255),  # 7: blue
    (255,   0, 255),  # 8: magenta
    (255, 255, 255),  # 9: white
]

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
            line = line.strip()
            if line:
                yield line

# -----------------------------------------------------------------------------

def parse_bool_arg(argvIndex, default, descr):
    # argvIndex: index in sys.argv
    # default:   bool
    # descr:     description, str
    # return:    bool

    if len(sys.argv) < argvIndex + 1:
        return default

    value = sys.argv[argvIndex]
    if value not in ("0", "1"):
        sys.exit(f"{descr} argument must be 0 or 1.")
    return bool(int(value))

def get_object_properties(inputFile):
    # read properties of object from input file;
    # return (width, depth, height, palette);
    #     the first 3 are in cubes;
    #     palette has (red, green, blue) for indexes 1-9

    width = depth = height = None
    palette = DEFAULT_PALETTE.copy()

    for line in get_lines(inputFile):
        if line.upper().startswith("W"):
            width = decode_int(line[1:], 1, 256, "object width")
        elif line.upper().startswith("D"):
            depth = decode_int(line[1:], 1, 256, "object depth")
        elif line.upper().startswith("H"):
            height = decode_int(line[1:], 1, 256, "object height")
        elif line.upper().startswith("C"):
            index_ = decode_int(line[1], 0, 9, "colour index")
            if index_ > 0:
                palette[index_-1] = decode_colour_code(line[2:])
        elif (
                not line.startswith("B")  # legacy command for C0...
            and not line.startswith("|")
            and not line.startswith("#")
        ):
            sys.exit("Syntax error: " + line)

    if any(v is None for v in (width, depth, height)):
        sys.exit("Must define width, depth and height.")

    return (width, depth, height, palette)

def get_object_data(inputFile):
    # generate colours of building blocks from input file
    # (a tuple of ints per "|" line)

    for line in get_lines(inputFile):
        if line.startswith("|"):
            try:
                yield tuple(int(c, 10) for c in line[1:].replace(" ", "0"))
            except ValueError:
                sys.exit("Only spaces and digits are allowed after '|'.")

def have_cubes_x_symmetry(cubes, width):
    # does the object have X symmetry (left vs. right)?
    #     cubes:  {(x, y, z): colour, ...}
    #     width:  width of object
    #     return: bool

    # use integers only to be safe
    doubleXOffset = width - 1
    centredCubes = [
        (x * 2 - doubleXOffset, y, z, cubes[(x, y, z)]) for (x, y, z) in cubes
    ]
    return all((-x, y, z, c) in centredCubes for (x, y, z, c) in centredCubes)

def get_largest_solid_cuboid_here(x, y, z, cubes, volumeLimit):
    # find the largest unassigned non-transparent one-colour cuboid starting
    # from the specified location; hidden cubes may get any colour
    # cubes:       {(x, y, z): colourIndex, ...}
    # volumeLimit: don't bother searching for cuboids larger than this
    #              (speed optimisation; 0=no limit)
    # return:      (width, depth, height) of cuboid

    totalWidth  = max(c[0] for c in cubes) + 1
    totalDepth  = max(c[1] for c in cubes) + 1
    totalHeight = max(c[2] for c in cubes) + 1
    startColour = cubes[(x, y, z)]

    largestVolume = 0
    bestWidth     = 0
    bestDepth     = 0
    bestHeight    = 0

    for height in range(1, totalHeight - z + 1):
        for depth in range(1, totalDepth - y + 1):
            for width in range(1, totalWidth - x + 1):
                if volumeLimit == 0 or height * depth * width <= volumeLimit:
                    isSolid = True
                    for z2 in range(z, z + height):
                        for y2 in range(y, y + depth):
                            for x2 in range(x, x + width):
                                if cubes.get((x2, y2, z2), 0) != startColour:
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

def get_largest_solid_cuboid(cubes, volumeLimit):
    # find the largest unassigned non-transparent one-colour cuboid anywhere;
    # hidden cubes may get any colour
    # cubes:       {(x, y, z): colourIndex, ...}
    # volumeLimit: don't bother searching for cuboids larger than this (speed
    #              optimisation; 0=no limit)
    # return:      (x, y, z)

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
                        x, y, z, cubes, volumeLimit
                    )
                    volume = width * depth * height
                    if volume > largestVolume:
                        largestVolume = volume
                        bestX = x
                        bestY = y
                        bestZ = z

    return (bestX, bestY, bestZ)

def cubes_to_cuboids(cubes):
    # combine unit cubes into larger rectangular cuboids;
    # hidden cubes may get any colour
    # cubes:    {(x, y, z): colourIndex, ...}; modified in-place
    # generate: (x, y, z, width, depth, height, colourIndex) per call

    # largest cuboid found so far (0=none)
    volumeLimit = 0

    while len(cubes) > 0:
        # find the largest unassigned non-transparent one-colour cuboid
        (x, y, z) = get_largest_solid_cuboid(cubes, volumeLimit)
        (width, depth, height) = get_largest_solid_cuboid_here(
            x, y, z, cubes, volumeLimit
        )
        volumeLimit = width * depth * height

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

def cubes_to_cuboids_unoptimised(cubes):
    # like cubes_to_cuboids(), but each cuboid is just a cube
    # cubes:    {(x, y, z): colourIndex, ...}
    # generate: (x, y, z, width, depth, height, colourIndex) per call

    for (x, y, z) in cubes:
        yield (x, y, z, 1, 1, 1, cubes[(x, y, z)])

def print_colour_definitions(indexesUsed, palette):
    # indexesUsed: distinct non-transparent colour indexes used by object data
    # palette: list with (red, green, blue) for colour indexes 1-9

    for (ind, (red, green, blue)) in enumerate(palette):
        if ind + 1 in indexesUsed:
            print("COL{} = [{:3}/255,{:3}/255,{:3}/255];".format(
                ind + 1, red, green, blue
            ))

def print_cube_data(cuboids, totalWidth, totalDepth, totalHeight):
    # cuboids: [(x, y, z, width, depth, height, colourIndex), ...]
    # X coordinates have already been centred around 0

    # scale (Nanoblock are 4/3 as tall as wide or long)
    # and translate (centre cuboids around Y=0 and Z=0)
    yOffset = -(totalDepth  - 1) / 2
    zOffset = -(totalHeight - 1) / 2
    print(f"scale([1,1,4/3]) translate([0,{yOffset},{zOffset}]) {{")

    # sort
    cuboids.sort(key=lambda c: c[0])  # by X
    cuboids.sort(key=lambda c: c[1])  # by Y
    cuboids.sort(key=lambda c: c[2])  # by Z
    # first X=0, then X<0, then X>0
    cuboids.sort(key=lambda c: (0 if c[0] == 0 else (1 if c[0] < 0 else 2)))

    prevX = None

    for (x, y, z, w, d, h, colourIndex) in cuboids:
        if x == 0 and prevX is None:
            print(f"{'':4}// X = 0, by ascending Z")
        elif x < 0 and (prevX is None or prevX == 0):
            print()
            print(f"{'':4}// X < 0, by ascending Z")
        elif x > 0 and (prevX is None or prevX < 0):
            print()
            print(f"{'':4}// X > 0, by ascending Z")
        #
        print(
            f"{'':4}color(COL{colourIndex}) "
            f"translate([{x:5},{y:4},{z:4}]) "
            "cuboid("
            + ("" if max(w, d, h) == 1 else f"{w:2},{d:2},{h:2}")
            + ");"
        )
        #
        prevX = x

    print("}")  # end translate() and scale()

def main():
    # parse args
    if not 2 <= len(sys.argv) <= 4:
        sys.exit(
            "Convert a voxel file into an OpenSCAD file. "
            "Arguments: inputFile combineColours optimiseCuboids. "
            "The last two args are optional. "
            "Valid values are 0 or 1 for each. "
            "See README.md for details."
        )
    inputFile = sys.argv[1]
    if not os.path.isfile(inputFile):
        sys.exit("Input file not found.")

    combineColours  = parse_bool_arg(2, False, "combineColours")
    optimiseCuboids = parse_bool_arg(3, True,  "optimiseCuboids")

    (width, depth, height, palette) = get_object_properties(inputFile)

    # get object data (colours of building blocks)
    objData = list(get_object_data(inputFile))
    if max(len(l) for l in objData) > width:
        sys.exit(f"Can't have more than {width} characters after '|'.")
    if len(objData) != height * depth:
        sys.exit(f"Must have {height*depth} lines starting with '|'.")
    if max((max(l) if l else 0) for l in objData) > len(palette):
        sys.exit(
            f"Can't have colour numbers greater than {len(palette)}."
        )

    if combineColours:
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

    # mirror Y coordinates
    usedCubes = dict(
        ((x, depth - 1 - y, z), usedCubes[(x, y, z)])
        for (x, y, z) in usedCubes
    )

    hiddenCubes = set(
        (x, y, z) for (x, y, z) in usedCubes if
            (x - 1, y,     z    ) in usedCubes
        and (x + 1, y,     z    ) in usedCubes
        and (x,     y - 1, z    ) in usedCubes
        and (x,     y + 1, z    ) in usedCubes
        and (x,     y    , z - 1) in usedCubes
        and (x,     y    , z + 1) in usedCubes
    )

    print(f"// model read: {os.path.basename(inputFile)}")
    print(
        f"// model size in cubes: {width=}, {depth=}, {height=}, "
        f"volume={len(usedCubes)}"
    )
    print(
        "// is the model left-right symmetric: "
        + ("yes" if have_cubes_x_symmetry(usedCubes, width) else "no")
    )
    print(f"// hidden cubes (all faces touch other cubes): {len(hiddenCubes)}")

    startTime = time.time()
    if optimiseCuboids:
        cuboids = list(cubes_to_cuboids(usedCubes))
    else:
        cuboids = list(cubes_to_cuboids_unoptimised(usedCubes))
    print(
        f"// optimised model to {len(cuboids)} cuboids in "
        f"{time.time()-startTime:.1f} seconds"
    )
    print("// volume of largest cuboid: {} cubes".format(
        max(c[3] * c[4] * c[5] for c in cuboids)
    ))

    # centre X coordinates around 0
    xOffset = (width - 1) / 2
    cuboids = [
        (x - xOffset, y, z, w, d, h, c) for (x, y, z, w, d, h, c) in cuboids
    ]

    hasCuboidXSymmetry = all(
        (-x, y, z, w, d, h, c) in cuboids for (x, y, z, w, d, h, c) in cuboids
    )
    print(
        "// is the set of optimised cuboids left-right symmetric: "
        + ("yes" if hasCuboidXSymmetry else "no")
    )
    print()

    print("// colours")
    print_colour_definitions(frozenset(c[6] for c in cuboids), palette)
    print()
    print("module cuboid(w=1, d=1, h=1) {")
    print(f"{'':4}cube([w,d,h], center=true);")
    print("}")
    print()
    print_cube_data(cuboids, width, depth, height)

main()
