deformation potential analysis
# ===============================

# Safety check
ls strain_*/OUTCAR > /dev/null 2>&1 || {
  echo "ERROR: strain_*/OUTCAR not found"
  exit 1
}

# --------------------------------
# 1. Extract TOTAL ENERGY vs strain
# --------------------------------
echo "# strain(%) Energy(eV)" > energy_vs_strain.dat
for d in strain_*; do
  s=${d#strain_}
  e=$(grep "free  energy   TOTEN" $d/OUTCAR | tail -1 | awk '{print $5}')
  echo "$s $e" >> energy_vs_strain.dat
done

awk 'NR>1{print $1/100,$2}' energy_vs_strain.dat > energy_vs_strain_eps.dat

# --------------------------------
# 2. Extract FERMI ENERGY vs strain
# --------------------------------
echo "# strain(%) EFermi(eV)" > ef_vs_strain.dat
for d in strain_*; do
  s=${d#strain_}
  ef=$(grep "E-fermi" $d/OUTCAR | tail -1 | awk '{print $3}')
  echo "$s $ef" >> ef_vs_strain.dat
done

awk 'NR>1{print $1/100,$2}' ef_vs_strain.dat > ef_vs_strain_eps.dat

# --------------------------------
# 3. Fit + plot (Python)
# --------------------------------
python << 'EOF'
import numpy as np
import matplotlib.pyplot as plt

# ---- Energy vs strain ----
strain_E, energy = np.loadtxt("energy_vs_strain_eps.dat", unpack=True)
coef_E = np.polyfit(strain_E, energy, 1)
fit_E = np.polyval(coef_E, strain_E)

# ---- Fermi energy vs strain ----
strain_F, ef = np.loadtxt("ef_vs_strain_eps.dat", unpack=True)
coef_F = np.polyfit(strain_F, ef, 1)
fit_F = np.polyval(coef_F, strain_F)

print("\n===== RESULTS =====")
print(f"dE_total/dε = {coef_E[0]:.6f} eV")
print(f"Electronic deformation potential E1 = {coef_F[0]:.6f} eV")

# ---- Plot 1: Total Energy ----
plt.figure()
plt.plot(strain_E, energy, 'o', label="DFT data")
plt.plot(strain_E, fit_E, '-', label="Linear fit")
plt.xlabel("Strain ε")
plt.ylabel("Total Energy (eV)")
plt.legend()
plt.tight_layout()
plt.savefig("energy_vs_strain.png", dpi=300)

# ---- Plot 2: Fermi Energy ----
plt.figure()
plt.plot(strain_F, ef, 'o', label="DFT data")
plt.plot(strain_F, fit_F, '-', label="Linear fit")
plt.xlabel("Strain ε")
plt.ylabel("Fermi Energy (eV)")
plt.legend()
plt.tight_layout()
plt.savefig("ef_vs_strain.png", dpi=300)

plt.show()
EOF

echo "Plots saved:"
echo "  energy_vs_strain.png"
echo "  ef_vs_strain.png"

