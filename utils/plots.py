"""Plotly figures for RAINWISE. Presentation only - every number comes from models/."""
from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from models import cold, warm
from models.constants import c_to_k

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


# ------------------------------------------------------------------ cold cloud
def free_energy(res) -> go.Figure:
    r = np.linspace(0, res.r_star_m * 2.6, 400)
    hom = cold.free_energy_curve(r, res.T_K, res.gamma, 1.0)
    het = cold.free_energy_curve(r, res.T_K, res.gamma, res.f)
    scale = 1e-18
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=r * 1e9, y=hom / scale, name="homogeneous (pure water)", line=dict(color=HOM, width=3)))
    fig.add_trace(go.Scatter(x=r * 1e9, y=het / scale, name=f"heterogeneous on AgI (θ = {res.theta_deg:g}°)",
                             line=dict(color=HET, width=3)))
    fig.add_vline(x=res.r_star_m * 1e9, line=dict(color="#CBD2DB", dash="dash"),
                  annotation_text=f"r* = {res.r_star_m * 1e9:.2f} nm", annotation_font=dict(color=MUTED, size=12))
    for y, c, lab in ((res.dG_hom_J, HOM, "ΔG*<sub>hom</sub>"), (res.dG_het_J, HET, "ΔG*<sub>het</sub>")):
        fig.add_trace(go.Scatter(x=[res.r_star_m * 1e9], y=[y / scale], mode="markers", showlegend=False,
                                 marker=dict(size=10, color=c, line=dict(color="white", width=2))))
        fig.add_annotation(x=res.r_star_m * 1e9, y=y / scale, text=lab, showarrow=False, xshift=40,
                           font=dict(color=c, size=12))
    fig.add_hline(y=0, line=dict(color="#94A3B8", width=1))
    fig.update_xaxes(title="radius of ice nucleus r [nm]")
    fig.update_yaxes(title="ΔG(r) [10<sup>−18</sup> J]", range=[-res.dG_hom_J / scale * 0.8, res.dG_hom_J / scale * 1.3])
    return _style(fig, "Energy barrier to form an ice nucleus — AgI lowers the peak", 500)


def barrier_vs_T(theta_deg: float, gamma: float, T_sel_C: float) -> go.Figure:
    Tc = np.linspace(-40, -2, 200)
    hom, het = [], []
    for t in Tc:
        r = cold.analyse(c_to_k(t), theta_deg, gamma)
        hom.append(r.dG_hom_kT)
        het.append(r.dG_het_kT)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=Tc, y=hom, name="homogeneous (pure water)", line=dict(color=HOM, width=3)))
    fig.add_trace(go.Scatter(x=Tc, y=het, name=f"on AgI (θ = {theta_deg:g}°)", line=dict(color=HET, width=3)))
    fig.add_vline(x=T_sel_C, line=dict(color="#CBD2DB", dash="dash"), annotation_text="selected T",
                  annotation_font=dict(color=MUTED, size=11))
    fig.update_xaxes(title="cloud temperature [°C]", autorange="reversed")
    fig.update_yaxes(title="barrier ΔG* [kT]", type="log")
    return _style(fig, "The barrier falls as the cloud gets colder — and is far lower on AgI")


def bergeron(T_sel_C: float) -> go.Figure:
    Tc = np.linspace(-40, 0, 200)
    Tk = c_to_k(Tc)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=Tc, y=cold.p_sat_liquid(Tk), name="p*<sub>liq</sub> over supercooled water",
                             line=dict(color=LIQ, width=3)))
    fig.add_trace(go.Scatter(x=Tc, y=cold.p_sat_ice(Tk), name="p*<sub>ice</sub> over ice", line=dict(color=ICE, width=3)))
    fig.add_trace(go.Scatter(x=Tc, y=(cold.liquid_to_ice_ratio(Tk) - 1) * 100, yaxis="y2", name="p*<sub>liq</sub>/p*<sub>ice</sub> − 1 [%]",
                             line=dict(color="#F59E0B", width=2, dash="dash")))
    fig.add_vline(x=T_sel_C, line=dict(color="#CBD2DB", dash="dash"))
    fig.update_layout(yaxis2=dict(title="ice supersaturation at water saturation [%]", overlaying="y", side="right",
                                  showgrid=False, title_font=dict(color=MUTED)))
    fig.update_xaxes(title="temperature [°C]")
    fig.update_yaxes(title="saturation vapour pressure [Pa]")
    return _style(fig, "Bergeron (WBF) process — ice has the lower vapour pressure below 0 °C")
