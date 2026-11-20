"""Warm-cloud (hygroscopic) seeding: Kelvin effect + Raoult's law = Koehler curve.

    Kelvin:  p_eq(r) = p_eq,flat * exp(2 gamma V_m / (r R T)),  V_m = M_w / rho_w
    Raoult:  p_w = a_w * p*_w   (a_w < 1 when salt is dissolved)
    Koehler: S_eq - 1 = A/r - B/r^3
             A = 2 gamma M_w / (R T rho_w)                (curvature / Kelvin term)
             B = 3 i m_s M_w / (4 pi rho_w M_s)            (solute / Raoult term)
    Critical point:  r_c = sqrt(3B/A),  s_c = S_c - 1 = sqrt(4A^3 / (27 B))
    Activation:      ambient supersaturation s >= s_c
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .constants import M_W, R, RHO_W, SALTS, SIGMA_W


def _props(salt):
    """Accept a salt key from data/salts.csv or a property dict made with constants.make_salt()."""
    if isinstance(salt, dict):
        return salt
    if salt not in SALTS:
        raise ValueError(f"Unknown salt {salt!r}.")
    return SALTS[salt]


def kelvin_A(T_K: float, sigma: float = SIGMA_W) -> float:  # noqa: D401
    """Curvature coefficient A [m]."""
    if T_K <= 0:
        raise ValueError("Temperature must be in kelvin and positive.")
    return 2.0 * sigma * M_W / (R * T_K * RHO_W)


def salt_mass(salt, dry_diameter_m: float) -> float:
    """Mass of a dry salt sphere [kg]: m_s = rho_s * (pi/6) * D_dry^3."""
    if dry_diameter_m <= 0:
        raise ValueError("Dry diameter must be positive.")
    return _props(salt)["rho"] * np.pi / 6.0 * dry_diameter_m ** 3


def raoult_B(salt, dry_diameter_m: float) -> float:
    """Solute coefficient B [m^3]."""
    p = _props(salt)
    return 3.0 * p["i"] * salt_mass(salt, dry_diameter_m) * M_W / (4.0 * np.pi * RHO_W * p["M"])


def kelvin_supersaturation(r_m, T_K: float, sigma: float = SIGMA_W) -> np.ndarray:
    """Supersaturation (fraction) a PURE water droplet of radius r needs: exp(A/r) - 1 (Kelvin equation)."""
    return np.exp(kelvin_A(T_K, sigma) / np.asarray(r_m, dtype=float)) - 1.0


def koehler_s(r_m, A: float, B: float) -> np.ndarray:
    """Equilibrium supersaturation S_eq - 1 (fraction) = A/r - B/r^3."""
    r = np.asarray(r_m, dtype=float)
    return A / r - B / r ** 3


@dataclass(frozen=True)
class WarmResult:
    salt: str
    label: str
    dry_diameter_m: float
    T_K: float
    sigma: float
    A_m: float
    B_m3: float
    r_c_m: float
    s_c_pct: float
    s_ambient_pct: float

    @property
    def activates(self) -> bool:
        return self.s_ambient_pct >= self.s_c_pct

    @property
    def margin_pct(self) -> float:
        return self.s_ambient_pct - self.s_c_pct

    @property
    def pure_water_same_size_pct(self) -> float:
        """Supersaturation a pure-water droplet as small as the dry particle (r = D_dry/2) would need (Kelvin only)."""
        return float(kelvin_supersaturation(self.dry_diameter_m / 2, self.T_K, self.sigma)) * 100.0


def critical_point(A: float, B: float) -> tuple[float, float]:
    """(r_c [m], s_c [fraction]) of the Koehler curve.

    d(A/r - B/r^3)/dr = -A/r^2 + 3B/r^4 = 0  ->  r_c = sqrt(3B/A)
    substituting back: s_c = A/r_c - B/r_c^3 = (2/3) A/r_c = sqrt(4A^3 / (27B))
    """
    return float(np.sqrt(3.0 * B / A)), float(np.sqrt(4.0 * A ** 3 / (27.0 * B)))


def analyse(salt, dry_diameter_m: float, T_K: float, s_ambient_pct: float, sigma: float = SIGMA_W) -> WarmResult:
    p = _props(salt)
    if s_ambient_pct < 0:
        raise ValueError("Ambient supersaturation must be >= 0 %.")
    A, B = kelvin_A(T_K, sigma), raoult_B(p, dry_diameter_m)
    r_c, s_c = critical_point(A, B)
    return WarmResult(p["key"], p["label"], dry_diameter_m, T_K, sigma, A, B, r_c, s_c * 100.0, s_ambient_pct)


def critical_curve(salt, dry_diameters_m, T_K: float, sigma: float = SIGMA_W) -> np.ndarray:
    """s_c [%] as a function of dry diameter."""
    A = kelvin_A(T_K, sigma)
    return np.array([critical_point(A, raoult_B(salt, d))[1] * 100.0 for d in np.atleast_1d(dry_diameters_m)])
