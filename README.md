# isometry
Draw an isometric image consisting of building blocks (small cubes) according to instructions in a text file.
Requires the [Pillow](https://python-pillow.org) module.

Table of contents:
* [3D coordinates](#3d-coordinates)
* [Command line arguments](#command-line-arguments)
* [Input file](#input-file)
* [Colour numbers](#colour-numbers)
* [More settings](#more-settings)
* [Other files](#other-files)

## 3D coordinates
Two types of 3D coordinates are supported. The building blocks (small cubes) have `t1` or `t2` in their filenames accordingly.

### Type 1
* X+ = right
* Y+ = left towards viewer
* Z+ = up

```
  +---+    Z
 /   /|    |
+---+ +    +---X
|   |/    /
+---+    Y
```

### Type 2
* X+ = right and towards viewer
* Y+ = left and towards viewer
* Z+ = up

```
 / \     Z
|\ /|    |
| | |   / \
 \|/   Y   X
```

## Command line arguments
*inputFile outputFile 3dCoordinateType blockWidth blockDepth blockHeight axesToReverse*
* *inputFile*: file to read (describes the 3D object; see below)
* *outputFile*: image file to write (PNG, RGB without alpha)
* *3dCoordinateType*: 1 or 2 (see above)
* *blockWidth, blockDepth, blockHeight*: size of building blocks (small cubes; must match `block-*.png`)
* *axesToReverse*:
  * optional
  * lets you mirror the object around the planes `X=0`, `Y=0` and/or `Z=0` planes before rendering it
  * a string consisting of one or more of the characters `X`, `Y` and `Z`
  * case insensitive

All arguments except *axesToReverse* are required.

## Input file
* Encoding: ASCII.
* Case insensitive.
* Leading whitespace is ignored.
* Empty lines are ignored.
* Comments (lines that start with `#`) are ignored.
* Specify width: `W` immediately followed by an integer.
* Specify depth: `D` immediately followed by an integer.
* Specify height: `H` immediately followed by an integer.
* Specify background color: `B` immediately followed by 6 hexadecimal digits (`RRGGBB`, `000000` to `ffffff`).
* Other lines:
  * Each group of *depth* lines describes a horizontal layer.
  * There are *height* &times; *depth* lines in total.
  * Bottom layer first.
  * Rear line first within each layer.
  * Each text line starts with `|`.
  * `|` is followed by up to *width* spaces or digits, excluding newline.
  * After `|`, a space or `0` denotes "no block" and `1`&ndash;`9` denotes a block of that colour (see below).
  * Missing trailing spaces are assumed to be "no block".

## Colour numbers
* 0: none (transparent)
* 1: black
* 2: blue
* 3: yellow
* 4: white

## More settings
The constants at the beginning of the program can be edited. You can change:
* the margins
* the background colour

## Other files
* `block-tT-wW-dD-hH.png`: the building blocks (small cubes); `T`/`W`/`H`/`D` are 3D coordinate type, width, height and depth.
