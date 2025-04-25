import json
import time
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class SisterActivity(Enum):
    """Enum for sister activity states."""
    IDLE = "idle"
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    ERROR = "error"
    COMPLETE = "complete"

@dataclass
class SisterStatus:
    """Data class for sister status information."""
    name: str
    safe_mode: bool
    current_level: int
    required_level: int
    activity: SisterActivity
    last_update: float
    tools: List[str]
    error_count: int
    enabled: bool
    current_action: Optional[str] = None
    action_progress: Optional[float] = None
    error_message: Optional[str] = None

class SisterStatusManager:
    """Manages and displays comprehensive status information for all sisters."""
    
    def __init__(self, config_path: str = "seven_sisters.config.json"):
        self.config_path = config_path
        self.sister_statuses: Dict[str, SisterStatus] = {}
        self.status_history: List[Dict] = []
        self.last_refresh = 0
        self.refresh_interval = 1.0  # seconds
    
    def load_config(self) -> bool:
        """Load sister configurations from the config file."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            for agent in config.get("agents", []):
                name = agent.get("name")
                if name:
                    self.sister_statuses[name] = SisterStatus(
                        name=name,
                        safe_mode=agent.get("safe_mode", True),
                        current_level=agent.get("current_level", 0),
                        required_level=agent.get("required_level", 1),
                        activity=SisterActivity.IDLE,
                        last_update=time.time(),
                        tools=agent.get("tools", []),
                        error_count=agent.get("error_count", 0),
                        enabled=agent.get("enabled", True)
                    )
            return True
        except Exception as e:
            print(f"Error loading config: {e}")
            return False
    
    def update_status(self, sister_name: str, status_data: Dict[str, Any]) -> None:
        """Update the status of a specific sister."""
        if sister_name in self.sister_statuses:
            status = self.sister_statuses[sister_name]
            
            # Update basic status fields
            if "safe_mode" in status_data:
                status.safe_mode = status_data["safe_mode"]
            if "current_level" in status_data:
                status.current_level = status_data["current_level"]
            if "activity" in status_data:
                try:
                    status.activity = SisterActivity(status_data["activity"])
                except ValueError:
                    status.activity = SisterActivity.IDLE
            if "error_count" in status_data:
                status.error_count = status_data["error_count"]
            if "enabled" in status_data:
                status.enabled = status_data["enabled"]
            
            # Update action-related fields
            if "current_action" in status_data:
                status.current_action = status_data["current_action"]
            if "action_progress" in status_data:
                status.action_progress = status_data["action_progress"]
            if "error_message" in status_data:
                status.error_message = status_data["error_message"]
            
            # Update timestamp
            status.last_update = time.time()
            
            # Add to history
            self.status_history.append({
                "timestamp": time.time(),
                "sister": sister_name,
                "status": status_data
            })
    
    def get_sister_status(self, sister_name: str) -> Optional[SisterStatus]:
        """Get the current status of a specific sister."""
        return self.sister_statuses.get(sister_name)
    
    def get_all_sister_statuses(self) -> Dict[str, SisterStatus]:
        """Get the current status of all sisters."""
        return self.sister_statuses
    
    def display_status(self, sister_name: Optional[str] = None) -> str:
        """Display the status of one or all sisters in a formatted string."""
        if sister_name:
            return self._format_sister_status(self.get_sister_status(sister_name))
        
        status_lines = []
        for name, status in sorted(self.sister_statuses.items()):
            status_lines.append(self._format_sister_status(status))
        
        return "\n".join(status_lines)
    
    def _format_sister_status(self, status: Optional[SisterStatus]) -> str:
        """Format a single sister's status for display."""
        if not status:
            return "❌ Sister status not available"
        
        # Determine status emoji based on activity
        activity_emoji = {
            SisterActivity.IDLE: "💤",
            SisterActivity.INITIALIZING: "⚙️",
            SisterActivity.READY: "✅",
            SisterActivity.BUSY: "🔄",
            SisterActivity.ERROR: "❌",
            SisterActivity.COMPLETE: "✨"
        }.get(status.activity, "❓")
        
        # Determine safe mode emoji
        safe_mode_emoji = "🛡️" if status.safe_mode else "⚔️"
        
        # Format the status string
        status_str = [
            f"{activity_emoji} {status.name}:",
            f"  Status: {status.activity.value}",
            f"  Safe Mode: {safe_mode_emoji}",
            f"  Level: {status.current_level}/{status.required_level}",
            f"  Enabled: {'✅' if status.enabled else '❌'}"
        ]
        
        # Add action information if available
        if status.current_action:
            progress = f" ({status.action_progress:.0%})" if status.action_progress else ""
            status_str.append(f"  Current Action: {status.current_action}{progress}")
        
        # Add error information if available
        if status.error_message:
            status_str.append(f"  Error: {status.error_message}")
        
        # Add tools information
        if status.tools:
            tools_str = ", ".join(status.tools)
            status_str.append(f"  Tools: {tools_str}")
        
        # Add last update time
        last_update = datetime.fromtimestamp(status.last_update).strftime("%H:%M:%S")
        status_str.append(f"  Last Update: {last_update}")
        
        return "\n".join(status_str)
    
    def get_status_history(self, sister_name: Optional[str] = None, 
                         start_time: Optional[float] = None,
                         end_time: Optional[float] = None) -> List[Dict]:
        """Get the status history for one or all sisters within a time range."""
        history = self.status_history
        
        if sister_name:
            history = [h for h in history if h["sister"] == sister_name]
        
        if start_time:
            history = [h for h in history if h["timestamp"] >= start_time]
        
        if end_time:
            history = [h for h in history if h["timestamp"] <= end_time]
        
        return history 