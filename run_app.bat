@echo off
REM RAINWISE launcher for Windows: installs the requirements (first run) and opens the app in your browser.
cd /d "%~dp0"
where py >nul 2>nul && (set PY=py) || (set PY=python)
echo Installing / checking packages ...
%PY% -m pip install -q -r requirements.txt
echo.
echo Starting RAINWISE ... the browser will open at http://localhost:8501
echo Keep this window open while using the app. Close it to stop the app.
start "" cmd /c "timeout /t 8 /nobreak >nul & start http://localhost:8501"
%PY% -m streamlit run app.py --server.headless true --server.port 8501
pause
