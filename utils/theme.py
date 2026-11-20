"""Visual layer for RAINWISE (HTML/CSS only, no physics)."""
from __future__ import annotations

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap');
:root{--ink:#0B1F33;--body:#334155;--muted:#6B7A8C;--line:#E6E9EE;--bg:#FAFAF8;--card:#FFFFFF;
  --accent:#1D4ED8;--accent-soft:#EEF3FF;--warm:#B45309;--warm-soft:#FFF7ED;--cold:#0369A1;--cold-soft:#F0F9FF;
  --ok:#15803D;--ok-soft:#F0FDF4;--no:#B91C1C;--no-soft:#FEF2F2;}
html, body, .stApp, p, li, td, th, label, input, textarea, button, .stMarkdown, [data-testid="stWidgetLabel"] p{
  font-family:'Inter','Segoe UI',sans-serif !important;}
.stApp{background:var(--bg);color:var(--body);}
header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu, footer,
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"]{display:none !important;}
.block-container{max-width:1240px !important;padding:0 2.2rem 4rem !important;}
h1, h2, h3, h4{color:var(--ink) !important;font-family:'Inter',sans-serif !important;letter-spacing:-0.01em;}
p, li{line-height:1.65;}
a{color:var(--accent);}

/* nav */
.rw-nav{display:flex;align-items:center;justify-content:space-between;padding:22px 0 18px;border-bottom:1px solid var(--line);}
.rw-brand{display:flex;align-items:center;gap:10px;font-weight:700;letter-spacing:.14em;font-size:.95rem;color:var(--ink);}
.rw-mark{width:22px;height:22px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);
  background:linear-gradient(135deg,#1D4ED8,#38BDF8);}
.rw-navmeta{font-size:.82rem;color:var(--muted);}

/* hero */
.rw-hero{padding:64px 0 40px;display:grid;grid-template-columns:1.5fr 1fr;gap:48px;align-items:center;}
.rw-eyebrow{font-size:.78rem;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:var(--accent);margin-bottom:14px;}
.rw-hero h1{font-family:'Instrument Serif',Georgia,serif !important;font-weight:400;font-size:3.4rem;line-height:1.06;
  margin:0 0 18px;padding:0;letter-spacing:-0.02em;}
.rw-hero h1 em{color:var(--accent);font-style:italic;}
.rw-hero p.lead{font-size:1.12rem;color:var(--body);max-width:560px;margin:0 0 26px;}
.rw-chips{display:flex;gap:8px;flex-wrap:wrap;}
.rw-chip{border:1px solid var(--line);background:#fff;border-radius:999px;padding:6px 14px;font-size:.84rem;color:var(--ink);}
.rw-hero-card{background:#fff;border:1px solid var(--line);border-radius:20px;padding:22px 24px;box-shadow:0 20px 50px -30px rgba(11,31,51,.35);}

/* tabs as navigation */
.stTabs [data-baseweb="tab-list"]{gap:28px;border-bottom:1px solid var(--line);}
.stTabs [data-baseweb="tab"]{padding:14px 2px;background:transparent;}
.stTabs [data-baseweb="tab"] p{font-size:.95rem !important;font-weight:600 !important;color:var(--muted);}
.stTabs [aria-selected="true"] p{color:var(--ink) !important;}
.stTabs [data-baseweb="tab-highlight"]{background:var(--ink) !important;height:2px !important;}
.stTabs [data-baseweb="tab-border"]{display:none;}

/* sections */
.rw-sec{margin:56px 0 18px;}
.rw-kicker{display:flex;align-items:center;gap:12px;font-size:.78rem;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);}
.rw-kicker .n{color:var(--accent);}
.rw-kicker .bar{flex:0 0 36px;height:1px;background:var(--line);}
.rw-sec h2{font-family:'Instrument Serif',Georgia,serif !important;font-weight:400;font-size:2.35rem;line-height:1.12;margin:10px 0 10px;padding:0;}
.rw-sec p.lead{font-size:1.05rem;max-width:820px;margin:0;color:var(--body);}

/* cards */
[class*="st-key-card"]{background:var(--card);border:1px solid var(--line) !important;border-radius:18px !important;
  padding:6px 8px;box-shadow:0 1px 2px rgba(11,31,51,.04);}
[class*="st-key-eq"]{background:var(--card);border:1px solid var(--line) !important;border-radius:18px !important;padding:4px 8px;}
.rw-card{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:22px 24px;height:100%;}
.rw-card h4{margin:0 0 6px;font-size:1.05rem;}
.rw-card p{margin:0;font-size:.95rem;}
.rw-card .tag{display:inline-block;font-size:.72rem;font-weight:600;letter-spacing:.12em;text-transform:uppercase;margin-bottom:10px;}
.rw-card.pain{border-top:3px solid #DC2626;} .rw-card.pain .tag{color:#DC2626;}
.rw-card.sol{border-top:3px solid var(--ok);} .rw-card.sol .tag{color:var(--ok);}
.rw-card.warm{border-top:3px solid var(--warm);} .rw-card.warm .tag{color:var(--warm);}
.rw-card.cold{border-top:3px solid var(--cold);} .rw-card.cold .tag{color:var(--cold);}
.rw-grid{display:grid;gap:16px;}
.rw-grid.g2{grid-template-columns:repeat(2,minmax(0,1fr));}
.rw-grid.g3{grid-template-columns:repeat(3,minmax(0,1fr));}
.rw-grid.g4{grid-template-columns:repeat(4,minmax(0,1fr));}
.rw-facts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border:1px solid var(--line);border-radius:18px;background:#fff;overflow:hidden;}
.rw-fact{padding:20px 24px;border-right:1px solid var(--line);}
.rw-fact:last-child{border-right:none;}
.rw-fact .k{font-size:.75rem;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);}
.rw-fact .v{font-family:'Instrument Serif',Georgia,serif;font-size:1.9rem;color:var(--ink);line-height:1.2;margin-top:4px;}
.rw-fact .s{font-size:.85rem;color:var(--muted);}
.rw-steps{counter-reset:s;list-style:none;padding:0;margin:0;}
.rw-steps li{counter-increment:s;position:relative;padding:0 0 12px 40px;}
.rw-steps li::before{content:counter(s);position:absolute;left:0;top:1px;width:26px;height:26px;border-radius:50%;
  background:var(--accent-soft);color:var(--accent);font-weight:600;font-size:.85rem;display:flex;align-items:center;justify-content:center;}

/* simulator */
.rw-panel-title{font-size:.75rem;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:4px 0 8px;}
.rw-kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:6px 0 14px;}
.rw-kpis.k3{grid-template-columns:repeat(3,minmax(0,1fr));}
.rw-kpi{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px 16px;}
.rw-kpi .k{font-size:.8rem;color:var(--muted);}
.rw-kpi .v{font-size:1.6rem;font-weight:600;color:var(--ink);line-height:1.25;margin:2px 0;letter-spacing:-0.01em;}
.rw-kpi .s{font-size:.78rem;color:var(--muted);line-height:1.4;}
.rw-kpi.ok .v{color:var(--ok);} .rw-kpi.no .v{color:var(--no);}
.rw-verdict{display:flex;gap:14px;align-items:flex-start;border-radius:14px;padding:16px 18px;margin:4px 0 14px;border:1px solid;}
.rw-verdict.ok{background:var(--ok-soft);border-color:#BBF7D0;}
.rw-verdict.no{background:var(--no-soft);border-color:#FECACA;}
.rw-verdict .dot{flex:0 0 10px;height:10px;border-radius:50%;margin-top:7px;}
.rw-verdict.ok .dot{background:var(--ok);} .rw-verdict.no .dot{background:var(--no);}
.rw-verdict b.h{color:var(--ink);display:block;margin-bottom:2px;}
.rw-verdict span{font-size:.95rem;}
.rw-salt{font-weight:600;color:var(--ink);font-size:.95rem;margin:8px 0 2px;}
.rw-note{font-size:.85rem;color:var(--muted);line-height:1.55;}
.rw-case{border:1px solid var(--line);border-radius:14px;padding:14px 16px;background:#fff;}
.rw-case.on{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-soft);}
.rw-case .t{font-weight:600;color:var(--ink);}
.rw-flow{display:flex;gap:10px;align-items:stretch;flex-wrap:wrap;margin:8px 0 6px;}
.rw-node{flex:1 1 180px;background:#fff;border:1px solid var(--line);border-radius:16px;padding:16px 18px;}
.rw-node.hl{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-soft);}
.rw-node .k{font-size:.72rem;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);}
.rw-node b{display:block;color:var(--ink);font-size:1.02rem;margin:4px 0 2px;font-family:'SFMono-Regular',Consolas,monospace;}
.rw-node span{font-size:.85rem;color:var(--muted);}
.rw-arrow{align-self:center;color:var(--accent);font-size:1.4rem;}
.rw-table{width:100%;border-collapse:separate;border-spacing:0;background:#fff;border:1px solid var(--line);border-radius:14px;overflow:hidden;font-size:.86rem;}
.rw-table th{background:#F6F8FB;color:var(--muted);font-weight:600;font-size:.74rem;letter-spacing:.08em;text-transform:uppercase;text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);}
.rw-table td{padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top;color:var(--body);line-height:1.45;}
.rw-table tr:last-child td{border-bottom:none;}
.rw-table td.mono{font-family:'SFMono-Regular',Consolas,monospace;font-size:.8rem;color:var(--ink);}
.rw-foot{margin-top:72px;padding:22px 0;border-top:1px solid var(--line);font-size:.82rem;color:var(--muted);display:flex;justify-content:space-between;}
[data-testid="stExpander"] details{border-radius:14px !important;border-color:var(--line) !important;background:#fff;}
.stButton button{border-radius:999px;}
@media (max-width: 900px){.rw-hero{grid-template-columns:1fr;}.rw-grid.g2,.rw-grid.g3,.rw-grid.g4,.rw-facts,.rw-kpis{grid-template-columns:1fr;}}
</style>
"""

# simple schematic of the cloud layers (based on the course notes: warm < 0 degC line < mixed-phase < glaciated)
CLOUD_SVG = """
<svg viewBox="0 0 520 330" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Inter, sans-serif">
  <defs>
    <linearGradient id="g1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E0F2FE"/><stop offset="1" stop-color="#FFF7ED"/></linearGradient>
  </defs>
  <rect x="0" y="0" width="520" height="330" rx="18" fill="url(#g1)"/>
  <path d="M150 300 C 120 300 110 262 140 252 C 132 214 172 196 196 210 C 196 170 236 150 262 160 C 270 120 300 70 330 66
           C 300 52 236 46 210 40 L 420 40 C 380 48 352 58 340 70 C 372 86 372 140 352 162 C 388 170 398 214 372 226
           C 402 236 400 300 360 300 Z" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5"/>
  <line x1="24" y1="206" x2="496" y2="206" stroke="#0369A1" stroke-width="1.5" stroke-dasharray="6 5"/>
  <text x="30" y="200" font-size="11" fill="#0369A1" font-weight="600">FREEZING LEVEL · 0 °C</text>
  <g font-size="12" fill="#0B1F33">
    <text x="30" y="58" font-weight="600">Glaciated</text><text x="30" y="74" fill="#6B7A8C">ice only · ≈ −40 °C · ~7,600 m</text>
    <text x="30" y="128" font-weight="600" fill="#0369A1">Cold cloud (mixed-phase)</text>
    <text x="30" y="144" fill="#6B7A8C">supercooled water + ice · T &lt; 0 °C</text>
    <text x="30" y="160" fill="#6B7A8C">~5,500 m · seed with AgI</text>
    <text x="30" y="246" font-weight="600" fill="#B45309">Warm cloud</text>
    <text x="30" y="262" fill="#6B7A8C">liquid water only · T &gt; 0 °C</text>
    <text x="30" y="278" fill="#6B7A8C">~1,000 m · seed with NaCl / CaCl₂</text>
  </g>
  <g fill="#93C5FD"><circle cx="300" cy="250" r="3"/><circle cx="318" cy="268" r="2.5"/><circle cx="282" cy="276" r="2"/>
    <circle cx="340" cy="244" r="2"/></g>
  <g stroke="#1D4ED8" stroke-width="1.4"><path d="M300 110 l0 12 M294 116 l12 0 M296 112 l8 8 M304 112 l-8 8"/>
    <path d="M330 140 l0 10 M325 145 l10 0"/><path d="M276 150 l0 10 M271 155 l10 0"/></g>
</svg>
"""


def nav() -> str:
    return ('<div class="rw-nav"><div class="rw-brand"><span class="rw-mark"></span>RAINWISE</div>'
            '</div>')


def section(num: str, kicker: str, title: str, lead: str = "") -> str:
    lead_html = f'<p class="lead">{lead}</p>' if lead else ""
    return (f'<div class="rw-sec"><div class="rw-kicker"><span class="n">{num}</span><span class="bar"></span>'
            f'<span>{kicker}</span></div><h2>{title}</h2>{lead_html}</div>')


def card(tag: str, title: str, body: str, kind: str = "") -> str:
    return f'<div class="rw-card {kind}"><div class="tag">{tag}</div><h4>{title}</h4><p>{body}</p></div>'


def grid(items: list[str], cols: int = 2) -> str:
    return f'<div class="rw-grid g{cols}">' + "".join(items) + "</div>"


def facts(items: list[tuple[str, str, str]]) -> str:
    return '<div class="rw-facts">' + "".join(
        f'<div class="rw-fact"><div class="k">{k}</div><div class="v">{v}</div><div class="s">{s}</div></div>'
        for k, v, s in items) + "</div>"


def kpis(items: list[tuple], cols: int = 4) -> str:
    """items: (label, value, sub, kind, tooltip)."""
    cls = "rw-kpis" + (" k3" if cols == 3 else "")
    out = [f'<div class="{cls}">']
    for k, v, s, kind, tip in items:
        out.append(f'<div class="rw-kpi {kind}" title="{tip}"><div class="k">{k}</div><div class="v">{v}</div>'
                   f'<div class="s">{s}</div></div>')
    return "".join(out) + "</div>"


def verdict(ok: bool, head: str, body: str) -> str:
    return (f'<div class="rw-verdict {"ok" if ok else "no"}"><div class="dot"></div><div>'
            f'<b class="h">{head}</b><span>{body}</span></div></div>')


def footer() -> str:
    return ('<div class="rw-foot"><span>RAINWISE · educational simulator built on textbook thermodynamics</span>'
            '<span>Does not predict rainfall</span></div>')


def table(df, mono_cols: tuple = ()) -> str:
    """Render a DataFrame as a clean wrapping HTML table."""
    head = "".join(f"<th>{c}</th>" for c in df.columns)
    rows = []
    for _, r in df.iterrows():
        cells = "".join(f'<td class="{"mono" if c in mono_cols else ""}">{r[c]}</td>' for c in df.columns)
        rows.append(f"<tr>{cells}</tr>")
    return f'<table class="rw-table"><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table>'
