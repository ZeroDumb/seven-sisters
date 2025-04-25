# 🧰 Tool_Guide.md

## 🧬 Agent-to-Tool Mapping
Welcome to the loadout list of *The Seven Sisters*. Each agent is uniquely equipped with tools mapped to her specialty and operational modes. This isn’t just recon — this is personality-based execution orchestration. You're not launching a script, you're invoking a mindset.

# 🧰 Tool_Guide.md

## 🧬 Agent-to-Tool Mapping

| 🧍‍♀️ Sister   | 🔧 Mapped Tools                                           | ⚙️ Ops Levels | 🧠 Functionality                                                                 |
|-------------|-----------------------------------------------------------|--------------|----------------------------------------------------------------------------------|
| **Seven**   | config, CLI routing, summary/log                         | 1, 4, 5      | Main controller; parses flags, assigns sister jobs                             |
| **Harley**  | chaos-runner.sh, dnsrecon, massdns                       | 2, 3, 5      | Launches noisy tools, fuzzers, and brute force chaos                           |
| **Alice**   | waybackurls, gau, dirsearch, github-dorker              | 0, 1, 3      | Finds strange or hidden things; feeds recon loop                               |
| **Marla**   | tamper, burp, weird curl chains                         | 2, 3, 4      | Messes with headers, cookies, sessions                                          |
| **Luna**    | wappalyzer, anomaly heuristics, retire.js              | 0, 1, 2      | Runs tech detection, plugin analyzers, fringe modules                          |
| **Lisbeth** | nmap, nuclei, httpx, xsstrike                           | 0, 1, 4      | Runs exploit pathfinding quietly, reports risks                                |
| **The Bride** | delete.sh, final payloads, kill switches              | 1, 4, 5      | Clean up, archive, kill. The wrap-up script of doom                            |

## 🧪 Tool Descriptions & Setup

### **Seven — The Orchestrator**
- **Python 3.x**, `click`, `rich`
- 📁 `/tools/seven/`
- Orchestration, config loading, and command routing

### **Harley — The Wildfire**
- `dnsrecon`, `massdns`, `ffuf`
- 📁 `/tools/harley/`
- DNS noise, fuzzing, brute force automation

### **Alice — The Seeker**
- `gau`, `waybackurls`, `dirsearch`, `github-dorker`
- 📁 `/tools/alice/`
- URL mining, endpoint finding, forgotten artifacts

### **Marla — The Breakdown**
- `burp`, `tamper-data`, `curl` chains
- 📁 `/tools/marla/`
- Header injection, session tampering, auth oddities

### **Luna — The Dreamwalker**
- `wappalyzer`, `retire.js`, custom `anomalies.py`
- 📁 `/tools/luna/`
- Tech fingerprinting, plugin discovery, heuristic checks

### **Lisbeth — The Cipher**
- `nmap`, `nuclei`, `httpx`, `xsstrike`
- 📁 `/tools/lisbeth/`
- Low-noise scanning, vulnerability checking, CVE discovery

### **The Bride — The Executioner**
- `delete.sh`, `awscli`, `zip`, `scp`, `final-payload.py`
- 📁 `/tools/bride/`
- Final data exfil, kill ops, logging and archiving

---

> Each sister will receive her own startup script, optional install routine, and signature startup message. 
> Don't forget: the **start phrase is** `I solemnly swear that I am up to no good` and the **end phrase is** `Mischief Managed`.

More updates coming in the build structure! Let’s finish this one hoodie at a time.


## 🔁 Staying Grounded in Scope
We built this with humor, story, and flair — but **"Out of Scope™"** is still very real. This isn’t just a cool skin on basic scripts. It’s a **lesson, a tool, a philosophy**, and a **blueprint** for how far one person and AI can go — and a soft, sarcastic reminder that even the best explorers need rules.

- The goal: **teach + showcase + question boundaries**.
- The result: **command-line theater meets practical automation**.
- The risk: it becomes another forgotten dream.
- The fix: don’t let it.

Mischief Managed.
