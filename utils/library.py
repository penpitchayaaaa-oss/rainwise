"""Editable salt library: the base table (data/salts.csv) plus the user's edits from the in-app table.

Pure functions so they can be tested without Streamlit.
"""
from __future__ import annotations

import math

import pandas as pd

from models.constants import make_salt

COLUMNS = ["key", "label", "M_g_per_mol", "density_g_per_cm3", "ions_i", "source"]


def apply_edits(base: pd.DataFrame, edits: dict | None) -> pd.DataFrame:
    """Apply st.data_editor deltas {edited_rows, deleted_rows, added_rows} to the base table."""
    df = base.copy().reset_index(drop=True)
    if not edits:
        return df
    for idx, change in (edits.get("edited_rows") or {}).items():
        for col, val in change.items():
            df.at[int(idx), col] = val
    deleted = [int(i) for i in (edits.get("deleted_rows") or [])]
    if deleted:
        df = df.drop(index=deleted)
    added = [r for r in (edits.get("added_rows") or []) if r]
    if added:
        df = pd.concat([df, pd.DataFrame(added)], ignore_index=True)
    for c in COLUMNS:
        if c not in df.columns:
            df[c] = None
    return df[COLUMNS].reset_index(drop=True)


def _blank(v) -> bool:
    return v is None or (isinstance(v, float) and math.isnan(v)) or str(v).strip() == ""


def to_salts(df: pd.DataFrame) -> tuple[dict, list[str]]:
    """Convert the table to {key: salt properties}; returns (salts, problems)."""
    salts, problems = {}, []
    for n, row in df.iterrows():
        if all(_blank(row.get(c)) for c in COLUMNS):
            continue
        label = "" if _blank(row.get("label")) else str(row["label"]).strip()
        key = "" if _blank(row.get("key")) else str(row["key"]).strip()
        key = key or label
        name = label or key or f"row {n + 1}"
        try:
            if not key:
                raise ValueError
            salt = make_salt(key, label or key, float(row["M_g_per_mol"]), float(row["density_g_per_cm3"]),
                             int(float(row["ions_i"])))
        except (TypeError, ValueError):
            problems.append(f"{name}: needs a name, a positive molar mass and density, and ions i ≥ 1")
            continue
        if key in salts:
            problems.append(f"{name}: the key '{key}' is used twice; only the first row is used")
            continue
        salts[key] = salt
    return salts, problems
