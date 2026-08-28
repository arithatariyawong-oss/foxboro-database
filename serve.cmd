@echo off
REM Fallback launcher: use this only if opening index.html directly is blocked.
REM Serves this folder at http://127.0.0.1:8712 and opens it in the browser.
cd /d "%~dp0"
start "" http://127.0.0.1:8712/index.html
python -m http.server 8712 --bind 127.0.0.1
