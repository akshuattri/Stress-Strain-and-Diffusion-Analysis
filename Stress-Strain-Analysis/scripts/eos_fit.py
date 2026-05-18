import numpy as np
import subprocess
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# --------------------------------------------------
# Birch-Murnaghan Equation of State
# --------------------------------------------------
def birch_murnaghan(V, E0, B0, BP, V0):
    eta = (V0 / V)**(2.0/3.0) - 1.0
    return E0 + (9.0 * V0 * B0 / 16.0) * (
        (eta**3) * BP + (eta**2) * (6.0 - 4.0 * eta)
    )

# --------------------------------------------------
# Strain directories (order does not matter)
# --------------------------------------------------
dirs = [
    "strain_-1",
    "strain_-0.5",
    "strain_0.0",
    "strain_+0.5",
    "strain_+1"
]

volumes = []
energies = []

# --------------------------------------------------
# Extract volume and energy from OUTCAR
# --------------------------------------------------
for d in dirs:
    outcar = f"{d}/OUTCAR"

    # Volume
    vol_cmd = f"grep 'volume of cell' {outcar} | tail -1 | awk '{{print $5}}'"
    volume = float(subprocess.check_output(vol_cmd, shell=True))
    
    # Energy
    ene_cmd = f"grep 'free  energy   TOTEN' {outcar} | tail -1 | awk '{{print $5}}'"
    energy = float(subprocess.check_output(ene_cmd, shell=True))

    volumes.append(volume)
    energies.append(energy)

volumes = np.array(volumes)
energies = np.array(energies)

# --------------------------------------------------
# Initial guesses
# --------------------------------------------------
E0_guess = energies.min()
V0_guess = volumes[np.argmin(energies)]
B0_guess = 0.5   # eV/Å^3
BP_guess = 4.0

p0 = [E0_guess, B0_guess, BP_guess, V0_guess]

# --------------------------------------------------
# EOS fit
# --------------------------------------------------
params, _ = curve_fit(birch_murnaghan, volumes, energies, p0=p0)

E0, B0, BP, V0 = params

# --------------------------------------------------
# Unit conversion: eV/Å^3 → GPa
# --------------------------------------------------
B0_GPa = B0 * 160.21766208

# --------------------------------------------------
# Print results
# --------------------------------------------------
print("========== Birch–Murnaghan EOS Fit ==========")
print(f"Equilibrium volume V0  = {V0:.4f} Å^3")
print(f"Bulk modulus B0        = {B0_GPa:.2f} GPa")
print(f"Pressure derivative B' = {BP:.2f}")
print("============================================")

# --------------------------------------------------
# Plot EOS
# --------------------------------------------------
V_fit = np.linspace(min(volumes)*0.99, max(volumes)*1.01, 200)
E_fit = birch_murnaghan(V_fit, *params)

plt.scatter(volumes, energies, color='red', label='DFT data')
plt.plot(V_fit, E_fit, label='BM EOS fit')
plt.xlabel("Volume (Å³)")
plt.ylabel("Energy (eV)")
plt.legend()
plt.tight_layout()
plt.savefig("eos_fit.png", dpi=300)
plt.show()

