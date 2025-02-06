# isometry
Draw an isometric image consisting of cubes according to instructions in a text file. Requires the [Pillow](https://python-pillow.org) module.

Table of contents:
* [Axes](#axes)
* [Command line arguments](#command-line-arguments)
* [Input file](#input-file)
* [Colour numbers](#colour-numbers)
* [More settings](#more-settings)
* [Other files](#other-files)

## 3D coordinates
Two types of 3D coordinates are supported. The small cubes have `type1` or `type2` in their filenames accordingly.

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
* input file (required, see below)
* output file (required, PNG, RGB without alpha)
* axes to reverse (optional; a string consisting of one or more of `X`, `Y` and `Z`; case insensitive)

## Input file
* Encoding: ASCII.
* Case insensitive.
* Leading whitespace is ignored.
* Empty lines are ignored.
* Comments (lines that start with `#`) are ignored.
* Specify width: `W` immediately followed by an integer.
* Specify depth: `D` immediately followed by an integer.
* Specify height: `H` immediately followed by an integer.
* Other lines:
  * Each group of *depth* lines describes a horizontal layer.
  * There are *height* &times; *depth* lines in total.
  * Bottom layer first.
  * Rear line first within each layer.
  * Each text line starts with `|`.
  * `|` is followed by up to *width* spaces or digits, excluding newline.
  * After `|`, a space or `0` denotes "no cube" and `1`&ndash;`9` denotes a cube of that colour (see below).
  * Missing trailing spaces are assumed to be "no cube".

## Colour numbers
* 1: black
* 2: blue
* 3: yellow
* 4: white

## More settings
The constants at the beginning of the program can be edited. You can change:
* the dimensions of the building blocks (only the combinations corresponding to `minicube-*.png` files are allowed; see below)
* the margins
* the background colour

## Other files
* `minicube-tT-wW-dD-hH-cC.png`: the cubes used as building blocks; `T`/`W`/`H`/`D`/`C` are 3D coordinate type, width, height, depth and colour (see above).
