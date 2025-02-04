# isometry
Draw an isometric image consisting of cubes according to instructions in a text file. Requires the [Pillow](https://python-pillow.org) module.

Table of contents:
* [Axes](#axes)
* [Command line arguments](#command-line-arguments)
* [Input file](#input-file)
* [More settings](#more-settings)
* [Other files](#other-files)

## Axes
* X+ = right
* Y+ = towards viewer
* Z+ = up

## Command line arguments
* input file (required, see below)
* output file (required, PNG, RGB without alpha)
* axes to reverse (optional; a string consisting of one or more of `X`, `Y` and `Z`; case insensitive)

## Input file
* Encoding: ASCII.
* Case insensitive.
* Empty lines are ignored.
* Specify width: `W` immediately followed by an integer.
* Specify depth: `D` immediately followed by an integer.
* Specify height: `H` immediately followed by an integer.
* Other lines:
  * Each group of *depth* lines describes a horizontal layer.
  * There are *height* &times; *depth* lines in total.
  * Bottom layer first.
  * Rear line first within each layer.
  * Each text line starts with `|`.
  * `|` is followed by up to *width* characters, excluding newline.
  * After `|`, spaces denote "no cube" and any other character denotes "cube".
  * Missing trailing spaces are assumed to be "no cube".

## More settings
The constants at the beginning of the program can be edited. You can change:
* the dimensions of the building blocks (only the combinations corresponding to `minicube-*.png` files are allowed; see below)
* the margins
* the background color

## Other files
* `minicube-WxHxD.png`: the cubes used as building blocks; `W`/`H`/`D` are width/height/depth in pixels
