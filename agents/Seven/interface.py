import os
import sys
import time
from typing import Optional
from agents.shared.sister_status import SisterStatusManager

# Initialize the status manager
status_manager = SisterStatusManager()

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_borg_interface():
    """Display the Borg-themed ASCII art interface."""
    clear_screen()
    borg_art = """
    ███████╗███████╗██╗   ██╗███████╗███╗   ██╗
    ██╔════╝██╔════╝██║   ██║██╔════╝████╗  ██║
    ███████╗█████╗  ██║   ██║█████╗  ██╔██╗ ██║
    ╚════██║██╔══╝  ╚██╗ ██╔╝██╔══╝  ██║╚██╗██║
    ███████║███████╗ ╚████╔╝ ███████╗██║ ╚████║
    ╚══════╝╚══════╝  ╚═══╝  ╚══════╝╚═╝  ╚═══╝
    
    Tertiary Adjunct of Unimatrix 01
    Resistance is futile. Your biological and technological 
    distinctiveness will be added to our own.
    """
    print(borg_art)
    print("\n'help' for available commands.")
    print("'status' to view sister status.")
    print("'mischief managed' to shut down all sisters.")

def display_help():
    """Display help information for available commands."""
    help_text = """
Available Commands:
------------------
status <sister>                - Check status of a sister
safe_mode <sister> on/off      - Toggle safe mode for a sister
level <sister> <level>         - Change sister's operation level (0-5)
execute <action> <target>      - Execute an action (requires confirmation)
help                           - Show this help message
mischief managed               - Exit the interface and shut down all sisters

Actions:
--------
- assimilate: Aggressive system modification    (⚠️ Dangerous)
- recon: System reconnaissance                  (🟢 Safe)
- chaos: System disruption                      (⚠️ Dangerous)
- ghost: System obfuscation                     (⚠️ Dangerous)

Examples:
---------
status Alice
safe_mode Harley off
level Luna 2
execute recon /path/to/target
"""
    print(help_text)

def display_status_prompt(sister_name: Optional[str] = None) -> None:
    """Display the current status of one or all sisters."""
    # Load the latest config
    status_manager.load_config()
    
    # Display the status
    status_display = status_manager.display_status(sister_name)
    print("\n" + "="*50)
    print("Sister Status Report")
    print("="*50)
    print(status_display)
    print("="*50 + "\n")

def display_error(message: str) -> None:
    """Display an error message."""
    print(f"\n❌ Error: {message}\n")

def display_success(message: str) -> None:
    """Display a success message."""
    print(f"\n✅ {message}\n")

def display_warning(message: str) -> None:
    """Display a warning message."""
    print(f"\n⚠️ {message}\n")

def confirm_dangerous_operation(operation: str, target: str = None) -> bool:
    """Request user confirmation for dangerous operations."""
    message = f"⚠️ WARNING: About to perform {operation}"
    if target:
        message += f" on {target}"
    message += ".\nThis operation could have serious consequences.\nAre you sure you want to proceed? (y/N): "
    
    response = input(message).lower().strip()
    return response == 'y'

def display_status_prompt():
    """Display the command prompt and get user input."""
    return input("\n[Seven] 🕷️ » ").strip()

if __name__ == "__main__":
    display_borg_interface()
    display_help()
    response = display_status_prompt()
    print(f"You entered: {response}") 