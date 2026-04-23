# Convert a voxel file into an OpenSCAD file.

# Litten:
#   cubeOverlap=0: 105 cuboids, total volume 535
#   cubeOverlap=1:  92 cuboids, total volume 765
#   cubeOverlap=2:  83 cuboids, total volume 879

import os, sys, time

# index of the "don't care" colour (optimised to transparent or any colour)
DONT_CARE_COLOUR = -1
# index of transparent colour
TRANSPARENT_COLOUR = 0
# what colour index to combine opaque colours into
COMBINED_COLOUR = 1

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

def get_outside_cubes(opaqueCubes, width, depth, height):
    # opaqueCubes: set-like with (x, y, z) of each opaque cube in the object
    # width, depth, height: size of object in cubes
    # return: set with (x, y, z) of each (transparent) outside cube

    # algorithm: orthogonal flood fill using 1 cube of transparent padding on
    # each side of the object

    # start from two opposite corners for speed
    outsideCubes = set(( (-1, -1, -1), (width, depth, height) ))

    while True:
        newCubes   = set()              # new outside cubes
        oldCubeCnt = len(outsideCubes)  # old outside cube count
        # for each known outside cube, add transparent orthogonal neighbours
        for (x, y, z) in outsideCubes:
            for offset in (-1, 1):
                neighX = x + offset
                neighY = y + offset
                neighZ = z + offset
                if -1 <= neighX <= width and (neighX, y, z) not in opaqueCubes:
                    newCubes.add((neighX, y, z))
                if -1 <= neighY <= depth and (x, neighY, z) not in opaqueCubes:
                    newCubes.add((x, neighY, z))
                if (
                    -1 <= neighZ <= height
                    and (x, y, neighZ) not in opaqueCubes
                ):
                    newCubes.add((x, y, neighZ))
        outsideCubes.update(newCubes)
        if len(outsideCubes) == oldCubeCnt:
            break

    # remove cubes that belong in the transparent padding
    outsideCubes = set(
        (x, y, z) for (x, y, z) in outsideCubes if
            0 <= x < width
        and 0 <= y < depth
        and 0 <= z < height
    )

    return outsideCubes

def get_visible_cubes(opaqueCubes, outsideCubes, width, depth, height):
    # opaqueCubes: set-like with (x, y, z) of each opaque cube in the object
    # outsideCubes: set-like with (x, y, z) of each transparent cube outside
    #               the object
    # width, depth, height: size of object in cubes
    # generate: (x, y, z) of each (opaque) visible cube

    # algorithm: an opaque cube is visible if:
    #   - it is an orthogonal neighbour of an outside cube
    #   and/or
    #   - it is at the face (or edge or corner) of the space in which the
    #     object is

    for (x, y, z) in opaqueCubes:
        neighbours = frozenset((
            (x - 1, y,     z    ),
            (x + 1, y,     z    ),
            (x,     y - 1, z    ),
            (x,     y + 1, z    ),
            (x,     y,     z - 1),
            (x,     y,     z + 1),
        ))
        if (
               min(x, y, z) == 0
            or x in (0, width  - 1)
            or y in (0, depth  - 1)
            or z in (0, height - 1)
            or neighbours & outsideCubes
        ):
            yield (x, y, z)

def get_cuboid_volume(x, y, z, width, depth, height, cubes):
    # x, y, z: cuboid start coordinates
    # width, depth, height: cuboid size
    # cubes: opaque cubes:       {(x, y, z): colourIndex, ...}
    # return: volume of cuboid in cubes, excluding "don't care" colours

    volume = 0
    for x2 in range(x, x + width):
        for y2 in range(y, y + depth):
            for z2 in range(z, z + height):
                # if not in cubes dict, it was in freed cubes dict
                if cubes.get(
                    (x2, y2, z2), TRANSPARENT_COLOUR
                ) not in (DONT_CARE_COLOUR, TRANSPARENT_COLOUR):
                    volume += 1
    return volume

def get_largest_solid_cuboid_here(x, y, z, cubes, freedCubes, volumeLimit):
    # find the largest unassigned opaque one-colour cuboid starting from the
    # specified location
    # cubes:       {(x, y, z): colourIndex, ...}
    # freedCubes:  {(x, y, z): colourIndex, ...}
    # volumeLimit: don't bother searching for cuboids larger than this
    #              (speed optimisation; 0=no limit)
    # return:      (width, depth, height) of cuboid

    totalWidth  = max(c[0] for c in cubes) + 1
    totalDepth  = max(c[1] for c in cubes) + 1
    totalHeight = max(c[2] for c in cubes) + 1
    startColour = cubes.get((x, y, z), freedCubes.get((x, y, z)))

    if startColour in (DONT_CARE_COLOUR, TRANSPARENT_COLOUR):
        raise ValueError

    largestVolume = 0

    for height in range(1, totalHeight - z + 1):
        for depth in range(1, totalDepth - y + 1):
            for width in range(1, totalWidth - x + 1):
                if volumeLimit == 0 or largestVolume < volumeLimit:
                    # excluding "don't care" colours; 0 = not solid
                    volume = 0
                    for z2 in range(z, z + height):
                        for y2 in range(y, y + depth):
                            for x2 in range(x, x + width):
                                thisColour = cubes.get(
                                    (x2, y2, z2),
                                    freedCubes.get((x2, y2, z2),
                                        TRANSPARENT_COLOUR
                                    )
                                )
                                if (
                                    thisColour == startColour
                                    and (x2, y2, z2) in cubes
                                ):
                                    volume += 1
                                elif thisColour in (
                                    startColour, DONT_CARE_COLOUR
                                ):
                                    pass
                                else:
                                    # cuboid is not solid
                                    volume = 0
                                    break
                            if volume == 0:
                                break
                        if volume == 0:
                            break
                    if volume > largestVolume:
                        largestVolume = volume
                        bestWidth  = width
                        bestDepth  = depth
                        bestHeight = height

    if largestVolume == 0:
        raise ValueError

    return (bestWidth, bestDepth, bestHeight)

def get_largest_solid_cuboid(cubes, freedCubes, volumeLimit):
    # find the largest unassigned opaque one-colour cuboid anywhere
    # cubes:       opaque cubes:       {(x, y, z): colourIndex, ...}
    # freedCubes:  freed opaque cubes: {(x, y, z): colourIndex, ...}
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
                thisColour = cubes.get((x, y, z), TRANSPARENT_COLOUR)
                if thisColour not in (DONT_CARE_COLOUR, TRANSPARENT_COLOUR):
                    (width, depth, height) = get_largest_solid_cuboid_here(
                        x, y, z, cubes, freedCubes, volumeLimit
                    )
                    volume = get_cuboid_volume(
                        x, y, z, width, depth, height, cubes
                    )
                    if volume > largestVolume:
                        largestVolume = volume
                        bestX = x
                        bestY = y
                        bestZ = z

    if largestVolume == 0:
        raise ValueError

    return (bestX, bestY, bestZ)

def cubes_to_cuboids(cubes, cubeOverlap):
    # combine unit cubes into larger rectangular cuboids
    # cubes: opaque cubes: {(x, y, z): colourIndex, ...}; modified in-place
    # cubeOverlap: int
    # generate: (x, y, z, width, depth, height, colourIndex) per call

    # largest cuboid found so far (0=none)
    volumeLimit = 0

    # visible (opaque) cubes freed; may be overlapped with the same colour
    # or not; only if cubeOverlap=2; {(x, y, z): colourIndex, ...}
    freedCubes = {}

    while True:
        # find the largest unassigned opaque one-colour cuboid
        (x, y, z) = get_largest_solid_cuboid(cubes, freedCubes, volumeLimit)
        (width, depth, height) = get_largest_solid_cuboid_here(
            x, y, z, cubes, freedCubes, volumeLimit
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
                    if cubeOverlap == 0 or (
                        cubeOverlap == 1
                        and cubes[(x2, y2, z2)] != DONT_CARE_COLOUR
                    ):
                        cubes.pop((x2, y2, z2))
                    elif cubeOverlap == 2 and (x2, y2, z2) in cubes:
                        freedCubes[(x2, y2, z2)] = cubes[(x2, y2, z2)]
                        cubes.pop((x2, y2, z2))

        # exit if no colours besides "don't care"
        if not set(cubes.values()) - set((DONT_CARE_COLOUR,)):
            break

def cubes_to_cuboids_unoptimised(cubes):
    # like cubes_to_cuboids(), but each cuboid is just a cube
    # cubes:    opaque cubes: {(x, y, z): colourIndex, ...}
    # generate: (x, y, z, width, depth, height, colourIndex) per call

    for (x, y, z) in cubes:
        yield (x, y, z, 1, 1, 1, cubes[(x, y, z)])

def print_colour_definitions(indexesUsed, palette):
    # indexesUsed: distinct opaque colour indexes used by object data
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
    if not 2 <= len(sys.argv) <= 5:
        sys.exit(
            "Convert a voxel file into an OpenSCAD file. "
            "Arguments: inputFile combineColours optimisationLevel "
            "cubeOverlap. "
            "combineColours: 0 or 1, default=0. "
            "optimisationLevel: 0-2, default=2. "
            "cubeOverlap: 0-2, default=2. "
            "See README.md for details."
        )
    inputFile = sys.argv[1]
    if not os.path.isfile(inputFile):
        sys.exit("Input file not found.")

    if len(sys.argv) >= 3:
        combineColours = bool(decode_int(sys.argv[2], 0, 1, "combineColours"))
    else:
        combineColours = False
    if len(sys.argv) >= 4:
        optimisationLevel = decode_int(sys.argv[3], 0, 2, "optimisationLevel")
    else:
        optimisationLevel = 2
    if len(sys.argv) >= 5:
        cubeOverlap = decode_int(sys.argv[4], 0, 2, "cubeOverlap")
    else:
        cubeOverlap = 2

    (width, depth, height, palette) = get_object_properties(inputFile)

    # get object data (colours of building blocks)
    objData = list(get_object_data(inputFile))
    print("// model read:", os.path.basename(inputFile))
    if max(len(l) for l in objData) > width:
        sys.exit(f"Can't have more than {width} characters after '|'.")
    if len(objData) != height * depth:
        sys.exit(f"Must have {height*depth} lines starting with '|'.")
    if max((max(l) if l else 0) for l in objData) > len(palette):
        sys.exit(
            f"Can't have colour numbers greater than {len(palette)}."
        )

    print(f"// size in cubes: {width=}, {depth=}, {height=}")

    # wrap each layer in its own tuple to get a tuple of tuples of tuples
    objData = tuple(
        tuple(objData[i:i+depth]) for i in range(0, height * depth, depth)
    )

    # convert object data into a dict
    opaqueCubes = dict()  # {(x, y, z): colour, ...}
    for (z, layer) in enumerate(objData):
        for (y, row) in enumerate(layer):
            for (x, colour) in enumerate(row):
                if colour != TRANSPARENT_COLOUR:
                    opaqueCubes[(x, y, z)] = colour
    del objData

    # mirror Y coordinates
    opaqueCubes = dict(
        ((x, depth - 1 - y, z), opaqueCubes[(x, y, z)])
        for (x, y, z) in opaqueCubes
    )

    print(
        "// make all opaque colours black:",
        ("yes" if combineColours else "no")
    )
    if combineColours:
        opaqueCubes = dict(
            (c, (
                opaqueCubes[c]
                if opaqueCubes[c] in (DONT_CARE_COLOUR, TRANSPARENT_COLOUR)
                else COMBINED_COLOUR
            )) for c in opaqueCubes
        )
    print(
        "// distinct colours (incl. transparent):",
        len(set(opaqueCubes.values()))
    )
    print(
        "// is the model left-right symmetric:",
        ("yes" if have_cubes_x_symmetry(opaqueCubes, width) else "no")
    )

    # there can be four kinds of cubes in the object:
    # - outside (always transparent)
    # - surface (visible, always opaque, separates outside from hidden)
    # - transparent hidden (below surface)
    # - opaque hidden (below surface)

    # get coordinates of (transparent) cubes outside the object
    outsideCubes = get_outside_cubes(opaqueCubes, width, depth, height)

    # get coordinates of (opaque) visible cubes
    visibleCubes = set(get_visible_cubes(
        opaqueCubes, outsideCubes, width, depth, height
    ))

    # get coordinates of (opaque or transparent) hidden cubes
    hiddenCubes = set()
    for z in range(height):
        for y in range(depth):
            for x in range(width):
                if (x, y, z) not in outsideCubes and (x, y, z) not in visibleCubes:
                    hiddenCubes.add((x, y, z))
    del outsideCubes
    hiddenOpaqueCubeCnt = len(opaqueCubes) - len(visibleCubes)

    print("// opaque cubes defined:", len(opaqueCubes))
    print("// opaque cubes visible:", len(visibleCubes))
    print("// opaque cubes hidden:",  hiddenOpaqueCubeCnt)
    print(
        "// transparent cubes hidden:", len(hiddenCubes) - hiddenOpaqueCubeCnt
    )

    startTime = time.time()
    if optimisationLevel == 2:
        print("// optimisation level: 2 (full)")
        print(
            "// allow overlapping cubes:", {
                0: "no",
                1: "hidden only",
                2: "hidden&visible",
            }[cubeOverlap]
        )
        # mark hidden cubes as the "don't care" colour
        for (x, y, z) in hiddenCubes:
            opaqueCubes[(x, y, z)] = DONT_CARE_COLOUR
        cuboids = list(cubes_to_cuboids(opaqueCubes, cubeOverlap))
    else:
        if optimisationLevel == 1:
            print("// optimisation level: 1 (only delete hidden cubes)")
            for (x, y, z) in hiddenCubes:
                del opaqueCubes[(x, y, z)]
        else:
            print("// optimisation level: 0 (none)")
        cuboids = list(cubes_to_cuboids_unoptimised(opaqueCubes))
    print(
        f"// optimised model to {len(cuboids)} cuboids in "
        f"{time.time()-startTime:.1f} seconds"
    )
    print("// volume of largest cuboid: {} cubes".format(
        max(c[3] * c[4] * c[5] for c in cuboids)
    ))
    print("// total cuboid volume: {} cubes".format(
        sum(c[3] * c[4] * c[5] for c in cuboids)
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
        "// is the set of optimised cuboids left-right symmetric:",
        ("yes" if hasCuboidXSymmetry else "no")
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
