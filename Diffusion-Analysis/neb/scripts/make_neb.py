import numpy as np
import os

def read_poscar(fname, natoms=26):
    with open(fname) as f:
        lines = f.readlines()
    header = lines[:8]
    coords = np.array([list(map(float, l.split())) for l in lines[8:8+natoms]])
    return header, coords

h0, c0 = read_poscar("00/POSCAR")
h1, c1 = read_poscar("05/POSCAR")

nimg = 4

for i in range(1, nimg+1):
    t = i/(nimg+1)
    ci = (1-t)*c0 + t*c1
    d = f"{i:02d}"
    os.makedirs(d, exist_ok=True)
    with open(f"{d}/POSCAR", "w") as f:
        f.writelines(h0)
        for row in ci:
            f.write(f"{row[0]: .16f} {row[1]: .16f} {row[2]: .16f}\n")

