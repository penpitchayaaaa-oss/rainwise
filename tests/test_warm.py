"""Warm cloud: Kelvin, Raoult, Koehler."""
import numpy as np
import pytest

from models import warm
from models.constants import SALTS, c_to_k, make_salt

T = c_to_k(15.0)


def test_critical_point_matches_numerical_maximum():
    for salt in SALTS:
        for d in (50e-9, 100e-9, 1e-6):
            A, B = warm.kelvin_A(T), warm.raoult_B(salt, d)
            r_c, s_c = warm.critical_point(A, B)
            r = np.geomspace(r_c / 20, r_c * 20, 200001)
            s = warm.koehler_s(r, A, B)
            assert s.max() == pytest.approx(s_c, rel=1e-6)
            assert r[s.argmax()] == pytest.approx(r_c, rel=1e-3)


def test_kelvin_supersaturation_decreases_and_tends_to_A_over_r():
    r = np.array([0.01e-6, 0.1e-6, 1e-6, 10e-6])
    s = warm.kelvin_supersaturation(r, T)
    assert np.all(np.diff(s) < 0)
    assert s[-1] == pytest.approx(warm.kelvin_A(T) / r[-1], rel=1e-3)


def test_kelvin_A_is_about_1_nm():
    assert warm.kelvin_A(c_to_k(25.0)) == pytest.approx(1.05e-9, rel=0.02)


def test_sc_scales_with_dry_diameter_to_minus_three_halves():
    s1 = warm.analyse("NaCl", 100e-9, T, 0.3).s_c_pct
    s2 = warm.analyse("NaCl", 400e-9, T, 0.3).s_c_pct
    assert s1 / s2 == pytest.approx(4 ** 1.5, rel=1e-9)


def test_nacl_activates_more_easily_than_cacl2_at_equal_size():
    assert warm.analyse("NaCl", 100e-9, T, 0.3).s_c_pct < warm.analyse("CaCl2", 100e-9, T, 0.3).s_c_pct


def test_activation_rule():
    r = warm.analyse("NaCl", 100e-9, T, 0.0)
    assert not r.activates
    assert warm.analyse("NaCl", 100e-9, T, r.s_c_pct + 1e-6).activates


def test_custom_salt_and_validation():
    kcl = make_salt("custom", "KCl", 74.55, 1.98, 2)
    assert warm.analyse(kcl, 100e-9, T, 0.3).s_c_pct > 0
    with pytest.raises(ValueError):
        make_salt("bad", "X", -1, 1, 1)
    with pytest.raises(ValueError):
        warm.analyse("NaCl", -1e-9, T, 0.3)
    with pytest.raises(ValueError):
        warm.kelvin_A(-5)
