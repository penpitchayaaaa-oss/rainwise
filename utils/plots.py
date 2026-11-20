"""Plotly figures for RAINWISE. Presentation only - every number comes from models/."""
from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from models import agi, warm
from models.constants import CF_TREF, c_to_k

INK, MUTED, GRID = "#0B1F33", "#6B7A8C", "#ECEFF3"
SALT_COLOR = {"NaCl": "#1D4ED8", "CaCl2": "#0F766E"}
CUSTOM_COLOR = "#B45309"


def _color(key):
    return SALT_COLOR.get(key, CUSTOM_COLOR)


def _html(label):
    return "".join(f"<sub>{c}</sub>" if c.isdigit() else c for c in label.replace("₂", "2").replace("₃", "3"))
HOM, HET = "#94A3B8", "#1D4ED8"
LIQ, ICE = "#0EA5E9", "#1E3A8A"


def _style(fig: go.Figure, title: str, height: int = 470) -> go.Figure:
    fig.update_layout(
        template="plotly_white", height=height, margin=dict(l=70, r=24, t=56, b=110),
        title=dict(text=title, x=0, xanchor="left", font=dict(size=15, color=INK, family="Inter, sans-serif")),
        font=dict(family="Inter, Segoe UI, sans-serif", size=12.5, color=INK),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FFFFFF",
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="left", x=0, font=dict(size=12),
                    bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor="white", font=dict(family="Inter, sans-serif")))
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor="#CBD2DB", ticks="outside", tickcolor="#CBD2DB",
                     title_font=dict(color=MUTED))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor="#CBD2DB", ticks="outside", tickcolor="#CBD2DB",
                     title_font=dict(color=MUTED))
    return fig


# ------------------------------------------------------------------ warm cloud
def kelvin_only(T_K: float, r_sel_um: float, sigma: float) -> go.Figure:
    r = np.geomspace(0.005e-6, 5e-6, 300)
    s = warm.kelvin_supersaturation(r, T_K, sigma) * 100
    fig = go.Figure(go.Scatter(x=r * 1e6, y=s, name="pure water droplet", line=dict(color=INK, width=2.5)))
    s_sel = float(warm.kelvin_supersaturation(r_sel_um * 1e-6, T_K, sigma)) * 100
    fig.add_trace(go.Scatter(x=[r_sel_um], y=[s_sel], mode="markers+text", marker=dict(size=10, color="#DC2626"),
                             text=[f"  s = {s_sel:.3g} %"], textposition="middle right", name="selected radius"))
    fig.add_hrect(y0=0.1, y1=1.0, fillcolor="#1D4ED8", opacity=0.07, line_width=0,
                  annotation_text="typical cloud s (0.1–1 %)", annotation_position="top left",
                  annotation_font=dict(color=MUTED, size=11))
    fig.update_xaxes(title="droplet radius r [µm]", type="log")
    fig.update_yaxes(title="supersaturation needed, s [%]", type="log")
    return _style(fig, "Kelvin effect — the smaller the droplet, the more supersaturation it needs")


def koehler(results: list, s_amb_pct: float, show_parts: bool = True) -> go.Figure:
    fig = go.Figure()
    ymax = s_amb_pct
    rmax = max(r.r_c_m for r in results) * 8
    rmin = min((r.B_m3 / r.A_m) ** 0.5 for r in results) * 0.75
    rr = np.geomspace(rmin, rmax, 600)
    for i, res in enumerate(results):
        c = _color(res.salt)
        s = warm.koehler_s(rr, res.A_m, res.B_m3) * 100
        lab = _html(res.label)
        if show_parts and i == 0:
            fig.add_trace(go.Scatter(x=rr * 1e6, y=res.A_m / rr * 100, name="Kelvin term  +A/r",
                                     line=dict(color="#94A3B8", width=1.5, dash="dot")))
        if show_parts:
            fig.add_trace(go.Scatter(x=rr * 1e6, y=-res.B_m3 / rr ** 3 * 100, name=f"Raoult term  −B/r³ ({lab})",
                                     line=dict(color=c, width=1.2, dash="dot"), opacity=0.7))
        fig.add_trace(go.Scatter(x=rr * 1e6, y=s, name=f"Köhler curve ({lab})", line=dict(color=c, width=3)))
        fig.add_trace(go.Scatter(x=[res.r_c_m * 1e6], y=[res.s_c_pct], mode="markers", showlegend=False,
                                 marker=dict(size=11, color=c, line=dict(color="white", width=2)),
                                 hovertemplate=f"{lab}<br>r<sub>c</sub> = %{{x:.3g}} µm<br>s<sub>c</sub> = %{{y:.3g}} %<extra></extra>"))
        fig.add_annotation(x=np.log10(res.r_c_m * 1e6), y=res.s_c_pct, text=f"S<sub>c</sub> {res.s_c_pct:.3g} %",
                           showarrow=False, yshift=14 if i == 0 else -16, font=dict(color=c, size=12))
        ymax = max(ymax, res.s_c_pct)
    fig.add_hline(y=s_amb_pct, line=dict(color="#16A34A", width=2, dash="dash"),
                  annotation_text=f"ambient supersaturation s = {s_amb_pct:g} %", annotation_position="top right",
                  annotation_font=dict(color="#16A34A", size=12))
    fig.add_hline(y=0, line=dict(color="#94A3B8", width=1))
    fig.update_xaxes(title="wet droplet radius r [µm]", type="log")
    fig.update_yaxes(title="equilibrium supersaturation S<sub>eq</sub> − 1 [%]", range=[-ymax * 1.6, ymax * 1.6 + 0.02])
    return _style(fig, "Köhler curve = Kelvin effect + Raoult effect", 520)


def critical_vs_size(salts: list[dict], T_K: float, s_amb_pct: float, d_sel_m: float, sigma: float) -> go.Figure:
    d = np.geomspace(20e-9, 5e-6, 80)
    fig = go.Figure()
    for p in salts:
        fig.add_trace(go.Scatter(x=d * 1e6, y=warm.critical_curve(p, d, T_K, sigma), name=_html(p["label"]),
                                 line=dict(color=_color(p["key"]), width=3)))
    fig.add_hline(y=s_amb_pct, line=dict(color="#16A34A", width=2, dash="dash"),
                  annotation_text="ambient s — particles to the right activate", annotation_position="top right",
                  annotation_font=dict(color="#16A34A", size=12))
    fig.add_vline(x=d_sel_m * 1e6, line=dict(color="#94A3B8", width=1, dash="dot"),
                  annotation_text="selected size", annotation_font=dict(color=MUTED, size=11))
    fig.update_xaxes(title="dry salt diameter D<sub>dry</sub> [µm]", type="log")
    fig.update_yaxes(title="critical supersaturation S<sub>c</sub> − 1 [%]", type="log")
    return _style(fig, "Bigger salt particles activate at lower supersaturation")


# ------------------------------------------------------------------ cold cloud: AgI condensation-freezing
SW_COLORS = ["#BFDBFE", "#60A5FA", "#2563EB", "#1E3A8A"]
T_COLORS = ["#BAE6FD", "#38BDF8", "#0284C7", "#0C4A6E"]


def _limit_line(fig):
    fig.add_hline(y=1.0, line=dict(color="#DC2626", width=1.5, dash="dash"),
                  annotation_text="F = 1 (every particle) — above this the equation is outside its range",
                  annotation_position="bottom left", annotation_font=dict(color="#DC2626", size=11))


def cf_vs_temperature(T_sel_C: float, Sw_sel: float) -> go.Figure:
    """Effect of temperature: F vs T for several S_w."""
    Tc = np.linspace(-40, CF_TREF - 273.15 - 0.05, 300)
    fig = go.Figure()
    sws = sorted({1.001, 1.002, 1.005, 1.01} - {round(Sw_sel, 4)})
    for c, sw in zip(SW_COLORS, sws):
        fig.add_trace(go.Scatter(x=Tc, y=agi.fraction_curve(c_to_k(Tc), sw), name=f"S<sub>w</sub> = {sw:g}",
                                 line=dict(color=c, width=2)))
    if Sw_sel > 1:
        fig.add_trace(go.Scatter(x=Tc, y=agi.fraction_curve(c_to_k(Tc), Sw_sel), name=f"your S<sub>w</sub> = {Sw_sel:g}",
                                 line=dict(color=INK, width=4)))
        if T_sel_C < CF_TREF - 273.15:
            y = float(agi.raw_fraction(c_to_k(T_sel_C), Sw_sel))
            fig.add_trace(go.Scatter(x=[T_sel_C], y=[y], mode="markers", showlegend=False,
                                     marker=dict(size=12, color="#DC2626", line=dict(color="white", width=2))))
    _limit_line(fig)
    fig.add_vline(x=CF_TREF - 273.15, line=dict(color="#94A3B8", dash="dot"),
                  annotation_text="starts at −4.5 °C", annotation_font=dict(color=MUTED, size=11))
    fig.update_xaxes(title="cloud temperature [°C]", autorange="reversed")
    fig.update_yaxes(title="active fraction F [–] (log scale)", type="log", range=[-7, 0.6])
    return _style(fig, "Effect of temperature: colder cloud → more AgI particles become ice")


def cf_vs_humidity(T_sel_C: float, Sw_sel: float) -> go.Figure:
    """Effect of humidity: F vs S_w for several temperatures."""
    S = np.linspace(1.0001, 1.03, 300)
    fig = go.Figure()
    temps = [t for t in (-10.0, -15.0, -20.0, -25.0) if abs(t - T_sel_C) > 0.5]
    for c, t in zip(T_COLORS, temps):
        fig.add_trace(go.Scatter(x=(S - 1) * 100, y=agi.fraction_curve(c_to_k(t), S), name=f"{t:g} °C",
                                 line=dict(color=c, width=2)))
    if T_sel_C < CF_TREF - 273.15:
        fig.add_trace(go.Scatter(x=(S - 1) * 100, y=agi.fraction_curve(c_to_k(T_sel_C), S), name=f"your T = {T_sel_C:g} °C",
                                 line=dict(color=INK, width=4)))
        if Sw_sel > 1:
            fig.add_trace(go.Scatter(x=[(Sw_sel - 1) * 100], y=[float(agi.raw_fraction(c_to_k(T_sel_C), Sw_sel))],
                                     mode="markers", showlegend=False,
                                     marker=dict(size=12, color="#DC2626", line=dict(color="white", width=2))))
    _limit_line(fig)
    fig.update_xaxes(title="supersaturation over water, (S<sub>w</sub> − 1) × 100 [%]")
    fig.update_yaxes(title="active fraction F [–] (log scale)", type="log", range=[-7, 0.6])
    return _style(fig, "Effect of humidity: wetter cloud → more AgI particles become ice")


def inp_vs_agi(F: float, N_sel: float) -> go.Figure:
    """Effect of AgI amount: INP = F * N * 1000."""
    N = np.geomspace(0.1, 1000, 200)
    fig = go.Figure(go.Scatter(x=N, y=F * N * 1000, name=f"F = {F:.3g}", line=dict(color=INK, width=4)))
    fig.add_trace(go.Scatter(x=[N_sel], y=[F * N_sel * 1000], mode="markers+text", showlegend=False,
                             text=[f"  {F * N_sel * 1000:,.3g} L⁻¹"], textposition="middle right",
                             marker=dict(size=12, color="#DC2626", line=dict(color="white", width=2))))
    fig.update_xaxes(title="AgI concentration N<sub>AgI</sub> [cm⁻³]", type="log")
    fig.update_yaxes(title="ice-nucleating particles INP [L⁻¹]", type="log")
    return _style(fig, "Effect of AgI amount: 10× more AgI → 10× more ice crystals")
