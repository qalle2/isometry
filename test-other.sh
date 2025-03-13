# miscellaneous tests

rm -f test-out/*.png

echo "== These should not cause errors =="

python3 isometry.py test-in/cube1x1x1.txt test-out/cube1x1x1-1.png 0 2
python3 isometry.py test-in/cube1x1x1.txt test-out/cube1x1x1-2.png 2 2

python3 isometry.py test-in/cube5x5x5.txt test-out/cube5x5x5-1.png 0 2
python3 isometry.py test-in/cube5x5x5.txt test-out/cube5x5x5-2.png 2 2

python3 isometry.py test-in/cube6x5x4.txt test-out/cube6x5x4-1a.png 0 0
python3 isometry.py test-in/cube6x5x4.txt test-out/cube6x5x4-1b.png 1 0
python3 isometry.py test-in/cube6x5x4.txt test-out/cube6x5x4-1c.png 2 0
python3 isometry.py test-in/cube6x5x4.txt test-out/cube6x5x4-2a.png 0 2
python3 isometry.py test-in/cube6x5x4.txt test-out/cube6x5x4-2b.png 1 2
python3 isometry.py test-in/cube6x5x4.txt test-out/cube6x5x4-2c.png 2 2

python3 isometry.py test-in/cubechecker.txt test-out/cubechecker1.png 0 2
python3 isometry.py test-in/cubechecker.txt test-out/cubechecker2.png 2 2

python3 isometry.py test-in/cubesparse.txt test-out/cubesparse1.png 0 2
python3 isometry.py test-in/cubesparse.txt test-out/cubesparse2.png 2 2

python3 isometry.py test-in/octahedron1.txt test-out/octahedron1-1.png 0 2
python3 isometry.py test-in/octahedron1.txt test-out/octahedron1-2.png 2 2

python3 isometry.py test-in/octahedron2.txt test-out/octahedron2-1.png 0 2
python3 isometry.py test-in/octahedron2.txt test-out/octahedron2-2.png 2 2

echo

echo "== These should cause four distinct errors =="
python3 isometry.py
python3 isometry.py test-in/axes.txt    test-out/axes-1a.png 9 9
python3 isometry.py test-in/nonexistent test-out/axes-1a.png 0 0
python3 isometry.py test-in/axes.txt    test-out/axes-1a.png 0 0
echo
