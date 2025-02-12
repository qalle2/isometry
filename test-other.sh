# miscellaneous tests

rm -f test-out/*.png

python3 isometry.py test-in/axes.txt test-out/axes-t1a.png 1 17  0 17
python3 isometry.py test-in/axes.txt test-out/axes-t1b.png 1 17 12 12
python3 isometry.py test-in/axes.txt test-out/axes-t2a.png 2 12  0 17
python3 isometry.py test-in/axes.txt test-out/axes-t2b.png 2 15  8 16

python3 isometry.py test-in/cube1x1x1.txt test-out/cube1x1x1-t1.png 1 17 12 12
python3 isometry.py test-in/cube1x1x1.txt test-out/cube1x1x1-t2.png 2 15  8 17

python3 isometry.py test-in/cube5x5x5.txt test-out/cube5x5x5-t1.png 1 17 12 12
python3 isometry.py test-in/cube5x5x5.txt test-out/cube5x5x5-t2.png 2 15  8 17

python3 isometry.py test-in/cube6x5x4.txt test-out/cube6x5x4-t1.png 1 17 12 12
python3 isometry.py test-in/cube6x5x4.txt test-out/cube6x5x4-t2.png 2 15  8 17

python3 isometry.py test-in/cubechecker.txt test-out/cubechecker-t1.png 1 17 12 12
python3 isometry.py test-in/cubechecker.txt test-out/cubechecker-t2.png 2 15  8 17

python3 isometry.py test-in/cubesparse.txt test-out/cubesparse-t1.png 1 17 12 12
python3 isometry.py test-in/cubesparse.txt test-out/cubesparse-t2.png 2 15  8 17

python3 isometry.py test-in/octahedron1.txt test-out/octahedron1-t1.png 1 17 12 12
python3 isometry.py test-in/octahedron1.txt test-out/octahedron1-t2.png 2 15  8 17

python3 isometry.py test-in/octahedron2.txt test-out/octahedron2-t1.png 1 17 12 12
python3 isometry.py test-in/octahedron2.txt test-out/octahedron2-t2.png 2 15  8 17
