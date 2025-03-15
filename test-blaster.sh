# Blaster Master vehicle

rm -f test-out/*.png

# from bottom
python3 voxel2png.py test-in/blaster.txt test-out/a.png 12 0 0

# from the same level
python3 voxel2png.py test-in/blaster.txt test-out/c0.png  0 0  0
python3 voxel2png.py test-in/blaster.txt test-out/c1.png  0 0  1
python3 voxel2png.py test-in/blaster.txt test-out/c2.png  0 0  2
python3 voxel2png.py test-in/blaster.txt test-out/c3.png  0 0  3
python3 voxel2png.py test-in/blaster.txt test-out/c4.png  0 0  4
python3 voxel2png.py test-in/blaster.txt test-out/c5.png  0 0  5
python3 voxel2png.py test-in/blaster.txt test-out/c6.png  0 0  6
python3 voxel2png.py test-in/blaster.txt test-out/c7.png  0 0  7
python3 voxel2png.py test-in/blaster.txt test-out/c8.png  0 0  8
python3 voxel2png.py test-in/blaster.txt test-out/c9.png  0 0  9
python3 voxel2png.py test-in/blaster.txt test-out/c10.png 0 0 10
python3 voxel2png.py test-in/blaster.txt test-out/c11.png 0 0 11
python3 voxel2png.py test-in/blaster.txt test-out/c12.png 0 0 12
python3 voxel2png.py test-in/blaster.txt test-out/c13.png 0 0 13
python3 voxel2png.py test-in/blaster.txt test-out/c14.png 0 0 14
python3 voxel2png.py test-in/blaster.txt test-out/c15.png 0 0 15

# from top
python3 voxel2png.py test-in/blaster.txt test-out/e.png 4 8 0
