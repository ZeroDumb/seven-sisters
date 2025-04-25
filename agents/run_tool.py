import os
import subprocess
import sys
import platform
import json

# Determine bash path based on platform
if platform.system() == "Windows":
    # Try common Git Bash locations on Windows
    possible_paths = [
        "C:\\Program Files\\Git\\bin\\bash.exe",
        "C:\\Program Files (x86)\\Git\\bin\\bash.exe",
        os.path.expanduser("~\\AppData\\Local\\Programs\\Git\\bin\\bash.exe")
    ]
    bash_path = None
    for path in possible_paths:
        if os.path.exists(path):
            bash_path = path
            break
    if not bash_path:
        print("Error: Could not find Git Bash. Please install Git for Windows.")
        sys.exit(1)
else:
    bash_path = "/bin/bash"  # macOS/Linux default

# Define tool mapping
AGENT_TOOL_MAP = {
    "Harley": "boom.sh",
    "Alice": "alice_recon.sh",
    "Lisbeth": "ghost.sh",
    "Luna": "starlight.sh",
    "Marla": "chaos.sh",
    "Seven": "assimilate.sh",
    "Bride": "vengeance.sh"
}

def run_agent_tool(agent, target=None):
    if agent not in AGENT_TOOL_MAP:
        print(f"\n[{agent}] » Uh-oh! I don't even know that sister. Who dat?")
        return

    # Load config and get agent information
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "seven_sisters.config.json")
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as e:
        print(f"\n[{agent}] » Failed to load config: {e}")
        return

    agent_config = next((a for a in config["agents"] if a["name"] == agent), None)
    if not agent_config:
        print(f"\n[{agent}] » No config found. I feel... lost.")
        return

    # Use target from config if not provided
    if target is None:
        target = agent_config.get("target", "https://example.com")

    tool_name = AGENT_TOOL_MAP[agent]
    tool_path = os.path.join(os.path.dirname(__file__), "tools", tool_name)

    if not os.path.isfile(tool_path):
        print(f"\n[{agent}] » Uh-oh! My tool is missing! Where'd it go?")
        return

    try:
        subprocess.run([bash_path, tool_path, target], check=True)
    except FileNotFoundError:
        print(f"\n[{agent}] » Uh-oh! Couldn't find Bash at: {bash_path}")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"\n[{agent}] » Tool failed with exit code {e.returncode}!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_tool.py [Agent] [TargetURL]")
        sys.exit(1)

    agent = sys.argv[1]
    target = sys.argv[2] if len(sys.argv) > 2 else None
    run_agent_tool(agent, target)
