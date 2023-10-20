# isometry
Draw an isometric image consisting of cubes according to instructions in a text file.

## Command line arguments
* input file (see below)
* output file (PNG)

## Input file
* Encoding: ASCII.
* Case insensitive.
* Empty lines are ignored.
* Specify width:  `W` immediately followed by an integer.
* Specify length: `L` immediately followed by an integer.
* Specify height: `H` immediately followed by an integer.
* Other lines:
  * Each group of *length* lines describes a horizontal layer.
  * There are *height* &times; *length* lines in total.
  * Bottom layer first.
  * Rear line first within each layer.
  * Each text line starts with `|`.
  * `|` is followed by up to *width* characters, excluding newline.
  * After `|`, spaces denote "no cube" and any other character denotes "cube".
  * Missing trailing spaces are assumed to be "no cube".
