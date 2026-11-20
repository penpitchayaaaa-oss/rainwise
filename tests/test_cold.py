"""Cold cloud: Clausius-Clapeyron, classical nucleation theory, heterogeneous factor."""
import numpy as np
import pytest

from models import cold
from models.constants import T0, c_to_k


def mk_ice(T):   # Murphy & Koop (2005) Eq. 7
    return np.exp(9.550426 - 5723.265 / T + 3.53068 * np.log(T) - 0.00728332 * T)


def mk_liq(T):   # Murphy & Koop (2005) Eq. 10
    return np.exp(54.842763 - 6763.22 / T - 4.210 * np.log(T) + 0.000367 * T
                  + np.tanh(0.0415 * (T - 218.8)) * (53.878 - 1331.22 / T - 9.44523 * np.log(T) + 0.014025 * T))


def test_clausius_clapeyron_close_to_murphy_koop():
    """Constant-dh Clausius-Clapeyron vs the Murphy & Koop (2005) reference fits."""
    T = c_to_k(np.linspace(-40, 0, 41))
    assert np.max(np.abs(cold.p_sat_ice(T) / mk_ice(T) - 1)) < 0.01           # ice: within 1 % to -40 degC
    T20 = c_to_k(np.linspace(-20, 0, 21))
    assert np.max(np.abs(cold.p_sat_liquid(T20) / mk_liq(T20) - 1)) < 0.02    # liquid: within 2 % to -20 degC
    assert np.max(np.abs(cold.p_sat_liquid(T) / mk_liq(T) - 1)) < 0.08        # and within 8 % to -40 degC


def test_bergeron_ice_below_liquid():
    T = c_to_k(np.linspace(-40, -1, 40))
    assert np.all(cold.p_sat_ice(T) < cold.p_sat_liquid(T))
    assert cold.p_sat_ice(T0) == pytest.approx(cold.p_sat_liquid(T0))


def test_driving_force_negative_and_close_to_fusion_form():
    T = c_to_k(-5.0)
    dgv = cold.volume_free_energy(T)
    approx = -(917.0 / 0.01801528) * 6010 * (1 - T / T0)
    assert dgv < 0
    assert dgv == pytest.approx(approx, rel=0.02)


def test_barrier_is_the_maximum_of_the_energy_curve():
    T = c_to_k(-20.0)
    r_star, dG = cold.critical_nucleus(T)
    assert cold.free_energy_curve(r_star, T) == pytest.approx(dG, rel=1e-12)
    h = r_star * 1e-6
    slope = (cold.free_energy_curve(r_star + h, T) - cold.free_energy_curve(r_star - h, T)) / (2 * h)
    assert abs(slope) < 1e-9 * dG / r_star


def test_wetting_factor_limits():
    assert cold.wetting_factor(0) == pytest.approx(0)
    assert cold.wetting_factor(90) == pytest.approx(0.5)
    assert cold.wetting_factor(180) == pytest.approx(1)
    with pytest.raises(ValueError):
        cold.wetting_factor(200)


def test_barrier_falls_with_temperature_and_agi_lowers_it():
    b = [cold.analyse(c_to_k(t), 45).dG_hom_J for t in (-5, -10, -20, -30)]
    assert all(x > y for x, y in zip(b, b[1:]))
    r = cold.analyse(c_to_k(-10), 45)
    assert r.dG_het_J < r.dG_hom_J
    assert r.r_star_m == cold.critical_nucleus(c_to_k(-10))[0]


def test_units_and_domain():
    with pytest.raises(ValueError):
        cold.critical_nucleus(T0 + 1)
    with pytest.raises(ValueError):
        cold.p_sat_ice(-10.0)
