"""RAINWISE - the thermodynamics of cloud seeding, made interactive.

Run:  streamlit run app.py      (Windows: double-click run_app.bat)
Physics lives in models/ (warm.py, cold.py); this file is layout and wording only.
"""
from __future__ import annotations

import inspect
import os

import pandas as pd
import streamlit as st

from models import cold, warm
from models.constants import CONSTANTS_FILE, GAMMA_IW, SALTS_FILE, SIGMA_W, THETA_AGI, c_to_k
from utils import plots
from utils import theme as ui
from utils.library import COLUMNS as SALT_COLUMNS
from utils.library import apply_edits, to_salts

st.set_page_config(page_title="RAINWISE — Cloud Seeding Thermodynamics", page_icon=":material/water_drop:",
                   layout="wide", initial_sidebar_state="collapsed")

# On the public website (Streamlit Community Cloud mounts the repo under /mount/src) nothing is written to disk.
PUBLIC = os.path.exists("/mount/src") or os.environ.get("RAINWISE_PUBLIC") == "1"
AGI_ONSET_C = -4.0   # AgI starts to work at about -4 to -5 degC (course notes; Marcolli et al., 2016)
DEFAULTS = {"w_salts": ["NaCl", "CaCl2"], "w_d_nm": 100.0, "w_T_C": 15.0, "w_s": 0.30, "w_parts": True,
            "w_r_um": 0.1, "w_sigma": SIGMA_W * 1000, "c_T_C": -10.0, "c_theta": float(THETA_AGI),
            "c_gamma": GAMMA_IW * 1000}
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)

# ---- editable salt library: base table from data/salts.csv + edits made in the in-app table
if "salt_base" not in st.session_state:
    st.session_state["salt_base"] = pd.read_csv(SALTS_FILE)
    st.session_state["salt_ver"] = 0
EDITOR_KEY = f"salt_editor_{st.session_state['salt_ver']}"
SALT_TABLE = apply_edits(st.session_state["salt_base"], st.session_state.get(EDITOR_KEY))
LIBRARY, LIBRARY_PROBLEMS = to_salts(SALT_TABLE)
st.session_state["w_salts"] = [k for k in st.session_state["w_salts"] if k in LIBRARY]


def reset(prefix: str) -> None:
    for k, v in DEFAULTS.items():
        if k.startswith(prefix):
            st.session_state[k] = v


def html(s: str) -> None:
    st.markdown(s, unsafe_allow_html=True)


def sub(label: str) -> str:
    return "".join(f"<sub>{c}</sub>" if c.isdigit() else c for c in label.replace("₂", "2").replace("₃", "3"))


def save_salts() -> None:
    table = apply_edits(st.session_state["salt_base"], st.session_state.get(EDITOR_KEY))
    good, _ = to_salts(table)
    keep = table[[(str(k).strip() if pd.notna(k) and str(k).strip() else str(l).strip()) in good
                  for k, l in zip(table["key"], table["label"])]].copy()
    keep["key"] = [str(k).strip() if pd.notna(k) and str(k).strip() else str(l).strip()
                   for k, l in zip(keep["key"], keep["label"])]
    keep.to_csv(SALTS_FILE, index=False)
    st.session_state["salt_base"] = keep.reset_index(drop=True)
    st.session_state["salt_ver"] += 1
    st.session_state["salt_msg"] = f"Saved {len(keep)} salts to data/salts.csv."


def reload_salts() -> None:
    st.session_state["salt_base"] = pd.read_csv(SALTS_FILE)
    st.session_state["salt_ver"] += 1
    st.session_state["salt_msg"] = "Reloaded data/salts.csv; unsaved edits were discarded."


REPO = "https://github.com/penpitchayaaaa-oss/rainwise"


def code_link(obj) -> str:
    """Link to the exact lines of a function or class on GitHub."""
    file = os.path.relpath(inspect.getsourcefile(obj), os.path.dirname(os.path.abspath(__file__))).replace(os.sep, "/")
    lines, start = inspect.getsourcelines(obj)
    return (f'<a href="{REPO}/blob/main/{file}#L{start}-L{start + len(lines) - 1}" target="_blank">'
            f'{os.path.basename(file)} · line {start}</a>')


def data_link(name: str) -> str:
    return f'<a href="{REPO}/blob/main/data/{name}" target="_blank">{name}</a>'


def repo_link(path: str, text: str) -> str:
    return f'<a href="{REPO}/tree/main/{path}" target="_blank">{text}</a>'


SYMBOLS = {"R": "R", "k_B": "k<sub>B</sub>", "T0": "T<sub>0</sub>", "p_tp": "p<sub>tp</sub>", "M_w": "M<sub>w</sub>",
           "rho_w": "ρ<sub>w</sub>", "rho_ice": "ρ<sub>ice</sub>", "sigma_w": "γ (σ<sub>w</sub>)",
           "dh_vap": "Δh<sub>vap</sub>", "dh_fus": "Δh<sub>fus</sub>", "gamma_iw": "γ<sub>iw</sub>",
           "theta_AgI": "θ<sub>AgI</sub>"}
_PRETTY = [("p*_liq", "p*<sub>liq</sub>"), ("p*_ice", "p*<sub>ice</sub>"), ("dG_v", "ΔG<sub>v</sub>"), ("dG*", "ΔG*"),
           ("f(theta)", "f(θ)"), ("degC", "°C"), ("gamma", "γ"), ("deg", "°"), ("mol-1", "mol⁻¹"), ("K-1", "K⁻¹"),
           ("m-3", "m⁻³"), ("m-2", "m⁻²"), ("Clausius-Clapeyron", "Clausius–Clapeyron"), ("Pruss", "Pruß"),
           ("dh_", "Δh_"), ("p*_liq", "p*<sub>liq</sub>")]


def _pretty(text) -> str:
    t = str(text)
    for a, b in _PRETTY:
        t = t.replace(a, b)
    return t


def _num(v: float) -> str:
    if v != 0 and (abs(v) < 1e-3 or abs(v) >= 1e6):
        m, e = f"{v:.7g}".split("e")
        return f"{m} × 10<sup>{int(e)}</sup>".replace("-", "−")
    return f"{v:,.10g}"


def pretty_constants(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({"Symbol": [SYMBOLS.get(s, s) for s in df["symbol"]], "Name": [_pretty(n) for n in df["name"]],
                         "Value": [_num(v) for v in df["value"]], "Unit": [_pretty(u) for u in df["unit"]],
                         "Used in": [_pretty(u) for u in df["used_in"]], "Source": [_pretty(s) for s in df["source"]]})


def pretty_salts(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({"Salt": [sub(str(l)) if str(l) else str(k) for k, l in zip(df["key"], df["label"])],
                         "M<sub>s</sub> [g mol⁻¹]": df["M_g_per_mol"], "ρ<sub>s</sub> [g cm⁻³]": df["density_g_per_cm3"],
                         "Ions i": df["ions_i"], "Source": df["source"]})


def size(m: float) -> str:
    return f"{m * 1e9:,.0f} nm" if m < 1e-6 else f"{m * 1e6:.3g} µm"


# =============================================================================== header + hero
html(ui.CSS)
html(ui.INTRO_CSS)
html(ui.nav())
html(f"""
<div class="rw-hero">
  <div>
    <div class="rw-eyebrow">The thermodynamics of cloud seeding</div>
    <h1>Why does a seeded cloud rain?<br><em>Thermodynamics</em> explains it.</h1>
    <p class="lead">RAINWISE turns the physics behind Royal Rainmaking into a model you can test. Pick a seeding
    agent, set the cloud conditions and see whether droplets and ice crystals can grow, using five
    textbook principles.</p>
    <div class="rw-chips"><span class="rw-chip">Kelvin effect</span><span class="rw-chip">Raoult's law</span>
    <span class="rw-chip">Köhler curve</span><span class="rw-chip">Nucleation theory</span>
    <span class="rw-chip">Clausius–Clapeyron</span></div>
  </div>
  <div class="rw-hero-card">{ui.CLOUD_SVG}</div>
</div>""")

tab_over, tab_warm, tab_cold, tab_method = st.tabs(["Overview", "Warm-cloud seeding", "Cold-cloud seeding",
                                                    "How it works"])

# =============================================================================== OVERVIEW
with tab_over:
    html(ui.intro_flow())
    html(ui.section("00", "The idea", "Two kinds of cloud. Two problems. Two solutions.",
                    "Clouds are full of water, yet many never rain: their droplets or ice crystals stay too small to "
                    "fall. Cloud seeding adds particles that help them grow. Which particle works depends on whether "
                    "the cloud is above or below 0 °C."))
    html(ui.grid([
        ui.card("Warm cloud · T > 0 °C", "Problem: tiny droplets evaporate",
                "Curvature (the <b>Kelvin effect</b>) raises the vapour pressure of a small droplet, so it needs "
                "strong supersaturation to grow. <br><br><b>Solution:</b> hygroscopic salts (NaCl, CaCl₂). Dissolved salt "
                "lowers the water activity (<b>Raoult's law</b>) so droplets can grow. The <b>Köhler curve</b> shows when "
                "they <i>activate</i>.", "warm"),
        ui.card("Cold cloud · T < 0 °C", "Problem: supercooled water will not freeze",
                "Forming an ice nucleus means crossing an <b>energy barrier ΔG*</b>, so water stays liquid below 0 °C. "
                "<br><br><b>Solution:</b> silver iodide (AgI), whose ice-like surface lowers ΔG* (heterogeneous "
                "nucleation). The new crystals then grow quickly because p*<sub>ice</sub> &lt; p*<sub>liq</sub> "
                "(<b>Bergeron process</b>, from Clausius–Clapeyron).", "cold"),
    ], 2))
    html(ui.section("", "How each page is organised", "What · Where · When · Why · How · Result"))
    html(ui.grid([
        ui.card("01 · What", "The method", "What is sprayed into the cloud, and what it does.", ""),
        ui.card("02 · Where", "The cloud", "Cloud type, typical altitude and temperature.", ""),
        ui.card("03 · When", "The timing", "The weather and cloud stage at which each seeding step starts.", ""),
    ], 3))
    st.write("")
    html(ui.grid([
        ui.card("04 · Why", "The physics", "The thermodynamic reason the cloud does not rain by itself.", ""),
        ui.card("05 · How", "Pain point → solution", "How the seeding agent removes that obstacle.", ""),
        ui.card("06 · Result", "The equation, then the simulator",
                "The governing curve, with an interactive model to test any agent, size and temperature.", ""),
    ], 3))

# =============================================================================== WARM CLOUD
with tab_warm:
    html(ui.section("01", "What", "Hygroscopic seeding gives water vapour a better place to condense.",
                    "Salt particles such as NaCl or CaCl₂ are released into the updraft below a warm cloud. They absorb "
                    "water, dissolve, and become large solution droplets. These grow faster than natural droplets, "
                    "collide and merge with smaller ones (<b>collision–coalescence</b>), and become heavy enough to fall."))
    c1, c2 = st.columns([1.1, 1], gap="large")
    with c1:
        html('<div class="rw-card"><div class="tag" style="color:#1D4ED8">Collision–coalescence</div>'
             '<ol class="rw-steps"><li>Droplets of different sizes fall at different speeds.</li>'
             '<li>Large droplets fall faster and sweep up small ones in their path.</li>'
             '<li>The droplets merge into larger drops.</li>'
             '<li>Once heavy enough, the drops fall as rain.</li></ol></div>')
        html(ui.COALESCENCE_SVG)
    with c2:
        html(ui.section("02", "Where", "Inside a warm cloud"))
        html(ui.facts([("Cloud", "Warm", "liquid water only"), ("Altitude", "~1,000 m", "≈ 3,000 ft"),
                       ("Temperature", "> 0 °C", "no ice involved")]))

    html(ui.section("03", "When", "Seed in the morning, while the clouds are still growing.",
                    "In the Royal Rainmaking technique the warm-cloud steps follow the life of the cloud. Each step starts "
                    "only when the weather and the cloud reach a set condition (Department of Royal Rainmaking and "
                    "Agricultural Aviation)."))
    html(ui.grid([
        ui.card("Step 1 · Triggering", "Morning, RH ≥ 60 %",
                "Starts when the sky is clear or has a few cumulus and the average relative humidity is at least "
                "60 %. NaCl is dispersed upwind at 7,000–8,000 ft to start cloud formation.", "warm"),
        ui.card("Step 2 · Fattening", "Cloud tops reach 10,000 ft",
                "CaCl₂ is released into the clouds at about 8,000 ft. Its heat of dissolution strengthens the updraft "
                "and the droplets keep growing.", "warm"),
        ui.card("Step 3 · Attacking (sandwich)", "Tops ≥ 10,000 ft, moving to target",
                "Two aircraft fly together: NaCl near the cloud top (~9,000 ft) and urea about 1,000 ft above the "
                "cloud base, to make the mature cloud rain over the target.", "warm"),
        ui.card("Step 4 · Enhancing", "After the attack",
                "Dry ice is released about 1,000 ft below the cloud base to cool the air and help the rain fall.", "warm"),
    ], 4))
    html('<p class="rw-note" style="margin-top:10px">A cloud counts as <b>warm</b> while its top is warmer than 0 °C. '
         'Thermodynamic link: salt must be in the cloud while the supersaturation is building, so the large salt '
         'particles (lowest S<sub>c</sub>) activate first.</p>')

    html(ui.section("04", "Why", "Small droplets evaporate, which is the Kelvin effect.",
                    "A curved surface holds its molecules less tightly than a flat one. The equilibrium vapour pressure "
                    "above a small droplet is therefore higher. Unless the air is strongly supersaturated, a newborn "
                    "droplet evaporates before it can grow."))
    c1, c2 = st.columns([1, 1.35], gap="large")
    with c1:
        html(ui.KELVIN_SVG)
        with st.container(border=True, key="eq_kelvin"):
            st.latex(r"p_{eq}(r)=p_{eq,\,flat}\,\exp\!\left(\frac{2\gamma V_m}{rRT}\right)")
            st.latex(r"S=\frac{p_v}{p_{sat}},\qquad s=S-1")
            html('<p class="rw-note">p<sub>eq</sub>: equilibrium vapour pressure over the droplet · γ: surface tension · '
                 'V<sub>m</sub>: molar volume of water · r: droplet radius · S: saturation ratio · s: supersaturation.<br>'
                 'The smaller r is, the larger p<sub>eq</sub> becomes.</p>')
        st.slider(r"Try a pure-water droplet radius $r$ [µm]", 0.01, 2.0, key="w_r_um", step=0.01)
        r_try = st.session_state["w_r_um"]
        need = float(warm.kelvin_supersaturation(r_try * 1e-6, c_to_k(st.session_state["w_T_C"]),
                                                 st.session_state["w_sigma"] / 1000)) * 100
        html(f'<p class="rw-note">A pure-water droplet of <b>{r_try:g} µm</b> needs <b>s = {need:.3g} %</b> to stay '
             f'in equilibrium. Real clouds rarely exceed about 1 %.</p>')
    with c2:
        st.plotly_chart(plots.kelvin_only(c_to_k(st.session_state["w_T_C"]), r_try, st.session_state["w_sigma"] / 1000),
                        width="stretch")

    html(ui.section("05", "How", "Add salt and Raoult's law lowers the vapour pressure."))
    html(ui.grid([
        ui.card("Pain point", "Too much supersaturation needed",
                "For water vapour to condense on tiny droplets, the air must be far more supersaturated than real "
                "clouds provide. Without help, droplets stay small and the cloud does not rain.", "pain"),
        ui.card("Solution", "Hygroscopic salts: NaCl, CaCl₂",
                "When salt dissolves in a droplet, the water activity a<sub>w</sub> drops below 1. The vapour pressure "
                "of water over the solution is lower than over pure water, so vapour condenses more easily and the "
                "droplet can keep growing.", "sol"),
    ], 2))
    st.write("")
    with st.container(border=True, key="eq_raoult"):
        st.latex(r"p_w = a_w\,p^{*}_w \qquad (a_w<1 \;\Rightarrow\; p_w<p^{*}_w)")
        html('<p class="rw-note" style="text-align:center">p<sub>w</sub>: vapour pressure of water over the solution · '
             'a<sub>w</sub>: water activity · p*<sub>w</sub>: vapour pressure of pure water</p>')
    st.plotly_chart(plots.explain_raoult(c_to_k(15.0)), width="stretch", key="fig_raoult")
    html('<p class="rw-figcap">Figure — the red curve is a drop of pure water; the blue curve is the same drop with '
         'dissolved NaCl (100 nm dry particle, 15 °C). The salt pulls the whole curve down, so the drop can grow in a '
         'normal cloud.</p>')

    html(ui.section("06", "Result", "The Köhler curve combines both effects.",
                    "Adding the Kelvin (curvature) and Raoult (solute) effects gives the equilibrium supersaturation of a "
                    "solution droplet of radius r. The peak of the curve is the critical point."))
    c1, c2 = st.columns([1, 1], gap="large")
    with c1:
        with st.container(border=True, key="eq_kohler"):
            st.latex(r"S_{eq}-1=\frac{A}{r}-\frac{B}{r^{3}}")
            st.latex(r"A=\frac{2\gamma M_w}{RT\rho_w},\qquad B=\frac{3\,i\,m_s M_w}{4\pi\rho_w M_s}")
            st.latex(r"r_c=\sqrt{\frac{3B}{A}},\qquad S_c-1=\sqrt{\frac{4A^{3}}{27B}}")
            html('<p class="rw-note">A/r: Kelvin effect · −B/r³: Raoult effect · i: ions per formula unit (NaCl 2, CaCl₂ 3) · '
                 'm<sub>s</sub>, M<sub>s</sub>: mass and molar mass of dissolved salt · r<sub>c</sub>: critical radius · '
                 'S<sub>c</sub>: critical supersaturation.</p>')
    case_placeholder = c2.empty()
    st.plotly_chart(plots.explain_koehler(c_to_k(15.0)), width="stretch", key="fig_koehler")
    html('<p class="rw-figcap">Figure — how to read the Köhler curve. Red dashed: the Kelvin effect pushes the needed '
         'supersaturation up for small drops. Green dashed: the dissolved salt pulls it down. Black: the sum. Left of the '
         'peak the drop is a stable haze droplet; once the cloud\'s supersaturation (blue dotted line) is above the peak, '
         'the drop passes r<sub>c</sub> and keeps growing (Case 2).</p>')

    # ---------------------------------------------------------------- simulator
    html(ui.section("▶", "Simulator", "Will this salt particle become a cloud droplet?",
                    "Change the inputs on the left. The results and charts update instantly."))
    left, right = st.columns([1, 2.4], gap="large")
    with left:
        with st.container(border=True, key="card_w_in"):
            html('<div class="rw-panel-title">Seeding agent</div>')
            salts = st.multiselect("Salt", list(LIBRARY), key="w_salts", label_visibility="collapsed",
                                   format_func=lambda s: LIBRARY[s]["label"])
            html('<p class="rw-note">Need another salt? Add it in the <b>Salt library</b> table below.</p>')
            html('<div class="rw-panel-title">Particle</div>')
            st.number_input(r"Dry salt diameter $D_{dry}$ [nm]", 20.0, 10000.0, key="w_d_nm", step=10.0,
                            help="Size of the salt crystal before it takes up water. 1 µm = 1000 nm. "
                                 "Seeding powders are typically 1–5 µm.")
            html('<div class="rw-panel-title">Cloud</div>')
            st.number_input(r"Temperature $T$ [°C]", 0.0, 40.0, key="w_T_C", step=1.0,
                            help="Warm cloud, so above 0 °C. Enters the Kelvin term A.")
            st.number_input(r"Ambient supersaturation $s$ [%]", 0.0, 3.0, key="w_s", step=0.05,
                            help="How far the air is above saturation: s = 0.3 % means RH = 100.3 %. "
                                 "Typical clouds: 0.1–1 %.")
            st.toggle("Show Kelvin and Raoult terms on the chart", key="w_parts")
            with st.expander("Advanced"):
                st.number_input(r"Surface tension of water $\gamma$ [mJ m⁻²]", 50.0, 80.0, key="w_sigma", step=0.5,
                                help="Default 72 mJ m⁻² from data/constants.csv.")
            st.button("Reset", on_click=reset, args=("w_",), width="stretch")
    with right:
        if not salts:
            st.info("Select at least one salt.")
        else:
            try:
                T_K = c_to_k(st.session_state["w_T_C"])
                d_m = st.session_state["w_d_nm"] * 1e-9
                s_amb = st.session_state["w_s"]
                sigma = st.session_state["w_sigma"] / 1000
                props = [LIBRARY[s] for s in salts]
                res = [warm.analyse(p, d_m, T_K, s_amb, sigma) for p in props]
                for r in res:
                    lab = sub(r.label)
                    if r.activates:
                        html(ui.verdict(True, f"{lab} activates and becomes a cloud droplet",
                                        f"The cloud's supersaturation ({s_amb:g} %) is above the critical value S<sub>c</sub> − 1 = "
                                        f"{r.s_c_pct:.3g} %, so the droplet grows past r<sub>c</sub> = {size(r.r_c_m)} and keeps growing."))
                    else:
                        html(ui.verdict(False, f"{lab} does not activate",
                                        f"The cloud's supersaturation ({s_amb:g} %) is below S<sub>c</sub> − 1 = {r.s_c_pct:.3g} %, so the "
                                        f"droplet stays at a small equilibrium size. Use a larger particle or a wetter cloud."))
                for r in res:
                    lab = sub(r.label)
                    html(f'<div class="rw-salt">{lab} · dry diameter {size(d_m)}</div>' + ui.kpis([
                        ("Critical radius r<sub>c</sub>", size(r.r_c_m), "the top of the Köhler curve", "",
                         "critical radius = √(3B/A)"),
                        ("Critical supersaturation", f"{r.s_c_pct:.3g} %", "S<sub>c</sub> − 1 (lower = easier)", "",
                         "critical supersaturation = √(4A³/27B)"),
                        ("Cloud − critical", f"{r.margin_pct:+.3g} %", "positive = activates",
                         "ok" if r.activates else "no", "cloud supersaturation minus critical supersaturation"),
                        ("Without salt", f"{r.pure_water_same_size_pct:.3g} %", "pure-water drop of the same size", "",
                         "Kelvin equation only: exp(A/r) − 1, with r = half the dry diameter"),
                    ]))
                g1, g2 = st.tabs(["Köhler curve", "Critical supersaturation vs size"])
                with g1:
                    st.plotly_chart(plots.koehler(res, s_amb, st.session_state["w_parts"]), width="stretch")
                with g2:
                    st.plotly_chart(plots.critical_vs_size(props, T_K, s_amb, d_m, sigma), width="stretch")
                with st.expander("Calculation details"):
                    st.dataframe(pd.DataFrame([{
                        "salt": r.label, "ions i": p["i"], "molar mass [g/mol]": round(p["M"] * 1000, 3), "density [g/cm³]": p["rho"] / 1000,
                        "salt mass [kg]": f"{warm.salt_mass(p, d_m):.3e}",
                        "A [m]": f"{r.A_m:.4e}", "B [m³]": f"{r.B_m3:.4e}", "critical radius [µm]": round(r.r_c_m * 1e6, 4),
                        "critical supersaturation [%]": round(r.s_c_pct, 4), "activates": "yes" if r.activates else "no"} for r, p in zip(res, props)]),
                        hide_index=True, width="stretch")
                any_act = any(r.activates for r in res)
                case_placeholder.markdown(
                    f'<div class="rw-case {"" if any_act else "on"}"><div class="t">Case 1 · S &lt; S<sub>c</sub></div>'
                    '<span class="rw-note">The droplet cannot pass the critical radius. A droplet smaller than the '
                    'stable equilibrium grows up to it, and one larger shrinks back. It stays a haze droplet.</span></div><br>'
                    f'<div class="rw-case {"on" if any_act else ""}"><div class="t">Case 2 · S ≥ S<sub>c</sub>: droplet activation</div>'
                    '<span class="rw-note">The droplet passes r<sub>c</sub> and keeps growing by condensation. This is '
                    'the step that turns a salt particle into a cloud droplet.</span></div>'
                    '<p class="rw-note" style="margin-top:10px">The highlighted case is the one that applies to the '
                    'simulator settings below.</p>', unsafe_allow_html=True)
            except ValueError as exc:
                st.error(f"Cannot calculate with these inputs: {exc}")

    # ---------------------------------------------------------------- salt library (editable)
    html(ui.section("＋", "Salt library", "Add your own salt",
                    "The Köhler B term needs only three properties of a salt: molar mass M<sub>s</sub>, density "
                    "ρ<sub>s</sub> and the number of ions i it releases. Edit a cell, or click <b>+</b> under the table "
                    "to add a row. New salts appear in the simulator straight away."))
    lib_l, lib_r = st.columns([2.4, 1], gap="large")
    with lib_l:
        st.data_editor(
            st.session_state["salt_base"], key=EDITOR_KEY, num_rows="dynamic", hide_index=True, width="stretch",
            column_order=SALT_COLUMNS,
            column_config={
                "key": st.column_config.TextColumn("Key", help="Short unique ID, e.g. KCl"),
                "label": st.column_config.TextColumn("Name shown", help="Use ₂ ₃ for subscripts, e.g. MgCl₂"),
                "M_g_per_mol": st.column_config.NumberColumn("Molar mass [g mol⁻¹]", min_value=0.0, format="%.2f"),
                "density_g_per_cm3": st.column_config.NumberColumn("Density [g cm⁻³]", min_value=0.0, format="%.3f"),
                "ions_i": st.column_config.NumberColumn("Ions i", min_value=1, max_value=10, step=1,
                                                        help="Ions released on full dissociation: KCl 2, MgCl₂ 3"),
                "source": st.column_config.TextColumn("Source", help="Where the values come from"),
            })
        for msg in LIBRARY_PROBLEMS:
            st.warning(msg)
    with lib_r:
        with st.container(border=True, key="card_lib"):
            html('<div class="rw-panel-title">Examples you can add</div>'
                 '<p class="rw-note">KCl · 74.55 g mol⁻¹ · 1.98 g cm⁻³ · i = 2<br>'
                 'MgCl₂ · 95.21 g mol⁻¹ · 2.32 g cm⁻³ · i = 3<br>'
                 '(NH₄)₂SO₄ · 132.14 g mol⁻¹ · 1.77 g cm⁻³ · i = 3<br>Values from the CRC Handbook.</p>')
            if PUBLIC:
                html('<p class="rw-note">On the public website your edits stay in your own session only. '
                     'Download the table to keep it.</p>')
                st.download_button("Download this table", SALT_TABLE.to_csv(index=False).encode(), "salts.csv",
                                   width="stretch", type="primary")
            else:
                st.button("Save to data/salts.csv", on_click=save_salts, width="stretch", type="primary",
                          help="Makes the table permanent. Without saving, edits last until the app is closed.")
            st.button("Discard edits", on_click=reload_salts, width="stretch")
            if st.session_state.get("salt_msg"):
                html(f'<p class="rw-note">{st.session_state.pop("salt_msg")}</p>')

# =============================================================================== COLD CLOUD
with tab_cold:
    html(ui.section("01", "What", "Glaciogenic seeding helps supercooled water turn into ice.",
                    "A cold cloud holds water droplets below 0 °C that have not frozen, called <b>supercooled water</b>. "
                    "Seeding with silver iodide (AgI) provides <b>ice-nucleating particles</b> that let ice form easily."))
    c1, c2 = st.columns([1.1, 1], gap="large")
    with c1:
        html('<div class="rw-card"><div class="tag" style="color:#0369A1">From vapour to snow to rain</div>'
             '<ol class="rw-steps"><li>The cloud holds droplets below 0 °C that are still liquid (supercooled water).</li>'
             '<li>AgI acts as an ice-nucleating particle: water molecules arrange into ice on its surface '
             '(heterogeneous nucleation), because the energy barrier is lower.</li>'
             '<li>The ice crystal grows as vapour deposits on it (deposition) and as it collects supercooled droplets (riming).</li>'
             '<li>The crystal becomes heavy enough to fall, and may melt into rain in air warmer than 0 °C.</li></ol></div>')
    with c2:
        html(ui.section("02", "Where", "Inside a cold cloud"))
        html(ui.facts([("Cloud", "Cold", "supercooled water + ice"), ("Altitude", "~5,500 m", "≈ 18,000 ft"),
                       ("Temperature", "< 0 °C", "ice can exist")]))

    html(ui.section("03", "When", "Seed when the cloud top is below 0 °C and still holds liquid water.",
                    "The cold-cloud steps start only when the cloud has grown tall enough for its top to be below "
                    "freezing, where supercooled droplets are waiting to be frozen (Department of Royal Rainmaking and "
                    "Agricultural Aviation)."))
    html(ui.grid([
        ui.card("Step 5 · Cold-cloud attack", "Cloud tops reach 20,000 ft",
                "AgI flares are fired at the cloud top, about 21,500 ft. Freezing releases latent heat, which makes "
                "the cloud more buoyant and strengthens the updraft.", "cold"),
        ui.card("Step 6 · Super sandwich", "Tops above 20,000 ft",
                "At least three aircraft: AgI at about 21,500 ft, NaCl at about 10,000 ft and urea at the cloud base, "
                "combining cold-cloud and warm-cloud seeding.", "cold"),
        ui.card("Condition", "Colder than about −4 to −5 °C",
                "AgI starts to work at about −4 to −5 °C, and the cloud must still contain supercooled water. "
                "The simulator below flags temperatures that are too warm.", "cold"),
    ], 3))

    html(ui.section("04", "Why", "Freezing has an energy barrier.",
                    "Making a tiny ice nucleus costs energy to create the ice–water interface, but releases energy as the "
                    "more stable ice forms. Below the critical radius r* the cost wins and the nucleus melts back. Above it, "
                    "the nucleus grows on its own."))
    c1, c2 = st.columns([1, 1], gap="large")
    with c1:
        with st.container(border=True, key="eq_cnt"):
            st.latex(r"\Delta G(r)=\underbrace{4\pi r^{2}\gamma}_{\Delta G_S\,(+)}+\underbrace{\tfrac{4}{3}\pi r^{3}\Delta G_v}_{\Delta G_V\,(-)}")
            st.latex(r"r^{*}=\frac{2\gamma}{|\Delta G_v|},\qquad \Delta G^{*}=\frac{16\pi\gamma^{3}}{3\,|\Delta G_v|^{2}}")
            html('<p class="rw-note">γ: ice–water interfacial energy · ΔG<sub>v</sub>: free-energy change per unit volume '
                 '(negative below 0 °C) · r*: critical radius · ΔG*: activation energy (the barrier).</p>')
    with c2:
        html(ui.table(pd.DataFrame({"Size": ["r < r*", "r = r*", "r > r*"],
                                    "Behaviour": ["Unstable: the nucleus shrinks and disappears",
                                                  "At the top of the barrier: unstable equilibrium",
                                                  "Grows on its own and lowers its energy"]})))
        html('<p class="rw-note">The driving force comes from the vapour-pressure difference between supercooled water '
             'and ice: ΔG<sub>v</sub> = −(ρ<sub>ice</sub>/M<sub>w</sub>) RT ln(p*<sub>liq</sub>/p*<sub>ice</sub>). '
             'At 0 °C it is zero, so the barrier is infinite. The colder the cloud, the lower the barrier.</p>')
    st.plotly_chart(plots.explain_cnt(c_to_k(-10.0), GAMMA_IW), width="stretch", key="fig_cnt")
    html('<p class="rw-figcap">Figure — making an ice embryo at −10 °C. Red dashed: building the ice–water surface costs '
         'energy (grows with r²). Blue dashed: forming the more stable ice releases energy (grows with r³). Black: the total '
         'has a hill of height ΔG* at r*. Smaller embryos melt back; larger ones keep growing.</p>')

    html(ui.section("05", "How", "AgI lowers the barrier, a process called heterogeneous nucleation."))
    html(ui.grid([
        ui.card("Pain point", "ΔG* is too high",
                "Water molecules alone (homogeneous nucleation) rarely clear the barrier, so ice nuclei do not form and "
                "supercooled water can persist to about −38 °C.", "pain"),
        ui.card("Solution", "Silver iodide, or dry ice",
                "<b>AgI</b> has a crystal structure close to ice, so water molecules arrange into ice on its surface and "
                "ΔG* drops. AgI starts working around −4 to −5 °C. <b>Dry ice</b> (−78.5 °C) instead cools the air "
                "until water freezes on its own.", "sol"),
    ], 2))
    st.write("")
    c1, c2 = st.columns([1, 1], gap="large")
    with c1:
        with st.container(border=True, key="eq_het"):
            st.latex(r"\Delta G^{*}_{het}=f(\theta)\,\Delta G^{*}_{hom},\qquad f(\theta)=\frac{(2+\cos\theta)(1-\cos\theta)^{2}}{4}")
            html('<p class="rw-note">This is how heterogeneous nucleation is usually quantified in classical nucleation '
                 'theory (Fletcher, 1958). θ is the contact angle of the ice embryo on the particle. θ → 0° means a perfect '
                 'template (f → 0, no barrier) and θ = 180° means no help (f = 1). r* does not change; only the height of '
                 'the barrier does.</p>')
    with c2:
        html(ui.card("Value used", "θ ≈ 45° for AgI",
                     "Marcolli et al. (2016) report a contact angle of 45–50° for AgI. The simulator starts at 45° and "
                     "lets you vary it. Treat it as a representative value, not a precise property.", ""))
    st.plotly_chart(plots.free_energy(cold.analyse(c_to_k(-10.0), THETA_AGI)), width="stretch", key="fig_het")
    html('<p class="rw-figcap">Figure — the same −10 °C ice embryo in pure water (grey) and on AgI (blue). The critical '
         'radius r* is the same, but the hill is about 17 times lower on AgI, so ice forms much more easily.</p>')

    html(ui.section("06", "Result", "Once ice exists, it grows at the droplets' expense.",
                    "Clausius–Clapeyron with Δh<sub>sub</sub> = Δh<sub>vap</sub> + Δh<sub>fus</sub> shows that below 0 °C "
                    "the vapour pressure over ice is lower than over supercooled water. Vapour leaves the droplets and "
                    "deposits on the crystals: the <b>Wegener–Bergeron–Findeisen (Bergeron) process</b>."))
    with st.container(border=True, key="eq_cc"):
        st.latex(r"\frac{d\ln p^{*}}{d(1/T)}=-\frac{\Delta h}{R};\qquad \Delta h_{sub}=\Delta h_{vap}+\Delta h_{fus}"
                 r"\;\Rightarrow\; p^{*}_{ice}<p^{*}_{liq}\ \text{for}\ T<0\,^{\circ}\mathrm{C}")
    b1, b2 = st.columns([1, 1.35], gap="large")
    with b1:
        html(ui.BERGERON_SVG)
        html('<p class="rw-figcap">The air around a droplet and an ice crystal is the same, but ice holds its molecules '
             'more tightly (lower p*). Vapour therefore flows from the droplet to the crystal.</p>')
    with b2:
        st.plotly_chart(plots.bergeron(-10.0), width="stretch", key="fig_bergeron")
        html('<p class="rw-figcap">Figure — vapour pressure over supercooled water (light blue) and over ice (dark blue) from '
             'Clausius–Clapeyron. The orange line shows how supersaturated the air is for ice when it is just saturated for '
             'water: about 10 % at −10 °C and 23 % at −20 °C.</p>')

    # ---------------------------------------------------------------- simulator
    html(ui.section("▶", "Simulator", "How much does AgI lower the barrier at this temperature?",
                    "Change the cloud temperature and the AgI contact angle. The barrier is shown in joules and as a "
                    "multiple of kT, the thermal energy a molecule has to work with."))
    left, right = st.columns([1, 2.4], gap="large")
    with left:
        with st.container(border=True, key="card_c_in"):
            html('<div class="rw-panel-title">Cloud</div>')
            st.number_input(r"Temperature $T$ [°C]", -40.0, -1.0, key="c_T_C", step=1.0,
                            help="Cold cloud: below 0 °C. At 0 °C the barrier is infinite.")
            html('<div class="rw-panel-title">Seeding agent: AgI</div>')
            st.slider(r"Contact angle $\theta$ [°]", 0.0, 180.0, key="c_theta", step=1.0,
                      help="45–50° reported for AgI (Marcolli et al., 2016). 180° = no help (homogeneous).")
            html(f'<p class="rw-note">f(θ) = <b>{cold.wetting_factor(st.session_state["c_theta"]):.3f}</b>, the fraction '
                 'of the homogeneous barrier left on AgI.</p>')
            with st.expander("Advanced"):
                st.number_input(r"Ice–water interfacial energy $\gamma$ [mJ m⁻²]", 10.0, 40.0, key="c_gamma", step=0.5,
                                help="Default 22.5 mJ m⁻² (Tarn et al., 2021, near −36 °C), held constant.")
            st.button("Reset ", on_click=reset, args=("c_",), width="stretch")
    with right:
        try:
            T_C = st.session_state["c_T_C"]
            res = cold.analyse(c_to_k(T_C), st.session_state["c_theta"], st.session_state["c_gamma"] / 1000)
            if T_C > AGI_ONSET_C:
                html(ui.verdict(False, "Too warm for AgI to work yet",
                                f"At {T_C:g} °C the cloud is warmer than about −4 to −5 °C, where AgI starts to nucleate ice. "
                                "The barrier is still lowered on paper, but in practice seeding waits until the cloud top is "
                                "colder (Step 5 needs cloud tops of about 20,000 ft)."))
            html(ui.verdict(True, f"AgI lowers the barrier by {res.reduction_pct:.0f} %",
                            f"At {T_C:g} °C, forming an ice nucleus in pure water costs ΔG* ≈ {res.dG_hom_kT:,.0f} kT. "
                            f"On AgI it costs ≈ {res.dG_het_kT:,.1f} kT. Once ice forms, the air, which is saturated for "
                            f"the droplets, is {res.ice_supersaturation_pct:.1f} % supersaturated for ice, so the crystals grow."))
            html(ui.kpis([
                ("Critical radius r*", f"{res.r_star_m * 1e9:.2f} nm", "same with or without AgI", "", "r* = 2γ/|ΔG_v|"),
                ("Barrier, pure water", f"{res.dG_hom_kT:,.0f} kT", f"ΔG*<sub>hom</sub> = {res.dG_hom_J * 1e18:.3g} × 10⁻¹⁸ J",
                 "no", "ΔG* = 16πγ³ / 3ΔGᵥ²"),
                ("Barrier on AgI", f"{res.dG_het_kT:,.1f} kT", f"ΔG*<sub>het</sub> = {res.dG_het_J * 1e18:.3g} × 10⁻¹⁸ J",
                 "ok", "f(θ) × barrier for pure water"),
                ("Driving force |ΔG<sub>v</sub>|", f"{abs(res.dGv) / 1e6:.3g} MJ m⁻³", "grows as T falls", "",
                 "(ρ of ice / Mw) RT ln(p*liq / p*ice)"),
            ]))
            html(ui.kpis([
                ("p*<sub>liq</sub> over supercooled water", f"{res.p_liq:.1f} Pa", "Clausius–Clapeyron, Δh<sub>vap</sub>", "", ""),
                ("p*<sub>ice</sub> over ice", f"{res.p_ice:.1f} Pa", "Clausius–Clapeyron, Δh<sub>sub</sub>", "", ""),
                ("Ice supersaturation", f"{res.ice_supersaturation_pct:.1f} %", "when air is saturated for water", "ok",
                 "p*liq / p*ice − 1"),
            ], 3))
            g1, g2, g3 = st.tabs(["Energy barrier ΔG(r)", "Barrier vs temperature", "Bergeron process"])
            with g1:
                st.plotly_chart(plots.free_energy(res), width="stretch")
            with g2:
                st.plotly_chart(plots.barrier_vs_T(st.session_state["c_theta"], res.gamma, T_C), width="stretch")
            with g3:
                st.plotly_chart(plots.bergeron(T_C), width="stretch")
        except ValueError as exc:
            st.error(f"Cannot calculate with these inputs: {exc}")

# =============================================================================== HOW IT WORKS
with tab_method:
    html(ui.section("A", "Architecture", "From your input to the number on screen",
                    "RAINWISE has no hidden model. Four plain files do all the work, and you can open each of them."))
    html('<div class="rw-flow">'
         '<div class="rw-node"><div class="k">Input</div><b>You</b><span>sliders and boxes in the simulator</span></div>'
         '<div class="rw-arrow">+</div>'
         '<div class="rw-node"><div class="k">Database</div><b>data/*.csv</b><span>constants.csv · salts.csv, each value with its source</span></div>'
         '<div class="rw-arrow">→</div>'
         '<div class="rw-node hl"><div class="k">Equations</div><b>models/</b><span>warm.py (Kelvin, Raoult, Köhler) · cold.py (CNT, Clausius–Clapeyron)</span></div>'
         '<div class="rw-arrow">→</div>'
         '<div class="rw-node"><div class="k">Output</div><b>app.py + utils/plots.py</b><span>result cards and charts</span></div>'
         '</div>')

    html(ui.section("B", "Method", "How RAINWISE was built, step by step",
                    "Eight plain steps, in the order they were done. Each one can be checked in the code."))
    html('<ol class="rw-steps rw-method">'
         '<li><b>Start from the course notes.</b> For each cloud type we asked the same questions: What is sprayed, '
         'Where and When it is done, Why the cloud does not rain by itself, How the agent helps, and what the Result '
         'is. Only the equations written in the notes were used.</li>'
         '<li><b>Write the problem as inputs and outputs.</b> Warm cloud: salt, dry size D<sub>dry</sub>, temperature T and '
         'cloud supersaturation s go in; the critical radius r<sub>c</sub>, the critical supersaturation S<sub>c</sub> and '
         '“activates or not” come out. Cold cloud: T and the AgI contact angle θ go in; the barrier ΔG* comes out.</li>'
         '<li><b>Collect every number the equations need.</b> Constants such as R, M<sub>w</sub>, ρ<sub>w</sub>, γ and '
         'Δh<sub>fus</sub> were taken from reference books and papers and written into two tables (the database below), '
         'each with its source. No number is typed inside the calculation code.</li>'
         '<li><b>Turn each equation into one small function.</b> One equation = one Python function, all in SI units '
         '(metres, kelvin, joules). For example, A = 2γM<sub>w</sub>/(RTρ<sub>w</sub>) is the function “kelvin_A”.</li>'
         '<li><b>Find the special points with calculus.</b> The peak of the Köhler curve and the top of the energy barrier are '
         'where the slope is zero (dS/dr = 0, dΔG/dr = 0). Solving these by hand gives exact formulas for r<sub>c</sub>, '
         'S<sub>c</sub>, r* and ΔG*, so the app needs no trial and error.</li>'
         '<li><b>Check the code against the maths and against real data</b> (see Verification below).</li>'
         '<li><b>Build the screens.</b> The page only collects your inputs, calls the functions and shows the answers as '
         'cards and charts. The page itself contains no physics.</li>'
         '<li><b>Publish.</b> The code is stored on GitHub and the website runs it on Streamlit Community Cloud. Any change '
         'pushed to GitHub updates the website automatically.</li></ol>')

    A_ex = warm.kelvin_A(c_to_k(15.0))
    m_ex = warm.salt_mass("NaCl", 100e-9)
    B_ex = warm.raoult_B("NaCl", 100e-9)
    rc_ex, sc_ex = warm.critical_point(A_ex, B_ex)
    html('<div class="rw-card" style="margin-top:14px"><div class="tag" style="color:#1D4ED8">Follow one number</div>'
         '<h4>Will a 100 nm NaCl particle activate in a 15 °C cloud with s = 0.3 %?</h4>'
         '<ol class="rw-steps" style="margin-top:10px">'
         f'<li>Kelvin coefficient: A = 2(0.072)(0.018015) / (8.314 × 288.15 × 997) = <b>{A_ex * 1e9:.3f} nm</b></li>'
         f'<li>Salt mass: m<sub>s</sub> = 2165 × π(100 × 10<sup>−9</sup>)<sup>3</sup>/6 = <b>{m_ex * 1e18:.3f} × 10<sup>−18</sup> kg</b></li>'
         f'<li>Raoult coefficient: B = 3 × 2 × m<sub>s</sub> × 0.018015 / (4π × 997 × 0.05844) = '
         f'<b>{B_ex * 1e22:.3f} × 10<sup>−22</sup> m<sup>3</sup></b></li>'
         f'<li>Critical radius: r<sub>c</sub> = √(3B/A) = <b>{rc_ex * 1e6:.3f} µm</b></li>'
         f'<li>Critical supersaturation: S<sub>c</sub> − 1 = √(4A<sup>3</sup>/27B) = <b>{sc_ex * 100:.3f} %</b></li>'
         f'<li>Compare: 0.3 % ≥ {sc_ex * 100:.3f} %, so the particle <b>activates</b>. These are the same numbers the '
         'simulator shows with its default settings.</li></ol></div>')

    html(ui.section("C", "Traceability", "Every number, traced to its equation and source",
                    "Click a link in the <b>Code</b> column to open the exact lines on GitHub."))
    trace = pd.DataFrame([
        ["Warm", "s needed by a pure-water droplet (“Without salt”)", "s = exp(A/r) − 1", "Exponential, closed form",
         code_link(warm.kelvin_supersaturation), "σ, M<sub>w</sub>, ρ<sub>w</sub>, R", "Kelvin equation [3, 4]"],
        ["Warm", "Kelvin coefficient A", "A = 2γM<sub>w</sub> / (RTρ<sub>w</sub>)", "Algebra",
         code_link(warm.kelvin_A), "σ, M<sub>w</sub>, ρ<sub>w</sub>, R", "Köhler (1936) [2]"],
        ["Warm", "Dissolved salt mass m<sub>s</sub>", "m<sub>s</sub> = ρ<sub>s</sub>πD<sub>dry</sub><sup>3</sup>/6",
         "Volume of a sphere", code_link(warm.salt_mass), data_link("salts.csv") + ": ρ<sub>s</sub>", "Geometry"],
        ["Warm", "Raoult coefficient B", "B = 3i m<sub>s</sub>M<sub>w</sub> / (4πρ<sub>w</sub>M<sub>s</sub>)",
         "Algebra (Raoult + van ’t Hoff i)", code_link(warm.raoult_B), data_link("salts.csv") + ": M<sub>s</sub>, i",
         "Köhler (1936) [2]; [3, 4]"],
        ["Warm", "Köhler curve", "S<sub>eq</sub> − 1 = A/r − B/r<sup>3</sup>", "Evaluated at 600 radii (log-spaced)",
         code_link(warm.koehler_s), "—", "[2, 3]"],
        ["Warm", "Critical radius r<sub>c</sub> and S<sub>c</sub>",
         "r<sub>c</sub> = √(3B/A); S<sub>c</sub> − 1 = √(4A<sup>3</sup>/27B)", "Calculus: dS/dr = 0 (maximum)",
         code_link(warm.critical_point), "—", "[3, 5]"],
        ["Warm", "Activates? (green / red)", "s ≥ S<sub>c</sub> − 1", "Comparison", code_link(warm.WarmResult),
         "your input s", "[3]"],
        ["Warm", "S<sub>c</sub> vs dry size chart", "S<sub>c</sub> at 80 diameters", "Parameter sweep",
         code_link(warm.critical_curve), "—", "[3]"],
        ["Cold", "p*<sub>liq</sub> and p*<sub>ice</sub>", "ln(p*/p<sub>tp</sub>) = −(Δh/R)(1/T − 1/T<sub>0</sub>)",
         "Integrated Clausius–Clapeyron (constant Δh)", code_link(cold.p_sat_liquid) + "<br>" + code_link(cold.p_sat_ice),
         "Δh<sub>vap</sub>, Δh<sub>fus</sub>, p<sub>tp</sub>, T<sub>0</sub>", "[3, 4]; Δh [9]; p<sub>tp</sub> [10]"],
        ["Cold", "Ice supersaturation",
         "p*<sub>liq</sub>/p*<sub>ice</sub> − 1 = exp[(Δh<sub>fus</sub>/R)(1/T − 1/T<sub>0</sub>)] − 1",
         "Ratio of the two curves", code_link(cold.liquid_to_ice_ratio), "Δh<sub>fus</sub>", "[3, 4]"],
        ["Cold", "Driving force ΔG<sub>v</sub>",
         "ΔG<sub>v</sub> = −(ρ<sub>ice</sub>/M<sub>w</sub>)RT ln(p*<sub>liq</sub>/p*<sub>ice</sub>)",
         "Chemical-potential difference per volume", code_link(cold.volume_free_energy), "ρ<sub>ice</sub>, M<sub>w</sub>", "[4]"],
        ["Cold", "Energy curve ΔG(r)", "4πr<sup>2</sup>γ + (4/3)πr<sup>3</sup>ΔG<sub>v</sub>", "Polynomial in r",
         code_link(cold.free_energy_curve), "γ<sub>iw</sub>", "Nucleation theory [4]"],
        ["Cold", "r* and ΔG*<sub>hom</sub>",
         "r* = 2γ/|ΔG<sub>v</sub>|; ΔG* = 16πγ<sup>3</sup>/(3ΔG<sub>v</sub><sup>2</sup>)", "Calculus: dΔG/dr = 0 (maximum)",
         code_link(cold.critical_nucleus), "γ<sub>iw</sub>", "[4]"],
        ["Cold", "ΔG*<sub>het</sub> on AgI", "f(θ)·ΔG*<sub>hom</sub>; f = (2 + cos θ)(1 − cos θ)<sup>2</sup>/4",
         "Spherical-cap geometry", code_link(cold.wetting_factor), "θ<sub>AgI</sub>", "Fletcher (1958) [6]; θ [7]"],
        ["Cold", "Barrier in kT", "ΔG* / (k<sub>B</sub>T)", "Division", code_link(cold.ColdResult), "k<sub>B</sub>", "CODATA [12]"],
    ], columns=["Module", "What you see", "Equation", "Mathematics", "Code", "Data used", "Reference"])
    html(ui.table(trace, ("Equation",)))

    html(ui.section("D", "Derivations", "Where the closed-form results come from"))
    d1, d2 = st.columns(2, gap="large")
    with d1:
        with st.expander(r"Köhler critical point: $r_c$ and $S_c$", expanded=True):
            st.latex(r"\frac{d}{dr}\left(\frac{A}{r}-\frac{B}{r^{3}}\right)=-\frac{A}{r^{2}}+\frac{3B}{r^{4}}=0")
            st.latex(r"\Rightarrow\; r_c=\sqrt{\frac{3B}{A}}")
            st.latex(r"S_c-1=\frac{A}{r_c}-\frac{B}{r_c^{3}}=\frac{2}{3}\frac{A}{r_c}=\sqrt{\frac{4A^{3}}{27B}}")
            html('<p class="rw-note">A larger salt particle has a larger B, so S<sub>c</sub> falls as D<sub>dry</sub><sup>−3/2</sup>.</p>')
        with st.expander("Raoult term B from the dissolved salt"):
            st.latex(r"a_w\approx1-\frac{i\,n_s}{n_w},\quad n_s=\frac{m_s}{M_s},\quad n_w=\frac{4\pi r^{3}\rho_w}{3M_w}")
            st.latex(r"\Rightarrow\; -\frac{B}{r^{3}},\qquad B=\frac{3\,i\,m_s M_w}{4\pi\rho_w M_s}")
            html('<p class="rw-note">Dilute solution with complete dissociation into i ions (ideal van \'t Hoff factor).</p>')
    with d2:
        with st.expander("Critical ice nucleus: r* and ΔG*", expanded=True):
            st.latex(r"\frac{d\Delta G}{dr}=8\pi r\gamma+4\pi r^{2}\Delta G_v=0\;\Rightarrow\; r^{*}=-\frac{2\gamma}{\Delta G_v}")
            st.latex(r"\Delta G^{*}=4\pi r^{*2}\gamma+\tfrac{4}{3}\pi r^{*3}\Delta G_v=\frac{16\pi\gamma^{3}}{3\Delta G_v^{2}}")
        with st.expander(r"Clausius–Clapeyron and $\Delta G_v$"):
            st.latex(r"\int_{p_{tp}}^{p^{*}} d\ln p=-\frac{\Delta h}{R}\int_{1/T_0}^{1/T} d\!\left(\tfrac{1}{T}\right)"
                     r"\;\Rightarrow\; p^{*}=p_{tp}\exp\!\left[-\frac{\Delta h}{R}\left(\frac{1}{T}-\frac{1}{T_0}\right)\right]")
            st.latex(r"\frac{p^{*}_{liq}}{p^{*}_{ice}}=\exp\!\left[\frac{\Delta h_{fus}}{R}\left(\frac{1}{T}-\frac{1}{T_0}\right)\right],\qquad"
                     r"\Delta G_v=-\frac{\rho_{ice}}{M_w}RT\ln\frac{p^{*}_{liq}}{p^{*}_{ice}}")
            html('<p class="rw-note">Δh is taken as constant between 0 and −40 °C, which is the main approximation.</p>')

    html(ui.section("E", "Database", "The values the equations read",
                    "Both tables are plain CSV files in the data folder: " + data_link("constants.csv") + " and "
                    + data_link("salts.csv") + ". The app reads them every time it starts."))
    cdf = pd.read_csv(CONSTANTS_FILE)
    html('<div class="rw-panel-title">Constants</div>' + ui.table(pretty_constants(cdf), ("Value",)))
    st.write("")
    html('<div class="rw-panel-title">Salts — edit them in Warm-cloud seeding → Salt library</div>'
         + ui.table(pretty_salts(SALT_TABLE.fillna("")), ()))
    st.write("")
    b1, b2, _ = st.columns([1, 1, 3])
    b1.download_button("Download constants.csv", cdf.to_csv(index=False).encode(), "constants.csv", width="stretch")
    b2.download_button("Download salts.csv", SALT_TABLE.to_csv(index=False).encode(), "salts.csv", width="stretch")

    html(ui.section("F", "Your own values", "Three ways to change an input"))
    html(ui.grid([
        ui.card("Level 1 · Simulator", "Move a slider",
                "Particle size, temperature, ambient supersaturation and the AgI contact angle are inputs on each "
                "simulator panel. Results update instantly.", ""),
        ui.card("Level 2 · Salt library & Advanced", "Try a new substance",
                "In <b>Warm-cloud seeding → Salt library</b>, edit the table or add a row with molar mass, density and "
                "number of ions i, for example KCl (74.55 g mol⁻¹, 1.98 g cm⁻³, i = 2). Click <b>Save</b> to write it to "
                "data/salts.csv. <b>Advanced</b> changes γ or γ<sub>iw</sub> for this session.", ""),
        ui.card("Level 3 · Database files", "Change a constant",
                "Edit a value in <b>data/constants.csv</b> (or data/salts.csv) with Excel or a text editor, save, then "
                "restart the app (close and reopen run_app.bat). Always fill in the <i>source</i> column.", ""),
    ], 3))

    html(ui.section("G", "Verification", "How we know the numbers are right",
                    "Every check below is written as an automated test in " + repo_link("tests", "the tests folder")
                    + ". Running <code>python -m pytest</code> repeats all 19 checks in a few seconds, and all of them pass."))
    html('<ul class="rw-checks">'
         '<li><b>Is the formula really the peak of the curve?</b> We drew the Köhler curve at 200,000 points and picked the '
         'highest one by brute force. It matches r<sub>c</sub> = √(3B/A) and S<sub>c</sub> − 1 = √(4A<sup>3</sup>/27B) to '
         'one part in a million. The same test is done for the ice barrier: ΔG at r* equals ΔG*, and the slope there is zero.</li>'
         '<li><b>Does a hand calculation give the same answer?</b> The worked example above (100 nm NaCl, 15 °C) gives '
         'S<sub>c</sub> − 1 = 0.106 % on paper and in the app.</li>'
         '<li><b>Does it agree with measured data?</b> Our Clausius–Clapeyron vapour pressures were compared with '
         'Murphy &amp; Koop (2005), a fit to laboratory measurements. Over ice the difference is under 1 % from 0 to −40 °C. '
         'Over supercooled water it is under 2 % down to −20 °C and 8 % at −40 °C.</li>'
         '<li><b>Do the trends make physical sense?</b> A bigger salt particle needs less supersaturation (exactly '
         'D<sub>dry</sub><sup>−3/2</sup>). A pure-water drop needs far more than a salty one. A colder cloud has a lower ice '
         'barrier, and AgI always gives a lower barrier than pure water. Below 0 °C, p*<sub>ice</sub> is always less than '
         'p*<sub>liq</sub>, and the two are equal at 0 °C.</li>'
         '<li><b>Do the extreme cases come out right?</b> The AgI factor gives f = 0 at θ = 0° (perfect template), '
         'f = 0.5 at 90° and f = 1 at 180° (no help).</li>'
         '<li><b>Are bad inputs caught?</b> A temperature typed in °C where kelvin is needed is refused, a salt with a '
         'negative molar mass is refused, and an incomplete row in the salt library is flagged and not used.</li>'
         '<li><b>Does the whole app run?</b> One test opens the full website and changes the inputs; another adds, edits and '
         'deletes salts in the library. Both check that nothing breaks.</li></ul>')

    html(ui.section("H", "Limits", "What this model does not do"))
    html(ui.grid([
        ui.card("Equilibrium only", "No time, no rainfall",
                "The model shows whether growth is possible, not how fast it is or how much rain falls.", ""),
        ui.card("Ideal solution", "Dilute Köhler form",
                "A/r − B/r³ assumes a dilute, fully dissociated solution. It is accurate near activation and less so "
                "for very concentrated haze droplets.", ""),
        ui.card("Constant properties", "Δh, γ, θ held fixed",
                "Clausius–Clapeyron uses constant Δh. Against Murphy &amp; Koop (2005) the ice supersaturation is "
                "10.6 % vs 10.2 % at −10 °C and 23.3 % vs 21.6 % at −20 °C. It is accurate in the usual seeding range "
                "(−5 to −20 °C) and overestimated below about −30 °C. γ<sub>iw</sub> is a single value near −36 °C.", ""),
    ], 3))

    html(ui.section("I", "References", "Sources"))
    st.markdown(
        "1. Course notes, Topic 13: Royal Rainmaking and Cloud Seeding (What / Where / Why / How / Result framework).\n"
        "2. Köhler, H. (1936). The nucleus in and the growth of hygroscopic droplets. *Trans. Faraday Soc.*, 32, 1152–1161.\n"
        "3. Wallace, J. M., & Hobbs, P. V. (2006). *Atmospheric Science: An Introductory Survey* (2nd ed.). Academic Press.\n"
        "4. Pruppacher, H. R., & Klett, J. D. (1997). *Microphysics of Clouds and Precipitation* (2nd ed.). Kluwer.\n"
        "5. Rogers, R. R., & Yau, M. K. (1989). *A Short Course in Cloud Physics* (3rd ed.). Pergamon.\n"
        "6. Fletcher, N. H. (1958). Size effect in heterogeneous nucleation. *J. Chem. Phys.*, 29, 572–576.\n"
        "7. Marcolli, C., Nagare, B., Welti, A., & Lohmann, U. (2016). Ice nucleation efficiency of AgI: review and new "
        "insights. *Atmos. Chem. Phys.*, 16, 8915–8937. doi:10.5194/acp-16-8915-2016\n"
        "8. Tarn, M. D., Sikora, S. N. F., Porter, G. C. E., Shim, J., & Murray, B. J. (2021). Homogeneous freezing of water "
        "using microfluidics. *Micromachines*, 12, 223. doi:10.3390/mi12020223\n"
        "9. Rumble, J. R. (ed.). *CRC Handbook of Chemistry and Physics*. CRC Press.\n"
        "10. Wagner, W., & Pruß, A. (2002). The IAPWS formulation 1995 for the thermodynamic properties of ordinary water "
        "substance. *J. Phys. Chem. Ref. Data*, 31, 387–535.\n"
        "11. Murphy, D. M., & Koop, T. (2005). Review of the vapour pressures of ice and supercooled water for atmospheric "
        "applications. *Q. J. R. Meteorol. Soc.*, 131, 1539–1565 (used only to check accuracy).\n"
        "12. Tiesinga, E., et al. (2021). CODATA recommended values of the fundamental physical constants: 2018. "
        "*J. Phys. Chem. Ref. Data*, 50, 033105.\n"
        "13. Department of Royal Rainmaking and Agricultural Aviation. *Royal Rainmaking Technology* (e-book, steps I–VI). "
        "ASEAN Weather Modification Centre. https://awmc.royalrain.go.th/asean/ebook_pic/1727245596.pdf")

# =============================================================================== PROTOTYPE STATUS (end of page)
html(ui.prototype_notice())
html(ui.section("", "Improvements", "What comes next",
                "The roadmap to turn the prototype into a validated tool. The first three items are the most important: "
                "the model needs to be verified against real measurements."))
html(ui.roadmap())
