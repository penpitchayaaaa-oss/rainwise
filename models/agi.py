"""Cold-cloud seeding with AgI - one mechanism only: condensation-freezing.

Water vapour condenses on an AgI particle into a tiny droplet, which then freezes.
Yang et al. (2024), Eq. 2 (after Xue et al., 2013a; DeMott, 1995):

    F = a * ((T_ref - T) / T_s)^3 * (S_w - 1)^2        a = 900, T_ref = 268.66 K, T_s = 10 K
    valid for T < T_ref (about -4.5 degC) and S_w > 1 (air supersaturated with respect to water)

    INP [L^-1] = F * N_AgI [cm^-3] * 1000              (1 cm^-3 = 1000 L^-1)

F is the fraction of AgI particles that become ice. It must lie between 0 and 1; a value above 1 means the
fit is being used outside the range it was made for, so it is flagged and not turned into an INP number.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from .constants import CF_A, CF_TREF, CF_TS


@dataclass(frozen=True)
class CFResult:
    T_K: float
    Sw: float
    N_per_cm3: float
    fraction: Optional[float]   # None when the equation does not apply
    status: str                 # "ok", "too_warm", "not_supersaturated", "above_one"
    message: str

    @property
    def usable(self) -> bool:
        return self.status == "ok"

    @property
    def inp_per_L(self) -> Optional[float]:
        return inp_per_litre(self.fraction, self.N_per_cm3) if self.usable else None


def _check(T_K, Sw, N=1.0):
    if np.any(np.asarray(T_K) <= 0):
        raise ValueError("Temperature must be in kelvin.")
    if np.any(np.asarray(Sw) <= 0):
        raise ValueError("Water saturation ratio must be positive.")
    if np.any(np.asarray(N) < 0):
        raise ValueError("AgI concentration cannot be negative.")


def raw_fraction(T_K, Sw):
    """Eq. 2 evaluated as written (no validity check). Works on arrays."""
    _check(T_K, Sw)
    return CF_A * ((CF_TREF - np.asarray(T_K, float)) / CF_TS) ** 3 * (np.asarray(Sw, float) - 1.0) ** 2


def inp_per_litre(fraction: float, N_per_cm3: float) -> float:
    """Ice-nucleating particles per litre of air."""
    _check(300.0, 1.0, N_per_cm3)
    return fraction * N_per_cm3 * 1000.0


def active_fraction(T_K: float, Sw: float, N_per_cm3: float = 10.0) -> CFResult:
    """Active fraction with the validity checks of Eq. 2."""
    _check(T_K, Sw, N_per_cm3)
    if T_K >= CF_TREF:
        return CFResult(T_K, Sw, N_per_cm3, None, "too_warm",
                        f"Too warm: AgI condensation-freezing starts below {CF_TREF - 273.15:.1f} °C.")
    if Sw <= 1.0:
        return CFResult(T_K, Sw, N_per_cm3, 0.0, "not_supersaturated",
                        "The air is not supersaturated with respect to water (S_w ≤ 1), so no droplet can condense on "
                        "the AgI: F = 0.")
    F = float(raw_fraction(T_K, Sw))
    if F > 1.0:
        return CFResult(T_K, Sw, N_per_cm3, F, "above_one",
                        "F is above 1, which is impossible for a fraction: the equation is being used outside the "
                        "range of the laboratory data it was fitted to.")
    return CFResult(T_K, Sw, N_per_cm3, F, "ok", "Within the range of the equation.")


def fraction_curve(T_K, Sw):
    """F over arrays for charts; NaN where the equation does not apply (T >= T_ref or S_w <= 1)."""
    T = np.asarray(T_K, float)
    S = np.asarray(Sw, float)
    F = raw_fraction(T, S)
    return np.where((T < CF_TREF) & (S > 1.0), F, np.nan)
