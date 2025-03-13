rm -f test-out/*.png

python3 isometry.py test-in/axes.txt test-out/a0.png 0 0
python3 isometry.py test-in/axes.txt test-out/a1.png 1 0
python3 isometry.py test-in/axes.txt test-out/a2.png 2 0
python3 isometry.py test-in/axes.txt test-out/a3.png 3 0
python3 isometry.py test-in/axes.txt test-out/b0.png 0 2
python3 isometry.py test-in/axes.txt test-out/b1.png 1 2
python3 isometry.py test-in/axes.txt test-out/b2.png 2 2
python3 isometry.py test-in/axes.txt test-out/b3.png 3 2
