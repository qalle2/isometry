rm -f test-out/*.scad

python3 voxel2scad.py test-in/eevee.txt > test-out/eevee.scad
grep "optimised"                          test-out/eevee.scad

python3 voxel2scad.py test-in/lucario.txt > test-out/lucario.scad
grep "optimised"                            test-out/lucario.scad

python3 voxel2scad.py test-in/megablastoise.txt > test-out/megablastoise.scad
grep "optimised"                                  test-out/megablastoise.scad

python3 voxel2scad.py test-in/vaporeon.txt > test-out/vaporeon.scad
grep "optimised"                             test-out/vaporeon.scad
