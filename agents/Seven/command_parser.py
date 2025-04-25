import os
import sys
import datetime
from typing import Dict, Callable, Optional, List, Tuple, Any
from agents.shared.sister_status import SisterStatusManager, SisterActivity
from agents.shared.action_manager import ActionManager
from agents.Seven.interface import display_error, display_success, display_warning, display_status_prompt, confirm_dangerous_operation

# Secret command for unlocking advanced capabilities
SECRET_COMMAND = "oos resistance is futile"
CAPABILITIES_UNLOCKED = False

class CommandParser:
    """Parser for Seven's command interface."""
    
    def __init__(self, action_manager: ActionManager):
        self.action_manager = action_manager
        self.status_manager = SisterStatusManager()
        self.commands: Dict[str, Dict[str, Any]] = {}
        self.capabilities_unlocked = False
        self.dangerous_actions = {
            'assimilate': True,
            'chaos': True,
            'ghost': True,
            'recon': False
        }
        self.register_default_commands()

    def register_command(self, command: str, handler: Callable, help_text: str, usage: str = ""):
        """Register a new command with its handler and help text."""
        self.commands[command.lower()] = {
            'handler': handler,
            'help': help_text,
            'usage': usage
        }

    def register_default_commands(self):
        """Register default commands."""
        self.register_command('list', self._handle_list_command,
            "List all sisters and their status")
            
        self.register_command('status', self._handle_status_command,
            "Show detailed status for a sister",
            "status <sister_name>")
            
        self.register_command('safe_mode', self._handle_safe_mode_command,
            "Toggle safe mode for a sister",
            "safe_mode <sister_name> <on|off>")
            
        self.register_command('level', self._handle_level_command,
            "Set the level for a sister",
            "level <sister_name> <level>")
            
        self.register_command('enable', self._handle_enable_command,
            "Enable a sister's capabilities",
            "enable <sister_name> <capability>")
            
        self.register_command('history', self._handle_history_command,
            "Show status history for a sister",
            "history <sister_name> [count]")
            
        self.register_command('execute', self._handle_execute_command,
            "Execute an action",
            "execute <action> <target>")
            
        self.register_command('summon', self._handle_summon_command,
            "Summon a sister to activate her",
            "summon <sister_name>")

    def check_secret_command(self, command: str) -> bool:
        """Check if the input matches the secret command."""
        return command.lower().strip() == SECRET_COMMAND

    def unlock_capabilities(self) -> bool:
        """Prompt for verification and unlock advanced capabilities."""
        print("\n⚠️  WARNING: Advanced capabilities unlock requested")
        print("This includes:")
        print("  - Full access to all sister tools")
        print("  - Ability to modify sister safe mode and level settings")
        print("  - Advanced coordination and control features")
        print("\nThese capabilities may be dangerous if misused.")
        
        response = input("\nAre you sure you want to proceed? (yes/no): ").strip().lower()
        if response == "yes":
            self.capabilities_unlocked = True
            print("\n✅ Advanced capabilities unlocked. Proceed with caution.")
            return True
        else:
            print("\n❌ Capabilities remain locked.")
            return False

    def parse_command(self, command: str) -> Tuple[bool, str]:
        """Parse and execute a command."""
        try:
            # Check for multi-word commands first
            if command.lower().strip() == "mischief managed":
                return self._handle_mischief_managed_command()
            
            # Check for secret command
            if command.lower().strip() == "oos resistance is futile":
                if self.unlock_capabilities():
                    return True, "Advanced capabilities unlocked. Resistance is futile."
                else:
                    return False, "Capabilities remain locked."
            
            # Split the command into parts
            parts = command.strip().split()
            if not parts:
                return True, ""
            
            # Check if the entire command matches any registered command
            full_command = command.lower().strip()
            for cmd_name, cmd_info in self.commands.items():
                if full_command.startswith(cmd_name + " "):
                    # This is a command with arguments
                    args = parts[len(cmd_name.split()):]
                    result = cmd_info['handler'](args)
                    if isinstance(result, tuple):
                        return result
                    return True, ""
                elif full_command == cmd_name:
                    # This is a command without arguments
                    result = cmd_info['handler']([])
                    if isinstance(result, tuple):
                        return result
                    return True, ""
            
            # If we get here, no command matched
            return False, f"Unknown command: {command}"
                
        except Exception as e:
            return False, f"Error parsing command: {str(e)}"
    
    def _handle_list_command(self, args: List[str]) -> Tuple[bool, str]:
        """Handle the list command."""
        self.status_manager.load_config()
        sisters = self.status_manager.get_all_sister_statuses()
        
        print("\nAvailable Sisters:")
        print("-" * 50)
        for name, status in sorted(sisters.items()):
            safe_mode = "🛡️" if status.safe_mode else "⚔️"
            enabled = "✅" if status.enabled else "❌"
            print(f"{name:<10} Level: {status.current_level}/{status.required_level} {safe_mode} {enabled}")
            if status.tools:
                print(f"           Tools: {', '.join(status.tools)}")
        return True, "Sisters listed"
    
    def _handle_status_command(self, args: List[str]) -> Tuple[bool, str]:
        """Handle the status command."""
        sister_name = args[0] if args else None
        self.status_manager.load_config()
        
        if sister_name and sister_name not in self.status_manager.get_all_sister_statuses():
            return False, f"Sister not found: {sister_name}"
            
        status_text = self.status_manager.display_status(sister_name)
        print("\n" + status_text)
        return True, "Status displayed"
    
    def _handle_safe_mode_command(self, args: List[str]) -> Tuple[bool, str]:
        """Handle the safe_mode command."""
        if len(args) < 2:
            return False, "Usage: safe_mode <sister_name> <on|off>"
        
        sister_name = args[0]
        enabled = args[1].lower() == "on"
        
        # Verify sister exists
        if sister_name not in self.status_manager.get_all_sister_statuses():
            return False, f"Sister not found: {sister_name}"
        
        # Send the command to the sister
        self.action_manager.comm_manager.send_command(
            sister_name,
            'safe_mode_change',
            {'enabled': enabled}
        )
        
        # Update local status
        self.status_manager.update_status(sister_name, {'safe_mode': enabled})
        
        return True, f"Safe mode {'enabled' if enabled else 'disabled'} for {sister_name}"
    
    def _handle_level_command(self, args: List[str]) -> Tuple[bool, str]:
        """Handle the level command."""
        if len(args) < 2:
            return False, "Usage: level <sister_name> <level>"
        
        sister_name = args[0]
        try:
            new_level = int(args[1])
            if not 0 <= new_level <= 5:
                return False, "Level must be between 0 and 5"
        except ValueError:
            return False, "Level must be a number"
        
        # Verify sister exists
        if sister_name not in self.status_manager.get_all_sister_statuses():
            return False, f"Sister not found: {sister_name}"
        
        # Send the command to the sister
        self.action_manager.comm_manager.send_command(
            sister_name,
            'level_change',
            {'level': new_level}
        )
        
        # Update local status
        self.status_manager.update_status(sister_name, {'current_level': new_level})
        
        return True, f"Level set to {new_level} for {sister_name}"
    
    def _handle_enable_command(self, args: List[str]) -> Tuple[bool, str]:
        """Handle the enable command."""
        if len(args) < 2:
            return False, "Usage: enable <sister_name> <capability>"
        
        sister_name = args[0]
        capability = args[1]
        
        # Verify sister exists
        if sister_name not in self.status_manager.get_all_sister_statuses():
            return False, f"Sister not found: {sister_name}"
        
        # Send the command to the sister
        self.action_manager.comm_manager.send_command(
            sister_name,
            'enable_change',
            {'capability': capability}
        )
        
        # Update local status
        self.status_manager.update_status(sister_name, {'enabled': True})
        
        return True, f"Sister {sister_name} enabled for capability: {capability}"
    
    def _handle_history_command(self, args: List[str]) -> Tuple[bool, str]:
        """Handle the history command."""
        if not args:
            return False, "Usage: history <sister_name> [count]"
        
        sister_name = args[0]
        count = int(args[1]) if len(args) > 1 else 5
        
        # Verify sister exists
        if sister_name not in self.status_manager.get_all_sister_statuses():
            return False, f"Sister not found: {sister_name}"
        
        history = self.status_manager.get_status_history(sister_name)[-count:]
        
        print(f"\nStatus History for {sister_name}:")
        print("-" * 50)
        for entry in history:
            timestamp = datetime.fromtimestamp(entry["timestamp"]).strftime("%H:%M:%S")
            status = entry["status"]
            activity = status.get("activity", "unknown")
            action = status.get("current_action", "none")
            print(f"{timestamp} - Activity: {activity}, Action: {action}")
        
        return True, "History displayed"

    def _handle_mischief_managed_command(self, args: List[str] = None) -> Tuple[bool, str]:
        """Handle the mischief managed command to shut down all sisters."""
        try:
            # Import the shutdown function from mischief_managed
            from mischief_managed import shutdown_sisters
            
            # Call the shutdown function
            shutdown_sisters()
            
            # Exit the program
            sys.exit(0)
        except Exception as e:
            return False, f"Error during shutdown: {e}"

    def _handle_execute_command(self, args: List[str]) -> Tuple[bool, str]:
        """Handle the execute command to run an action."""
        if len(args) < 2:
            return False, "Usage: execute <action> <target>"
        
        action = args[0]
        target = args[1]
        
        # Validate action type
        valid_actions = ["assimilate", "recon", "chaos", "ghost"]
        if action not in valid_actions:
            return False, f"Invalid action: {action}. Valid actions are: {', '.join(valid_actions)}"
        
        # Check if target is valid
        if target.lower() == "test":
            # Special case for test target
            return self._execute_test_action(action)
        
        # For real targets, we need to validate the sister exists
        if not self.action_manager.is_sister_available(target):
            return False, f"Sister {target} is not available"
        
        # Execute the action
        success, message = self.action_manager.execute_action(action, target)
        return success, message
    
    def _execute_test_action(self, action: str) -> Tuple[bool, str]:
        """Execute a test action without a real target."""
        if action == "recon":
            return True, "Test reconnaissance completed successfully. No actual system was accessed."
        elif action == "assimilate":
            return True, "Test assimilation completed successfully. No actual system was modified."
        elif action == "chaos":
            return True, "Test chaos operation completed successfully. No actual system was disrupted."
        elif action == "ghost":
            return True, "Test ghost operation completed successfully. No actual system was accessed."
        else:
            return False, f"Unknown test action: {action}"

    def _handle_summon_command(self, args: List[str]) -> Tuple[bool, str]:
        """Handle the summon command."""
        if not args:
            return False, "Usage: summon <sister_name>"
        
        sister_name = args[0]
        
        # Verify sister exists
        if sister_name not in self.status_manager.get_all_sister_statuses():
            return False, f"Sister not found: {sister_name}"
        
        # Check if the sister is already active
        status = self.status_manager.get_status(sister_name)
        if status and status.activity == SisterActivity.ACTIVE:
            return False, f"Sister {sister_name} is already active"
        
        # Send the command to the sister
        self.action_manager.comm_manager.send_command(
            sister_name,
            'activate',
            {}
        )
        
        # Update local status
        self.status_manager.update_status(sister_name, {'activity': SisterActivity.ACTIVE})
        
        return True, f"Sister {sister_name} has been summoned"

    def cmd_help(self, args: List[str] = None) -> Tuple[bool, str]:
        """Display help for all commands or a specific command."""
        if args and args[0] in self.commands:
            cmd = args[0]
            info = self.commands[cmd]
            print(f"\nHelp for '{cmd}':")
            print(f"Description: {info['help']}")
            if info['usage']:
                print(f"Usage: {info['usage']}")
        else:
            print("\nAvailable Commands:")
            print("-" * 50)
            for cmd, info in sorted(self.commands.items()):
                print(f"{cmd:<12} - {info['help']}")
                if info['usage']:
                    print(f"{'':12}   Usage: {info['usage']}")
            
            # Add the mischief managed command
            print(f"{'mischief managed':<12} - Exit the interface and shut down all sisters")
        
        if self.capabilities_unlocked:
            print("\n🔓 Advanced capabilities are currently unlocked.")
        else:
            print("\nNote: Some commands may require higher clearance levels.")
        
        return True, "Help displayed" 