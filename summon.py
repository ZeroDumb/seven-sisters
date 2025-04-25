import os
import json
import subprocess
import time
import random
import zmq
import threading
import sys
from agents.shared.tool_check import scan_all_tools

# Add the project root to Python path to ensure imports work
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Print diagnostic information
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")

# Try to import the dependency checker, with a fallback
try:
    from agents.shared.dependency_check import check_dependencies
    DEPENDENCY_CHECKER_AVAILABLE = True
except ImportError as e:
    DEPENDENCY_CHECKER_AVAILABLE = False
    print(f"⚠️ Dependency checker not available: {e}")
    print("⚠️ Continuing without dependency checking.")

SESSION_CONFIG_PATH = os.path.expanduser("~/.7sisters/session_config.json")
with open(SESSION_CONFIG_PATH, "r") as f:
    session = json.load(f)

safe_mode = session.get("safe_mode", True)
op_level = session.get("ops_level", 1)

CONFIG_PATH = "seven_sisters.config.json"

# IPC Configuration
IPC_PORT = 5555
IPC_ADDRESS = f"tcp://127.0.0.1:{IPC_PORT}"

# Sister status tracking
sister_status = {}
sister_status_lock = threading.Lock()

def dramatic_pause(msg, delay=0.4):
    print(msg)
    time.sleep(delay)

def speak(name, msg):
    print(f"[{name}] » {msg}")
    time.sleep(0.4)

def setup_ipc():
    """Set up the IPC system for sister communication."""
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(IPC_ADDRESS)
    return socket

def find_bash():
    """Find bash executable on the system."""
    # Common Git Bash locations on Windows
    common_paths = [
        "C:\\Program Files\\Git\\bin\\bash.exe",
        "C:\\Program Files (x86)\\Git\\bin\\bash.exe",
        os.path.expanduser("~\\AppData\\Local\\Programs\\Git\\bin\\bash.exe"),
        "C:\\msys64\\usr\\bin\\bash.exe",
        "C:\\cygwin64\\bin\\bash.exe"
    ]
    
    # Check common paths first
    for path in common_paths:
        if os.path.exists(path):
            return path
            
    # Try to find bash in PATH
    if os.name == 'nt':  # Windows
        try:
            result = subprocess.run(['where', 'bash'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass
    else:  # Unix-like
        try:
            result = subprocess.run(['which', 'bash'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
            
    return None

def get_bash_path_from_user():
    """Prompt user for bash path."""
    print("\n⚠️  Bash not found in common locations.")
    print("Please provide the path to your bash executable.")
    print("Common locations:")
    print("  - Git Bash: C:\\Program Files\\Git\\bin\\bash.exe")
    print("  - MSYS2: C:\\msys64\\usr\\bin\\bash.exe")
    print("  - Cygwin: C:\\cygwin64\\bin\\bash.exe")
    print("  - Custom installation: [your path]")
    
    while True:
        path = input("\nEnter bash path (or press Enter to use Windows cmd): ").strip()
        if not path:  # User chose to use cmd
            return None
        if os.path.exists(path):
            return path
        print("❌ Path not found. Please try again.")

def launch_sister(name, script_path, env):
    """Launch a sister in a separate terminal window."""
    if os.name == 'nt':  # Windows
        # Try to find bash
        bash_path = find_bash()
        
        if not bash_path:
            # Ask user for bash path or confirmation to use cmd
            bash_path = get_bash_path_from_user()
            
            if not bash_path:
                print("⚠️  Proceeding with Windows cmd...")
                cmd = f'start cmd /k "python {script_path}"'
            else:
                # Convert Windows path to Unix-style for bash
                unix_script_path = script_path.replace('\\', '/')
                cmd = f'start "" "{bash_path}" --login -i -c "python {unix_script_path}; exec bash"'
        else:
            # Use found bash
            unix_script_path = script_path.replace('\\', '/')
            cmd = f'start "" "{bash_path}" --login -i -c "python {unix_script_path}; exec bash"'
    else:  # Unix-like
        # Use 'gnome-terminal', 'xterm', or similar
        cmd = f'gnome-terminal -- bash -c "python {script_path}; exec bash"'
    
    subprocess.Popen(cmd, shell=True, env=env)
    # Initialize sister status as "starting"
    with sister_status_lock:
        sister_status[name] = "starting"

def listen_for_sister_status():
    """Listen for status updates from sisters."""
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(IPC_ADDRESS)
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    
    while True:
        try:
            message = socket.recv_string()
            data = json.loads(message)
            if data.get("type") == "status_update":
                sister_name = data.get("sister")
                status = data.get("status")
                with sister_status_lock:
                    sister_status[sister_name] = status
                    print(f"Status update: {sister_name} is now {status}")
        except Exception as e:
            print(f"Error in status listener: {e}")
            time.sleep(1)

def summon_the_haunt():
    """Summon all the sisters based on configuration."""
    # Check for configuration file
    if not os.path.exists(CONFIG_PATH):
        print("❌ Configuration file not found. Please create seven_sisters.config.json")
        return
    
    # Check dependencies if available
    if DEPENDENCY_CHECKER_AVAILABLE:
        if not check_dependencies():
            print("❌ Missing dependencies. Please install required dependencies.")
            sys.exit(1)
    else:
        print("⚠️ Dependency checking skipped. Some features may not work correctly.")
    
    # Scan for tools and exit if user chooses not to proceed
    if not scan_all_tools():
        print("❌ Operation cancelled due to missing tools.")
        sys.exit(1)
    
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    agents = config.get("agents", [])
    if not agents:
        print("🕳️ No agents defined. The void stares back.")
        return

    # Get the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Set up IPC
    ipc_socket = setup_ipc()
    
    # Start the status listener thread
    status_thread = threading.Thread(target=listen_for_sister_status, daemon=True)
    status_thread.start()
    
    # First, launch Seven regardless of safe mode or level
    seven_agent = None
    for agent in agents:
        if agent["name"] == "Seven":
            seven_agent = agent
            break
    
    if seven_agent:
        name = seven_agent["name"]
        script_path = os.path.join("agents", name, "init.py")
        if os.path.exists(script_path):
            speak(name, "👻 Summoning the Queen...")
            print(f"DEBUG: Attempting to launch {script_path}")
            env = os.environ.copy()
            env["PYTHONPATH"] = project_root
            env["SEVEN_IS_BOSS"] = "true"  # Special flag for Seven
            launch_sister(name, script_path, env)
            time.sleep(1)  # Give Seven a head start
    
    # Then launch the other sisters
    for agent in agents:
        name = agent["name"]
        
        # Skip Seven as she's already launched
        if name == "Seven":
            continue
            
        enabled = agent.get("enabled", True)
        modes = agent.get("modes", [])

        # Block unsafe sisters in safe mode
        if safe_mode and 5 in modes:
            speak(name, "🛑 Blocked by safe mode. Harley will be upset.")
            continue

        # Block overly spicy agents based on op_level
        if any(m > op_level for m in modes):
            speak(name, f"⚙️ {name} exceeds operation level {op_level}. Standing down.")
            continue

        if not enabled:
            playful_excuses = [
                f"{name} is still brushing her hair. Come back later.",
                f"{name}? Oh no, she's in 'Do Not Disturb' mode.",
                f"{name} sent an auto-reply: 'Not today, human.'",
                f"{name} ghosted us. Classic."
            ]
            speak(name, random.choice(playful_excuses))
            continue

        script_path = os.path.join("agents", name, "init.py")
        if os.path.exists(script_path):
            speak(name, "👻 Summoning...")
            print(f"DEBUG: Attempting to launch {script_path}")
            env = os.environ.copy()
            env["PYTHONPATH"] = project_root
            launch_sister(name, script_path, env)
            time.sleep(0.5)
        else:
            vanished_lines = [
                f"{name}? She rage-quit the load process.",
                f"{name} ghosted the boot sequence. Classic.",
                f"{name} was here a second ago... probably in the vents.",
                f"{name} refuses to perform without glitter and applause.",
                f"{name} is in timeout after what happened *last time.*",
                f"{name} just whispered 'nope' and walked into the firewall.",
                f"{name} left a note: 'Gone to find better config files.'",
                f"{name}? She tried to launch... then spontaneously combusted."
            ]
            speak(name, f"⚠️ {random.choice(vanished_lines)}")
    
    # Wait for all sisters to initialize
    print("\nWaiting for sisters to initialize...")
    time.sleep(2)
    
    # Check sister status
    with sister_status_lock:
        for sister, status in sister_status.items():
            print(f"{sister}: {status}")


if __name__ == "__main__":
    dramatic_pause("🔮 Casting startup spell: 'I solemnly swear that I am up to no good'")
    
    summon_the_haunt()
