# Vaporeon from all directions

rm -f test-out/*.png

# from the same level

python3 isometry.py test-in/vaporeon.txt test-out/a00.png 0 0
python3 isometry.py test-in/vaporeon.txt test-out/a04.png 0 0 ZZZ
python3 isometry.py test-in/vaporeon.txt test-out/a08.png 0 0 ZZ
python3 isometry.py test-in/vaporeon.txt test-out/a12.png 0 0 Z

python3 isometry.py test-in/vaporeon.txt test-out/a01.png 1 0
python3 isometry.py test-in/vaporeon.txt test-out/a05.png 1 0 ZZZ
python3 isometry.py test-in/vaporeon.txt test-out/a09.png 1 0 ZZ
python3 isometry.py test-in/vaporeon.txt test-out/a13.png 1 0 Z

python3 isometry.py test-in/vaporeon.txt test-out/a02.png 2 0
python3 isometry.py test-in/vaporeon.txt test-out/a06.png 2 0 ZZZ
python3 isometry.py test-in/vaporeon.txt test-out/a10.png 2 0 ZZ
python3 isometry.py test-in/vaporeon.txt test-out/a14.png 2 0 Z

python3 isometry.py test-in/vaporeon.txt test-out/a03.png 3 0
python3 isometry.py test-in/vaporeon.txt test-out/a07.png 3 0 ZZZ
python3 isometry.py test-in/vaporeon.txt test-out/a11.png 3 0 ZZ
python3 isometry.py test-in/vaporeon.txt test-out/a15.png 3 0 Z

# from 45 degrees up

python3 isometry.py test-in/vaporeon.txt test-out/b00.png 0 2
python3 isometry.py test-in/vaporeon.txt test-out/b04.png 0 2 ZZZ
python3 isometry.py test-in/vaporeon.txt test-out/b08.png 0 2 ZZ
python3 isometry.py test-in/vaporeon.txt test-out/b12.png 0 2 Z

python3 isometry.py test-in/vaporeon.txt test-out/b01.png 1 2
python3 isometry.py test-in/vaporeon.txt test-out/b05.png 1 2 ZZZ
python3 isometry.py test-in/vaporeon.txt test-out/b09.png 1 2 ZZ
python3 isometry.py test-in/vaporeon.txt test-out/b13.png 1 2 Z

python3 isometry.py test-in/vaporeon.txt test-out/b02.png 2 2
python3 isometry.py test-in/vaporeon.txt test-out/b06.png 2 2 ZZZ
python3 isometry.py test-in/vaporeon.txt test-out/b10.png 2 2 ZZ
python3 isometry.py test-in/vaporeon.txt test-out/b14.png 2 2 Z

python3 isometry.py test-in/vaporeon.txt test-out/b03.png 3 2
python3 isometry.py test-in/vaporeon.txt test-out/b07.png 3 2 ZZZ
python3 isometry.py test-in/vaporeon.txt test-out/b11.png 3 2 ZZ
python3 isometry.py test-in/vaporeon.txt test-out/b15.png 3 2 Z
