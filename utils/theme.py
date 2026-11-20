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
.rw-hero h1{font-family:'Instrument Serif',Georgia,serif !important;font-weight:400;font-size:clamp(2.1rem,7.2vw,3.4rem);line-height:1.08;overflow-wrap:normal;word-break:keep-all;hyphens:none;
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
.rw-method li{margin-bottom:6px;}
.rw-figcap{font-size:.85rem;color:var(--muted);line-height:1.55;margin:-6px 0 18px;max-width:900px;}
.rw-checks{padding-left:1.1rem;margin:0;}
.rw-checks li{margin-bottom:10px;line-height:1.6;}
.rw-table a{color:var(--accent);text-decoration:none;font-family:'SFMono-Regular',Consolas,monospace;font-size:.8rem;white-space:nowrap;}
.rw-table a:hover{text-decoration:underline;}
@media (max-width: 600px){.rw-hero{padding:36px 0 24px;}.rw-hero h1{font-size:2.15rem;}.rw-sec h2{font-size:1.7rem;}.rw-fact .v{font-size:1.5rem;}.block-container{padding:0 1rem 3rem !important;}}
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


# original schematic drawings (not copied from any source)
KELVIN_SVG = """
<svg viewBox="0 0 520 210" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Inter, sans-serif">
  <rect width="520" height="210" rx="16" fill="#F8FAFC"/>
  <text x="130" y="26" text-anchor="middle" font-size="13" font-weight="600" fill="#0B1F33">Flat water surface</text>
  <rect x="40" y="140" width="180" height="40" rx="4" fill="#BFDBFE"/>
  <g stroke="#2563EB" stroke-width="2" marker-end="url(#a)"><line x1="90" y1="136" x2="90" y2="104"/><line x1="170" y1="136" x2="170" y2="104"/></g>
  <text x="130" y="80" text-anchor="middle" font-size="12" fill="#334155">few molecules escape</text>
  <text x="130" y="198" text-anchor="middle" font-size="12" fill="#0B1F33">p<tspan dy="4" font-size="9">eq,flat</tspan></text>
  <text x="390" y="26" text-anchor="middle" font-size="13" font-weight="600" fill="#0B1F33">Small droplet (radius r)</text>
  <circle cx="390" cy="135" r="30" fill="#BFDBFE"/>
  <g stroke="#DC2626" stroke-width="2" marker-end="url(#b)"><line x1="390" y1="102" x2="390" y2="68"/><line x1="417" y1="115" x2="447" y2="92"/>
    <line x1="363" y1="115" x2="333" y2="92"/><line x1="423" y1="142" x2="458" y2="146"/><line x1="357" y1="142" x2="322" y2="146"/></g>
  <text x="390" y="56" text-anchor="middle" font-size="12" fill="#334155">more molecules escape</text>
  <text x="390" y="198" text-anchor="middle" font-size="12" fill="#0B1F33">p<tspan dy="4" font-size="9">eq</tspan><tspan dy="-4">(r) &gt; p</tspan><tspan dy="4" font-size="9">eq,flat</tspan></text>
  <defs><marker id="a" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#2563EB"/></marker>
  <marker id="b" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#DC2626"/></marker></defs>
</svg>"""

BERGERON_SVG = """
<svg viewBox="0 0 520 210" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Inter, sans-serif">
  <rect width="520" height="210" rx="16" fill="#F8FAFC"/>
  <text x="260" y="26" text-anchor="middle" font-size="13" font-weight="600" fill="#0B1F33">Below 0 °C: vapour moves from droplets to ice</text>
  <circle cx="110" cy="115" r="34" fill="#BFDBFE"/><circle cx="110" cy="115" r="22" fill="none" stroke="#2563EB" stroke-dasharray="3 3"/>
  <text x="110" y="172" text-anchor="middle" font-size="12" fill="#334155">supercooled droplet</text>
  <text x="110" y="190" text-anchor="middle" font-size="12" fill="#DC2626">evaporates (shrinks)</text>
  <g stroke="#64748B" stroke-width="2" marker-end="url(#c)"><line x1="155" y1="100" x2="330" y2="100"/><line x1="155" y1="130" x2="330" y2="130"/></g>
  <text x="243" y="90" text-anchor="middle" font-size="12" fill="#0B1F33">water vapour</text>
  <text x="243" y="152" text-anchor="middle" font-size="12" fill="#0B1F33">p*<tspan dy="4" font-size="9">liq</tspan><tspan dy="-4"> &gt; p*</tspan><tspan dy="4" font-size="9">ice</tspan></text>
  <g transform="translate(400,115)" stroke="#1E3A8A" stroke-width="3" stroke-linecap="round">
    <line x1="0" y1="-38" x2="0" y2="38"/><line x1="-33" y1="-19" x2="33" y2="19"/><line x1="-33" y1="19" x2="33" y2="-19"/>
    <g stroke-width="2"><line x1="0" y1="-26" x2="-8" y2="-34"/><line x1="0" y1="-26" x2="8" y2="-34"/><line x1="0" y1="26" x2="-8" y2="34"/>
    <line x1="0" y1="26" x2="8" y2="34"/></g></g>
  <text x="400" y="172" text-anchor="middle" font-size="12" fill="#334155">ice crystal</text>
  <text x="400" y="190" text-anchor="middle" font-size="12" fill="#15803D">grows (deposition)</text>
  <defs><marker id="c" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#64748B"/></marker></defs>
</svg>"""

COALESCENCE_SVG = """
<svg viewBox="0 0 520 170" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Inter, sans-serif">
  <rect width="520" height="170" rx="16" fill="#F8FAFC"/>
  <g fill="#93C5FD"><circle cx="60" cy="60" r="7"/><circle cx="90" cy="95" r="6"/><circle cx="50" cy="120" r="5"/>
    <circle cx="200" cy="55" r="5"/><circle cx="225" cy="110" r="6"/><circle cx="410" cy="60" r="5"/><circle cx="440" cy="105" r="4"/></g>
  <circle cx="150" cy="80" r="16" fill="#2563EB"/><line x1="150" y1="100" x2="150" y2="135" stroke="#2563EB" stroke-width="2" marker-end="url(#d)"/>
  <circle cx="330" cy="95" r="26" fill="#1D4ED8"/><line x1="330" y1="125" x2="330" y2="158" stroke="#1D4ED8" stroke-width="2" marker-end="url(#d)"/>
  <text x="150" y="30" text-anchor="middle" font-size="12" fill="#0B1F33">large drop falls faster</text>
  <text x="330" y="40" text-anchor="middle" font-size="12" fill="#0B1F33">collects small drops → grows</text>
  <text x="455" y="150" text-anchor="middle" font-size="12" fill="#0B1F33">heavy enough → rain</text>
  <defs><marker id="d" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#1D4ED8"/></marker></defs>
</svg>"""


# ---------------------------------------------------------------- intro flow (animated) and prototype notice
_ICONS = {
    "book": '<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/><path d="M4 21V5"/><path d="M8 7h7M8 11h7"/>',
    "data": '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/><path d="M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/>',
    "fx": '<rect x="3" y="3" width="18" height="18" rx="4"/><path d="M10 7c-1.5 0-2 1-2 2v8M6.5 11h4"/><path d="M13 11l4 6M17 11l-4 6"/>',
    "sliders": '<path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0"/><circle cx="16" cy="6" r="2"/><circle cx="10" cy="12" r="2"/><circle cx="18" cy="18" r="2"/>',
    "chart": '<path d="M4 20V4"/><path d="M4 20h16"/><path d="M7 16c3-1 4-8 7-8s3 5 6 5"/>',
    "shield": '<path d="M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
}


def _icon(name: str) -> str:
    return (f'<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round">{_ICONS[name]}</svg>')


INTRO_STEPS = [
    ("book", "01 · Principles", "Course notes",
     "Kelvin effect, Raoult’s law, Köhler curve, nucleation theory, Clausius–Clapeyron."),
    ("data", "02 · Data", "Reference values",
     "Constants from the CRC Handbook, IAPWS-95 and peer-reviewed papers. Every value has a source."),
    ("fx", "03 · Equations", "Model code",
     "One equation = one Python function, in SI units. No hidden fitting."),
    ("sliders", "04 · Your inputs", "Cloud conditions",
     "Salt and particle size, temperature, humidity (supersaturation), amount of AgI."),
    ("chart", "05 · Results", "Numbers & charts",
     "Critical radius and supersaturation, activation verdict, AgI active fraction and ice crystals (INP)."),
    ("shield", "06 · Checks", "Verification",
     "18 automated checks against the maths and hand calculations. Field validation still to come."),
]


def intro_flow() -> str:
    boxes = []
    for i, (ic, k, t, d) in enumerate(INTRO_STEPS):
        boxes.append(f'<div class="rw-fbox" style="animation-delay:{i * 0.12:.2f}s"><div class="rw-ficon">{_icon(ic)}</div>'
                     f'<div class="rw-fk">{k}</div><div class="rw-ft">{t}</div><div class="rw-fd">{d}</div></div>')
        if i < len(INTRO_STEPS) - 1:
            boxes.append('<div class="rw-flink"><span class="rw-fdot" style="animation-delay:'
                         f'{i * 0.35:.2f}s"></span></div>')
    return ('<div class="rw-intro"><div class="rw-intro-head"><span class="rw-badge2">Scientific simulator · prototype</span>'
            '<h3>Where every number in RAINWISE comes from</h3>'
            '<p>RAINWISE is <b>not</b> a weather forecast and does <b>not</b> predict rainfall. It is a scientific simulator: '
            'you change the cloud conditions and it calculates what textbook thermodynamics says should happen.</p></div>'
            f'<div class="rw-fflow">{"".join(boxes)}</div></div>')


INTRO_CSS = """
<style>
.rw-intro{background:#fff;border:1px solid var(--line);border-radius:22px;padding:26px 26px 22px;margin:8px 0 6px;
  box-shadow:0 18px 40px -32px rgba(11,31,51,.45);}
.rw-intro-head h3{font-family:'Instrument Serif',Georgia,serif !important;font-weight:400;font-size:1.9rem;margin:10px 0 6px;padding:0;}
.rw-intro-head p{margin:0 0 18px;max-width:860px;color:var(--body);}
.rw-badge2{display:inline-block;font-size:.72rem;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);
  background:var(--accent-soft);border-radius:999px;padding:5px 12px;}
.rw-fflow{display:flex;align-items:stretch;gap:0;}
.rw-fbox{flex:1 1 0;min-width:0;border:1px solid var(--line);border-radius:16px;padding:14px 14px 12px;background:linear-gradient(180deg,#fff,#F7F9FC);
  opacity:0;transform:translateY(8px);animation:rwIn .6s ease forwards;transition:box-shadow .2s, transform .2s;}
.rw-fbox:hover{box-shadow:0 10px 24px -14px rgba(29,78,216,.45);transform:translateY(-2px);}
.rw-ficon{width:42px;height:42px;border-radius:12px;background:var(--accent-soft);color:var(--accent);display:flex;align-items:center;justify-content:center;margin-bottom:10px;}
.rw-fbox:last-child .rw-ficon{background:#F0FDF4;color:var(--ok);}
.rw-fk{font-size:.68rem;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);}
.rw-ft{font-weight:600;color:var(--ink);font-size:.98rem;margin:2px 0 4px;}
.rw-fd{font-size:.8rem;color:var(--muted);line-height:1.45;}
.rw-flink{flex:0 0 22px;align-self:center;height:2px;background:repeating-linear-gradient(90deg,#C7D2FE 0 4px,transparent 4px 7px);position:relative;}
.rw-fdot{position:absolute;top:-3px;left:0;width:8px;height:8px;border-radius:50%;background:var(--accent);animation:rwDot 2.1s ease-in-out infinite;}
@keyframes rwIn{to{opacity:1;transform:none;}}
@keyframes rwDot{0%{left:-2px;opacity:0;}20%{opacity:1;}80%{opacity:1;}100%{left:18px;opacity:0;}}
.rw-proto{margin:72px 0 24px;border-radius:22px;padding:28px;background:linear-gradient(135deg,#0B1F33 0%,#13305A 60%,#1D4ED8 130%);color:#E2E8F0;}
.rw-proto h3{font-family:'Instrument Serif',Georgia,serif !important;font-weight:400;font-size:2rem;color:#fff !important;margin:8px 0 6px;padding:0;}
.rw-proto p{color:#CBD5E1;margin:0;}
.rw-proto .rw-badge2{background:rgba(255,255,255,.12);color:#BFDBFE;}
.rw-pgrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:18px 0 6px;}
.rw-pcard{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.14);border-radius:16px;padding:14px 16px;}
.rw-pcard .k{font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;color:#93C5FD;font-weight:600;}
.rw-pcard .t{color:#fff;font-weight:600;margin:4px 0;}
.rw-pcard .d{font-size:.85rem;color:#CBD5E1;line-height:1.5;}
.rw-road{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:6px;}
.rw-ritem{display:flex;gap:12px;background:#fff;border:1px solid var(--line);border-radius:16px;padding:14px 16px;}
.rw-rnum{flex:0 0 30px;height:30px;border-radius:9px;background:var(--accent-soft);color:var(--accent);font-weight:700;display:flex;align-items:center;justify-content:center;font-size:.85rem;}
.rw-ritem b{color:var(--ink);}
.rw-ritem .d{font-size:.88rem;color:var(--body);line-height:1.5;margin-top:2px;}
.rw-tag{display:inline-block;font-size:.66rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;border-radius:6px;padding:2px 7px;margin-left:6px;vertical-align:2px;}
.rw-tag.v{background:#FEF3C7;color:#92400E;} .rw-tag.m{background:#E0E7FF;color:#3730A3;} .rw-tag.d{background:#DCFCE7;color:#166534;}
@media (max-width: 900px){.rw-fflow{flex-direction:column;gap:6px;}.rw-flink{flex:0 0 14px;width:2px;height:14px;align-self:center;
  background:repeating-linear-gradient(180deg,#C7D2FE 0 4px,transparent 4px 7px);}.rw-fdot{display:none;}
  .rw-pgrid,.rw-road{grid-template-columns:1fr;}}
</style>
"""


def prototype_notice() -> str:
    return ('<div class="rw-proto"><span class="rw-badge2">Prototype status</span>'
            '<h3>A prototype to test an idea — not an operational tool</h3>'
            '<p>RAINWISE is an educational and research prototype. Its calculations have been checked numerically, but they '
            'have <b>not yet been validated against real measurements</b> from clouds or laboratories.</p>'
            '<div class="rw-pgrid">'
            '<div class="rw-pcard"><div class="k">What it is</div><div class="t">A scientific simulator</div>'
            '<div class="d">Change the conditions and see what thermodynamic models predict, with every equation and value traceable.</div></div>'
            '<div class="rw-pcard"><div class="k">What it is not</div><div class="t">Not a forecast or rain predictor</div>'
            '<div class="d">It does not forecast the weather, predict rainfall amounts or decide real seeding operations.</div></div>'
            '<div class="rw-pcard"><div class="k">Tested so far</div><div class="t">Numerically verified</div>'
            '<div class="d">18 automated checks pass: maths, hand calculations, physical trends, limits of the equations '
            'and bad inputs.</div></div></div></div>')


ROADMAP = [
    ("v", "Validate warm-cloud results with measured data",
     "Compare the predicted critical supersaturation of NaCl and CaCl₂ particles with laboratory CCN-counter measurements."),
    ("v", "Validate the AgI active fraction with cloud-chamber data",
     "Check the condensation-freezing active fraction against measured freezing fractions of AgI particles."),
    ("v", "Measure the real seeding materials",
     "Particle size distribution of the powders, the hydrate state of CaCl₂ and the ice-nucleating ability of the AgI flares used."),
    ("m", "Add time: how fast drops and crystals grow",
     "Condensation growth rates and collision–coalescence, so the model can say how long growth takes."),
    ("m", "More AgI mechanisms",
     "Add the other AgI mechanisms (deposition, immersion, contact) and let properties change with temperature."),
    ("d", "Connect to real atmospheric soundings",
     "Read measured temperature and humidity profiles to show when and at which height the seeding conditions are met."),
    ("d", "Compare with Royal Rainmaking operation records",
     "Test whether the model's 'activates / AgI works' conditions match days when seeding was carried out."),
    ("d", "Expert review",
     "Review by atmospheric scientists and the Department of Royal Rainmaking and Agricultural Aviation before any wider use."),
]


def roadmap() -> str:
    tag = {"v": ("Need verification", "v"), "m": ("Model upgrade", "m"), "d": ("Data & deployment", "d")}
    items = []
    for i, (k, t, d) in enumerate(ROADMAP, 1):
        lab, cls = tag[k]
        items.append(f'<div class="rw-ritem"><div class="rw-rnum">{i}</div><div><b>{t}</b>'
                     f'<span class="rw-tag {cls}">{lab}</span><div class="d">{d}</div></div></div>')
    return '<div class="rw-road">' + "".join(items) + "</div>"

# full chain: droplet -> ice crystal (deposition) -> snow falls -> melts below 0 degC -> rain (original drawing)
ICE_TO_RAIN_SVG = """
<svg viewBox="0 0 1000 300" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Inter, sans-serif">
  <rect width="1000" height="300" rx="18" fill="#F8FAFC"/>
  <rect x="0" y="0" width="1000" height="205" rx="18" fill="#EFF6FF"/>
  <line x1="20" y1="205" x2="980" y2="205" stroke="#0369A1" stroke-width="1.5" stroke-dasharray="6 5"/>
  <text x="980" y="197" text-anchor="end" font-size="12" font-weight="600" fill="#0369A1">0 °C level</text>
  <text x="30" y="30" font-size="12" font-weight="600" fill="#0369A1">CLOUD BELOW 0 °C</text>
  <text x="30" y="290" font-size="12" font-weight="600" fill="#B45309">AIR ABOVE 0 °C</text>
  <g font-size="12" text-anchor="middle">
    <!-- 1 droplet -->
    <circle cx="110" cy="105" r="30" fill="#BFDBFE"/><circle cx="110" cy="105" r="19" fill="none" stroke="#2563EB" stroke-dasharray="3 3"/>
    <text x="110" y="62" font-weight="700" fill="#1D4ED8">1</text>
    <text x="110" y="155" fill="#0B1F33">supercooled droplet</text><text x="110" y="172" fill="#DC2626">evaporates</text>
    <!-- arrow vapour -->
    <g stroke="#64748B" stroke-width="2" marker-end="url(#ar)"><line x1="150" y1="95" x2="265" y2="95"/><line x1="150" y1="115" x2="265" y2="115"/></g>
    <text x="207" y="85" fill="#334155">water vapour</text><text x="207" y="135" fill="#334155">p*<tspan dy="4" font-size="9">liq</tspan><tspan dy="-4"> &gt; p*</tspan><tspan dy="4" font-size="9">ice</tspan></text>
    <!-- 2 crystal -->
    <g transform="translate(320,105)" stroke="#1E3A8A" stroke-width="3" stroke-linecap="round">
      <line x1="0" y1="-30" x2="0" y2="30"/><line x1="-26" y1="-15" x2="26" y2="15"/><line x1="-26" y1="15" x2="26" y2="-15"/></g>
    <text x="320" y="62" font-weight="700" fill="#1D4ED8">2</text>
    <text x="320" y="155" fill="#0B1F33">ice crystal grows</text><text x="320" y="172" fill="#15803D">deposition + riming</text>
    <line x1="365" y1="105" x2="470" y2="105" stroke="#64748B" stroke-width="2" marker-end="url(#ar)"/>
    <!-- 3 snowflake heavy -->
    <g transform="translate(530,105)" stroke="#1E3A8A" stroke-width="4" stroke-linecap="round">
      <line x1="0" y1="-40" x2="0" y2="40"/><line x1="-35" y1="-20" x2="35" y2="20"/><line x1="-35" y1="20" x2="35" y2="-20"/>
      <g stroke-width="2.5"><line x1="0" y1="-28" x2="-9" y2="-37"/><line x1="0" y1="-28" x2="9" y2="-37"/><line x1="0" y1="28" x2="-9" y2="37"/><line x1="0" y1="28" x2="9" y2="37"/></g></g>
    <text x="530" y="52" font-weight="700" fill="#1D4ED8">3</text>
    <text x="530" y="168" fill="#0B1F33">heavy enough → falls as snow</text>
    <line x1="590" y1="125" x2="700" y2="230" stroke="#64748B" stroke-width="2" marker-end="url(#ar)"/>
    <!-- 4 rain -->
    <path d="M770 205 C 755 230 750 245 770 255 C 790 245 785 230 770 205 Z" fill="#2563EB"/>
    <path d="M820 220 C 810 238 807 248 820 255 C 833 248 830 238 820 220 Z" fill="#60A5FA"/>
    <text x="795" y="198" font-weight="700" fill="#1D4ED8">4</text>
    <text x="900" y="240" fill="#0B1F33">melts → rain</text>
    <text x="900" y="257" fill="#B45309">reaches the ground</text>
  </g>
  <defs><marker id="ar" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#64748B"/></marker></defs>
</svg>"""
