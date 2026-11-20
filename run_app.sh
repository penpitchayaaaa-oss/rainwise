#!/usr/bin/env bash
# RAINWISE launcher for macOS/Linux
cd "$(dirname "$0")"
python3 -m pip install -q -r requirements.txt
( sleep 8; (xdg-open http://localhost:8501 || open http://localhost:8501) >/dev/null 2>&1 ) &
python3 -m streamlit run app.py --server.headless true --server.port 8501
