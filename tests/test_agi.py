"""Cold cloud: AgI condensation-freezing (Yang et al., 2024, Eq. 2) and INP."""
import numpy as np
import pytest

from models import agi
from models.constants import c_to_k


def test_hand_calculation_minus15():
    # (268.66 - 258.15)/10 = 1.051 ; 1.051^3 = 1.16094 ; 900 * 1.16094 * 0.002^2 = 4.179e-3
    r = agi.active_fraction(c_to_k(-15.0), 1.002, 10.0)
    assert r.usable
    assert r.fraction == pytest.approx(4.1794e-3, rel=1e-3)
    assert r.inp_per_L == pytest.approx(41.79, rel=1e-3)


def test_too_warm_is_not_computed():
    r = agi.active_fraction(c_to_k(-3.0), 1.01, 10.0)
    assert r.status == "too_warm" and r.fraction is None and r.inp_per_L is None


def test_no_supersaturation_gives_zero():
    r = agi.active_fraction(c_to_k(-15.0), 1.0, 10.0)
    assert r.status == "not_supersaturated" and r.fraction == 0.0


def test_fraction_above_one_is_flagged_not_clipped():
    r = agi.active_fraction(c_to_k(-30.0), 1.01, 10.0)
    assert r.status == "above_one" and r.fraction > 1 and r.inp_per_L is None


def test_colder_and_wetter_give_more_ice():
    T = c_to_k(np.array([-6.0, -10.0, -20.0, -30.0]))
    assert np.all(np.diff(agi.fraction_curve(T, 1.002)) > 0)
    S = np.array([1.001, 1.002, 1.005, 1.01])
    assert np.all(np.diff(agi.fraction_curve(c_to_k(-15.0), S)) > 0)


def test_inp_scales_linearly_with_agi_amount():
    r1 = agi.active_fraction(c_to_k(-15.0), 1.002, 1.0)
    r10 = agi.active_fraction(c_to_k(-15.0), 1.002, 10.0)
    assert r10.inp_per_L == pytest.approx(10 * r1.inp_per_L)


def test_bad_inputs_rejected():
    with pytest.raises(ValueError):
        agi.active_fraction(-15.0, 1.002, 10.0)      # degC instead of K
    with pytest.raises(ValueError):
        agi.active_fraction(c_to_k(-15.0), 1.002, -1.0)
