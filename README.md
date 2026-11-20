# RAINWISE — the thermodynamics of cloud seeding

An interactive educational simulator for Topic 13 (Royal Rainmaking and Cloud Seeding).
It follows the course-notes framework **What · Where · When · Why · How · Result** and uses only five
textbook principles:

| Cloud | Principle | Equation |
|---|---|---|
| Warm (> 0 °C), NaCl / CaCl₂ | Kelvin effect | p_eq(r) = p_eq,flat · exp(2γV_m / rRT) |
| | Raoult's law | p_w = a_w · p*_w |
| | Köhler curve | S_eq − 1 = A/r − B/r³ ; r_c = √(3B/A) ; S_c − 1 = √(4A³/27B) |
| Cold (< 0 °C), AgI | Classical nucleation theory (explanation) | ΔG(r) = 4πr²γ + (4/3)πr³ΔG_v ; r* = 2γ/abs(ΔG_v) ; ΔG* = 16πγ³ / 3ΔG_v² |
| | Clausius–Clapeyron (explanation) | d ln p* / d(1/T) = −Δh/R ; Δh_sub = Δh_vap + Δh_fus → p*_ice < p*_liq |
| | Condensation-freezing on AgI (calculated) | F = 900((268.66 − T)/10)³(S_w − 1)² (Yang et al., 2024, Eq. 2) ; INP = F × N_AgI × 1000 |

It does **not** predict rainfall.

## Run
Windows: install Python 3.10+ from python.org (tick "Add python.exe to PATH"), then double-click
`run_app.bat`. The browser opens at http://localhost:8501. Keep the black window open while using the app.

Any OS:
```
python -m pip install -r requirements.txt
python -m streamlit run app.py
python -m pytest            # 18 automated checks
```

## Where everything is
```
app.py              page layout and wording (no physics)
models/constants.py loads the database below
models/warm.py      Kelvin, Raoult, Köhler (warm cloud)
models/agi.py       AgI condensation-freezing: active fraction F and INP (cold cloud)
utils/plots.py      charts
utils/theme.py      visual design
data/constants.csv  every physical constant, with unit and source
data/salts.csv      molar mass, density and ion count of each salt
tests/              automated verification
slide_images/       16:9 screenshots for presentation slides
```

## Using your own values
1. **In the app:** sliders and boxes on each simulator panel.
2. **Salt library / Advanced:** in Warm-cloud seeding → Salt library, edit the table or add a row (molar mass, density, ions i) and click Save; change γ under Advanced.
3. **Database:** add a row to `data/salts.csv` or edit `data/constants.csv`, then restart the app. Always fill in the source column.

The "How it works" tab inside the app traces every displayed number to its equation, its mathematics,
the function that computes it, the data it reads, and the reference.
