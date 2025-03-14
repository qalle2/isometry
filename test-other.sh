# miscellaneous tests

rm -f test-out/*.png

echo "== These should not cause errors =="

python3 isometry.py test-in/cube1x1x1.txt   test-out/cube-1x1x1-r000.png     0 0 0
python3 isometry.py test-in/cube1x1x1.txt   test-out/cube-1x1x1-r002.png     0 0 2
python3 isometry.py test-in/cube1x1x1.txt   test-out/cube-1x1x1-r200.png     2 0 0
python3 isometry.py test-in/cube1x1x1.txt   test-out/cube-1x1x1-r202.png     2 0 2

python3 isometry.py test-in/cube6x5x4.txt   test-out/cube-6x5x4-r000.png     0 0 0
python3 isometry.py test-in/cube6x5x4.txt   test-out/cube-6x5x4-r001.png     0 0 1
python3 isometry.py test-in/cube6x5x4.txt   test-out/cube-6x5x4-r002.png     0 0 2
python3 isometry.py test-in/cube6x5x4.txt   test-out/cube-6x5x4-r003.png     0 0 3
python3 isometry.py test-in/cube6x5x4.txt   test-out/cube-6x5x4-r200.png     2 0 0
python3 isometry.py test-in/cube6x5x4.txt   test-out/cube-6x5x4-r201.png     2 0 1
python3 isometry.py test-in/cube6x5x4.txt   test-out/cube-6x5x4-r202.png     2 0 2
python3 isometry.py test-in/cube6x5x4.txt   test-out/cube-6x5x4-r203.png     2 0 3

python3 isometry.py test-in/cubechecker.txt test-out/cube-checkered-r000.png 0 0 0
python3 isometry.py test-in/cubechecker.txt test-out/cube-checkered-r001.png 0 0 1
python3 isometry.py test-in/cubechecker.txt test-out/cube-checkered-r002.png 0 0 2
python3 isometry.py test-in/cubechecker.txt test-out/cube-checkered-r003.png 0 0 3
python3 isometry.py test-in/cubechecker.txt test-out/cube-checkered-r200.png 2 0 0
python3 isometry.py test-in/cubechecker.txt test-out/cube-checkered-r201.png 2 0 1
python3 isometry.py test-in/cubechecker.txt test-out/cube-checkered-r202.png 2 0 2
python3 isometry.py test-in/cubechecker.txt test-out/cube-checkered-r203.png 2 0 3

echo

echo "== These should cause four distinct errors =="
python3 isometry.py
python3 isometry.py test-in/axes.txt    test-out/axes-1a.png 9 9
python3 isometry.py test-in/nonexistent test-out/axes-1a.png 0 0
python3 isometry.py test-in/axes.txt    test-out/axes-1a.png 0 0
echo
