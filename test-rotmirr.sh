# rotation/mirroring test

rm -f test-out/*.png

python3 isometry.py test-in/pee.txt test-out/pee-aaa-orig.png 2 15 8 16

python3 isometry.py test-in/pee.txt test-out/pee-rx1.png 2 15 8 16 X
python3 isometry.py test-in/pee.txt test-out/pee-rx2.png 2 15 8 16 XX
python3 isometry.py test-in/pee.txt test-out/pee-rx3.png 2 15 8 16 XXX
python3 isometry.py test-in/pee.txt test-out/pee-ry1.png 2 15 8 16 Y
python3 isometry.py test-in/pee.txt test-out/pee-ry2.png 2 15 8 16 YY
python3 isometry.py test-in/pee.txt test-out/pee-ry3.png 2 15 8 16 YYY
python3 isometry.py test-in/pee.txt test-out/pee-rz1.png 2 15 8 16 Z
python3 isometry.py test-in/pee.txt test-out/pee-rz2.png 2 15 8 16 ZZ
python3 isometry.py test-in/pee.txt test-out/pee-rz3.png 2 15 8 16 ZZZ

python3 isometry.py test-in/pee.txt test-out/pee-mx.png 2 15 8 16 "" X
python3 isometry.py test-in/pee.txt test-out/pee-my.png 2 15 8 16 "" Y
python3 isometry.py test-in/pee.txt test-out/pee-mz.png 2 15 8 16 "" Z
