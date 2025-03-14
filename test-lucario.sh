# Lucario from all directions (except right because of symmetry)

rm -f test-out/*.png

# from bottom
python3 isometry.py test-in/lucario.txt test-out/a.png  12 0 0

# from between bottom and same level
python3 isometry.py test-in/lucario.txt test-out/b0.png 10 0 0
python3 isometry.py test-in/lucario.txt test-out/b1.png 10 0 1
python3 isometry.py test-in/lucario.txt test-out/b2.png 10 0 2
python3 isometry.py test-in/lucario.txt test-out/b3.png 10 0 3
python3 isometry.py test-in/lucario.txt test-out/b4.png 10 0 4
python3 isometry.py test-in/lucario.txt test-out/b5.png 10 0 5
python3 isometry.py test-in/lucario.txt test-out/b6.png 10 0 6
python3 isometry.py test-in/lucario.txt test-out/b7.png 10 0 7
python3 isometry.py test-in/lucario.txt test-out/b8.png 10 0 8

# from the same level
python3 isometry.py test-in/lucario.txt test-out/c0.png 0 0 0
python3 isometry.py test-in/lucario.txt test-out/c1.png 0 0 1
python3 isometry.py test-in/lucario.txt test-out/c2.png 0 0 2
python3 isometry.py test-in/lucario.txt test-out/c3.png 0 0 3
python3 isometry.py test-in/lucario.txt test-out/c4.png 0 0 4
python3 isometry.py test-in/lucario.txt test-out/c5.png 0 0 5
python3 isometry.py test-in/lucario.txt test-out/c6.png 0 0 6
python3 isometry.py test-in/lucario.txt test-out/c7.png 0 0 7
python3 isometry.py test-in/lucario.txt test-out/c8.png 0 0 8

# from between same level and top
python3 isometry.py test-in/lucario.txt test-out/d0.png 2 0 0
python3 isometry.py test-in/lucario.txt test-out/d1.png 2 0 1
python3 isometry.py test-in/lucario.txt test-out/d2.png 2 0 2
python3 isometry.py test-in/lucario.txt test-out/d3.png 2 0 3
python3 isometry.py test-in/lucario.txt test-out/d4.png 2 0 4
python3 isometry.py test-in/lucario.txt test-out/d5.png 2 0 5
python3 isometry.py test-in/lucario.txt test-out/d6.png 2 0 6
python3 isometry.py test-in/lucario.txt test-out/d7.png 2 0 7
python3 isometry.py test-in/lucario.txt test-out/d8.png 2 0 8

# from top
python3 isometry.py test-in/lucario.txt test-out/e.png  4 8 0
