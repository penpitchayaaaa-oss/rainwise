"""Database files and app smoke tests."""
import os

import pytest

from models import constants as C


def test_database_loads_and_is_positive():
    vals = C.load_constants()
    assert len(vals) >= 8 and all(v > 0 for v in vals.values())
    assert set(C.SALTS) >= {"NaCl", "CaCl2"}
    assert C.SALTS["CaCl2"]["i"] == 3 and C.SALTS["NaCl"]["i"] == 2


AppTest = pytest.importorskip("streamlit.testing.v1").AppTest
APP = os.path.join(os.path.dirname(__file__), "..", "app.py")


def test_app_runs_with_defaults():
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception


def test_app_handles_changed_inputs():
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.multiselect(key="w_salts").set_value(["NaCl", "custom"]).run()
    at.number_input(key="w_d_nm").set_value(3000.0).run()
    at.number_input(key="c_T_C").set_value(-35.0).run()
    at.number_input(key="c_Sw").set_value(1.02).run()      # F > 1 -> warning, no INP
    at.number_input(key="c_N").set_value(100.0).run()
    at.number_input(key="c_T_C").set_value(-2.0).run()     # too warm
    assert not at.exception


def test_salt_library_edits():
    import pandas as pd
    from utils.library import apply_edits, to_salts
    base = pd.read_csv(C.SALTS_FILE)
    edits = {"edited_rows": {0: {"ions_i": 2}}, "deleted_rows": [1],
             "added_rows": [{"key": "KCl", "label": "KCl", "M_g_per_mol": 74.55, "density_g_per_cm3": 1.98,
                             "ions_i": 2, "source": "CRC"}, {"label": "Bad", "M_g_per_mol": -1}]}
    df = apply_edits(base, edits)
    salts, problems = to_salts(df)
    assert set(salts) == {"NaCl", "KCl"} and len(problems) == 1
    assert salts["KCl"]["M"] == pytest.approx(0.07455)
