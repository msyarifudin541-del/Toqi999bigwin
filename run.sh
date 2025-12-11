#!/bin/bash
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting Toqi99bigwin Server..."
python3 app.py
