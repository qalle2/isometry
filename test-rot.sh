# test rotations with axes.txt

rm -f test-out/*.png

# no rotations
python3 isometry.py test-in/axes.txt test-out/0-0-0.png  0  0  0

# X rotations
python3 isometry.py test-in/axes.txt test-out/2-0-0.png  2  0  0
python3 isometry.py test-in/axes.txt test-out/4-0-0.png  4  0  0
python3 isometry.py test-in/axes.txt test-out/6-0-0.png  6  0  0
python3 isometry.py test-in/axes.txt test-out/8-0-0.png  8  0  0
python3 isometry.py test-in/axes.txt test-out/a-0-0.png 10  0  0
python3 isometry.py test-in/axes.txt test-out/c-0-0.png 12  0  0
python3 isometry.py test-in/axes.txt test-out/e-0-0.png 14  0  0

# Y rotations
python3 isometry.py test-in/axes.txt test-out/0-4-0.png  0  4  0
python3 isometry.py test-in/axes.txt test-out/0-8-0.png  0  8  0
python3 isometry.py test-in/axes.txt test-out/0-c-0.png  0 12  0

# Z rotations
python3 isometry.py test-in/axes.txt test-out/0-0-1.png  0  0  1
python3 isometry.py test-in/axes.txt test-out/0-0-2.png  0  0  2
python3 isometry.py test-in/axes.txt test-out/0-0-3.png  0  0  3
python3 isometry.py test-in/axes.txt test-out/0-0-4.png  0  0  4
python3 isometry.py test-in/axes.txt test-out/0-0-5.png  0  0  5
python3 isometry.py test-in/axes.txt test-out/0-0-6.png  0  0  6
python3 isometry.py test-in/axes.txt test-out/0-0-7.png  0  0  7
python3 isometry.py test-in/axes.txt test-out/0-0-8.png  0  0  8
python3 isometry.py test-in/axes.txt test-out/0-0-9.png  0  0  9
python3 isometry.py test-in/axes.txt test-out/0-0-a.png  0  0 10
python3 isometry.py test-in/axes.txt test-out/0-0-b.png  0  0 11
python3 isometry.py test-in/axes.txt test-out/0-0-c.png  0  0 12
python3 isometry.py test-in/axes.txt test-out/0-0-d.png  0  0 13
python3 isometry.py test-in/axes.txt test-out/0-0-e.png  0  0 14
python3 isometry.py test-in/axes.txt test-out/0-0-f.png  0  0 15
