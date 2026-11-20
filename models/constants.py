"""Physical constants and salt properties, loaded from the database files in data/.

    data/constants.csv  - every physical constant, with unit and source
    data/salts.csv      - molar mass, density and ion count of each seeding salt

Edit those CSV files to change a value or add a salt; no code change is needed.
"""
from __future__ import annotations

import csv
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
CONSTANTS_FILE = os.path.join(DATA_DIR, "constants.csv")
SALTS_FILE = os.path.join(DATA_DIR, "salts.csv")


def load_constants(path: str = CONSTANTS_FILE) -> dict[str, float]:
    with open(path, newline="", encoding="utf-8") as fh:
        return {row["symbol"]: float(row["value"]) for row in csv.DictReader(fh)}


def load_salts(path: str = SALTS_FILE) -> dict[str, dict]:
    salts = {}
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            salts[row["key"]] = make_salt(row["key"], row["label"], float(row["M_g_per_mol"]),
                                          float(row["density_g_per_cm3"]), int(float(row["ions_i"])))
    return salts


def make_salt(key: str, label: str, M_g_per_mol: float, density_g_cm3: float, ions: int) -> dict:
    """Salt properties in SI units. Also used for user-defined salts in the app."""
    if M_g_per_mol <= 0 or density_g_cm3 <= 0 or ions < 1:
        raise ValueError("Molar mass and density must be positive and i >= 1.")
    html = "".join(f"<sub>{ch}</sub>" if ch.isdigit() else ch for ch in label.replace("₂", "2").replace("₃", "3"))
    return {"key": key, "label": label, "html": html, "M": M_g_per_mol / 1000.0, "rho": density_g_cm3 * 1000.0,
            "i": ions}


_C = load_constants()
R = _C["R"]
K_B = _C["k_B"]
T0 = _C["T0"]
P_TRIPLE = _C["p_tp"]
M_W = _C["M_w"]
RHO_W = _C["rho_w"]
RHO_ICE = _C["rho_ice"]
SIGMA_W = _C["sigma_w"]
DH_VAP = _C["dh_vap"]
DH_FUS = _C["dh_fus"]
DH_SUB = DH_VAP + DH_FUS          # Hess's law: sublimation = vaporisation + fusion
GAMMA_IW = _C["gamma_iw"]
THETA_AGI = _C["theta_AgI"]
SALTS = load_salts()


def c_to_k(t_c):
    return t_c + T0


def k_to_c(t_k):
    return t_k - T0
