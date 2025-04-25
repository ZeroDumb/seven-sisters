🧍‍♀️ Seven – The Orchestrator
Tools	Where to Find Them
CLI routing scripts	Python-based orchestration (main.py & summon.py)
Mission logging	Python logging module with timestamped reports
Config parser	JSON with Python's json module
🧭 Tip: She's your main.py. Everything branches from her. 

You're writing this one from scratch, naturally. Just like Seven would want.

🧍‍♀️ Harley – The Wildfire
Tool	Source
dnsrecon	pip install dnsrecon or from GitHub
massdns	GitHub (needs to be compiled)
chaos-runner.sh	You're writing this beautiful mess 😈

🧨 Bonus: Toss in some ffuf, dirbuster, or wfuzz if Harley needs more fireworks.

🧍‍♀️ Alice – The Seeker
Tool	Source
waybackurls	GitHub
gau	GitHub
dirsearch	GitHub
github-dorker	GitHub or build your own

🐇 Keep these light. She's chasing holes, not breaking doors.

🧍‍♀️ Marla – The Breakdown
Tool	Source
burpsuite	Community Edition from PortSwigger
tamper	Write your own, or script with curl, httpie, or modify sqlmap payloads
Weird curl/cookie hacks	You. Bash. Madness. Optional caffeine drip.

💊 Hint: She's your custom packet manipulator. Don't expect a UI — that's not her thing.

🧍‍♀️ Luna – The Dreamwalker
Tool	Source
wappalyzer	Wappalyzer CLI or Browser Extension
Anomaly heuristics	Script it: header weirdness, strange DNS, mismatched tech stacks

✨ Optional: Run her tools after Alice but before Lisbeth.

🧍‍♀️ Lisbeth – The Cipher
Tool	Source
nmap	nmap.org
nuclei	GitHub
httpx	GitHub
XSStrike	GitHub
👤 Silent, deadly, needs threads and clean output. 

Route her through a custom wrapper if you're feeling fancy.

🧍‍♀️ The Bride – The Executioner
Tool	Source
delete.sh	Custom kill script. Only run in terminal mode.
Final payloads	Your choice — serious cleanup or mock "termination"
Kill switches	Built into Seven or triggered manually

⚔️ This is your "End Game." Archive, red team cleanup, log export, maybe a little rsync magic.

seven-sisters/
├── seven/
├── harley/
├── alice/
├── marla/
├── luna/
├── lisbeth/
├── bride/
└── shared/   # helper libs, configs, logs
