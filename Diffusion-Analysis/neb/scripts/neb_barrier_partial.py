import numpy as np
import matplotlib.pyplot as plt
import os

images = sorted([d for d in os.listdir(".") if d.isdigit()])

energies = []
valid_images = []

for img in images:
    outcar = os.path.join(img, "OUTCAR")
    if not os.path.isfile(outcar):
        print(f"Warning: OUTCAR missing in image {img}, skipping.")
        continue

    with open(outcar) as f:
        for line in reversed(f.readlines()):
            if "free  energy   TOTEN" in line:
                energies.append(float(line.split()[-2]))
                valid_images.append(img)
                break

energies = np.array(energies)
energies -= energies[0]

reaction_coord = np.linspace(0, 1, len(energies))

Em = energies.max()
ts_image = valid_images[np.argmax(energies)]

print("\nNEB diffusion results (PARTIAL)")
print("--------------------------------")
print(f"Migration barrier (relative) = {Em:.3f} eV")
print(f"Saddle-point image          = {ts_image}")
print("NOTE: Endpoints missing. Barrier is provisional.")

plt.figure()
plt.plot(reaction_coord, energies, marker="o")
plt.xlabel("Reaction coordinate")
plt.ylabel("Energy (eV)")
plt.title("NEB energy profile (partial, endpoints missing)")
plt.tight_layout()
plt.savefig("neb_energy_profile_partial.png", dpi=300)
plt.close()

