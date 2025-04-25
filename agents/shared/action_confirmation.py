import os
import sys
import time
import json
from typing import Dict, List, Optional, Any, Tuple

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from output_handler import write_output

class ActionConfirmation:
    """
    A class to handle action confirmation for sister operations.
    Provides detailed summaries of planned actions, sister assignments,
    and requires explicit user approval before proceeding.
    """
    
    def __init__(self, config_path: str = "seven_sisters.config.json"):
        """
        Initialize the ActionConfirmation system.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.sister_emojis = {
            "Alice": "🐇",
            "Bride": "🔮",
            "Harley": "🎭",
            "Lisbeth": "👻",
            "Luna": "🌟",
            "Marla": "🧹",
            "Seven": "🕷️"
        }
        
        # Action type descriptions and impact levels
        self.action_types = {
            "assimilate": {
                "description": "Complete system takeover and control",
                "impact": "HIGH",
                "duration": "Long-term",
                "reversibility": "Difficult",
                "required_level": 4
            },
            "recon": {
                "description": "Information gathering and analysis",
                "impact": "LOW",
                "duration": "Short-term",
                "reversibility": "Immediate",
                "required_level": 0
            },
            "chaos": {
                "description": "System disruption and disorder",
                "impact": "MEDIUM",
                "duration": "Medium-term",
                "reversibility": "Moderate",
                "required_level": 2
            },
            "ghost": {
                "description": "Stealth operations and silent infiltration",
                "impact": "MEDIUM",
                "duration": "Medium-term",
                "reversibility": "Moderate",
                "required_level": 1
            }
        }
    
    def _load_config(self) -> Dict:
        """Load the configuration file."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {"agents": []}
    
    def _get_sister_config(self, sister_name: str) -> Optional[Dict]:
        """Get the configuration for a specific sister."""
        for agent in self.config.get("agents", []):
            if agent.get("name") == sister_name:
                return agent
        return None
    
    def _get_sister_emoji(self, sister_name: str) -> str:
        """Get the emoji for a specific sister."""
        return self.sister_emojis.get(sister_name, "❓")
    
    def _format_sister_status(self, sister_name: str) -> str:
        """Format the status of a sister for display."""
        sister_config = self._get_sister_config(sister_name)
        if not sister_config:
            return f"{self._get_sister_emoji(sister_name)} {sister_name}: Not configured"
        
        emoji = self._get_sister_emoji(sister_name)
        enabled = "✅" if sister_config.get("enabled", False) else "❌"
        safe_mode = "🛡️" if sister_config.get("safe_mode", True) else "⚔️"
        level = sister_config.get("current_level", 0)
        tools = sister_config.get("tools", [])
        
        return f"{emoji} {sister_name}: {enabled} (Level {level}) {safe_mode}\n   Tools: {', '.join(tools)}"
    
    def _calculate_risk_level(self, action_type: str, sisters: List[str]) -> Tuple[str, str, Dict]:
        """
        Calculate the risk level of an action based on the action type and sisters involved.
        
        Returns:
            Tuple of (risk_level, risk_description, risk_factors)
        """
        # Get the highest level sister involved
        max_level = 0
        risk_factors = []
        
        for sister_name in sisters:
            sister_config = self._get_sister_config(sister_name)
            if sister_config:
                level = sister_config.get("current_level", 0)
                max_level = max(max_level, level)
                
                # Check if sister's level is below required level for action
                required_level = self.action_types[action_type]["required_level"]
                if level < required_level:
                    risk_factors.append(f"{sister_name} is below required level {required_level}")
        
        # Check if any sister is not in safe mode
        unsafe_sisters = []
        for sister_name in sisters:
            sister_config = self._get_sister_config(sister_name)
            if sister_config and not sister_config.get("safe_mode", True):
                unsafe_sisters.append(sister_name)
        
        if unsafe_sisters:
            risk_factors.append(f"Sisters not in safe mode: {', '.join(unsafe_sisters)}")
        
        # Determine risk level based on action type and sister properties
        action_info = self.action_types[action_type]
        base_risk = action_info["impact"]
        
        if base_risk == "HIGH" or (unsafe_sisters and max_level >= 4):
            risk_level = "HIGH"
            risk_description = f"This {action_type} operation involves high-risk operations and may cause significant changes."
        elif base_risk == "MEDIUM" or (unsafe_sisters and max_level >= 2):
            risk_level = "MEDIUM"
            risk_description = f"This {action_type} operation involves moderate-risk operations."
        else:
            risk_level = "LOW"
            risk_description = f"This {action_type} operation involves low-risk operations."
        
        return risk_level, risk_description, risk_factors
    
    def confirm_action(self, action_type: str, target: str, sisters: List[str]) -> bool:
        """
        Display a detailed summary of the planned action and request confirmation.
        
        Args:
            action_type: The type of action to be performed
            target: The target of the action
            sisters: List of sisters involved in the action
            
        Returns:
            True if the action is confirmed, False otherwise
        """
        # Clear the screen for better visibility
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Print the action confirmation header
        print("\n" + "=" * 80)
        print(f"ACTION CONFIRMATION: {action_type.upper()} OPERATION")
        print("=" * 80 + "\n")
        
        # Display the target
        print(f"TARGET: {target}\n")
        
        # Display action type information
        action_info = self.action_types[action_type]
        print("ACTION TYPE INFORMATION:")
        print(f"  • Description: {action_info['description']}")
        print(f"  • Impact Level: {action_info['impact']}")
        print(f"  • Duration: {action_info['duration']}")
        print(f"  • Reversibility: {action_info['reversibility']}")
        print(f"  • Required Level: {action_info['required_level']}\n")
        
        # Display the sisters involved
        print("SISTERS ASSIGNED:")
        for sister in sisters:
            print(f"  {self._format_sister_status(sister)}")
        print()
        
        # Calculate and display the risk level
        risk_level, risk_description, risk_factors = self._calculate_risk_level(action_type, sisters)
        risk_emoji = "🔴" if risk_level == "HIGH" else "🟡" if risk_level == "MEDIUM" else "🟢"
        print(f"RISK ASSESSMENT: {risk_emoji} {risk_level}")
        print(f"  {risk_description}")
        if risk_factors:
            print("\n  Risk Factors:")
            for factor in risk_factors:
                print(f"    • {factor}")
        print()
        
        # Display the action summary
        print("ACTION SUMMARY:")
        print(f"  • Operation Type: {action_type}")
        print(f"  • Target: {target}")
        print(f"  • Sisters: {', '.join(sisters)}")
        print(f"  • Risk Level: {risk_level}")
        print(f"  • Impact: {action_info['impact']}")
        print(f"  • Duration: {action_info['duration']}")
        print(f"  • Reversibility: {action_info['reversibility']}")
        print()
        
        # Request confirmation
        print("=" * 80)
        print("CONFIRMATION REQUIRED")
        print("=" * 80)
        print(f"\nDo you want to proceed with this {action_type} operation? (yes/no): ")
        
        # Get user input
        response = input().strip().lower()
        
        # Log the confirmation result
        if response == "yes":
            write_output("Seven", target, f"✅ Action confirmed: {action_type} operation on {target} with sisters {', '.join(sisters)}")
            return True
        else:
            write_output("Seven", target, f"❌ Action cancelled: {action_type} operation on {target} with sisters {', '.join(sisters)}")
            return False
    
    def display_action_summary(self, action_type: str, target: str, sisters: List[str]) -> None:
        """
        Display a summary of the planned action without requesting confirmation.
        Useful for informational purposes.
        
        Args:
            action_type: The type of action to be performed
            target: The target of the action
            sisters: List of sisters involved in the action
        """
        # Clear the screen for better visibility
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Print the action summary header
        print("\n" + "=" * 80)
        print(f"ACTION SUMMARY: {action_type.upper()} OPERATION")
        print("=" * 80 + "\n")
        
        # Display the target
        print(f"TARGET: {target}\n")
        
        # Display action type information
        action_info = self.action_types[action_type]
        print("ACTION TYPE INFORMATION:")
        print(f"  • Description: {action_info['description']}")
        print(f"  • Impact Level: {action_info['impact']}")
        print(f"  • Duration: {action_info['duration']}")
        print(f"  • Reversibility: {action_info['reversibility']}")
        print(f"  • Required Level: {action_info['required_level']}\n")
        
        # Display the sisters involved
        print("SISTERS ASSIGNED:")
        for sister in sisters:
            print(f"  {self._format_sister_status(sister)}")
        print()
        
        # Calculate and display the risk level
        risk_level, risk_description, risk_factors = self._calculate_risk_level(action_type, sisters)
        risk_emoji = "🔴" if risk_level == "HIGH" else "🟡" if risk_level == "MEDIUM" else "🟢"
        print(f"RISK ASSESSMENT: {risk_emoji} {risk_level}")
        print(f"  {risk_description}")
        if risk_factors:
            print("\n  Risk Factors:")
            for factor in risk_factors:
                print(f"    • {factor}")
        print()
        
        # Display the action summary
        print("ACTION DETAILS:")
        print(f"  • Operation Type: {action_type}")
        print(f"  • Target: {target}")
        print(f"  • Sisters: {', '.join(sisters)}")
        print(f"  • Risk Level: {risk_level}")
        print(f"  • Impact: {action_info['impact']}")
        print(f"  • Duration: {action_info['duration']}")
        print(f"  • Reversibility: {action_info['reversibility']}")
        print()
        
        print("=" * 80)
        print("Press Enter to continue...")
        input()


# Example usage
if __name__ == "__main__":
    confirmation = ActionConfirmation()
    
    # Example 1: Display an action summary
    confirmation.display_action_summary(
        action_type="recon",
        target="example.com",
        sisters=["Alice", "Luna"]
    )
    
    # Example 2: Request confirmation for an action
    if confirmation.confirm_action(
        action_type="assimilate",
        target="example.com",
        sisters=["Seven", "Harley"]
    ):
        print("Action confirmed! Proceeding with operation...")
    else:
        print("Action cancelled. Operation aborted.") 