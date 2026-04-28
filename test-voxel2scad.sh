rm -f test-out/*.scad

python3 voxel2scad.py test-in/eevee.txt          > test-out/eevee.scad
python3 voxel2scad.py test-in/lapras.txt         > test-out/lapras.scad
python3 voxel2scad.py test-in/litten.txt         > test-out/litten-default.scad
python3 voxel2scad.py test-in/litten.txt 1       > test-out/litten-1colour.scad
python3 voxel2scad.py test-in/litten.txt 0 1 0   > test-out/litten-nocombine.scad
python3 voxel2scad.py test-in/litten.txt 0 0 1 0 > test-out/litten-nooverlap.scad
python3 voxel2scad.py test-in/lucario.txt        > test-out/lucario.scad
python3 voxel2scad.py test-in/vaporeon.txt       > test-out/vaporeon.scad

# these are slow so test them last
python3 voxel2scad.py test-in/megablastoise.txt  > test-out/megablastoise.scad
python3 voxel2scad.py test-in/megacharizardy.txt > test-out/megacharizardy.scad
