import os
import sys
import json
import subprocess
import time

# Add the project root to Python path to ensure imports work
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Print diagnostic information
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")

# Try to import the dependency checker
try:
    from agents.shared.dependency_check import check_dependencies
    DEPENDENCY_CHECKER_AVAILABLE = True
except ImportError as e:
    DEPENDENCY_CHECKER_AVAILABLE = False
    print(f"⚠️ Dependency checker not available: {e}")
    print("⚠️ Continuing without dependency checking.")

SESSION_CONFIG = os.path.join(os.path.expanduser("~"), ".7sisters", "session_config.json")
CONFIG_DIR = os.path.dirname(SESSION_CONFIG)
SUMMON_SCRIPT = "summon.py"
CONFIG_PATH = "seven_sisters.config.json"

ASCII_LOGO = r"""
███████╗    ███████╗██╗███████╗████████╗███████╗██████╗ ███████╗
╚════██║    ██╔════╝██║██╔════╝╚══██╔══╝██╔════╝██╔══██╗██╔════╝
     ██║ █╗ ███████╗██║███████╗   ██║   █████╗  ██████╔╝███████╗ 
     ██║ ╚╝ ╚════██║██║╚════██║   ██║   ██╔══╝  ██╔══██╗╚════██║ 
     ██║    ███████║██║███████║   ██║   ███████╗██║  ██║███████║     
     ╚═╝    ╚══════╝╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚══════╝ TM
 ┌──────────────────────────────────────────────────────────────┐
 │ Seven Sisters :: Operational Mayhem Framework v0.7x          │
 │ Agent-based cyber-recon. Deployable chaos. Terminal lore.    │
 │ Built by one human. Maintained by seven AI maniacs.          │
 └──────────────────────────────────────────────────────────────┘
"""

def intro():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(ASCII_LOGO)
    print("\033[1;31mWARNING: This system is for educational purposes only.\033[0m")
    print("\033[1;31mYou are responsible for your own actions. You must use your brain.\033[0m")
    print("\033[1;31mCreators are not liable in any way. and this is provided as is.\033[0m") 
    print("\033[1;31mUse responsibly.\033[0m")
    print("\nWelcome to the Seven Sisters system.")
    print("Summon at your own risk.\n")
    time.sleep(1)

    phrase = input("Type the sacred phrase to begin: ").strip()
    if phrase.lower() != "i solemnly swear that i am up to no good":
        print("\n[Seven] » Unauthorized incantation. Self-destruct countdown initiated.")
        time.sleep(0.75)
        print("Just kidding.") 
        time.sleep(0.09)
        print("Maybe")
        sys.exit(1)

def write_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

def get_user_settings():
    print("\n[Seven] » Initializing session setup wizard...")
    
    safe_mode = input("[Seven] » Enable Safe Mode? (Y/n): ").strip().lower()
    safe_mode = (safe_mode != 'n')

    while True:
        try:
            level = int(input("[Seven] » Select operational level (0 - Ghost, 5 - Terminal): "))
            if 0 <= level <= 5:
                break
            else:
                print("[Seven] » Invalid level. Try again.")
        except ValueError:
            print("[Seven] » Numbers only, please.")

    target = input("[Seven] » Input primary target (domain, IP, or project name): ").strip()

    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(SESSION_CONFIG, "w") as f:
        json.dump({
            "safe_mode": safe_mode,
            "ops_level": level,
            "target": target
        }, f, indent=2)

    print("\n[Seven] » Session configured. Initializing the Sisterhood...")
    time.sleep(1)
    
    # Load and update the main config file
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
            
        # Inject session config into agents
        for agent in config.get("agents", []):
            agent["safe_mode"] = safe_mode
            agent["current_level"] = level
            agent["target"] = target
            
        # Write the updated config
        write_config(config)
        
        print(f"\n[Seven] » Session saved with level {level}, target '{target}', safe_mode: {safe_mode}")
    except Exception as e:
        print(f"\n[Seven] » Failed to update agent configurations: {e}")

def launch_sisters():
    """Launch the sisters with dependency checking."""
    # Check dependencies first
    if DEPENDENCY_CHECKER_AVAILABLE:
        print("\n[System] » Checking dependencies...")
        if not check_dependencies():
            print("[System] » Critical dependencies missing. Cannot proceed.")
            sys.exit(1)
        print("[System] » All dependencies verified.")
    
    try:
        subprocess.run(["python", SUMMON_SCRIPT])
    except Exception as e:
        print(f"[System] » Failed to summon the haunt: {e}")

if __name__ == "__main__":
    intro()
    get_user_settings()
    launch_sisters()
