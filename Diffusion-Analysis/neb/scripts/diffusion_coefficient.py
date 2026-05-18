import numpy as np
import matplotlib.pyplot as plt

kB = 8.617333262e-5  # eV/K

# ==========================================================
# CASE A: NEB-based diffusion (Arrhenius / TST)
# ==========================================================
def diffusion_from_neb(
    Em,              # migration barrier (eV)
    a,               # jump distance (Angstrom)
    T_list,          # list of temperatures (K)
    nu=1e13,         # attempt frequency (Hz)
    dim=3            # diffusion dimensionality
):
    a_m = a * 1e-10  # Å → m
    D = []

    for T in T_list:
        D_T = (a_m**2 * nu / (2*dim)) * np.exp(-Em / (kB*T))
        D.append(D_T)

    return np.array(D)

# ==========================================================
# CASE B: AIMD diffusion (MSD → D)
# ==========================================================
def diffusion_from_msd(time, msd, dim=3):
    # Einstein relation
    slope = np.polyfit(time, msd, 1)[0]
    D = slope / (2*dim)
    return D

# ==========================================================
# Example usage
# ==========================================================
if __name__ == "__main__":

    # ======================
    # SELECT METHOD HERE
    # ======================
    METHOD = "NEB"   # options: "NEB", "AIMD"

    # ======================================================
    # NEB example (recommended, low cost)
    # ======================================================
    if METHOD == "NEB":
        Em = 0.67              # eV (example)
        a = 2.48               # Angstrom (jump distance)
        T_list = np.array([600, 800, 1000, 1200])

        D = diffusion_from_neb(Em, a, T_list)

        # Arrhenius plot
        plt.figure()
        plt.plot(1/T_list, np.log(D), marker="o")
        plt.xlabel("1/T (1/K)")
        plt.ylabel("ln D (m²/s)")
        plt.title("Arrhenius diffusion coefficient (NEB)")
        plt.tight_layout()
        plt.savefig("diffusion_arrhenius_neb.png", dpi=300)
        plt.close()

        print("\nNEB-based diffusion coefficients:")
        for T, d in zip(T_list, D):
            print(f"T = {T:4d} K  →  D = {d:.3e} m²/s")

    # ======================================================
    # AIMD example (expensive but direct)
    # ======================================================
    if METHOD == "AIMD":
        # Example MSD data (replace with real data)
        time = np.array([0, 1, 2, 3, 4, 5]) * 1e-12  # seconds
        msd = np.array([0, 0.5, 1.2, 2.1, 3.1, 4.3]) * 1e-20  # m²

        D = diffusion_from_msd(time, msd)

        plt.figure()
        plt.plot(time, msd, marker="o")
        plt.xlabel("Time (s)")
        plt.ylabel("MSD (m²)")
        plt.title("Mean square displacement (AIMD)")
        plt.tight_layout()
        plt.savefig("msd_plot.png", dpi=300)
        plt.close()

        print(f"\nAIMD diffusion coefficient: D = {D:.3e} m²/s")

