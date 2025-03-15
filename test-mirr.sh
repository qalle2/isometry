# test mirroring with pee.txt

rm -f test-out/*.png

python3 voxel2png.py test-in/pee.txt test-out/mir-none.png 2 0 1
python3 voxel2png.py test-in/pee.txt test-out/mir-x.png    2 0 1 X
python3 voxel2png.py test-in/pee.txt test-out/mir-y.png    2 0 1 Y
python3 voxel2png.py test-in/pee.txt test-out/mir-z.png    2 0 1 Z
python3 voxel2png.py test-in/pee.txt test-out/mir-xy.png   2 0 1 XY
python3 voxel2png.py test-in/pee.txt test-out/mir-xz.png   2 0 1 XZ
python3 voxel2png.py test-in/pee.txt test-out/mir-yz.png   2 0 1 YZ
python3 voxel2png.py test-in/pee.txt test-out/mir-xyz.png  2 0 1 XYZ
