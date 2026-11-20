"""Cold-cloud (glaciogenic) seeding with AgI: classical nucleation theory + Bergeron process.

    Clausius-Clapeyron:  d ln p*/d(1/T) = -dh/R ;  dh_sub = dh_vap + dh_fus  ->  p*_ice < p*_liq below 0 degC
    Driving force:       dG_v = -(rho_ice / M_w) R T ln(p*_liq / p*_ice)        [J m-3]  (< 0 below 0 degC)
    Free energy:         dG(r) = 4 pi r^2 gamma + (4/3) pi r^3 dG_v           (surface + volume)
    Critical nucleus:    r* = 2 gamma / |dG_v| ;   dG* = 16 pi gamma^3 / (3 dG_v^2)
    Heterogeneous (AgI): dG*_het = f(theta) dG*_hom ;  f = (2 + cos theta)(1 - cos theta)^2 / 4
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .constants import DH_FUS, DH_SUB, DH_VAP, GAMMA_IW, K_B, M_W, P_TRIPLE, R, RHO_ICE, T0, THETA_AGI


def _check_subzero(T_K):
    t = np.asarray(T_K, dtype=float)
    if np.any(t <= 0):
        raise ValueError("Temperature must be in kelvin.")
    return t


def p_sat_liquid(T_K):
    """Saturation vapour pressure over (supercooled) liquid water [Pa], Clausius-Clapeyron from 0 degC."""
    t = _check_subzero(T_K)
    return P_TRIPLE * np.exp(-DH_VAP / R * (1.0 / t - 1.0 / T0))


def p_sat_ice(T_K):
    """Saturation vapour pressure over ice [Pa], Clausius-Clapeyron with dh_sub = dh_vap + dh_fus."""
    t = _check_subzero(T_K)
    return P_TRIPLE * np.exp(-DH_SUB / R * (1.0 / t - 1.0 / T0))


def liquid_to_ice_ratio(T_K):
    """p*_liq / p*_ice = exp[(dh_fus / R)(1/T - 1/T0)]  (> 1 below 0 degC)."""
    t = _check_subzero(T_K)
    return np.exp(DH_FUS / R * (1.0 / t - 1.0 / T0))


def volume_free_energy(T_K):
    """dG_v [J m-3] for turning supercooled water into ice (negative below 0 degC)."""
    t = _check_subzero(T_K)
    return -(RHO_ICE / M_W) * R * t * np.log(liquid_to_ice_ratio(t))


def wetting_factor(theta_deg: float) -> float:
    """Heterogeneous-nucleation factor f(theta) in [0, 1]; theta = contact angle of ice on the particle."""
    if not 0 <= theta_deg <= 180:
        raise ValueError("Contact angle must be between 0 and 180 degrees.")
    c = np.cos(np.radians(theta_deg))
    return float((2 + c) * (1 - c) ** 2 / 4)


def free_energy_curve(r_m, T_K: float, gamma: float = GAMMA_IW, f: float = 1.0):
    """dG(r) [J] = f (4 pi r^2 gamma + 4/3 pi r^3 dG_v)."""
    r = np.asarray(r_m, dtype=float)
    return f * (4 * np.pi * r ** 2 * gamma + 4.0 / 3.0 * np.pi * r ** 3 * volume_free_energy(T_K))


@dataclass(frozen=True)
class ColdResult:
    T_K: float
    gamma: float
    theta_deg: float
    f: float
    dGv: float
    r_star_m: float
    dG_hom_J: float
    dG_het_J: float
    p_liq: float
    p_ice: float

    @property
    def kT(self) -> float:
        return K_B * self.T_K

    @property
    def dG_hom_kT(self) -> float:
        return self.dG_hom_J / self.kT

    @property
    def dG_het_kT(self) -> float:
        return self.dG_het_J / self.kT

    @property
    def reduction_pct(self) -> float:
        return (1 - self.f) * 100.0

    @property
    def ice_supersaturation_pct(self) -> float:
        """Supersaturation with respect to ice when the air is exactly saturated for liquid water."""
        return (self.p_liq / self.p_ice - 1.0) * 100.0


def critical_nucleus(T_K: float, gamma: float = GAMMA_IW) -> tuple[float, float]:
    """(r* [m], dG* [J]) for homogeneous nucleation.

    d(dG)/dr = 8 pi r gamma + 4 pi r^2 dG_v = 0  ->  r* = -2 gamma / dG_v = 2 gamma / |dG_v|
    substituting back: dG* = 16 pi gamma^3 / (3 dG_v^2)
    """
    if T_K >= T0:
        raise ValueError("Ice nucleation needs a temperature below 0 degC.")
    if gamma <= 0:
        raise ValueError("Interfacial energy must be positive.")
    dgv = float(volume_free_energy(T_K))
    return 2 * gamma / abs(dgv), 16 * np.pi * gamma ** 3 / (3 * dgv ** 2)


def analyse(T_K: float, theta_deg: float = THETA_AGI, gamma: float = GAMMA_IW) -> ColdResult:
    r_star, dG = critical_nucleus(T_K, gamma)
    f = wetting_factor(theta_deg)
    return ColdResult(T_K, gamma, theta_deg, f, float(volume_free_energy(T_K)), r_star, dG, f * dG,
                      float(p_sat_liquid(T_K)), float(p_sat_ice(T_K)))
