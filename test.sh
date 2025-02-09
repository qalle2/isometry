rm -f test-out/*.png

python3 isometry.py test-in/axes.txt test-out/axes-norev-t1.png  1 16 9 16
python3 isometry.py test-in/axes.txt test-out/axes-norev-t2.png  2 15 8 17
python3 isometry.py test-in/axes.txt test-out/axes-revxyz-t1.png 1 16 9 16 "" XYZ
python3 isometry.py test-in/axes.txt test-out/axes-revxyz-t2.png 2 15 8 17 "" XYZ

python3 isometry.py test-in/cube1x1x1.txt test-out/cube1x1x1-t1.png 1 16 9 16
python3 isometry.py test-in/cube1x1x1.txt test-out/cube1x1x1-t2.png 2 15 8 17

python3 isometry.py test-in/cube5x5x5.txt test-out/cube5x5x5-t1.png 1 16 9 16
python3 isometry.py test-in/cube5x5x5.txt test-out/cube5x5x5-t2.png 2 15 8 17

python3 isometry.py test-in/cube6x5x4.txt test-out/cube6x5x4-t1.png 1 16 9 16
python3 isometry.py test-in/cube6x5x4.txt test-out/cube6x5x4-t2.png 2 15 8 17

python3 isometry.py test-in/cubechecker.txt test-out/cubechecker-t1.png 1 16 9 16
python3 isometry.py test-in/cubechecker.txt test-out/cubechecker-t2.png 2 15 8 17

python3 isometry.py test-in/cubesparse.txt test-out/cubesparse-t1.png 1 16 9 16
python3 isometry.py test-in/cubesparse.txt test-out/cubesparse-t2.png 2 15 8 17

python3 isometry.py test-in/eevee.txt test-out/eevee-norev-t1a.png 1 16 0 16
python3 isometry.py test-in/eevee.txt test-out/eevee-norev-t1b.png 1 16 7 16
python3 isometry.py test-in/eevee.txt test-out/eevee-norev-t1c.png 1 16 8 16
python3 isometry.py test-in/eevee.txt test-out/eevee-norev-t1d.png 1 16 9 16
python3 isometry.py test-in/eevee.txt test-out/eevee-norev-t2a.png 2 15 8 15
python3 isometry.py test-in/eevee.txt test-out/eevee-norev-t2b.png 2 15 8 16
python3 isometry.py test-in/eevee.txt test-out/eevee-norev-t2c.png 2 15 8 17
python3 isometry.py test-in/eevee.txt test-out/eevee-revy-t1.png   1 16 9 16 "" Y
python3 isometry.py test-in/eevee.txt test-out/eevee-revy-t2.png   2 15 8 17 "" Y
python3 isometry.py test-in/eevee.txt test-out/eevee-revz-t1.png   1 16 9 16 "" Z
python3 isometry.py test-in/eevee.txt test-out/eevee-revz-t2.png   2 15 8 17 "" Z
python3 isometry.py test-in/eevee.txt test-out/eevee-revyz-t1.png  1 16 9 16 "" YZ
python3 isometry.py test-in/eevee.txt test-out/eevee-revyz-t2.png  2 15 8 17 "" YZ

python3 isometry.py test-in/octahedron1.txt test-out/octahedron1-t1.png 1 16 9 16
python3 isometry.py test-in/octahedron1.txt test-out/octahedron1-t2.png 2 15 8 17

python3 isometry.py test-in/octahedron2.txt test-out/octahedron2-t1.png 1 16 9 16
python3 isometry.py test-in/octahedron2.txt test-out/octahedron2-t2.png 2 15 8 17
