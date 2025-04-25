#!/bin/bash
echo "✨ Activating starlight protocol..."

# Tech stack analysis
wappalyzer "$1" > tech_report.txt
# Optional: anomaly detection scripts
python3 anomaly.py "$1"
