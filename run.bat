@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Starting Toqi99bigwin Server...
python app.py
pause
