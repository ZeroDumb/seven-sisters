#!/bin/bash
echo "👻 Ghost protocol engaged."

nmap -Pn -sV "$1" -oN scan_nmap.txt
nuclei -u "$1" -o nuclei_report.txt
httpx -u "$1" -silent -status-code
python3 xsstrike/xsstrike.py -u "$1"
