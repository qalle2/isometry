# has left-right symmetry

rm -f test-out/*.png

# from the same level
python3 voxel2png.py test-in/cube6x5x4.txt test-out/a0.png 0 0 0
python3 voxel2png.py test-in/cube6x5x4.txt test-out/a1.png 0 0 1
python3 voxel2png.py test-in/cube6x5x4.txt test-out/a2.png 0 0 2
python3 voxel2png.py test-in/cube6x5x4.txt test-out/a3.png 0 0 3
python3 voxel2png.py test-in/cube6x5x4.txt test-out/a4.png 0 0 4
python3 voxel2png.py test-in/cube6x5x4.txt test-out/a5.png 0 0 5
python3 voxel2png.py test-in/cube6x5x4.txt test-out/a6.png 0 0 6
python3 voxel2png.py test-in/cube6x5x4.txt test-out/a7.png 0 0 7
python3 voxel2png.py test-in/cube6x5x4.txt test-out/a8.png 0 0 8

# from between same level and top
python3 voxel2png.py test-in/cube6x5x4.txt test-out/b0.png 2 0 0
python3 voxel2png.py test-in/cube6x5x4.txt test-out/b1.png 2 0 1
python3 voxel2png.py test-in/cube6x5x4.txt test-out/b2.png 2 0 2
python3 voxel2png.py test-in/cube6x5x4.txt test-out/b3.png 2 0 3
python3 voxel2png.py test-in/cube6x5x4.txt test-out/b4.png 2 0 4
python3 voxel2png.py test-in/cube6x5x4.txt test-out/b5.png 2 0 5
python3 voxel2png.py test-in/cube6x5x4.txt test-out/b6.png 2 0 6
python3 voxel2png.py test-in/cube6x5x4.txt test-out/b7.png 2 0 7
python3 voxel2png.py test-in/cube6x5x4.txt test-out/b8.png 2 0 8
