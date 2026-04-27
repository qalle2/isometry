# Convert a voxel file into an OpenSCAD file.

# Litten (combineColours=0; different values for removeHidden, combineCubes and
# allowOverlap):
#     0, 0, any: cuboids=562, totalVolume=562
#     1, 0, any: cuboids=340, totalVolume=340
#     1, 1, 0:   cuboids=122, totalVolume=340
#     1, 1, 1:   cuboids=119, totalVolume=357
#     0, 1, 0:   cuboids=105, totalVolume=535
#     0, 1, 1:   cuboids= 83, totalVolume=879

import os, sys, time
from itertools import product

# --- the user may change these -----------------------------------------------

# how many spaces of indentation
INDENT = 4

# colour indexes in input file to (red, green, blue); 0-255 each;
# index 0 is transparent; palette may be overridden by input file
DEFAULT_PALETTE = {
    1: ( 85,  85,  85),  # dark grey
    2: (255,   0,   0),  # red
    3: (255, 128,   0),  # orange
    4: (255, 255,   0),  # yellow
    5: (  0, 255,   0),  # green
    6: (  0, 255, 255),  # cyan
    7: (  0,   0, 255),  # blue
    8: (255,   0, 255),  # magenta
    9: (255, 255, 255),  # white
}

HELP_TEXT = """\
Convert a voxel file into an OpenSCAD file.
Arguments: inputFile combineColours removeHidden combineCubes allowOverlap
The 2nd-5th arguments are optional and can be 0 (no) or 1 (yes). Their defaults
are 0, 0, 1, 1.
See README.md for details.\
"""

# --- the user should not change these ----------------------------------------

# index of the "don't care" colour (optimised to transparent or any colour)
DONT_CARE_COLOUR = -1
# index of transparent colour
TRANSPARENT_COLOUR = 0
# what colour index to combine opaque colours into
COMBINED_COLOUR = 1

# --- helper functions --------------------------------------------------------

def decode_int(stri, min_, max_, descr):
    # decode a string to an integer

    try:
        i = int(stri, 10)
        if not min_ <= i <= max_:
            raise ValueError
    except ValueError:
        sys.exit(f"{descr} must be an integer between {min_} and {max_}.")
    return i

def decode_bool(stri, descr):
    # decode "0" to False and "1" to True

    return bool(decode_int(stri, 0, 1, descr))

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

def parse_arguments():
    # parse command line arguments

    if not 2 <= len(sys.argv) <= 6:
        sys.exit(HELP_TEXT)
    inputFile = sys.argv[1]
    if not os.path.isfile(inputFile):
        sys.exit("Input file not found.")

    if len(sys.argv) >= 3:
        combineColours = decode_bool(sys.argv[2], "combineColours")
    else:
        combineColours = False

    if len(sys.argv) >= 4:
        removeHidden = decode_bool(sys.argv[3], "removeHidden")
    else:
        removeHidden = False

    if len(sys.argv) >= 5:
        combineCubes = decode_bool(sys.argv[4], "combineCubes")
    else:
        combineCubes = True

    if len(sys.argv) >= 6:
        allowOverlap = decode_bool(sys.argv[5], "allowOverlap")
    else:
        allowOverlap = True

    return (
        inputFile, combineColours, removeHidden, combineCubes, allowOverlap
    )

def get_object_properties(inputFile):
    # read properties of object from input file;
    # return (width, depth, height, palette);
    #     the first 3 are in cubes;
    #     palette: {1: (R,G,B), ..., 9: (R,G,B)}

    width = depth = height = None
    palette = DEFAULT_PALETTE.copy()

    for line in get_lines(inputFile):
        line = line.upper()
        if line.startswith("W"):
            width = decode_int(line[1:], 1, 256, "object width")
        elif line.startswith("D"):
            depth = decode_int(line[1:], 1, 256, "object depth")
        elif line.startswith("H"):
            height = decode_int(line[1:], 1, 256, "object height")
        elif line.startswith("C"):
            index_ = decode_int(line[1], 0, 9, "colour index")
            if index_ > 0:
                palette[index_] = decode_colour_code(line[2:])
        elif (
                not line.startswith("B")  # legacy command for C0...
            and not line.startswith("|")
            and not line.startswith("#")
        ):
            sys.exit("Syntax error: " + line)

    if width is None or depth is None or height is None:
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
    # return: set with (x, y, z) of each (transparent) cube outside the object

    # initialise with all transparent face/edge/corner cubes
    # (at least one of X, Y, Z is minimum or maximum)
    outsideCubes  = set(product((0, width - 1), range(depth), range(height)))
    outsideCubes.update(product(range(width), (0, depth - 1), range(height)))
    outsideCubes.update(product(range(width), range(depth), (0, height - 1)))

    # remove opaque cubes
    outsideCubes.difference_update(opaqueCubes)

    # use orthogonal flood fill to select adjacent transparent cubes
    while True:
        newOutsideCubes = set()
        # for each known outside cube, add transparent orthogonal neighbours
        for (x, y, z) in outsideCubes:
            for offset in (-1, 1):
                neighX = x + offset
                neighY = y + offset
                neighZ = z + offset
                if 0 <= neighX < width and (neighX, y, z) not in opaqueCubes:
                    newOutsideCubes.add((neighX, y, z))
                if 0 <= neighY < depth and (x, neighY, z) not in opaqueCubes:
                    newOutsideCubes.add((x, neighY, z))
                if 0 <= neighZ < height and (x, y, neighZ) not in opaqueCubes:
                    newOutsideCubes.add((x, y, neighZ))
        #
        oldCnt = len(outsideCubes)
        outsideCubes.update(newOutsideCubes)
        if len(outsideCubes) == oldCnt:
            break

    return outsideCubes

def get_visible_cubes(opaqueCubes, outsideCubes, width, depth, height):
    # opaqueCubes:  set-like with (x, y, z) of each opaque cube in the object
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
               x in (0, width  - 1)
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

def cubes_to_cuboids(cubes, allowOverlap):
    # combine unit cubes into larger rectangular cuboids
    # cubes: opaque cubes: {(x, y, z): colourIndex, ...}; modified in-place
    # allowOverlap: bool
    # generate: (x, y, z, width, depth, height, colourIndex) per call

    # largest cuboid found so far (0=none)
    volumeLimit = 0

    # visible (opaque) cubes freed; may be overlapped with the same colour
    # or not; only if allowOverlap; {(x, y, z): colourIndex, ...}
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
                    if not allowOverlap or (x2, y2, z2) in cubes:
                        if allowOverlap:
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
    # print colour definitions in OpenSCAD format
    # indexesUsed: distinct opaque colour indexes used by object data
    # palette: {1: (R,G,B), ..., 9: (R,G,B)}

    for ind in sorted(palette):
        if ind in indexesUsed:
            (red, green, blue) = palette[ind]
            print(
                f"COL{ind} = ["
                + ",".join(format(c / 255, ".2f") for c in (red, green, blue))
                + "];"
            )

def print_cuboid_data(cuboids, totalWidth, totalDepth, totalHeight):
    # print cuboid definitions in OpenSCAD format
    # cuboids: [(x, y, z, width, depth, height, colourIndex), ...]
    # X coordinates have already been centred around 0

    # note: the width:depth:height ratio of Nanoblocks seems to be 3:3:4 but we
    # use 1:1:1 anyway

    # centre cuboids around Y=0 and Z=0
    yOffset = -(totalDepth  - 1) / 2
    zOffset = -(totalHeight - 1) / 2
    print(f"translate([0,{yOffset},{zOffset}]) {{")

    # sort
    cuboids.sort(key=lambda c: c[0])  # by X
    cuboids.sort(key=lambda c: c[1])  # by Y
    cuboids.sort(key=lambda c: c[2])  # by Z
    cuboids.sort(key=lambda c: c[6])  # by colour

    prevColour = None

    for (x, y, z, w, d, h, colourIndex) in cuboids:
        if prevColour is None or colourIndex != prevColour:
            if prevColour is not None:
                print(f"{INDENT*' '}}}")  # end previous color()
            # start new color()
            print(f"{INDENT*' '}color(COL{colourIndex}) {{")
            prevColour = colourIndex

        sizeArgs = []
        if w > 1 or d > 1 or h > 1:
            sizeArgs.append(f"{w:2}")
        if d > 1 or h > 1:
            sizeArgs.append(f"{d:2}")
        if h > 1:
            sizeArgs.append(f"{h:2}")
        sizeArg = ",".join(sizeArgs)
        print(
            f"{2*INDENT*' '}translate([{x:5},{y:4},{z:4}]) cuboid({sizeArg});"
        )

    if prevColour is not None:
        print(f"{INDENT*' '}}}")  # end the last color()
    print("}")  # end translate()

def main():
    (
        inputFile, combineColours, removeHidden, combineCubes, allowOverlap
    ) = parse_arguments()

    (width, depth, height, palette) = get_object_properties(inputFile)

    # get object data (colour indexes of all cubes, transparent or opaque)
    objData = list(get_object_data(inputFile))
    print("// model read:", os.path.basename(inputFile))
    if max(len(l) for l in objData) > width:
        sys.exit(f"Can't have more than {width} characters after '|'.")
    if len(objData) != height * depth:
        sys.exit(f"Must have {height*depth} lines starting with '|'.")

    print(f"// size in cubes: {width=}, {depth=}, {height=}")

    # convert object data into a dict
    opaqueCubes = dict()  # {(x, y, z): colour, ...}
    for z in range(height):
        for y in range(depth):
            row = objData[z*depth+y]
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
        "// make all opaque colours the same colour:",
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
        "// model has left-right symmetry:",
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

    print("// defined opaque cubes:", len(opaqueCubes))
    print("// visible opaque cubes:", len(visibleCubes))
    print("// hidden opaque cubes:",  hiddenOpaqueCubeCnt)
    print(
        "// hidden transparent cubes:", len(hiddenCubes) - hiddenOpaqueCubeCnt
    )

    startTime = time.time()

    print("// remove hidden cubes:", ("yes" if removeHidden else "no"))
    print("// combine cubes into cuboids:", ("yes" if combineCubes else "no"))

    if removeHidden:
        # delete hidden cubes
        opaqueCubes = dict(
            (pos, opaqueCubes[pos])
            for pos in set(opaqueCubes) - hiddenCubes
        )
    elif combineCubes:
        # mark hidden cubes as the "don't care" colour
        opaqueCubes = dict(
            (
                pos,
                (DONT_CARE_COLOUR if pos in hiddenCubes else opaqueCubes[pos])
            ) for pos in opaqueCubes
        )

    if not combineCubes:
        # each cube becomes a cuboid
        cuboids = list(cubes_to_cuboids_unoptimised(opaqueCubes))
    else:
        print("// allow overlapping cubes:", ("yes" if allowOverlap else "no"))
        cuboids = list(cubes_to_cuboids(opaqueCubes, allowOverlap))

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
        "// set of optimised cuboids has left-right symmetry:",
        ("yes" if hasCuboidXSymmetry else "no")
    )
    print()

    print("// colours")
    print_colour_definitions(frozenset(c[6] for c in cuboids), palette)
    print()
    print("module cuboid(w=1, d=1, h=1) {")
    print(f"{INDENT*' '}cube([w,d,h], center=true);")
    print("}")
    print()
    print_cuboid_data(cuboids, width, depth, height)

main()
