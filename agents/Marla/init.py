import sys
import time
import os
import subprocess
import json
import random
import atexit

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from output_handler import write_output
from agents.shared.tool_check import verify_tools
from agents.shared.sister_comm import SisterCommManager, Message

SISTER_NAME = "Marla"
PID_DIR = os.path.join(os.path.expanduser("~"), ".7sisters", "pids")
PID_FILE = os.path.join(PID_DIR, f"{SISTER_NAME}.pid")
CONFIG_PATH = "seven_sisters.config.json"
BANTER_ENGINE = os.path.abspath("banter_engine.py")
FAIL_COUNTER_PATH = os.path.join(os.path.dirname(__file__), "marla_fail.count")

# Required tools for Marla
TOOL_NAME = "tools/chaos.sh"
# Marla's tool is safe to use in safe mode
SAFE_MODE_ALLOWED = True
# Marla's minimum required level
REQUIRED_LEVEL = 2

# Initialize communication manager
comm_manager = None

def increment_fail_counter():
    count = 0
    if os.path.exists(FAIL_COUNTER_PATH):
        with open(FAIL_COUNTER_PATH, "r") as f:
            count = int(f.read().strip())
    count += 1
    with open(FAIL_COUNTER_PATH, "w") as f:
        f.write(str(count))
    return count

def write_pid_file():
    os.makedirs(PID_DIR, exist_ok=True)
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

def speak(msg, style="normal"):
    """Enhanced speak function with different styles for Marla's character"""
    if style == "command":
        print(f"[{SISTER_NAME}] 🧹 » {msg}")
        time.sleep(0.3)
    elif style == "thought":
        print(f"[{SISTER_NAME}] 💭 » {msg}")
        time.sleep(0.2)
    else:
        print(f"[{SISTER_NAME}] 🧹 » {msg}")
        time.sleep(0.5)

def handle_seven_command(command_type, args):
    """Handle commands received from Seven with character-rich responses"""
    if command_type == "clean":
        speak("The Queen requests cleaning...", "command")
        time.sleep(0.3)
        speak("Time to make things sparkle", "thought")
        time.sleep(0.3)
        target = args.get('target', 'unknown')
        speak(f"Preparing to clean: {target}", "command")
        run_tool(target)
        return {'success': True, 'target': target}
    elif command_type == "status":
        speak("The Queen checks my cleaning status...", "command")
        time.sleep(0.3)
        speak("All cleaning protocols engaged, ready to sparkle", "thought")
        return {'status': 'ready'}
    else:
        speak("An unusual cleaning request from the Queen...", "thought")
        return {'status': 'unknown_command'}

def setup_commands(comm_manager):
    """Set up command handlers for Marla."""
    def handle_status_query(args):
        return {'status': 'operational'}
    
    def handle_chaos_command(args):
        target = args.get('target', '')
        return {'success': True, 'target': target}
    
    def handle_safe_mode_change(args):
        """Handle safe mode change command."""
        global SAFE_MODE_ALLOWED
        enabled = args.get("enabled", True)
        SAFE_MODE_ALLOWED = enabled
        speak(f"Safe mode {'enabled' if enabled else 'disabled'}")
        return {"success": True, "enabled": enabled}
    
    def handle_level_change(args):
        new_level = args.get('level', 2)
        # Load the current configuration
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            write_output(SISTER_NAME, "unknown", f"Error loading configuration: {e}")
            return {'success': False, 'error': f"Failed to load configuration: {e}"}
        
        # Update the level in configuration
        for agent in config.get("agents", []):
            if agent.get("name") == SISTER_NAME:
                current_level = agent.get("current_level", 2)
                agent["current_level"] = new_level
                
                # Log the change with appropriate emoji based on level change
                if new_level > current_level:
                    speak(f"🔼 My chaos level has increased to {new_level}!", "command")
                elif new_level < current_level:
                    speak(f"🔽 My chaos level has decreased to {new_level}...", "command")
                else:
                    speak(f"⚖️ My chaos level remains at {new_level}", "command")
                break
        
        # Save the updated configuration
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            write_output(SISTER_NAME, "unknown", f"Error saving configuration: {e}")
            return {'success': False, 'error': f"Failed to save configuration: {e}"}
        
        return {'success': True, 'level': new_level}
    
    def handle_activate_command(args):
        """Handle activate command from Seven."""
        speak("🧠 The Queen has summoned me! Time to assimilate...")
        write_output(SISTER_NAME, "unknown", "🧠 Sister activated by Seven")
        return {"success": True, "message": "Activated"}
    
    # Register command handlers
    comm_manager.command_handler.register_command('status', handle_status_query)
    comm_manager.command_handler.register_command('chaos', handle_chaos_command)
    comm_manager.command_handler.register_command('safe_mode_change', handle_safe_mode_change)
    comm_manager.command_handler.register_command('level_change', handle_level_change)
    comm_manager.command_handler.register_command('activate', handle_activate_command)

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    for agent in config.get("agents", []):
        if agent.get("name") == SISTER_NAME:
            return agent
    return {}

def trigger_banter(event_type="start"):
    subprocess.run(["python", BANTER_ENGINE, SISTER_NAME, event_type])

def run_tool(target):
    tool_exists, _ = verify_tools([TOOL_NAME], SISTER_NAME, speak)
    if tool_exists:
        speak(f"🧹 Beginning cleaning of: {target}", "command")
        write_output(SISTER_NAME, target, "🧹 Initiating cleaning operations")
        speak("Time to make it sparkle...", "thought")
        subprocess.run(["bash", TOOL_NAME, target])
        write_output(SISTER_NAME, target, "✅ Cleaning complete")
        speak("Everything's so clean and shiny...", "thought")
    else:
        speak("🧹 My cleaning tools are missing...", "command")
        write_output(SISTER_NAME, target, "❌ Tool script not found: chaos.sh")
        speak("How can I clean without my tools...", "thought")

def cleanup_pid_file():
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

def boot_sequence():
    speak("Initializing cleaning protocols...", "command")
    time.sleep(0.3)
    speak("Sparkle systems online.", "thought")
    time.sleep(0.3)
    speak("Shine matrix ready.", "thought")
    time.sleep(0.3)
    speak("The cleaning flows freely...", "command")
    time.sleep(0.3)
    speak("Ready to clean for the Queen.", "command")

def main():
    global comm_manager
    
    write_pid_file()
    atexit.register(cleanup_pid_file)

    # Set up communication
    comm_manager = SisterCommManager(SISTER_NAME)
    comm_manager.setup()
    setup_commands(comm_manager)
    
    # Send initial status
    comm_manager.send_status("initializing")

    try:
        config = load_config()
    except Exception:
        fails = increment_fail_counter()
        if fails >= 3:
            speak("My assimilation protocols are broken... I can't think straight!")
            write_output(SISTER_NAME, "unknown", "❌ Critical error: Config loading failed 3+ times")
        else:
            speak("Something's wrong with my neural pathways...")
            write_output(SISTER_NAME, "unknown", "⚠️ Config loading failed")
        sys.exit(1)
    if not config:
        speak("I don't even know who I am in this config... identity crisis!")
        write_output(SISTER_NAME, "unknown", "❌ Agent not found in config")
        return
        
    # Check safe mode and current level
    safe_mode = config.get("safe_mode", True)
    current_level = config.get("current_level", 0)
    
    # Check if the sister is enabled
    if not config.get("enabled", False):
        speak("I'm not in the mood for assimilation today... maybe later.")
        write_output(SISTER_NAME, "unknown", "🛑 Operation blocked: Sister disabled")
        return
    
    # Check safe mode - only block if safe mode is on and the tool is not safe mode allowed
    if safe_mode and not SAFE_MODE_ALLOWED:
        speak("🛑 Safe mode is on. No assimilation today.")
        write_output(SISTER_NAME, "unknown", "🛑 Operation blocked: Safe mode enabled and tool not safe mode allowed")
        return
    
    # Check level - allow if current level is greater than or equal to required level
    if current_level < REQUIRED_LEVEL:
        speak(f"⚙️ Too spicy for my current level ({current_level}). I need level {REQUIRED_LEVEL} or higher.")
        write_output(SISTER_NAME, "unknown", f"⚙️ Operation blocked: Level {current_level} below required {REQUIRED_LEVEL}")
        return
    
    # ✅ Tool verification
    if not verify_tools([TOOL_NAME], SISTER_NAME, speak):
        speak("⏳ My assimilation protocols are incomplete... tools missing.")
        write_output(SISTER_NAME, "unknown", "❌ Required tools not found")
        return
    
    # Initialize the sister
    speak("🧠 Summoning...")
    write_output(SISTER_NAME, "unknown", "🧠 Sister initialized")
    
    # Run the boot sequence
    boot_sequence()
    
    # Send status update
    comm_manager.send_status("ready")
    
    # Display the interface
    display_sister_interface()
    
    # Main command loop
    while True:
        try:
            # Wait for commands from Seven
            time.sleep(0.1)  # Small delay to prevent CPU hogging
            
            # Check for termination signal
            if comm_manager.termination_signal_received:
                speak("Time to power down...")
                break
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            speak(f"Oops! Something went wrong: {str(e)}")
            time.sleep(1)  # Prevent rapid error messages
    
    # Cleanup
    comm_manager.cleanup()
    cleanup_pid_file()

def display_sister_interface():
    """Display the sister's interface."""
    print(f"\n{'='*50}")
    print(f"🧠 {SISTER_NAME} is ready for commands from Seven")
    print(f"{'='*50}")
    print("Waiting for commands...")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    main()