# Eevee from all directions

rm -f test-out/*.png

python3 isometry.py test-in/eevee.txt test-out/b1.png 1 17  0 17
python3 isometry.py test-in/eevee.txt test-out/b3.png 1 17  0 17 Z
python3 isometry.py test-in/eevee.txt test-out/b5.png 1 17  0 17 ZZ
python3 isometry.py test-in/eevee.txt test-out/b7.png 1 17  0 17 ZZZ
python3 isometry.py test-in/eevee.txt test-out/b2.png 2 12  0 17 Z
python3 isometry.py test-in/eevee.txt test-out/b4.png 2 12  0 17 ZZ
python3 isometry.py test-in/eevee.txt test-out/b6.png 2 12  0 17 ZZZ
python3 isometry.py test-in/eevee.txt test-out/b8.png 2 12  0 17

python3 isometry.py test-in/eevee.txt test-out/a1.png 1 17 12 12
python3 isometry.py test-in/eevee.txt test-out/a3.png 1 17 12 12 Z
python3 isometry.py test-in/eevee.txt test-out/a5.png 1 17 12 12 ZZ
python3 isometry.py test-in/eevee.txt test-out/a7.png 1 17 12 12 ZZZ
python3 isometry.py test-in/eevee.txt test-out/a2.png 2 15  8 16 Z
python3 isometry.py test-in/eevee.txt test-out/a4.png 2 15  8 16 ZZ
python3 isometry.py test-in/eevee.txt test-out/a6.png 2 15  8 16 ZZZ
python3 isometry.py test-in/eevee.txt test-out/a8.png 2 15  8 16

python3 isometry.py test-in/eevee.txt test-out/c1.png 1 17 12 12 ""  Z
python3 isometry.py test-in/eevee.txt test-out/c3.png 1 17 12 12 Z   Z
python3 isometry.py test-in/eevee.txt test-out/c5.png 1 17 12 12 ZZ  Z
python3 isometry.py test-in/eevee.txt test-out/c7.png 1 17 12 12 ZZZ Z
python3 isometry.py test-in/eevee.txt test-out/c2.png 2 15  8 16 Z   Z
python3 isometry.py test-in/eevee.txt test-out/c4.png 2 15  8 16 ZZ  Z
python3 isometry.py test-in/eevee.txt test-out/c6.png 2 15  8 16 ZZZ Z
python3 isometry.py test-in/eevee.txt test-out/c8.png 2 15  8 16 ""  Z
