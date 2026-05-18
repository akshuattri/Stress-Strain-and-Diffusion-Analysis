import numpy as np
import matplotlib.pyplot as plt
import os

# ==========================================================
# Helper functions
# ==========================================================
def read_energy(outcar):
    with open(outcar) as f:
        for line in reversed(f.readlines()):
            if "free  energy   TOTEN" in line:
                return float(line.split()[-2])
    raise RuntimeError("Energy not found")

def read_max_force(outcar):
    maxf = 0.0
    with open(outcar) as f:
        for line in f:
            if "FORCES: max atom" in line:
                maxf = float(line.split()[-2])
    return maxf

def read_poscar(poscar):
    with open(poscar) as f:
        lines = f.readlines()
    scale = float(lines[1])
    lattice = np.array([list(map(float, lines[i].split())) for i in range(2,5)]) * scale
    natoms = sum(map(int, lines[6].split()))
    coords = []
    for i in range(8, 8 + natoms):
        coords.append(list(map(float, lines[i].split()[:3])))
    return np.array(coords), lattice

# ==========================================================
# Collect NEB images
# ==========================================================
images = ["01", "02", "03", "04"]

energies = []
forces = []
coords = []
valid_images = []

for img in images:
    outcar = os.path.join(img, "OUTCAR")
    poscar = os.path.join(img, "POSCAR")

    if not os.path.isfile(outcar):
        print(f"Skipping image {img} (no OUTCAR)")
        continue

    energies.append(read_energy(outcar))
    forces.append(read_max_force(outcar))
    c, lattice = read_poscar(poscar)
    coords.append(c)
    valid_images.append(img)

energies = np.array(energies)
forces = np.array(forces)

# ==========================================================
# Reaction coordinate (path length)
# ==========================================================
path = [0.0]
for i in range(1, len(coords)):
    disp = np.linalg.norm(coords[i] - coords[i-1], axis=1)
    path.append(path[-1] + disp.max())

path = np.array(path)
path /= path[-1]  # normalize to [0,1]

# ==========================================================
# Energies (relative)
# ==========================================================
energies -= energies[0]

Em = energies.max()
ts_idx = np.argmax(energies)
ts_img = valid_images[ts_idx]

Efwd = Em
Ebwd = Em - energies[-1]

print("\nNEB RESULTS")
print("-----------")
print(f"Migration barrier        = {Em:.3f} eV")
print(f"Transition state image   = {ts_img}")
print(f"Forward barrier          = {Efwd:.3f} eV")
print(f"Backward barrier         = {Ebwd:.3f} eV")

# ==========================================================
# 1. Annotated NEB energy profile (reaction coordinate)
# ==========================================================
plt.figure()
plt.plot(path, energies, marker="o")
plt.axvline(path[ts_idx], color="r", linestyle="--")
plt.text(path[ts_idx], Em, f" TS (image {ts_img})", color="r", va="bottom")
plt.xlabel("Reaction coordinate")
plt.ylabel("Relative energy (eV)")
plt.title("NEB energy profile (relative, TS highlighted)")
plt.tight_layout()
plt.savefig("neb_energy_profile_annotated.png", dpi=300)
plt.close()

# ==========================================================
# 2. Image index vs energy (discrete)
# ==========================================================
plt.figure()
plt.plot(range(len(energies)), energies, marker="o")
plt.xlabel("Image index")
plt.ylabel("Relative energy (eV)")
plt.title("NEB energy vs image index")
plt.tight_layout()
plt.savefig("neb_energy_vs_image.png", dpi=300)
plt.close()

# ==========================================================
# 3. Forward / backward barrier bar plot
# ==========================================================
plt.figure()
plt.bar(["Forward", "Backward"], [Efwd, Ebwd])
plt.ylabel("Barrier (eV)")
plt.title("Forward and backward diffusion barriers")
plt.tight_layout()
plt.savefig("neb_forward_backward_barrier.png", dpi=300)
plt.close()

# ==========================================================
# 4. Atomic displacement vs reaction coordinate
# ==========================================================
disp_max = []
for i in range(len(coords)):
    d = np.linalg.norm(coords[i] - coords[0], axis=1)
    disp_max.append(d.max())

plt.figure()
plt.plot(path, disp_max, marker="o")
plt.xlabel("Reaction coordinate")
plt.ylabel("Max atomic displacement (fractional)")
plt.title("Atomic displacement along NEB path")
plt.tight_layout()
plt.savefig("neb_atomic_displacement.png", dpi=300)
plt.close()

# ==========================================================
# 5. Max force vs reaction coordinate
# ==========================================================
plt.figure()
plt.plot(path, forces, marker="o")
plt.xlabel("Reaction coordinate")
plt.ylabel("Max force (eV/Å)")
plt.title("NEB force convergence")
plt.tight_layout()
plt.savefig("neb_force_vs_reaction_coordinate.png", dpi=300)
plt.close()

print("\nAll enhanced NEB plots generated successfully.")

