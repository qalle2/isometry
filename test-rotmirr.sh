# rotation/mirroring test

rm -f test-out/*.png

python3 isometry.py test-in/pee.txt test-out/pee-aaa-orig.png 2 2

python3 isometry.py test-in/pee.txt test-out/pee-rx1.png 2 2 X
python3 isometry.py test-in/pee.txt test-out/pee-rx2.png 2 2 XX
python3 isometry.py test-in/pee.txt test-out/pee-rx3.png 2 2 XXX
python3 isometry.py test-in/pee.txt test-out/pee-ry1.png 2 2 Y
python3 isometry.py test-in/pee.txt test-out/pee-ry2.png 2 2 YY
python3 isometry.py test-in/pee.txt test-out/pee-ry3.png 2 2 YYY
python3 isometry.py test-in/pee.txt test-out/pee-rz1.png 2 2 Z
python3 isometry.py test-in/pee.txt test-out/pee-rz2.png 2 2 ZZ
python3 isometry.py test-in/pee.txt test-out/pee-rz3.png 2 2 ZZZ

python3 isometry.py test-in/pee.txt test-out/pee-mx.png 2 2 "" X
python3 isometry.py test-in/pee.txt test-out/pee-my.png 2 2 "" Y
python3 isometry.py test-in/pee.txt test-out/pee-mz.png 2 2 "" Z
