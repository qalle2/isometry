# miscellaneous tests

rm -f test-out/*.png

echo "== These should not cause errors =="

python3 isometry.py test-in/axes.txt test-out/axes-1a.png 21  0  0 0 21
python3 isometry.py test-in/axes.txt test-out/axes-1b.png 19  8  0 0 21
python3 isometry.py test-in/axes.txt test-out/axes-1c.png 15 15  0 0 21
python3 isometry.py test-in/axes.txt test-out/axes-2a.png 21  0 16 0 16
python3 isometry.py test-in/axes.txt test-out/axes-2c.png 15 15  8 8 16

python3 isometry.py test-in/cube1x1x1.txt test-out/cube1x1x1-1.png 21  0 16 0 16
python3 isometry.py test-in/cube1x1x1.txt test-out/cube1x1x1-2.png 15 15  8 8 16

python3 isometry.py test-in/cube5x5x5.txt test-out/cube5x5x5-1.png 21  0 16 0 16
python3 isometry.py test-in/cube5x5x5.txt test-out/cube5x5x5-2.png 15 15  8 8 16

python3 isometry.py test-in/cube6x5x4.txt test-out/cube6x5x4-1a.png 21  0  0 0 21
python3 isometry.py test-in/cube6x5x4.txt test-out/cube6x5x4-1b.png 19  8  0 0 21
python3 isometry.py test-in/cube6x5x4.txt test-out/cube6x5x4-1c.png 15 15  0 0 21
python3 isometry.py test-in/cube6x5x4.txt test-out/cube6x5x4-2a.png 21  0 16 0 16
python3 isometry.py test-in/cube6x5x4.txt test-out/cube6x5x4-2c.png 15 15  8 8 16

python3 isometry.py test-in/cubechecker.txt test-out/cubechecker1.png 21  0 16 0 16
python3 isometry.py test-in/cubechecker.txt test-out/cubechecker2.png 15 15  8 8 16

python3 isometry.py test-in/cubesparse.txt test-out/cubesparse1.png 21  0 16 0 16
python3 isometry.py test-in/cubesparse.txt test-out/cubesparse2.png 15 15  8 8 16

python3 isometry.py test-in/octahedron1.txt test-out/octahedron1-1.png 21  0 16 0 16
python3 isometry.py test-in/octahedron1.txt test-out/octahedron1-2.png 15 15  8 8 16

python3 isometry.py test-in/octahedron2.txt test-out/octahedron2-1.png 21  0 16 0 16
python3 isometry.py test-in/octahedron2.txt test-out/octahedron2-2.png 15 15  8 8 16

echo

echo "== These should cause five distinct errors =="
python3 isometry.py
python3 isometry.py test-in/axes.txt    test-out/axes-t1a.png  0  0  0  0  0
python3 isometry.py test-in/axes.txt    test-out/axes-t1a.png 99 99 99 99 99
python3 isometry.py test-in/nonexistent test-out/axes-t1a.png 21  0  0 0  21
python3 isometry.py test-in/axes.txt    test-out/axes-t1a.png 21  0  0 0  21
echo
