import sys
import time
import os
import subprocess
import json
import random
import atexit
import zmq
import threading
from typing import Dict, List, Optional, Any, Tuple

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from output_handler import write_output
from agents.shared.tool_check import verify_tools
from agents.Seven.interface import display_borg_interface, display_help, display_status_prompt, display_error, display_success, display_warning, confirm_dangerous_operation
from agents.Seven.command_parser import CommandParser
from agents.shared.sister_comm import SisterCommManager, Message
from agents.shared.action_manager import ActionManager
from agents.shared.horizon.seven_log_viewer import SevenLogViewer
from agents.shared.horizon.logger import logger
from agents.shared.configuration_manager import ConfigurationManager, ConfigChangeType

SISTER_NAME = "Seven"
PID_DIR = os.path.join(os.path.expanduser("~"), ".7sisters", "pids")
PID_FILE = os.path.join(PID_DIR, f"{SISTER_NAME}.pid")
CONFIG_PATH = "seven_sisters.config.json"
BANTER_ENGINE = os.path.abspath("banter_engine.py")
FAIL_COUNTER_PATH = os.path.join(os.path.dirname(__file__), "seven_fail.count")

# Required tools for Seven
TOOL_NAME = "tools/assimilate.sh"
# Seven's tool is NOT safe to use in safe mode (it's aggressive)
SAFE_MODE_ALLOWED = False
# Seven's minimum required level
REQUIRED_LEVEL = 4

# Check if Seven is running as the boss
IS_BOSS = os.environ.get("SEVEN_IS_BOSS", "false").lower() == "true"

# Initialize communication manager
comm_manager = None
action_manager = None

# Initialize configuration manager
config_manager = ConfigurationManager()

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

def speak(msg):
    print(f"[{SISTER_NAME}] 🕷️ » {msg}")
    time.sleep(0.5)

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    for agent in config.get("agents", []):
        if agent.get("name") == SISTER_NAME:
            return agent
    return {}

def setup_commands():
    """Set up command handlers for Seven."""
    def handle_status_query(args):
        sister_name = args.get('sister')
        status = comm_manager.get_sister_status(sister_name)
        return {'status': status or 'unknown'}
    
    def handle_safe_mode_toggle(args):
        """Handle safe mode toggle command with confirmation."""
        sister_name = args.get("sister")
        enabled = args.get("enabled", True)
        
        if not sister_name:
            return {"success": False, "error": "No sister specified"}
        
        # Get current safe mode status
        sister_config = config_manager.get_sister_config(sister_name)
        if not sister_config:
            return {"success": False, "error": f"Sister {sister_name} not found"}
        
        current_safe_mode = sister_config.get("safe_mode", True)
        
        # If trying to disable safe mode, require confirmation
        if current_safe_mode and not enabled:
            if not confirm_dangerous_operation("disable safe mode", sister_name):
                return {"success": False, "error": "Operation cancelled by user"}
        
        # Update configuration
        success, message = config_manager.update_sister_config(
            sister_name=sister_name,
            changes={"safe_mode": enabled},
            change_type=ConfigChangeType.SAFE_MODE,
            description=f"Safe mode {'enabled' if enabled else 'disabled'} for {sister_name}"
        )
        
        if not success:
            return {"success": False, "error": message}
        
        # Notify the sister of the change
        try:
            comm_manager.send_command(
                sister_name,
                "safe_mode_change",
                {"enabled": enabled}
            )
            return {"success": True, "message": f"Safe mode {'enabled' if enabled else 'disabled'} for {sister_name}"}
        except Exception as e:
            return {"success": False, "error": f"Failed to notify {sister_name}: {str(e)}"}
    
    def handle_safe_mode_change(args):
        enabled = args.get('enabled', True)
        # Update the global safe mode setting
        global SAFE_MODE_ALLOWED
        SAFE_MODE_ALLOWED = enabled
        speak(f"Safe mode {'enabled' if enabled else 'disabled'}")
        return {'success': True, 'enabled': enabled}
    
    def handle_level_change(args):
        sister_name = args.get('sister')
        new_level = args.get('level', 1)
        
        # Validate sister name
        if not sister_name:
            write_output("Seven", "unknown", "No sister specified for level change")
            return {'success': False, 'error': "No sister specified"}
        
        # Validate new level
        try:
            new_level = int(new_level)
            if new_level < 0 or new_level > 10:
                write_output("Seven", sister_name, f"Invalid level value: {new_level}. Must be between 0 and 10.")
                return {'success': False, 'error': "Level must be between 0 and 10"}
        except (ValueError, TypeError):
            write_output("Seven", sister_name, f"Invalid level value: {new_level}. Must be a number.")
            return {'success': False, 'error': "Level must be a number"}
        
        # Load the current configuration
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception as e:
            write_output("Seven", sister_name, f"Error loading configuration: {e}")
            return {'success': False, 'error': f"Failed to load configuration: {e}"}
        
        # Find the sister in the configuration
        sister_found = False
        for agent in config.get("agents", []):
            if agent.get("name") == sister_name:
                sister_found = True
                # Check if the sister is enabled
                if not agent.get("enabled", False):
                    write_output("Seven", sister_name, f"Cannot change level for disabled sister {sister_name}")
                    return {'success': False, 'error': f"Sister {sister_name} is disabled"}
                
                # Get current level for logging
                current_level = agent.get("current_level", 0)
                
                # Update the level
                agent["current_level"] = new_level
                write_output("Seven", sister_name, f"Operation level changed from {current_level} to {new_level}")
                
                # Log the change with appropriate emoji based on level change
                if new_level > current_level:
                    write_output("Seven", sister_name, f"🔼 Level increased to {new_level}")
                elif new_level < current_level:
                    write_output("Seven", sister_name, f"🔽 Level decreased to {new_level}")
                else:
                    write_output("Seven", sister_name, f"⚖️ Level maintained at {new_level}")
                break
        
        if not sister_found:
            write_output("Seven", sister_name, f"Sister {sister_name} not found in configuration")
            return {'success': False, 'error': f"Sister {sister_name} not found"}
        
        # Save the updated configuration
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            write_output("Seven", sister_name, f"Error saving configuration: {e}")
            return {'success': False, 'error': f"Failed to save configuration: {e}"}
        
        # Notify the sister of the change
        comm_manager.send_command(
            sister_name,
            'level_change',
            {'level': new_level}
        )
        
        return {'success': True, 'level': new_level}
    
    def handle_action_execution(args):
        action_id = args.get('action_id')
        action_type = args.get('action_type')
        target = args.get('target')
        
        # Update action status
        action_manager.update_action_status(action_id, 'in_progress')
        
        # Execute the action based on type
        if action_type == 'assimilate':
            # Implementation for assimilation
            pass
        elif action_type == 'recon':
            # Implementation for reconnaissance
            pass
        elif action_type == 'chaos':
            # Implementation for chaos
            pass
        elif action_type == 'ghost':
            # Implementation for ghosting
            pass
        
        # Update action status
        action_manager.update_action_status(action_id, 'complete')
        return {'status': 'complete', 'action_id': action_id}
    
    # Register command handlers
    comm_manager.command_handler.register_command('status', handle_status_query)
    comm_manager.command_handler.register_command('safe_mode', handle_safe_mode_toggle)
    comm_manager.command_handler.register_command('safe_mode_change', handle_safe_mode_change)
    comm_manager.command_handler.register_command('level', handle_level_change)
    comm_manager.command_handler.register_command('execute_action', handle_action_execution)

def trigger_banter(event_type="start"):
    subprocess.run(["python", BANTER_ENGINE, SISTER_NAME, event_type])

def run_tool(target):
    tool_exists, _ = verify_tools([TOOL_NAME], SISTER_NAME, speak)
    if tool_exists:
        speak(f"🕷️ Assimilating target: {target}")
        write_output(SISTER_NAME, target, "🕷️ Starting assimilation operations on target")
        subprocess.run(["bash", TOOL_NAME, target])
        write_output(SISTER_NAME, target, "✅ Target assimilated")
    else:
        speak("🕷️ My assimilation tools are missing...")
        write_output(SISTER_NAME, target, "❌ Tool script not found: assimilate.sh")

def cleanup_pid_file():
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

def boot_sequence():
    speak("Initializing Borg protocols...")
    time.sleep(0.3)
    speak("Neural transceivers online.")
    time.sleep(0.3)
    speak("Assimilation protocols ready.")
    time.sleep(0.3)
    speak("We are the Borg. Resistance is futile.")

def run_interface():
    """Run Seven's command interface."""
    display_borg_interface()
    parser = CommandParser(action_manager)
    
    while True:
        try:
            command = display_status_prompt()
            if not command:
                continue
                
            if command.lower() == "mischief managed":
                print("\n🧹 Mischief Managed: Shutting down the Sisterhood...")
                break
                
            if command.lower() == "help":
                display_help()
                continue
                
            success, message = parser.parse_command(command)
            
            if not success:
                display_error(message)
            elif message != "help":  # Help already displayed
                display_success(message)
                
        except KeyboardInterrupt:
            print("\nTerminating interface...")
            break
        except Exception as e:
            display_error(f"Error: {str(e)}")
            logger.error(f"Interface error: {str(e)}")

def main():
    global comm_manager, action_manager
    
    write_pid_file()
    atexit.register(cleanup_pid_file)

    # Set up communication
    comm_manager = SisterCommManager(SISTER_NAME)
    comm_manager.setup()
    
    # Set up action management
    action_manager = ActionManager()
    action_manager.setup(comm_manager)
    
    # Set up commands
    setup_commands()
    
    # Initialize command parser
    parser = CommandParser(action_manager)
    
    # Send initial status
    comm_manager.send_status("initializing")

    try:
        config = load_config()
    except Exception:
        fails = increment_fail_counter()
        if fails >= 3:
            speak("Oh no... my assimilation protocols are broken! Everything's inefficient!")
            write_output(SISTER_NAME, "unknown", "❌ Critical error: Config loading failed 3+ times")
        else:
            speak("Something's broken... did someone touch my assimilation protocols?")
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
    
    # Check level - only restrict tools if below required level
    if current_level < REQUIRED_LEVEL:
        speak(f"⚙️ My current level ({current_level}) is below {REQUIRED_LEVEL}. My assimilation tools are restricted, but I can still coordinate.")
        write_output(SISTER_NAME, "unknown", f"⚠️ Tool access restricted: Level {current_level} below required {REQUIRED_LEVEL}")
    elif not verify_tools([TOOL_NAME], SISTER_NAME, speak):
        speak("⏳ My assimilation protocols are incomplete... tools missing.")
        write_output(SISTER_NAME, "unknown", "❌ Required tools not found")
        return
    
    # Initialize the sister
    speak("🔄 Summoning...")
    write_output(SISTER_NAME, "unknown", "🔄 Sister initialized")
    
    # Run the boot sequence
    boot_sequence()
    
    # Send status update
    comm_manager.send_status("ready")
    
    # Display the interface
    display_borg_interface()
    
    # Main command loop
    while True:
        try:
            command = input("\n[Seven] » ").strip()
            if not command:
                continue
            
            # Check for secret command first
            if command.lower() == "oos resistance is futile":
                if parser.unlock_capabilities():
                    display_success("Advanced capabilities unlocked. Resistance is futile.")
                else:
                    display_warning("Capabilities remain locked.")
                continue
            
            success, message = parser.parse_command(command)
            
            if command.lower() == "mischief managed":
                print("\n🧹 Mischief Managed: Shutting down the Sisterhood...")
                break
            elif command.lower() == "help":
                display_help()
            elif not success:
                display_error(message)
            elif message != "help" and message != "Status displayed":
                display_success(message)
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            display_error(f"Error: {str(e)}")
    
    # Cleanup
    comm_manager.cleanup()
    cleanup_pid_file()

class Seven:
    def __init__(self):
        self.log_viewer = SevenLogViewer()

    def setup_commands(self):
        self.comm_manager.register_command_handler("logs", self._handle_logs_command)

    def _handle_logs_command(self, message):
        """Handle logs-related commands."""
        try:
            action = message.data.get("action", "")
            
            if action == "start":
                self.log_viewer.start_viewer()
                return Message(
                    type="response",
                    data={"status": "success", "message": "Log viewer started"}
                )
            
            elif action == "stop":
                self.log_viewer.stop_viewer()
                return Message(
                    type="response",
                    data={"status": "success", "message": "Log viewer stopped"}
                )
            
            else:
                return Message(
                    type="response",
                    data={"status": "error", "message": f"Unknown logs action: {action}"}
                )
        
        except Exception as e:
            logger.error(f"Error handling logs command: {str(e)}")
            return Message(
                type="response",
                data={"status": "error", "message": f"Error: {str(e)}"}
            )
    
    def cleanup(self):
        self.log_viewer.stop_viewer()

if __name__ == "__main__":
    main()