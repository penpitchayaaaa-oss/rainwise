"""RAINWISE - the thermodynamics of cloud seeding, made interactive.

Run:  streamlit run app.py      (Windows: double-click run_app.bat)
Physics lives in models/ (warm.py, agi.py); this file is layout and wording only.
"""
from __future__ import annotations

import importlib
import inspect
import math
import os

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from models import agi, warm
from models.constants import CONSTANTS_FILE, SALTS_FILE, SIGMA_W, c_to_k
from utils import anim, plots
from utils import theme as ui
from utils.library import COLUMNS as SALT_COLUMNS
from utils.library import apply_edits, to_salts

# Streamlit Cloud can keep an older copy of these modules in memory after a redeploy; reload them so the
# page always uses the files that were just pushed.
plots = importlib.reload(plots)
ui = importlib.reload(ui)
anim = importlib.reload(anim)

st.set_page_config(page_title="RAINWISE — Cloud Seeding Thermodynamics", page_icon=":material/water_drop:",
                   layout="wide", initial_sidebar_state="collapsed")

# On the public website (Streamlit Community Cloud mounts the repo under /mount/src) nothing is written to disk.
PUBLIC = os.path.exists("/mount/src") or os.environ.get("RAINWISE_PUBLIC") == "1"
DEFAULTS = {"w_salts": ["NaCl", "CaCl2"], "w_d_nm": 100.0, "w_T_C": 15.0, "w_s": 0.30, "w_parts": True,
            "w_r_um": 0.1, "w_sigma": SIGMA_W * 1000, "c_T_C": -15.0, "c_Sw": 1.002, "c_N": 10.0}
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


SYMBOLS = {"R": "R", "T0": "T<sub>0</sub>", "M_w": "M<sub>w</sub>", "rho_w": "ρ<sub>w</sub>", "sigma_w": "γ (σ<sub>w</sub>)",
           "cf_a": "a", "cf_Tref": "T<sub>ref</sub>", "cf_Ts": "T<sub>s</sub>"}
_PRETTY = [("p*_liq", "p*<sub>liq</sub>"), ("p*_ice", "p*<sub>ice</sub>"), ("dG_v", "ΔG<sub>v</sub>"), ("dG*", "ΔG*"),
           ("f(theta)", "f(θ)"), ("degC", "°C"), ("gamma", "γ"), ("deg", "°"), ("mol-1", "mol⁻¹"), ("K-1", "K⁻¹"),
           ("m-3", "m⁻³"), ("m-2", "m⁻²"), ("Clausius-Clapeyron", "Clausius–Clapeyron"), ("Pruss", "Pruß"),
           ("dh_", "Δh_"), ("T_ref", "T<sub>ref</sub>")]


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
    <p class="lead">RAINWISE turns the physics behind Royal Rainmaking into a model you can test.
    Pick a seeding agent, set the cloud conditions and see whether droplets and ice crystals can grow, using five textbook principles.</p>
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
    html(ui.page_map())

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
        components.html(anim.warm_rain_html(), height=anim.WARM_FRAME_H)
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
    ], 3))
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
        _Tk, _sg = c_to_k(st.session_state["w_T_C"]), st.session_state["w_sigma"] / 1000
        _s001 = float(warm.kelvin_supersaturation(0.01e-6, _Tk, _sg)) * 100
        _s1 = float(warm.kelvin_supersaturation(1e-6, _Tk, _sg)) * 100
        html(ui.chart_note(
            "The curve is the supersaturation a pure-water droplet needs to stay in equilibrium at each radius "
            "(both axes logarithmic). The red dot is the radius you chose with the slider.",
            f"The smaller the droplet, the more supersaturation it needs: {_s001:.3g} % at 0.01 µm but only "
            f"{_s1:.2g} % at 1 µm. Real clouds rarely exceed about 1 %, so a newborn pure-water droplet evaporates "
            "before it can grow. This curvature barrier is what salt seeding removes."))

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

    # ---------------------------------------------------------------- simulator
    st.write("")
    html(ui.table(pd.DataFrame({
        "Question": ["Why add salt at all?", "Bigger salt particle?", "More humid cloud?", "Which salt works best?"],
        "Short answer": [
            "Dissolved salt lowers the vapour pressure of the droplet (Raoult), so it needs far less supersaturation to grow.",
            "It activates more easily: 4× bigger → 8× less supersaturation needed (S<sub>c</sub> ∝ D<sub>dry</sub><sup>−3/2</sup>).",
            "When the cloud's supersaturation s reaches S<sub>c</sub> − 1, the particle becomes a cloud droplet.",
            "Compare any salts — NaCl, CaCl₂ or one you add. More ions per volume (i·ρ<sub>s</sub>/M<sub>s</sub>) → lower "
            "S<sub>c</sub>. Particle size still matters more than salt type."],
        "Where to look": ["Köhler curve (turn on Kelvin and Raoult terms)", "Chart: Critical supersaturation vs size",
                          "Card: Cloud − critical (green / red)", "Select several salts; add new ones in the Salt library"],
    })))

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
                                        f"{r.s_c_pct:.3g} %, so the droplet grows past r<sub>c</sub> = {size(r.r_c_m)} and keeps growing."
                                        f"<br><b>Why:</b> the dissolved salt lowers the vapour pressure over the droplet "
                                        f"(Raoult's law), which pulls the peak of its Köhler curve down to {r.s_c_pct:.3g} %. "
                                        f"The cloud is above that peak, so once the droplet passes r<sub>c</sub> it needs less and "
                                        f"less supersaturation and its growth no longer stops."))
                    else:
                        if s_amb > 0:
                            d_min = math.ceil(d_m * (r.s_c_pct / s_amb) ** (2 / 3) * 1e9) * 1e-9
                            bigger = f"<b>a larger particle</b> (at least about {size(d_min)} dry diameter)"
                        else:
                            bigger = "<b>a larger particle</b>"
                        html(ui.verdict(False, f"{lab} does not activate",
                                        f"The cloud's supersaturation ({s_amb:g} %) is below S<sub>c</sub> − 1 = {r.s_c_pct:.3g} %, so the "
                                        f"droplet stops at a small equilibrium size (a haze droplet) and cannot pass r<sub>c</sub>."
                                        f"<br><b>What would make it activate, and why:</b> {bigger}, because a bigger dry "
                                        f"particle dissolves more salt, which strengthens the Raoult term B and lowers the barrier "
                                        f"(S<sub>c</sub> − 1 falls as D<sub>dry</sub><sup>−3/2</sup>); or <b>a wetter cloud</b> "
                                        f"(s of at least {r.s_c_pct:.3g} %), because more water vapour lifts the cloud's "
                                        f"supersaturation above the peak of the Köhler curve, so the droplet can climb over it."))
                for r in res:
                    lab = sub(r.label)
                    html(f'<div class="rw-salt">{lab} · dry diameter {size(d_m)}</div>' + ui.kpis([
                        ("Critical radius r<sub>c</sub>", size(r.r_c_m), "the top of the Köhler curve", "",
                         "critical radius = √(3B/A)"),
                        ("Critical supersaturation", f"{r.s_c_pct:.3g} %", "S<sub>c</sub> − 1 (lower = easier)", "",
                         "critical supersaturation = √(4A³/27B)"),
                        ("Cloud − critical", f"{r.margin_pct:+.3g} %", "positive = activates",
                         "ok" if r.activates else "no", "cloud supersaturation minus critical supersaturation"),
                    ], 3))
                g1, g2 = st.tabs(["Köhler curve", "Critical supersaturation vs size"])
                with g1:
                    st.plotly_chart(plots.koehler(res, s_amb, st.session_state["w_parts"]), width="stretch")
                    _peaks = "; ".join(
                        f"{sub(r.label)}: peak {r.s_c_pct:.3g} % is "
                        + ("below the cloud line, so it <b>activates</b>" if r.activates else "above the cloud line, so it <b>stays haze</b>")
                        for r in res)
                    html(ui.chart_note(
                        "Each thick curve is the supersaturation a droplet of that salt needs at each wet radius. On the "
                        "rising left side it is a stable haze droplet; the dot at the top is the critical point "
                        "(r<sub>c</sub>, S<sub>c</sub> − 1). The green dashed line is the supersaturation your cloud provides."
                        + (" Dotted lines are the two parts: the Kelvin term (+A/r) and the Raoult term (−B/r³)."
                           if st.session_state["w_parts"] else ""),
                        f"If the green line is above the peak, the droplet can pass r<sub>c</sub> and grow without limit "
                        f"(activation). If the line cuts the curve below the peak, growth stops where they cross. {_peaks}."))
                with g2:
                    st.plotly_chart(plots.critical_vs_size(props, T_K, s_amb, d_m, sigma), width="stretch")
                    if s_amb > 0:
                        _mins = "; ".join(f"{sub(r.label)} from about {size(math.ceil(d_m * (r.s_c_pct / s_amb) ** (2 / 3) * 1e9) * 1e-9)}" for r in res)
                        _mins = f" In this cloud the smallest particles that activate are: {_mins}."
                    else:
                        _mins = " With s = 0 % no particle activates."
                    html(ui.chart_note(
                        "Each curve gives the critical supersaturation that a dry particle of that salt needs (both axes "
                        "logarithmic). The green dashed line is your cloud; the dotted vertical line is your particle size. "
                        "Particles to the right of the point where a curve crosses the green line activate.",
                        "The curves fall with a slope of −3/2: doubling the dry size lowers S<sub>c</sub> − 1 by about "
                        "2.8 times. Particle size matters more than salt type, because the curves of different salts lie "
                        "close together." + _mins))
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
        ui.card("Step 4 · Cold-cloud attack", "Cloud tops reach 20,000 ft",
                "AgI flares are fired at the cloud top, about 21,500 ft. Freezing releases latent heat, which makes "
                "the cloud more buoyant and strengthens the updraft.", "cold"),
        ui.card("Step 5 · Super sandwich", "Tops above 20,000 ft",
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

    html(ui.section("05", "How", "AgI lowers the barrier, a process called heterogeneous nucleation."))
    html(ui.grid([
        ui.card("Pain point", "ΔG* is too high",
                "Water molecules alone (homogeneous nucleation) rarely clear the barrier, so ice nuclei do not form and "
                "supercooled water can persist to about −38 °C.", "pain"),
        ui.card("Solution", "Silver iodide (AgI)",
                "<b>AgI</b> has a crystal structure close to ice, so water molecules arrange into ice on its surface and "
                "ΔG* drops. AgI starts working around −4 to −5 °C.", "sol"),
    ], 2))

    html(ui.section("06", "Result", "From ice crystal to rain.",
                    "Clausius–Clapeyron with Δh<sub>sub</sub> = Δh<sub>vap</sub> + Δh<sub>fus</sub> shows that below 0 °C "
                    "the vapour pressure over ice is lower than over supercooled water. So once AgI has made an ice crystal, "
                    "the crystal takes vapour from the droplets around it and grows (the <b>Wegener–Bergeron–Findeisen "
                    "process</b>), and it also collects supercooled droplets (riming). When it is heavy enough it falls as "
                    "snow, and it melts into rain as it passes the 0 °C level on its way to the ground."))
    with st.container(border=True, key="eq_cc"):
        st.latex(r"\frac{d\ln p^{*}}{d(1/T)}=-\frac{\Delta h}{R};\qquad \Delta h_{sub}=\Delta h_{vap}+\Delta h_{fus}"
                 r"\;\Rightarrow\; p^{*}_{ice}<p^{*}_{liq}\ \text{for}\ T<0\,^{\circ}\mathrm{C}")
    components.html(anim.cold_rain_html(), height=anim.COLD_FRAME_H)

    # ---------------------------------------------------------------- the model used for numbers
    html(ui.section("07", "Model", "How many ice crystals does AgI make? One mechanism, one equation.",
                    "The theory above explains <i>why</i> AgI works. To calculate <i>how many</i> ice crystals it makes, "
                    "RAINWISE uses one measured relation for one mechanism: <b>condensation-freezing</b> — water vapour "
                    "condenses on the AgI particle into a tiny droplet, which then freezes."))
    m1, m2 = st.columns([1.15, 1], gap="large")
    with m1:
        with st.container(border=True, key="eq_cf"):
            st.latex(r"F = a\left(\frac{T_{ref}-T}{T_s}\right)^{3}\left(S_w-1\right)^{2}")
            st.latex(r"\mathrm{INP}\,[\mathrm{L^{-1}}] = F\times N_{AgI}\,[\mathrm{cm^{-3}}]\times 1000")
            html('<p class="rw-note">F: active fraction — the share of AgI particles that become ice (0 to 1) · '
                 'a = 900 · T<sub>ref</sub> = 268.66 K (−4.5 °C) · T<sub>s</sub> = 10 K · T: cloud temperature [K] · '
                 'S<sub>w</sub>: water saturation ratio (1.002 = 0.2 % supersaturated) · N<sub>AgI</sub>: AgI particles per '
                 'cm³ · INP: ice-nucleating particles per litre of air (1 cm⁻³ = 1000 L⁻¹).<br>'
                 'Source: Yang et al. (2024), Eq. 2, based on laboratory data of DeMott (1995).</p>')
    with m2:
        html(ui.card("When the equation applies", "T below −4.5 °C and S<sub>w</sub> above 1",
                     "Warmer than −4.5 °C: not computed. S<sub>w</sub> ≤ 1: no droplet can form, so F = 0. If F comes out "
                     "above 1 (very cold and very humid), the equation is outside its range: the app shows a warning and "
                     "does not turn it into an INP number.", "pain"))
    st.write("")
    html(ui.table(pd.DataFrame({
        "Question": ["Colder cloud?", "More humid cloud?", "More AgI?"],
        "Short answer": ["More AgI particles turn into ice: F rises with (T<sub>ref</sub> − T)<sup>3</sup>.",
                         "F rises with (S<sub>w</sub> − 1)<sup>2</sup>: twice the supersaturation → 4× more ice.",
                         "Ice crystals rise in proportion: 10× more AgI → 10× more INP."],
        "Where to look": ["Chart: Effect of temperature", "Chart: Effect of humidity", "Chart: Effect of AgI amount"],
    })))

    # ---------------------------------------------------------------- simulator
    html(ui.section("▶", "Simulator", "How many ice crystals will AgI make in this cloud?",
                    "Set the cloud temperature, the humidity and the amount of AgI. The results and charts update instantly."))
    left, right = st.columns([1, 2.4], gap="large")
    with left:
        with st.container(border=True, key="card_c_in"):
            html('<div class="rw-panel-title">Cloud</div>')
            st.number_input(r"Temperature $T$ [°C]", -40.0, -1.0, key="c_T_C", step=1.0,
                            help="The equation applies below −4.5 °C.")
            st.number_input(r"Water saturation ratio $S_w$ [–]", 0.990, 1.050, key="c_Sw", step=0.001, format="%.3f",
                            help="1.000 = exactly saturated (RH 100 %). 1.002 = 0.2 % supersaturated. Clouds: about 1.000–1.01.")
            html(f'<p class="rw-note">→ RH = <b>{st.session_state["c_Sw"] * 100:.1f} %</b> · supersaturation over water '
                 f'<b>{(st.session_state["c_Sw"] - 1) * 100:+.2f} %</b></p>')
            html('<div class="rw-panel-title">Seeding agent: AgI</div>')
            st.number_input(r"AgI concentration $N_{AgI}$ [cm⁻³]", 0.1, 1000.0, key="c_N", step=1.0,
                            help="Number of AgI particles in each cubic centimetre of cloud air.")
            st.button("Reset ", on_click=reset, args=("c_",), width="stretch")
    with right:
        try:
            T_C, Sw, N = st.session_state["c_T_C"], st.session_state["c_Sw"], st.session_state["c_N"]
            res = agi.active_fraction(c_to_k(T_C), Sw, N)
            if res.status == "ok":
                html(ui.verdict(True, f"AgI makes about {res.inp_per_L:,.3g} ice crystals per litre",
                                f"At {T_C:g} °C and S<sub>w</sub> = {Sw:.3f}, F = {res.fraction:.3g}: about "
                                f"{res.fraction * 100:.3g} % of the AgI particles become ice. With {N:g} AgI particles per cm³ "
                                f"that is {res.inp_per_L:,.3g} ice-nucleating particles per litre of air."
                                "<br><b>Why:</b> below −4.5 °C the energy barrier for ice on AgI is low enough, and because "
                                "the air is supersaturated (S<sub>w</sub> > 1) water first condenses on each AgI particle and "
                                "the small droplet then freezes (condensation-freezing). A colder cloud gives more ice through "
                                "((T<sub>ref</sub> − T)/T<sub>s</sub>)³ and a wetter cloud through (S<sub>w</sub> − 1)²."))
            elif res.status == "too_warm":
                html(ui.verdict(False, "Too warm for AgI", res.message
                                + " <br><b>Why:</b> at this temperature the energy barrier to form ice is still too high, even "
                                "on AgI, so almost no particles freeze. Seeding therefore waits until the cloud top is colder "
                                "(Royal Rainmaking fires AgI at about 21,500 ft)."))
            elif res.status == "not_supersaturated":
                html(ui.verdict(False, "No condensation, so no condensation-freezing", res.message
                                + " <br><b>Why:</b> condensation-freezing needs liquid water to condense on the AgI first. "
                                "Without supersaturation over water no droplet forms, so there is nothing to freeze. Seed the "
                                "part of the cloud that is still rising, where the updraft cools the air and makes S<sub>w</sub> > 1."))
            else:
                html(ui.verdict(False, "Outside the range of the equation", res.message
                                + " <br><b>Why:</b> the power law was fitted to laboratory data at moderate cold and "
                                "humidity; pushed further it overshoots. Choose a warmer temperature or a lower S<sub>w</sub> "
                                "to get a meaningful number."))
            F_txt = "—" if res.fraction is None else f"{res.fraction:.3g}"
            inp_txt = "—" if res.inp_per_L is None else f"{res.inp_per_L:,.3g} L⁻¹"
            html(ui.kpis([
                ("Active fraction F", F_txt, "share of AgI particles that become ice",
                 "ok" if res.usable else "no", "F = 900((268.66 − T)/10)³(Sw − 1)²"),
                ("Ice-nucleating particles", inp_txt, "INP = F × N × 1000", "ok" if res.usable else "",
                 "per litre of cloud air"),
                ("Temperature term", "—" if res.status == "too_warm" else f"{((268.66 - c_to_k(T_C)) / 10) ** 3:.3g}",
                 "((T<sub>ref</sub> − T)/T<sub>s</sub>)³", "", "grows quickly as the cloud gets colder"),
                ("Humidity term", _num(max(Sw - 1, 0) ** 2) if Sw > 1 else "0", "(S<sub>w</sub> − 1)²", "",
                 "zero when the air is not supersaturated"),
            ]))
            g1, g2, g3 = st.tabs(["Effect of temperature", "Effect of humidity", "Effect of AgI amount"])
            with g1:
                st.plotly_chart(plots.cf_vs_temperature(T_C, Sw), width="stretch")
                if res.status != "too_warm":
                    _dT = -4.5 - T_C
                    _gain = ((_dT + 5) / _dT) ** 3
                    _from_to = f"from {T_C:g} °C to {T_C - 5:g} °C".replace("-", "−")
                    _tk = (f"At your humidity, cooling the cloud {_from_to} multiplies F by "
                           f"{_gain:.2g}. AgI therefore works best in the coldest part of the cloud that still holds "
                           "supercooled water.")
                else:
                    _tk = ("Your cloud is warmer than −4.5 °C, where the equation gives no ice: move right on the chart "
                           "(colder) to see AgI start to work.")
                html(ui.chart_note(
                    "Each line is one humidity; the thick line is yours and the red dot is your cloud. The horizontal "
                    "axis runs from warm (left) to cold (right). The vertical scale is logarithmic: each step up is 10 "
                    "times more ice.", _tk))
            with g2:
                st.plotly_chart(plots.cf_vs_humidity(T_C, Sw), width="stretch")
                html(ui.chart_note(
                    "Each line is one temperature; the thick line is yours. The horizontal axis is the supersaturation "
                    "over water, (S<sub>w</sub> − 1) × 100 %.",
                    "F is zero at S<sub>w</sub> = 1 and grows with (S<sub>w</sub> − 1)²: doubling the supersaturation "
                    "gives 4 times more ice. AgI therefore works best where the cloud is still growing and supersaturated."))
            with g3:
                if res.usable:
                    st.plotly_chart(plots.inp_vs_agi(res.fraction, N), width="stretch")
                    html(ui.chart_note(
                        "At your temperature and humidity, the line gives the ice crystals per litre for each AgI "
                        "concentration; the red dot is your N<sub>AgI</sub>.",
                        "Ice crystals rise in direct proportion: 10 times more AgI gives 10 times more ice. The model has "
                        "no upper limit. In a real cloud, too many ice crystals share the same water vapour, stay small and "
                        "may not fall (over-seeding); this model does not include that effect."))
                else:
                    st.info("Choose a temperature below −4.5 °C and S_w above 1 (with F ≤ 1) to see this chart.")
        except ValueError as exc:
            st.error(f"Cannot calculate with these inputs: {exc}")

# =============================================================================== HOW IT WORKS
with tab_method:
    html(ui.section("A", "Method", "How RAINWISE was built, step by step",
                    "Eight plain steps, in the order they were done. Each one can be checked in the code."))
    html('<ol class="rw-steps rw-method">'
         '<li><b>Start from the course notes.</b> For each cloud type we asked the same questions: What is sprayed, '
         'Where and When it is done, Why the cloud does not rain by itself, How the agent helps, and what the Result '
         'is. Only the equations written in the notes were used.</li>'
         '<li><b>Write the problem as inputs and outputs.</b> Warm cloud: salt, dry size D<sub>dry</sub>, temperature T and '
         'cloud supersaturation s go in; the critical radius r<sub>c</sub>, the critical supersaturation S<sub>c</sub> and '
         '“activates or not” come out. Cold cloud: temperature T, humidity S<sub>w</sub> and the amount of AgI N<sub>AgI</sub> go '
         'in; the active fraction F and the number of ice-nucleating particles (INP) come out.</li>'
         '<li><b>Collect every number the equations need.</b> Constants such as R, M<sub>w</sub>, ρ<sub>w</sub>, γ and '
         'Δh<sub>fus</sub> were taken from reference books and papers and written into two tables (the database below), '
         'each with its source. No number is typed inside the calculation code.</li>'
         '<li><b>Turn each equation into one small function.</b> One equation = one Python function, all in SI units '
         '(metres, kelvin, joules). For example, A = 2γM<sub>w</sub>/(RTρ<sub>w</sub>) is the function “kelvin_A”.</li>'
         '<li><b>Find the special points with calculus.</b> The peak of the Köhler curve is where the slope is zero '
         '(dS/dr = 0). Solving this by hand gives exact formulas for r<sub>c</sub> and S<sub>c</sub>, so the app needs no '
         'trial and error. For AgI, one measured relation (Yang et al., 2024) is used directly.</li>'
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

    html(ui.section("B", "Traceability", "Every number, traced to its equation and source",
                    "Click a link in the <b>Code</b> column to open the exact lines on GitHub."))
    trace = pd.DataFrame([
        ["Warm", "s needed by a pure-water droplet (Why chart)", "s = exp(A/r) − 1", "Exponential, closed form",
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
        ["Cold", "Active fraction F", "F = a((T<sub>ref</sub> − T)/T<sub>s</sub>)<sup>3</sup>(S<sub>w</sub> − 1)<sup>2</sup>",
         "Power law fitted to laboratory data", code_link(agi.raw_fraction), data_link("constants.csv") + ": a, T<sub>ref</sub>, T<sub>s</sub>",
         "Yang et al. (2024) Eq. 2 [6]; DeMott (1995) [8]"],
        ["Cold", "Status (valid / too warm / F > 1)", "T < T<sub>ref</sub>; S<sub>w</sub> > 1; 0 ≤ F ≤ 1", "Logical checks",
         code_link(agi.active_fraction), "—", "[6]"],
        ["Cold", "Ice-nucleating particles INP", "INP = F × N<sub>AgI</sub> × 1000", "Unit conversion cm⁻³ → L⁻¹",
         code_link(agi.inp_per_litre), "your input N<sub>AgI</sub>", "[6]"],
        ["Cold", "Effect charts (T, S<sub>w</sub>, N<sub>AgI</sub>)", "F and INP over a range of inputs", "Parameter sweeps",
         code_link(agi.fraction_curve), "—", "[6]"],
    ], columns=["Module", "What you see", "Equation", "Mathematics", "Code", "Data used", "Reference"])
    html(ui.table(trace, ("Equation",)))

    html(ui.section("C", "Derivations", "Where the closed-form results come from"))
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
        with st.expander("Critical ice nucleus: r* and ΔG* (explanation only)", expanded=True):
            st.latex(r"\frac{d\Delta G}{dr}=8\pi r\gamma+4\pi r^{2}\Delta G_v=0\;\Rightarrow\; r^{*}=-\frac{2\gamma}{\Delta G_v}")
            st.latex(r"\Delta G^{*}=4\pi r^{*2}\gamma+\tfrac{4}{3}\pi r^{*3}\Delta G_v=\frac{16\pi\gamma^{3}}{3\Delta G_v^{2}}")
        with st.expander(r"Clausius–Clapeyron and $\Delta G_v$ (explanation only)"):
            st.latex(r"\int_{p_{tp}}^{p^{*}} d\ln p=-\frac{\Delta h}{R}\int_{1/T_0}^{1/T} d\!\left(\tfrac{1}{T}\right)"
                     r"\;\Rightarrow\; p^{*}=p_{tp}\exp\!\left[-\frac{\Delta h}{R}\left(\frac{1}{T}-\frac{1}{T_0}\right)\right]")
            st.latex(r"\frac{p^{*}_{liq}}{p^{*}_{ice}}=\exp\!\left[\frac{\Delta h_{fus}}{R}\left(\frac{1}{T}-\frac{1}{T_0}\right)\right],\qquad"
                     r"\Delta G_v=-\frac{\rho_{ice}}{M_w}RT\ln\frac{p^{*}_{liq}}{p^{*}_{ice}}")
            html('<p class="rw-note">Δh is taken as constant between 0 and −40 °C, which is the main approximation.</p>')

    html(ui.section("D", "Database", "The values the equations read",
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

    html(ui.section("E", "Verification", "How we know the numbers are right",
                    "Each check below is written as an automated test in " + repo_link("tests", "the tests folder") + "."))
    html('<ul class="rw-checks">'
         '<li><b>Is the Köhler formula really the peak of the curve?</b> We drew the curve at 200,000 points and picked the '
         'highest one by brute force. It matches r<sub>c</sub> = √(3B/A) and S<sub>c</sub> − 1 = √(4A<sup>3</sup>/27B) to '
         'one part in a million.</li>'
         '<li><b>Does a hand calculation give the same answer?</b> Warm cloud: 100 nm NaCl at 15 °C gives S<sub>c</sub> − 1 = '
         '0.106 % on paper and in the app. Cold cloud: at −15 °C and S<sub>w</sub> = 1.002, '
         '900 × 1.051<sup>3</sup> × 0.002<sup>2</sup> = 0.00418, so 10 AgI particles per cm³ give 41.8 ice crystals per '
         'litre — the same as the app.</li>'
         '<li><b>Do the trends make physical sense?</b> A bigger salt particle needs less supersaturation (exactly '
         'D<sub>dry</sub><sup>−3/2</sup>). For AgI, F rises when '
         'the cloud gets colder and when it gets more humid, and INP is exactly proportional to the amount of AgI.</li>'
         '<li><b>Are the limits of the AgI equation respected?</b> Warmer than −4.5 °C: not computed. S<sub>w</sub> ≤ 1: '
         'F = 0. F above 1: shown with a warning and never turned into an INP number (it is not silently cut to 1).</li>'
         '<li><b>Are bad inputs caught?</b> A temperature typed in °C where kelvin is needed is refused, a negative AgI '
         'amount or a salt with a negative molar mass is refused, and an incomplete row in the salt library is flagged.</li>'
         '<li><b>Does the whole app run?</b> One test opens the full website and changes the inputs; another adds, edits and '
         'deletes salts in the library. Both check that nothing breaks.</li></ul>')

    html(ui.section("F", "Limits", "What this model does not do"))
    html(ui.grid([
        ui.card("Equilibrium only", "No time, no rainfall",
                "The model shows whether growth is possible, not how fast it is or how much rain falls.", ""),
        ui.card("Ideal solution", "Dilute Köhler form",
                "A/r − B/r³ assumes a dilute, fully dissociated solution. It is accurate near activation and less so "
                "for very concentrated haze droplets.", ""),
        ui.card("One AgI mechanism", "Condensation-freezing only",
                "Deposition, immersion and contact freezing are not included. The AgI equation is an empirical fit to "
                "laboratory data (DeMott, 1995); T<sub>s</sub> = 10 K is taken from the definition given after Eq. 1 in "
                "Yang et al. (2024), and F can exceed 1 when it is pushed outside its range.", ""),
    ], 3))

    html(ui.section("G", "References", "Sources"))
    st.markdown(
        "1. Course notes, Topic 13: Royal Rainmaking and Cloud Seeding (What / Where / Why / How / Result framework).\n"
        "2. Köhler, H. (1936). The nucleus in and the growth of hygroscopic droplets. *Trans. Faraday Soc.*, 32, 1152–1161.\n"
        "3. Wallace, J. M., & Hobbs, P. V. (2006). *Atmospheric Science: An Introductory Survey* (2nd ed.). Academic Press.\n"
        "4. Pruppacher, H. R., & Klett, J. D. (1997). *Microphysics of Clouds and Precipitation* (2nd ed.). Kluwer.\n"
        "5. Rogers, R. R., & Yau, M. K. (1989). *A Short Course in Cloud Physics* (3rd ed.). Pergamon.\n"
        "6. Yang, J., et al. (2024). Estimating the concentration of silver iodide needed to detect unambiguous "
        "signatures of glaciogenic cloud seeding. *Atmos. Chem. Phys.*, 24, 13833–13848. doi:10.5194/acp-24-13833-2024\n"
        "7. Xue, L., et al. (2013a). Implementation of a silver iodide cloud-seeding parameterization in WRF. Part I. "
        "*J. Appl. Meteor. Climatol.* (as cited in [6])\n"
        "8. DeMott, P. J. (1995). Quantitative descriptions of ice formation mechanisms of silver iodide-type aerosols. "
        "*Atmos. Res.* (as cited in [6])\n"
        "9. Rumble, J. R. (ed.). *CRC Handbook of Chemistry and Physics*. CRC Press.\n"
        "10. Tiesinga, E., et al. (2021). CODATA recommended values of the fundamental physical constants: 2018. "
        "*J. Phys. Chem. Ref. Data*, 50, 033105.\n"
        "11. Department of Royal Rainmaking and Agricultural Aviation. *Royal Rainmaking Technology* (e-book, steps I–VI). "
        "ASEAN Weather Modification Centre. https://awmc.royalrain.go.th/asean/ebook_pic/1727245596.pdf")

# =============================================================================== PROTOTYPE STATUS (end of page)
html(ui.prototype_notice())
html(ui.section("", "Improvements", "What comes next",
                "The roadmap to turn the prototype into a validated tool. The first three items are the most important: "
                "the model needs to be verified against real measurements."))
html(ui.roadmap())
