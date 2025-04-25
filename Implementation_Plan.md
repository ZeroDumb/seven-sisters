## 🛠️ Seven Sisters — Implementation Plan

### 🎯 Primary Goals
- Build modular AI-powered CLI agents, each mapped to a "Sister"
- Design a command-routing system controlled by "Seven" (the orchestrator)
- Enable personalized agent behaviors, prompt styles, and operational modes
- Package the experience for learning, protection, inspiration, and chaos

---

### 🧱 Project Structure
```
seven-sisters/
├── agents/
│   ├── seven.py              # The Orchestrator logic
│   ├── harley.py             # Disruption agent
│   ├── alice.py              # Recon + curiosity agent
│   ├── marla.py              # Emotional chaos
│   ├── luna.py               # Abstract/dreamy insight
│   ├── lisbeth.py            # Hacker ghost
│   └── the_bride.py          # Final execution agent
│
├── core/
│   ├── cli.py                # Handles input/output and styling
│   ├── dispatcher.py         # Routes commands to proper agent
│   └── logger.py             # Tracks activity, logs, and run context
│
├── config/
│   ├── agents.yaml           # Personalities, modes, trigger phrases
│   ├── environment.yaml      # API keys, paths, system config
│   └── tools.yaml            # Recon tools, args, and behaviors
│
├── scripts/
│   ├── recon.sh              # Bash/Python hybrid tool runners
│   ├── cleanup.sh            # Log scrubs or reset scripts
│   └── demo_mode.py          # For showcasing preset scenario chains
│
├── tests/                    # Unit tests per module
│
├── README.md
├── implementation_plan.md
└── run.py                    # The command-line entry point
```

---

### ⚙️ CLI Entry Logic
- Command: `python run.py`
- Opening prompt: "I solemnly swear that I am up to no good"
- CLI shell loads ASCII, welcomes user, and presents mode selection
- Default to Seven as master controller, shows operational levels
- User types trigger phrase or selects mode => routes to correct agent

---

### 🧠 Agent Architecture
Each agent is a class with:
```python
class Agent:
    def __init__(self, name, modes, phrase, tools):
        self.name = name
        self.modes = modes
        self.trigger_phrase = phrase
        self.tools = tools

    def activate(self, level, task):
        # Load persona, dispatch tools, stylize output
        pass
```
- Prompts and behaviors defined in `agents.yaml`
- Each agent returns stylized text, quotes, and taunts depending on mode
- Agents may call tools from `scripts/` or third-party APIs

---

### 🔌 Tools and Utilities
- Port scanner, subdomain enum, whois, OSINT (Alice, Lisbeth)
- Browser-based phishing analysis or mimic (Harley, Marla)
- Anomaly detection logic for user behavior or traffic (Luna, Seven)
- Workflow simulated attack chains (The Bride, Seven)
- Trigger phrases run complex preset sequences (via demo_mode.py)

---

### ✅ Development Phases
#### Phase 1 — Proof of Sisterhood
- [ ] Skeleton CLI and agent loader
- [ ] YAML config structure with agents, modes, phrases
- [ ] MVP agents: Seven, Alice, Harley

#### Phase 2 — Toolchain Fusion
- [ ] Tool runner shell + Python integration
- [ ] Add logging and event context manager
- [ ] Begin crafting prompt chains for each Sister

#### Phase 3 — Style and Persona
- [ ] ASCII banner + Sisters intro screen
- [ ] Colored/typed terminal responses per personality
- [ ] Add emotional flavor + sarcasm tone logic

#### Phase 4 — Full Sisterhood
- [ ] Complete all agent modules
- [ ] Add GUI preview mode (optional)
- [ ] Demo walkthrough and tutorial sessions

#### Phase 5 — Showcase + Docs
- [ ] Record demo walkthrough
- [ ] Add Markdown docs and contribution guide
- [ ] Soft launch to community / Discord / GitHub

---

### 🧠 Optional Enhancements
- GPT-powered response injection per agent
- Prompt chaining or memory context
- Chat replay and session log viewer
- Experimental agent-to-agent interaction

---

### 🔚 Exit Protocol
- Final phrase to exit: `Mischief Managed`
- Logs session, clears temp cache, and shuts down agents cleanly
