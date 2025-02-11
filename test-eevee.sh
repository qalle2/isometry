# note: bottom*.png except bottom.png need to be flipped vertically afterwards

rm -f test-out/*.png

python3 isometry.py test-in/eevee.txt test-out/top.png    1 17 0 17 X
python3 isometry.py test-in/eevee.txt test-out/bottom.png 1 17 0 17 X Y

python3 isometry.py test-in/eevee.txt test-out/front.png  1 17 0 17
python3 isometry.py test-in/eevee.txt test-out/rear.png   1 17 0 17 "" Y
python3 isometry.py test-in/eevee.txt test-out/right.png  1 17 0 17 Z
python3 isometry.py test-in/eevee.txt test-out/left.png   1 17 0 17 Z  X

python3 isometry.py test-in/eevee.txt test-out/frontleft.png  2 12 0 17
python3 isometry.py test-in/eevee.txt test-out/rearright.png  2 12 0 17 "" Y
python3 isometry.py test-in/eevee.txt test-out/frontright.png 2 12 0 17 Z
python3 isometry.py test-in/eevee.txt test-out/rearleft.png   2 12 0 17 Z  X

python3 isometry.py test-in/eevee.txt test-out/topfront.png    1 16 8 16
python3 isometry.py test-in/eevee.txt test-out/toprear.png     1 16 8 16 "" Y
python3 isometry.py test-in/eevee.txt test-out/bottomfront.png 1 16 8 16 "" Z
python3 isometry.py test-in/eevee.txt test-out/bottomrear.png  1 16 8 16 "" YZ
python3 isometry.py test-in/eevee.txt test-out/topright.png    1 16 8 16 Z
python3 isometry.py test-in/eevee.txt test-out/topleft.png     1 16 8 16 Z  X
python3 isometry.py test-in/eevee.txt test-out/bottomright.png 1 16 8 16 Z  Z
python3 isometry.py test-in/eevee.txt test-out/bottomleft.png  1 16 8 16 Z  XZ

python3 isometry.py test-in/eevee.txt test-out/topfrontleft.png     2 15 8 16
python3 isometry.py test-in/eevee.txt test-out/toprearright.png     2 15 8 16 "" Y
python3 isometry.py test-in/eevee.txt test-out/bottomfrontleft.png  2 15 8 16 "" Z
python3 isometry.py test-in/eevee.txt test-out/bottomrearright.png  2 15 8 16 "" YZ
python3 isometry.py test-in/eevee.txt test-out/topfrontright.png    2 15 8 16 Z
python3 isometry.py test-in/eevee.txt test-out/toprearleft.png      2 15 8 16 Z  X
python3 isometry.py test-in/eevee.txt test-out/bottomfrontright.png 2 15 8 16 Z  Z
python3 isometry.py test-in/eevee.txt test-out/bottomrearleft.png   2 15 8 16 Z  XZ
