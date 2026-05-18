#!/bin/bash

echo "# strain(%) Energy(eV)" > energy_vs_strain.dat

for d in strain_*; do
  s=${d#strain_}
  e=$(grep "free  energy   TOTEN" $d/OUTCAR | tail -1 | awk '{print $5}')
  echo "$s $e" >> energy_vs_strain.dat
done

awk 'NR>1{print $1/100,$2}' energy_vs_strain.dat > energy_vs_strain_eps.dat

python - << 'EOF'
import numpy as np
import matplotlib.pyplot as plt

strain, energy = np.loadtxt("energy_vs_strain_eps.dat", unpack=True)
coef = np.polyfit(strain, energy, 1)
fit = np.polyval(coef, strain)

print(f"dE/dε = {coef[0]:.6f} eV")

plt.plot(strain, energy, 'o', label="DFT data")
plt.plot(strain, fit, '-', label="Linear fit")
plt.xlabel("Strain ε")
plt.ylabel("Total Energy (eV)")
plt.legend()
plt.tight_layout()
plt.show()
EOF

