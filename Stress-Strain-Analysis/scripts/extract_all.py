import os
import numpy as np
import matplotlib.pyplot as plt

EV_A3_TO_GPA = 160.21766208

# ================= USER SETTINGS =================
volume_A3 = 11.39   # equilibrium volume (Å^3) from OUTCAR
strain_dirs = {
    -1.0: "strain_-1",
    -0.5: "strain_-0.5",
     0.0: "strain_0.0",
     0.5: "strain_+0.5",
     1.0: "strain_+1"
}
# ===============================================


def read_energy(outcar):
    with open(outcar) as f:
        for line in reversed(f.readlines()):
            if "free  energy   TOTEN" in line:
                return float(line.split()[-2])
    raise RuntimeError("Energy not found in OUTCAR")


def read_fermi(outcar):
    with open(outcar) as f:
        for line in f:
            if "E-fermi" in line:
                return float(line.split()[2])
    raise RuntimeError("Fermi energy not found in OUTCAR")


# ================= DATA EXTRACTION =================

strains = []
energies = []
fermis = []

for s_percent, d in strain_dirs.items():
    outcar = os.path.join(d, "OUTCAR")
    eps = s_percent * 1.0e-2    # percent → strain (ONLY ONCE)
    strains.append(eps)
    energies.append(read_energy(outcar))
    fermis.append(read_fermi(outcar))

strains = np.array(strains)
energies = np.array(energies)
fermis = np.array(fermis)

# Reference (zero strain)
E0 = energies[strains == 0.0][0]
Ef0 = fermis[strains == 0.0][0]

dE = energies - E0
dEf = fermis - Ef0


# ================= ENERGY–STRAIN FIT =================
# Enforce ΔE ∝ ε² explicitly

mask = strains != 0.0
x = strains[mask]**2
y = dE[mask]

A = np.polyfit(x, y, 1)[0]   # slope in eV

C11_minus_C12 = (2.0 * A / volume_A3) * EV_A3_TO_GPA


# ================= DEFORMATION POTENTIAL =================
# Linear response: ΔEf = (dEf/dε) ε

lin = np.polyfit(strains, fermis, 1)
deformation_potential = lin[0]   # eV


# ================= OUTPUT =================

print("========== DEFORMATION ANALYSIS ==========")
print(f"Biaxial modulus (C11 - C12) = {C11_minus_C12:.2f} GPa")
print(f"Deformation potential dEf/dε = {deformation_potential:.3f} eV")
print("==========================================")

# ================= PLOTS =================

# Energy vs strain
plt.figure()
plt.scatter(strains * 100, dE, color="red", label="DFT data")
xfit = np.linspace(min(strains), max(strains), 200)
plt.plot(xfit * 100, A * xfit**2, label="Quadratic fit")
plt.xlabel("Strain (%)")
plt.ylabel("ΔE (eV)")
plt.title("Energy vs Strain")
plt.legend()
plt.tight_layout()
plt.savefig("energy_strain_curve.png", dpi=300)

# Fermi level vs strain
plt.figure()
plt.scatter(strains * 100, fermis, color="blue", label="DFT data")
plt.plot(strains * 100, np.polyval(lin, strains), label="Linear fit")
plt.xlabel("Strain (%)")
plt.ylabel("Fermi Energy (eV)")
plt.title("Fermi Energy vs Strain")
plt.legend()
plt.tight_layout()
plt.savefig("fermi_vs_strain_curve.png", dpi=300)

plt.close("all")

