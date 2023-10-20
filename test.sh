rm -f test-out/*.png
python3 isometry.py test-in/axes.txt        test-out/axes.png
python3 isometry.py test-in/cube1.txt       test-out/cube1.png
python3 isometry.py test-in/cube2.txt       test-out/cube2.png
python3 isometry.py test-in/cubehole.txt    test-out/cubehole.png
python3 isometry.py test-in/octahedron1.txt test-out/octahedron1.png
python3 isometry.py test-in/octahedron2.txt test-out/octahedron2.png
python3 isometry.py test-in/sphere.txt      test-out/sphere.png
