# 🧠 Seven Sisters:

> **"I solemnly swear that I am up to no good."**

Welcome to **Seven Sisters**, a character-driven, AI-augmented, open-source research and recon tool designed to showcase the creative and technical potential of modern tooling—through the lens of narrative, automation, and community. What began as a chaotic middle-life side quest is now a CLI-centric, modular system built for learners, tinkerers, ethical hackers, and hoodie-wearing misfits.

It is part security toolkit, part AI prompt engine, and part character-driven operating narrative.

It was built to explore what one human (with caffeine, some coding, and AI companions) can make using freely available AI tools.

What started as a late-night middle-life curiosity has become a fully modular, CLI-based OSINT orchestration system powered by fictional agents and real-world tooling. Use it to explore what's possible — technically, creatively, ethically.

**⚠️ DISCLAIMER:** This was built as a demonstration, educational, and learning tool. Yes, it works, but you are responsible for what you do with it. In no way are the creators liable in any form or function, nor will you attempt to hold the creators liable in any form for any function or lack of function, or the results of your actions with this tool. This is meant for dry runs only, private VM spinups and in-scope projects. The use of this tool out of scope is not encouraged, or endorsed, and will likely land you on famous idiot criminals news feed somewhere. Further, to deter random acts of stupidity, I have purposely left the tool box empty. You will need to make sure you have all necessary tools installed. If you can't find or add the tools, then the 7-sisters aren't your girls anyway.

---

## 🎯 Project Goals

To build a creative, ethical, and technically impressive system that:
- Showcase what's possible with LLM-assisted development
- Enhances curiosity and learning
- Merges automation and personality
- Teach through character and creativity
- Enable safe experimentation with open-source tooling
- Encourage storytelling and ethics in the security space
- Offer something fun and still technically valuable

---

## 🌌 Features (Core System)

- **Seven Sisters**, each with distinct personalities, tools, and voice
- CLI-first experience with stylized prompts and ASCII banners
- Modular toolchains that reflect the "Operational Modes"
- Ethical-first: encourages safe, scoped research
- Config-driven: easy to extend, modify, and deploy
- Inter-Process Communication (IPC) system for sister coordination
- Character-driven guides for each sister's tools and capabilities

---

## 🧬 The Sisters

Each "Sister" acts as a role-driven agent within a larger mission:

| Agent     | Role           | Mode Range | Tagline              |
|-----------|----------------|------------|----------------------|
| Seven     | Orchestrator   | 1, 4, 5    |"You will assimilate" |
| Harley    | Disruptor      | 2, 3, 5    |"Yes puddin"          |
| Alice     | Scout          | 0, 1, 3    |"Rabbit hole runtime" |
| Marla     | Chaos Lens     | 2, 3, 4    |"Slide"               |
| Luna      | Seer           | 0, 1, 2    |"Starlight protocol"  |
| Lisbeth   | Ghost Hacker   | 0, 1, 4    |"Ghost protocol"      |
| The Bride | Cleaner        | 1, 4, 5    |"Kill command"        |

Each sister has a detailed guide in their respective directory (e.g., `agents/Seven/terminal_sequence.md`) that explains their tools, capabilities, and ethical usage.

---

## ⚙️ Technical Stack

- **Python** (Core orchestration & agent logic)
- **Bash/Shell** (Tool execution & integrations)
- **JSON** (Configuration & agent personas)
- **ZeroMQ** (Inter-Process Communication)
- **Common tools:** `nmap`, `gau`, `httpx`, `dirsearch`, `nuclei`, etc.
- **LLMs** – (Optional) Integration planned for on-device ***WIP***

---

## 🧱 Phases & Progress

### Phase 1 – MVP / CLI Foundation
- [x] Scaffold CLI: `main.py` & `summon.py`
- [x] Agent selector and protocol router
- [x] JSON config for each sister
- [x] Logging system with timestamped reports
- [x] Base execution: `init.py` modules
- [x] ASCII intros for Seven + Sisters

### Phase 2 – Toolchains & Character Layers
- [x] Add distinct tools per sister
- [x] Mode enforcement (Ghost, Recon, etc)
- [x] Logging per sister
- [x] Config toggles: silent vs noisy
- [x] Sister-specific guides and documentation

### Phase 3 – Showcase + Deployment
- [ ] Example scoped run with video capture
- [ ] Export report as Markdown & PDF
- [ ] Publish GitHub page and demo walkthrough
- [ ] Write companion blog post: *"How I built an ethical AI-driven OSINT tool with narrative."*

### Phase 4 – Demos, and Beyond
- [ ] DEFCON pitch deck
- [ ] Live terminal showcase at a meetup/conference

---
## 🧠 Use Cases

- Red team training in a fun shell
- CTF automation with flair
- OSINT practice & visualization
- Ethical hacking theater
- Terminal magic shows


---

## 🎒 Installation

```bash
git clone https://github.com/yourusername/7-sisters
cd 7-sisters
python3 main.py
```

---

## ✨ Inspiration

This project is a love letter to:
- Creative misfits who use AI as an amplifier
- Midlife rebuilders with too many tabs open
- The idea that security can be fun, stylized, and responsible
- The belief that great tools don't have to look boring

---

Each agent's tool script in `agents/tools/` is your Sister's personal spellbook, and `main.py` is how you summon the coven. 

---

## 📫 Get Involved

- Star the repo, fork the chaos, wear the hoodie
- Raise issues, suggest new toolchains, or open pull requests
- Write better banter 
- Scoped testing welcome (please stay ethical)

> **"Mischief Managed."**

