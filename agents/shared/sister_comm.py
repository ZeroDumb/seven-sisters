import zmq
import json
import time
import threading
import queue
import logging
import socket
import os
from typing import Dict, Any, Optional, Callable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('sister_comm')

# IPC Configuration
IPC_PORT = 5555
IPC_ADDRESS = f"tcp://127.0.0.1:{IPC_PORT}"

# Connection retry settings
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # seconds

class SisterStatusManager:
    """Manages sister status information."""
    def __init__(self):
        self.statuses = {}
        self.last_update = {}
    
    def update_status(self, sister_name, status):
        """Update a sister's status."""
        self.statuses[sister_name] = status
        self.last_update[sister_name] = time.time()
    
    def get_status(self, sister_name):
        """Get a sister's status."""
        return self.statuses.get(sister_name)
    
    def get_last_update(self, sister_name):
        """Get when a sister's status was last updated."""
        return self.last_update.get(sister_name)
    
    def cleanup(self):
        """Clean up resources."""
        self.statuses.clear()
        self.last_update.clear()

class Message:
    """Standardized message format for sister communication."""
    def __init__(self, msg_type: str, sender: str, target: str, content: Any):
        self.type = msg_type  # status, command, response, error
        self.sender = sender
        self.target = target
        self.content = content
        self.timestamp = time.time()
    
    def to_json(self) -> str:
        """Convert message to JSON string."""
        return json.dumps({
            'type': self.type,
            'sender': self.sender,
            'target': self.target,
            'content': self.content,
            'timestamp': self.timestamp
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """Create message from JSON string."""
        data = json.loads(json_str)
        return cls(
            msg_type=data['type'],
            sender=data['sender'],
            target=data['target'],
            content=data['content']
        )

class ErrorHandler:
    """Handles errors in sister communication."""
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_counts: Dict[str, int] = {}
    
    def handle_error(self, error_type: str, error: Exception) -> bool:
        """Handle an error and determine if it should be retried."""
        # Increment retry count for this error type
        if error_type not in self.retry_counts:
            self.retry_counts[error_type] = 0
        self.retry_counts[error_type] += 1
        
        # Log the error
        logger.error(f"Error ({error_type}): {error}")
        
        # Check if we should retry
        if self.retry_counts[error_type] <= self.max_retries:
            logger.info(f"Retrying {error_type} operation (attempt {self.retry_counts[error_type]}/{self.max_retries})")
            time.sleep(self.retry_delay)
            return True
        
        # Reset retry count and give up
        self.retry_counts[error_type] = 0
        return False

class CommandHandler:
    """Handles commands for a sister."""
    def __init__(self, sister_name: str):
        self.sister_name = sister_name
        self.commands: Dict[str, Callable] = {}
    
    def register_command(self, command: str, handler: Callable):
        """Register a command handler."""
        self.commands[command] = handler
    
    def handle_command(self, command: str, args: Any = None) -> Optional[Dict]:
        """Handle a command."""
        if command in self.commands:
            try:
                return self.commands[command](args or {})
            except Exception as e:
                logger.error(f"Error handling command {command}: {e}")
                return {'success': False, 'error': str(e)}
        return None
    
    def handle_response(self, command: str, response: Any):
        """Handle a response to a command."""
        # This is a placeholder for future implementation
        pass

class SisterCommManager:
    """Manages communication between sisters."""
    def __init__(self, sister_name: str):
        self.sister_name = sister_name
        self.pub_socket = None
        self.sub_socket = None
        self.running = False
        self.message_queue = queue.Queue()
        self.status_cache: Dict[str, str] = {}
        self.error_handler = ErrorHandler(MAX_RETRIES, RETRY_DELAY)
        self.command_handler = CommandHandler(sister_name)
        self.status_manager = SisterStatusManager()
        self.last_heartbeat = time.time()
        self.heartbeat_interval = 5  # seconds
        self.connection_timeout = 10  # seconds
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 3
        self.reconnect_delay = 1  # seconds
        self.initialization_timeout = 30  # seconds
        self.initialization_complete = False
        self.termination_signal_received = False
        
        # Register default command handlers
        self.command_handler.register_command("status", self._handle_status_command)
        self.command_handler.register_command("safe_mode_change", self._handle_safe_mode_change)
        self.command_handler.register_command("level_change", self._handle_level_change)
        self.command_handler.register_command("terminate", self._handle_termination)
    
    def _handle_termination(self, message):
        """Handle termination signal."""
        if message.sender == "Seven":  # Only accept termination from Seven
            self.termination_signal_received = True
            self.running = False
            return Message(
                type="response",
                data={"status": "success", "message": "Termination signal received"}
            )
        return Message(
            type="response",
            data={"status": "error", "message": "Unauthorized termination attempt"}
        )

    def setup(self):
        """Set up IPC connections."""
        try:
            # Create IPC directory if it doesn't exist
            os.makedirs(os.path.dirname(IPC_ADDRESS), exist_ok=True)
            
            # Connect sockets
            self._connect_socket()
            
            # Start message listener thread
            self.running = True
            self.listener_thread = threading.Thread(target=self._message_listener)
            self.listener_thread.daemon = True
            self.listener_thread.start()
            
            # Wait for initialization
            self._wait_for_initialization()
            
            return True
        except Exception as e:
            self.error_handler.handle_error("setup", str(e))
            return False

    def _wait_for_initialization(self):
        """Wait for initialization to complete."""
        start_time = time.time()
        while not self.initialization_complete:
            if time.time() - start_time > self.initialization_timeout:
                raise TimeoutError("Initialization timeout")
            time.sleep(0.1)

    def _connect_socket(self):
        """Connect to IPC socket."""
        try:
            context = zmq.Context()
            
            # Create SUB socket for receiving messages
            self.sub_socket = context.socket(zmq.SUB)
            self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")
            self.sub_socket.connect(IPC_ADDRESS)
            
            # Create PUB socket for sending messages
            self.pub_socket = context.socket(zmq.PUB)
            # Only Seven should bind the PUB socket, others should connect
            if self.sister_name == "Seven":
                self.pub_socket.bind(IPC_ADDRESS)
            else:
                self.pub_socket.connect(IPC_ADDRESS)
            
            # Set socket options
            self.sub_socket.setsockopt(zmq.RCVTIMEO, 1000)  # 1 second timeout
            self.pub_socket.setsockopt(zmq.SNDTIMEO, 1000)  # 1 second timeout
            
            return True
        except Exception as e:
            self.error_handler.handle_error("socket_connection", str(e))
            return False

    def _message_listener(self):
        """Listen for incoming messages."""
        while self.running and not self.termination_signal_received:
            try:
                if self.sub_socket:
                    message = self.sub_socket.recv_json()
                    if message:
                        self.message_queue.put(message)
                        
                        # Handle initialization message
                        if message.get("type") == "status" and message.get("data", {}).get("status") == "ready":
                            self.initialization_complete = True
                        
                        # Handle termination message
                        if message.get("type") == "command" and message.get("data", {}).get("command") == "terminate":
                            self._handle_termination(Message(**message))
            except zmq.error.Again:
                continue
            except Exception as e:
                self.error_handler.handle_error("message_listener", str(e))
                time.sleep(1)

    def cleanup(self):
        """Clean up resources."""
        self.running = False
        if self.sub_socket:
            self.sub_socket.close()
        if self.pub_socket:
            self.pub_socket.close()
        if hasattr(self, 'listener_thread'):
            self.listener_thread.join(timeout=1)
        
        # Clean up status cache
        self.status_cache.clear()
        
        # Clean up message queue
        while not self.message_queue.empty():
            self.message_queue.get()
        
        # Clean up status manager
        self.status_manager.cleanup()
    
    def send_message(self, message: Message):
        """Send a message through the IPC system."""
        try:
            if not self.pub_socket or self.pub_socket.closed:
                logger.warning(f"{self.sister_name} pub socket is closed, attempting to reconnect before sending")
                self._connect_socket()
            
            self.pub_socket.send_string(message.to_json())
        except zmq.error.ZMQError as e:
            if e.errno == zmq.ECONNRESET or e.errno == zmq.ECONNREFUSED:
                logger.warning(f"{self.sister_name} connection reset or refused while sending: {e}")
                time.sleep(RETRY_DELAY)
                self._connect_socket()
                # Try one more time after reconnecting
                try:
                    self.pub_socket.send_string(message.to_json())
                except Exception as retry_e:
                    logger.error(f"Failed to send message after reconnection: {retry_e}")
            else:
                logger.error(f"ZMQ error sending message: {e}")
        except Exception as e:
            if not self.error_handler.handle_error('connection', e):
                logger.error(f"Failed to send message: {e}")
    
    def send_status(self, status: str):
        """Send a status update."""
        message = Message('status', self.sister_name, 'all', status)
        self.send_message(message)
    
    def send_command(self, target: str, command: str, args: Any = None):
        """Send a command to a specific sister or all sisters."""
        message = Message('command', self.sister_name, target, {
            'command': command,
            'args': args
        })
        self.send_message(message)
    
    def get_sister_status(self, sister_name: str) -> Optional[str]:
        """Get the cached status of a sister."""
        return self.status_cache.get(sister_name)
    
    def _handle_status_command(self, args: Dict):
        """Handle a status command."""
        # Implementation of _handle_status_command method
        pass
    
    def _handle_safe_mode_change(self, args: Dict):
        """Handle a safe mode change command."""
        # Implementation of _handle_safe_mode_change method
        pass
    
    def _handle_level_change(self, args: Dict):
        """Handle a level change command."""
        # Implementation of _handle_level_change method
        pass

    def _handle_status_command(self, args: Dict):
        """Handle a status command."""
        # Implementation of _handle_status_command method
        pass

    def _handle_safe_mode_change(self, args: Dict):
        """Handle a safe mode change command."""
        # Implementation of _handle_safe_mode_change method
        pass

    def _handle_level_change(self, args: Dict):
        """Handle a level change command."""
        # Implementation of _handle_level_change method
        pass

    def _handle_status_command(self, args: Dict):
        """Handle a status command."""
        # Implementation of _handle_status_command method
        pass

    def _handle_safe_mode_change(self, args: Dict):
        """Handle a safe mode change command."""
        # Implementation of _handle_safe_mode_change method
        pass

    def _handle_level_change(self, args: Dict):
        """Handle a level change command."""
        # Implementation of _handle_level_change method
        pass 