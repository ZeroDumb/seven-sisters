import os
import json
import time
import shutil
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class ConfigChangeType(Enum):
    SAFE_MODE = "safe_mode"
    LEVEL = "level"
    ENABLED = "enabled"
    TOOLS = "tools"
    CUSTOM = "custom"

@dataclass
class ConfigChange:
    sister_name: str
    change_type: ConfigChangeType
    old_value: Any
    new_value: Any
    timestamp: float
    description: str

class ConfigurationManager:
    """Manages centralized configuration for all sisters."""
    
    def __init__(self, config_path: str = "seven_sisters.config.json"):
        self.config_path = config_path
        self.backup_path = f"{config_path}.backup"
        self.config: Dict = {}
        self.change_history: List[ConfigChange] = []
        self.load_config()
    
    def load_config(self) -> bool:
        """Load the configuration file."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading config: {e}")
            return False
    
    def save_config(self) -> bool:
        """Save the configuration file with backup."""
        try:
            # Create backup of current config
            if os.path.exists(self.config_path):
                shutil.copy2(self.config_path, self.backup_path)
            
            # Save new config
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            # Restore from backup if save failed
            if os.path.exists(self.backup_path):
                shutil.copy2(self.backup_path, self.config_path)
            return False
    
    def get_sister_config(self, sister_name: str) -> Optional[Dict]:
        """Get configuration for a specific sister."""
        for agent in self.config.get("agents", []):
            if agent.get("name") == sister_name:
                return agent
        return None
    
    def update_sister_config(self, sister_name: str, changes: Dict[str, Any], 
                           change_type: ConfigChangeType, description: str) -> Tuple[bool, str]:
        """
        Update configuration for a specific sister.
        
        Args:
            sister_name: Name of the sister to update
            changes: Dictionary of changes to apply
            change_type: Type of change being made
            description: Description of the change
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Find the sister in config
            sister_config = None
            sister_index = -1
            for i, agent in enumerate(self.config.get("agents", [])):
                if agent.get("name") == sister_name:
                    sister_config = agent
                    sister_index = i
                    break
            
            if not sister_config:
                return False, f"Sister {sister_name} not found in configuration"
            
            # Store old values for history
            old_values = {k: sister_config.get(k) for k in changes.keys()}
            
            # Apply changes
            for key, value in changes.items():
                sister_config[key] = value
            
            # Update the config
            self.config["agents"][sister_index] = sister_config
            
            # Record the change
            self.change_history.append(ConfigChange(
                sister_name=sister_name,
                change_type=change_type,
                old_value=old_values,
                new_value=changes,
                timestamp=time.time(),
                description=description
            ))
            
            # Save the configuration
            if not self.save_config():
                return False, "Failed to save configuration"
            
            return True, "Configuration updated successfully"
            
        except Exception as e:
            return False, f"Error updating configuration: {str(e)}"
    
    def get_change_history(self, sister_name: Optional[str] = None, 
                          change_type: Optional[ConfigChangeType] = None,
                          limit: int = 10) -> List[ConfigChange]:
        """Get the history of configuration changes."""
        history = self.change_history
        
        if sister_name:
            history = [c for c in history if c.sister_name == sister_name]
        
        if change_type:
            history = [c for c in history if c.change_type == change_type]
        
        return sorted(history, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def validate_config(self) -> Tuple[bool, List[str]]:
        """Validate the entire configuration."""
        errors = []
        
        if "agents" not in self.config:
            errors.append("No agents section in configuration")
            return False, errors
        
        for agent in self.config["agents"]:
            if "name" not in agent:
                errors.append("Agent missing name")
            if "enabled" not in agent:
                errors.append(f"Agent {agent.get('name', 'unknown')} missing enabled status")
            if "safe_mode" not in agent:
                errors.append(f"Agent {agent.get('name', 'unknown')} missing safe_mode status")
            if "current_level" not in agent:
                errors.append(f"Agent {agent.get('name', 'unknown')} missing current_level")
            if "required_level" not in agent:
                errors.append(f"Agent {agent.get('name', 'unknown')} missing required_level")
        
        return len(errors) == 0, errors 