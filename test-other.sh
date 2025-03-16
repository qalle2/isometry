# miscellaneous tests

rm -f test-out/*.png

echo "== These should not cause errors =="

python3 voxel2png.py test-in/cube1x1x1.txt   test-out/cube-1x1x1-r000.png     0 0 0
python3 voxel2png.py test-in/cube1x1x1.txt   test-out/cube-1x1x1-r002.png     0 0 2
python3 voxel2png.py test-in/cube1x1x1.txt   test-out/cube-1x1x1-r200.png     2 0 0
python3 voxel2png.py test-in/cube1x1x1.txt   test-out/cube-1x1x1-r202.png     2 0 2

python3 voxel2png.py test-in/cube6x5x4.txt   test-out/cube-6x5x4-r000.png     0 0 0
python3 voxel2png.py test-in/cube6x5x4.txt   test-out/cube-6x5x4-r001.png     0 0 1
python3 voxel2png.py test-in/cube6x5x4.txt   test-out/cube-6x5x4-r002.png     0 0 2
python3 voxel2png.py test-in/cube6x5x4.txt   test-out/cube-6x5x4-r003.png     0 0 3
python3 voxel2png.py test-in/cube6x5x4.txt   test-out/cube-6x5x4-r200.png     2 0 0
python3 voxel2png.py test-in/cube6x5x4.txt   test-out/cube-6x5x4-r201.png     2 0 1
python3 voxel2png.py test-in/cube6x5x4.txt   test-out/cube-6x5x4-r202.png     2 0 2
python3 voxel2png.py test-in/cube6x5x4.txt   test-out/cube-6x5x4-r203.png     2 0 3

python3 voxel2png.py test-in/cubechecker.txt test-out/cube-checkered-r000.png 0 0 0
python3 voxel2png.py test-in/cubechecker.txt test-out/cube-checkered-r001.png 0 0 1
python3 voxel2png.py test-in/cubechecker.txt test-out/cube-checkered-r002.png 0 0 2
python3 voxel2png.py test-in/cubechecker.txt test-out/cube-checkered-r003.png 0 0 3
python3 voxel2png.py test-in/cubechecker.txt test-out/cube-checkered-r200.png 2 0 0
python3 voxel2png.py test-in/cubechecker.txt test-out/cube-checkered-r201.png 2 0 1
python3 voxel2png.py test-in/cubechecker.txt test-out/cube-checkered-r202.png 2 0 2
python3 voxel2png.py test-in/cubechecker.txt test-out/cube-checkered-r203.png 2 0 3

echo

echo "== These should cause four distinct errors =="
echo "x" > test-out/already-exists
python3 voxel2png.py
python3 voxel2png.py test-in/axes.txt    test-out/out1.png       9 9 9
python3 voxel2png.py test-in/nonexistent test-out/out2.png       0 0 0
python3 voxel2png.py test-in/axes.txt    test-out/already-exists 0 0 0
rm test-out/already-exists
echo
