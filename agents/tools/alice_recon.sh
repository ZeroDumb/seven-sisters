#!/bin/bash
echo "🐇 Following the white rabbit..."

waybackurls "$1" > urls_wayback.txt
gau "$1" >> urls_wayback.txt
dirsearch -u "$1" -e php,html,js --output=dir_output.txt
python3 github-dorker.py -q "$1" --token $GITHUB_TOKEN
