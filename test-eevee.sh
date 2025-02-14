# Eevee from all directions

rm -f test-out/*.png

python3 isometry.py test-in/eevee.txt test-out/b1.png 21  0  0  0 21
python3 isometry.py test-in/eevee.txt test-out/b3.png 21  0  0  0 21 Z
python3 isometry.py test-in/eevee.txt test-out/b5.png 21  0  0  0 21 ZZ
python3 isometry.py test-in/eevee.txt test-out/b7.png 21  0  0  0 21 ZZZ
python3 isometry.py test-in/eevee.txt test-out/b2.png 15 15  0  0 21 Z
python3 isometry.py test-in/eevee.txt test-out/b4.png 15 15  0  0 21 ZZ
python3 isometry.py test-in/eevee.txt test-out/b6.png 15 15  0  0 21 ZZZ
python3 isometry.py test-in/eevee.txt test-out/b8.png 15 15  0  0 21

python3 isometry.py test-in/eevee.txt test-out/a1.png 21  0 16  0 16
python3 isometry.py test-in/eevee.txt test-out/a3.png 21  0 16  0 16 Z
python3 isometry.py test-in/eevee.txt test-out/a5.png 21  0 16  0 16 ZZ
python3 isometry.py test-in/eevee.txt test-out/a7.png 21  0 16  0 16 ZZZ
python3 isometry.py test-in/eevee.txt test-out/a2.png 15 15  8  8 16 Z
python3 isometry.py test-in/eevee.txt test-out/a4.png 15 15  8  8 16 ZZ
python3 isometry.py test-in/eevee.txt test-out/a6.png 15 15  8  8 16 ZZZ
python3 isometry.py test-in/eevee.txt test-out/a8.png 15 15  8  8 16

python3 isometry.py test-in/eevee.txt test-out/c1.png 21  0 16  0 16 ""  Z
python3 isometry.py test-in/eevee.txt test-out/c3.png 21  0 16  0 16 Z   Z
python3 isometry.py test-in/eevee.txt test-out/c5.png 21  0 16  0 16 ZZ  Z
python3 isometry.py test-in/eevee.txt test-out/c7.png 21  0 16  0 16 ZZZ Z
python3 isometry.py test-in/eevee.txt test-out/c2.png 15 15  8  8 16 Z   Z
python3 isometry.py test-in/eevee.txt test-out/c4.png 15 15  8  8 16 ZZ  Z
python3 isometry.py test-in/eevee.txt test-out/c6.png 15 15  8  8 16 ZZZ Z
python3 isometry.py test-in/eevee.txt test-out/c8.png 15 15  8  8 16 ""  Z
