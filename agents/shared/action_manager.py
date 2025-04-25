import os
import sys
import json
import time
import threading
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.shared.action_confirmation import ActionConfirmation
from agents.shared.sister_comm import SisterCommManager, Message
from output_handler import write_output

class ActionPhase(Enum):
    """Enum for action phases in multi-sister coordination."""
    INITIALIZATION = "initialization"
    PREPARATION = "preparation"
    EXECUTION = "execution"
    VERIFICATION = "verification"
    CLEANUP = "cleanup"

class ErrorType(Enum):
    """Enum for different types of errors that can occur during action execution."""
    CONNECTION = "connection_error"
    TIMEOUT = "timeout_error"
    EXECUTION = "execution_error"
    VALIDATION = "validation_error"
    COORDINATION = "coordination_error"
    SYSTEM = "system_error"

class ActionManager:
    """
    A class to manage and coordinate actions between sisters.
    Handles action planning, sister assignment, and execution coordination.
    """
    
    def __init__(self, config_path: str = "seven_sisters.config.json"):
        """
        Initialize the ActionManager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.confirmation = ActionConfirmation(config_path)
        self.action_history = []
        self.comm_manager = None
        self.action_status = {}
        self.action_timeouts = {}
        self.action_threads = {}
        self.coordination_locks = {}
        self.error_recovery_strategies = {
            ErrorType.CONNECTION: self._handle_connection_error,
            ErrorType.TIMEOUT: self._handle_timeout_error,
            ErrorType.EXECUTION: self._handle_execution_error,
            ErrorType.VALIDATION: self._handle_validation_error,
            ErrorType.COORDINATION: self._handle_coordination_error,
            ErrorType.SYSTEM: self._handle_system_error
        }
        
        # Action type capabilities and requirements
        self.action_capabilities = {
            "assimilate": {
                "required_sisters": ["Seven"],
                "optional_sisters": ["Harley", "Lisbeth"],
                "min_sisters": 1,
                "max_sisters": 3,
                "preferred_order": ["Seven", "Harley", "Lisbeth"],
                "timeout": 300,  # 5 minutes
                "retry_count": 2,
                "phases": {
                    ActionPhase.INITIALIZATION: ["Seven"],
                    ActionPhase.PREPARATION: ["Seven", "Harley"],
                    ActionPhase.EXECUTION: ["Seven", "Harley", "Lisbeth"],
                    ActionPhase.VERIFICATION: ["Seven"],
                    ActionPhase.CLEANUP: ["Seven", "Harley"]
                },
                "error_recovery": {
                    ErrorType.CONNECTION: {"max_retries": 3, "backoff_time": 5},
                    ErrorType.TIMEOUT: {"max_retries": 2, "backoff_time": 10},
                    ErrorType.EXECUTION: {"max_retries": 2, "backoff_time": 15},
                    ErrorType.VALIDATION: {"max_retries": 1, "backoff_time": 5},
                    ErrorType.COORDINATION: {"max_retries": 2, "backoff_time": 10},
                    ErrorType.SYSTEM: {"max_retries": 1, "backoff_time": 30}
                }
            },
            "recon": {
                "required_sisters": [],
                "optional_sisters": ["Alice", "Luna", "Marla"],
                "min_sisters": 1,
                "max_sisters": 3,
                "preferred_order": ["Alice", "Luna", "Marla"],
                "timeout": 180,  # 3 minutes
                "retry_count": 1,
                "phases": {
                    ActionPhase.INITIALIZATION: ["Alice"],
                    ActionPhase.PREPARATION: ["Alice", "Luna"],
                    ActionPhase.EXECUTION: ["Alice", "Luna", "Marla"],
                    ActionPhase.VERIFICATION: ["Alice", "Luna"],
                    ActionPhase.CLEANUP: ["Alice"]
                },
                "error_recovery": {
                    ErrorType.CONNECTION: {"max_retries": 2, "backoff_time": 5},
                    ErrorType.TIMEOUT: {"max_retries": 1, "backoff_time": 10},
                    ErrorType.EXECUTION: {"max_retries": 1, "backoff_time": 15},
                    ErrorType.VALIDATION: {"max_retries": 1, "backoff_time": 5},
                    ErrorType.COORDINATION: {"max_retries": 1, "backoff_time": 10},
                    ErrorType.SYSTEM: {"max_retries": 1, "backoff_time": 30}
                }
            },
            "chaos": {
                "required_sisters": ["Harley"],
                "optional_sisters": ["Lisbeth", "Marla"],
                "min_sisters": 1,
                "max_sisters": 3,
                "preferred_order": ["Harley", "Lisbeth", "Marla"],
                "timeout": 240,  # 4 minutes
                "retry_count": 2,
                "phases": {
                    ActionPhase.INITIALIZATION: ["Harley"],
                    ActionPhase.PREPARATION: ["Harley", "Lisbeth"],
                    ActionPhase.EXECUTION: ["Harley", "Lisbeth", "Marla"],
                    ActionPhase.VERIFICATION: ["Harley"],
                    ActionPhase.CLEANUP: ["Harley", "Lisbeth"]
                },
                "error_recovery": {
                    ErrorType.CONNECTION: {"max_retries": 3, "backoff_time": 5},
                    ErrorType.TIMEOUT: {"max_retries": 2, "backoff_time": 10},
                    ErrorType.EXECUTION: {"max_retries": 2, "backoff_time": 15},
                    ErrorType.VALIDATION: {"max_retries": 1, "backoff_time": 5},
                    ErrorType.COORDINATION: {"max_retries": 2, "backoff_time": 10},
                    ErrorType.SYSTEM: {"max_retries": 1, "backoff_time": 30}
                }
            },
            "ghost": {
                "required_sisters": ["Lisbeth"],
                "optional_sisters": ["Alice", "Marla"],
                "min_sisters": 1,
                "max_sisters": 2,
                "preferred_order": ["Lisbeth", "Alice", "Marla"],
                "timeout": 120,  # 2 minutes
                "retry_count": 1,
                "phases": {
                    ActionPhase.INITIALIZATION: ["Lisbeth"],
                    ActionPhase.PREPARATION: ["Lisbeth", "Alice"],
                    ActionPhase.EXECUTION: ["Lisbeth", "Alice"],
                    ActionPhase.VERIFICATION: ["Lisbeth"],
                    ActionPhase.CLEANUP: ["Lisbeth"]
                },
                "error_recovery": {
                    ErrorType.CONNECTION: {"max_retries": 2, "backoff_time": 5},
                    ErrorType.TIMEOUT: {"max_retries": 1, "backoff_time": 10},
                    ErrorType.EXECUTION: {"max_retries": 1, "backoff_time": 15},
                    ErrorType.VALIDATION: {"max_retries": 1, "backoff_time": 5},
                    ErrorType.COORDINATION: {"max_retries": 1, "backoff_time": 10},
                    ErrorType.SYSTEM: {"max_retries": 1, "backoff_time": 30}
                }
            }
        }
    
    def setup(self, comm_manager: SisterCommManager):
        """Set up the action manager with a communication manager."""
        self.comm_manager = comm_manager
        self._setup_command_handlers()
    
    def _setup_command_handlers(self):
        """Set up command handlers for action management."""
        def handle_action_status(args):
            action_id = args.get('action_id')
            sister_name = args.get('sister_name')
            status = args.get('status')
            details = args.get('details', {})
            phase = args.get('phase')
            
            if action_id in self.action_status:
                self.action_status[action_id]['sister_status'][sister_name] = {
                    'status': status,
                    'details': details,
                    'phase': phase,
                    'timestamp': time.time()
                }
                
                # Check if current phase is complete
                if self._is_phase_complete(action_id, phase):
                    self._advance_to_next_phase(action_id)
                
                # Check if all phases are complete
                if self._is_action_complete(action_id):
                    self._finalize_action(action_id)
        
        def handle_action_error(args):
            action_id = args.get('action_id')
            sister_name = args.get('sister_name')
            error = args.get('error')
            error_type = ErrorType(args.get('error_type', ErrorType.EXECUTION.value))
            phase = args.get('phase')
            
            if action_id in self.action_status:
                self.action_status[action_id]['sister_status'][sister_name] = {
                    'status': 'failed',
                    'error': error,
                    'error_type': error_type,
                    'phase': phase,
                    'timestamp': time.time()
                }
                
                # Handle the error based on its type
                if error_type in self.error_recovery_strategies:
                    if self.error_recovery_strategies[error_type](action_id, sister_name, error):
                        return  # Error handled successfully
                
                # If error couldn't be handled, mark as failed
                self._handle_action_failure(action_id, sister_name)
        
        # Register command handlers with the communication manager
        if self.comm_manager:
            self.comm_manager.command_handler.register_command('action_status', handle_action_status)
            self.comm_manager.command_handler.register_command('action_error', handle_action_error)
    
    def _should_retry_action(self, action_id: str, sister_name: str) -> bool:
        """Determine if an action should be retried for a sister."""
        if action_id not in self.action_status:
            return False
            
        action = self.action_status[action_id]
        action_type = action['action_type']
        retry_count = action['sister_status'].get(sister_name, {}).get('retry_count', 0)
        max_retries = self.action_capabilities[action_type]['retry_count']
        
        return retry_count < max_retries
    
    def _retry_action(self, action_id: str, sister_name: str):
        """Retry a failed action for a specific sister."""
        if action_id not in self.action_status:
            return
            
        action = self.action_status[action_id]
        retry_count = action['sister_status'].get(sister_name, {}).get('retry_count', 0) + 1
        
        # Update retry count
        if sister_name not in action['sister_status']:
            action['sister_status'][sister_name] = {}
        action['sister_status'][sister_name]['retry_count'] = retry_count
        
        # Send retry command
        self.comm_manager.send_command(
            sister_name,
            'execute_action',
            {
                'action_id': action_id,
                'action_type': action['action_type'],
                'target': action['target'],
                'retry_count': retry_count
            }
        )
        
        write_output("Seven", action['target'], 
                    f"Retrying {action['action_type']} operation for {sister_name} (attempt {retry_count})")
    
    def _handle_action_failure(self, action_id: str, sister_name: str):
        """Handle a failed action that has exceeded retry attempts."""
        if action_id not in self.action_status:
            return
            
        action = self.action_status[action_id]
        write_output("Seven", action['target'],
                    f"Action failed for {sister_name} after {action['sister_status'][sister_name].get('retry_count', 0)} attempts")
        
        # Check if we should continue with other sisters
        active_sisters = [
            s for s, status in action['sister_status'].items()
            if status.get('status') not in ['completed', 'failed']
        ]
        
        if not active_sisters:
            self._finalize_action(action_id, success=False)
    
    def _finalize_action(self, action_id: str, success: bool = True):
        """Finalize an action and update its status."""
        if action_id not in self.action_status:
            return
            
        action = self.action_status[action_id]
        action['status'] = 'completed' if success else 'failed'
        action['completion_time'] = time.time()
        
        # Update action history
        for history_action in self.action_history:
            if (history_action['action_type'] == action['action_type'] and
                history_action['target'] == action['target'] and
                history_action['sisters'] == action['sisters'] and
                history_action['status'] == 'executing'):
                history_action['status'] = 'completed' if success else 'failed'
                history_action['completion_time'] = action['completion_time']
                break
        
        # Clean up timeouts
        if action_id in self.action_timeouts:
            self.action_timeouts[action_id].cancel()
            del self.action_timeouts[action_id]
        
        # Clean up threads
        if action_id in self.action_threads:
            del self.action_threads[action_id]
        
        # Log completion
        status_msg = "completed successfully" if success else "failed"
        write_output("Seven", action['target'],
                    f"Action {status_msg}: {action['action_type']} operation on {action['target']}")
    
    def _execute_sister_action(self, action_id: str, sister_name: str):
        """Execute an action for a specific sister."""
        if action_id not in self.action_status:
            return
            
        action = self.action_status[action_id]
        action_type = action['action_type']
        
        # Initialize the action
        action['current_phase'] = None
        action['sister_status'] = {}
        
        # Start with the first phase
        self._advance_to_next_phase(action_id)
        
        # Set up timeout for the entire action
        timeout = self.action_capabilities[action_type]['timeout']
        self.action_timeouts[action_id] = threading.Timer(
            timeout,
            self._handle_action_timeout,
            args=[action_id, sister_name]
        )
        self.action_timeouts[action_id].start()
    
    def _handle_action_timeout(self, action_id: str, sister_name: str):
        """Handle an action timeout for a specific sister."""
        if action_id not in self.action_status:
            return
            
        action = self.action_status[action_id]
        write_output("Seven", action['target'],
                    f"Action timed out for {sister_name}")
        
        # Check if we should retry
        if self._should_retry_action(action_id, sister_name):
            self._retry_action(action_id, sister_name)
        else:
            self._handle_action_failure(action_id, sister_name)
    
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
    
    def _get_available_sisters(self) -> List[str]:
        """Get a list of available and enabled sisters."""
        available_sisters = []
        for agent in self.config.get("agents", []):
            if agent.get("enabled", False):
                available_sisters.append(agent.get("name"))
        return available_sisters
    
    def _validate_sister_availability(self, sisters: List[str]) -> Tuple[bool, str]:
        """
        Validate that all requested sisters are available and enabled.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        available_sisters = self._get_available_sisters()
        
        for sister in sisters:
            if sister not in available_sisters:
                return False, f"Sister {sister} is not available or enabled"
            
            sister_config = self._get_sister_config(sister)
            if not sister_config:
                return False, f"Configuration not found for sister {sister}"
        
        return True, ""
    
    def _plan_sister_assignment(self, action_type: str, target: str) -> Tuple[List[str], str]:
        """
        Plan the optimal sister assignment for an action.
        
        Returns:
            Tuple of (assigned_sisters, error_message)
        """
        if action_type not in self.action_capabilities:
            return [], f"Unknown action type: {action_type}"
        
        capabilities = self.action_capabilities[action_type]
        available_sisters = self._get_available_sisters()
        assigned_sisters = []
        
        # First, assign required sisters
        for sister in capabilities["required_sisters"]:
            if sister in available_sisters:
                assigned_sisters.append(sister)
            else:
                return [], f"Required sister {sister} is not available"
        
        # Then, assign optional sisters in preferred order
        for sister in capabilities["preferred_order"]:
            if (sister in capabilities["optional_sisters"] and 
                sister in available_sisters and 
                sister not in assigned_sisters and 
                len(assigned_sisters) < capabilities["max_sisters"]):
                assigned_sisters.append(sister)
        
        # Validate minimum sister requirement
        if len(assigned_sisters) < capabilities["min_sisters"]:
            return [], f"Not enough sisters available. Minimum required: {capabilities['min_sisters']}"
        
        return assigned_sisters, ""
    
    def plan_action(self, action_type: str, target: str) -> Tuple[bool, str, List[str]]:
        """
        Plan an action, including sister assignment and validation.
        
        Args:
            action_type: The type of action to perform
            target: The target of the action
            
        Returns:
            Tuple of (success, message, assigned_sisters)
        """
        # Validate action type
        if action_type not in self.action_capabilities:
            return False, f"Unknown action type: {action_type}", []
        
        # Plan sister assignment
        assigned_sisters, error = self._plan_sister_assignment(action_type, target)
        if error:
            return False, error, []
        
        # Validate sister availability
        is_valid, error = self._validate_sister_availability(assigned_sisters)
        if not is_valid:
            return False, error, []
        
        # Display action summary and request confirmation
        self.confirmation.display_action_summary(action_type, target, assigned_sisters)
        
        if self.confirmation.confirm_action(action_type, target, assigned_sisters):
            # Log the planned action
            self.action_history.append({
                "timestamp": time.time(),
                "action_type": action_type,
                "target": target,
                "sisters": assigned_sisters,
                "status": "planned"
            })
            
            write_output("Seven", target, f"Action planned: {action_type} operation on {target} with sisters {', '.join(assigned_sisters)}")
            return True, "Action planned successfully", assigned_sisters
        else:
            return False, "Action cancelled by user", []
    
    def execute_action(self, action_type: str, target: str, sisters: List[str]) -> Tuple[bool, str]:
        """
        Execute a planned action with the assigned sisters.
        
        Args:
            action_type: The type of action to perform
            target: The target of the action
            sisters: List of sisters assigned to the action
            
        Returns:
            Tuple of (success, message)
        """
        # Validate the action and sisters
        is_valid, error = self._validate_sister_availability(sisters)
        if not is_valid:
            return False, error
        
        # Generate action ID
        action_id = f"{action_type}_{target}_{int(time.time())}"
        
        # Initialize action status
        self.action_status[action_id] = {
            'action_type': action_type,
            'target': target,
            'sisters': sisters,
            'status': 'executing',
            'start_time': time.time(),
            'sister_status': {},
            'current_phase': None
        }
        
        # Update action history
        for action in self.action_history:
            if (action['action_type'] == action_type and
                action['target'] == target and
                action['sisters'] == sisters and
                action['status'] == 'planned'):
                action['status'] = 'executing'
                action['execution_time'] = time.time()
                break
        
        # Execute action for each sister
        for sister in sisters:
            thread = threading.Thread(
                target=self._execute_sister_action,
                args=[action_id, sister]
            )
            self.action_threads[action_id] = thread
            thread.start()
        
        write_output("Seven", target,
                    f"Executing {action_type} operation on {target} with sisters {', '.join(sisters)}")
        return True, "Action execution started"
    
    def get_action_history(self) -> List[Dict]:
        """Get the history of planned and executed actions."""
        return self.action_history
    
    def _is_phase_complete(self, action_id: str, phase: ActionPhase) -> bool:
        """Check if all sisters have completed the current phase."""
        if action_id not in self.action_status:
            return False
            
        action = self.action_status[action_id]
        action_type = action['action_type']
        required_sisters = self.action_capabilities[action_type]['phases'][phase]
        
        # Check if all required sisters have completed the phase
        sister_statuses = action['sister_status']
        return all(
            sister_status.get('status') == 'completed' and
            sister_status.get('phase') == phase
            for sister, sister_status in sister_statuses.items()
            if sister in required_sisters
        )
    
    def _is_action_complete(self, action_id: str) -> bool:
        """Check if all phases of the action are complete."""
        if action_id not in self.action_status:
            return False
            
        action = self.action_status[action_id]
        action_type = action['action_type']
        
        # Check if all phases are complete
        return all(
            self._is_phase_complete(action_id, phase)
            for phase in self.action_capabilities[action_type]['phases'].keys()
        )
    
    def _advance_to_next_phase(self, action_id: str):
        """Advance the action to the next phase."""
        if action_id not in self.action_status:
            return
            
        action = self.action_status[action_id]
        action_type = action['action_type']
        current_phase = action.get('current_phase')
        
        # Get the next phase
        phases = list(self.action_capabilities[action_type]['phases'].keys())
        if current_phase is None:
            next_phase = phases[0]
        else:
            current_index = phases.index(current_phase)
            if current_index < len(phases) - 1:
                next_phase = phases[current_index + 1]
            else:
                return  # All phases complete
        
        # Update current phase
        action['current_phase'] = next_phase
        
        # Execute next phase
        self._execute_phase(action_id, next_phase)
    
    def _execute_phase(self, action_id: str, phase: ActionPhase):
        """Execute a specific phase of the action."""
        if action_id not in self.action_status:
            return
            
        action = self.action_status[action_id]
        action_type = action['action_type']
        required_sisters = self.action_capabilities[action_type]['phases'][phase]
        
        # Send phase command to each required sister
        for sister in required_sisters:
            if sister in action['sisters']:
                self.comm_manager.send_command(
                    sister,
                    'execute_phase',
                    {
                        'action_id': action_id,
                        'action_type': action_type,
                        'target': action['target'],
                        'phase': phase.value
                    }
                )
        
        write_output("Seven", action['target'],
                    f"Executing {phase.value} phase of {action_type} operation")
    
    def _handle_connection_error(self, action_id: str, sister_name: str, error: str) -> bool:
        """Handle connection errors with retry logic."""
        if action_id not in self.action_status:
            return False
            
        action = self.action_status[action_id]
        action_type = action['action_type']
        error_config = self.action_capabilities[action_type]['error_recovery'][ErrorType.CONNECTION]
        
        # Get current retry count
        retry_count = action['sister_status'].get(sister_name, {}).get('connection_retries', 0)
        
        if retry_count < error_config['max_retries']:
            # Increment retry count
            if sister_name not in action['sister_status']:
                action['sister_status'][sister_name] = {}
            action['sister_status'][sister_name]['connection_retries'] = retry_count + 1
            
            # Wait for backoff time
            time.sleep(error_config['backoff_time'])
            
            # Attempt to reconnect
            write_output("Seven", action['target'],
                        f"Attempting to reconnect to {sister_name} (attempt {retry_count + 1})")
            
            # Retry the current phase
            self._retry_phase(action_id, sister_name)
            return True
        
        return False
    
    def _handle_timeout_error(self, action_id: str, sister_name: str, error: str) -> bool:
        """Handle timeout errors with retry logic."""
        if action_id not in self.action_status:
            return False
            
        action = self.action_status[action_id]
        action_type = action['action_type']
        error_config = self.action_capabilities[action_type]['error_recovery'][ErrorType.TIMEOUT]
        
        # Get current retry count
        retry_count = action['sister_status'].get(sister_name, {}).get('timeout_retries', 0)
        
        if retry_count < error_config['max_retries']:
            # Increment retry count
            if sister_name not in action['sister_status']:
                action['sister_status'][sister_name] = {}
            action['sister_status'][sister_name]['timeout_retries'] = retry_count + 1
            
            # Wait for backoff time
            time.sleep(error_config['backoff_time'])
            
            # Retry with increased timeout
            write_output("Seven", action['target'],
                        f"Retrying {sister_name} with increased timeout (attempt {retry_count + 1})")
            
            # Retry the current phase
            self._retry_phase(action_id, sister_name)
            return True
        
        return False
    
    def _handle_execution_error(self, action_id: str, sister_name: str, error: str) -> bool:
        """Handle execution errors with retry logic."""
        if action_id not in self.action_status:
            return False
            
        action = self.action_status[action_id]
        action_type = action['action_type']
        error_config = self.action_capabilities[action_type]['error_recovery'][ErrorType.EXECUTION]
        
        # Get current retry count
        retry_count = action['sister_status'].get(sister_name, {}).get('execution_retries', 0)
        
        if retry_count < error_config['max_retries']:
            # Increment retry count
            if sister_name not in action['sister_status']:
                action['sister_status'][sister_name] = {}
            action['sister_status'][sister_name]['execution_retries'] = retry_count + 1
            
            # Wait for backoff time
            time.sleep(error_config['backoff_time'])
            
            # Retry with error details
            write_output("Seven", action['target'],
                        f"Retrying {sister_name} after execution error: {error} (attempt {retry_count + 1})")
            
            # Retry the current phase
            self._retry_phase(action_id, sister_name)
            return True
        
        return False
    
    def _handle_validation_error(self, action_id: str, sister_name: str, error: str) -> bool:
        """Handle validation errors with retry logic."""
        if action_id not in self.action_status:
            return False
            
        action = self.action_status[action_id]
        action_type = action['action_type']
        error_config = self.action_capabilities[action_type]['error_recovery'][ErrorType.VALIDATION]
        
        # Get current retry count
        retry_count = action['sister_status'].get(sister_name, {}).get('validation_retries', 0)
        
        if retry_count < error_config['max_retries']:
            # Increment retry count
            if sister_name not in action['sister_status']:
                action['sister_status'][sister_name] = {}
            action['sister_status'][sister_name]['validation_retries'] = retry_count + 1
            
            # Wait for backoff time
            time.sleep(error_config['backoff_time'])
            
            # Retry with validation details
            write_output("Seven", action['target'],
                        f"Retrying {sister_name} after validation error: {error} (attempt {retry_count + 1})")
            
            # Retry the current phase
            self._retry_phase(action_id, sister_name)
            return True
        
        return False
    
    def _handle_coordination_error(self, action_id: str, sister_name: str, error: str) -> bool:
        """Handle coordination errors with retry logic."""
        if action_id not in self.action_status:
            return False
            
        action = self.action_status[action_id]
        action_type = action['action_type']
        error_config = self.action_capabilities[action_type]['error_recovery'][ErrorType.COORDINATION]
        
        # Get current retry count
        retry_count = action['sister_status'].get(sister_name, {}).get('coordination_retries', 0)
        
        if retry_count < error_config['max_retries']:
            # Increment retry count
            if sister_name not in action['sister_status']:
                action['sister_status'][sister_name] = {}
            action['sister_status'][sister_name]['coordination_retries'] = retry_count + 1
            
            # Wait for backoff time
            time.sleep(error_config['backoff_time'])
            
            # Retry with coordination details
            write_output("Seven", action['target'],
                        f"Retrying {sister_name} after coordination error: {error} (attempt {retry_count + 1})")
            
            # Retry the current phase
            self._retry_phase(action_id, sister_name)
            return True
        
        return False
    
    def _handle_system_error(self, action_id: str, sister_name: str, error: str) -> bool:
        """Handle system errors with retry logic."""
        if action_id not in self.action_status:
            return False
            
        action = self.action_status[action_id]
        action_type = action['action_type']
        error_config = self.action_capabilities[action_type]['error_recovery'][ErrorType.SYSTEM]
        
        # Get current retry count
        retry_count = action['sister_status'].get(sister_name, {}).get('system_retries', 0)
        
        if retry_count < error_config['max_retries']:
            # Increment retry count
            if sister_name not in action['sister_status']:
                action['sister_status'][sister_name] = {}
            action['sister_status'][sister_name]['system_retries'] = retry_count + 1
            
            # Wait for backoff time
            time.sleep(error_config['backoff_time'])
            
            # Retry with system error details
            write_output("Seven", action['target'],
                        f"Retrying {sister_name} after system error: {error} (attempt {retry_count + 1})")
            
            # Retry the current phase
            self._retry_phase(action_id, sister_name)
            return True
        
        return False
    
    def _retry_phase(self, action_id: str, sister_name: str):
        """Retry the current phase for a specific sister."""
        if action_id not in self.action_status:
            return
            
        action = self.action_status[action_id]
        current_phase = action.get('current_phase')
        
        if current_phase:
            self._execute_phase(action_id, current_phase)


# Example usage
if __name__ == "__main__":
    manager = ActionManager()
    
    # Example 1: Plan and execute a recon action
    success, message, sisters = manager.plan_action("recon", "example.com")
    if success:
        print(f"Action planned successfully with sisters: {', '.join(sisters)}")
        success, message = manager.execute_action("recon", "example.com", sisters)
        print(f"Execution result: {message}")
    else:
        print(f"Planning failed: {message}")
    
    # Example 2: Plan and execute an assimilate action
    success, message, sisters = manager.plan_action("assimilate", "example.com")
    if success:
        print(f"Action planned successfully with sisters: {', '.join(sisters)}")
        success, message = manager.execute_action("assimilate", "example.com", sisters)
        print(f"Execution result: {message}")
    else:
        print(f"Planning failed: {message}")
    
    # Display action history
    print("\nAction History:")
    for action in manager.get_action_history():
        print(f"  • {action['action_type']} on {action['target']} with {', '.join(action['sisters'])} - {action['status']}") 