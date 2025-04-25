import os
import signal
import time
import socket
import psutil
import zmq
import logging
import shutil
import sys

# Configure logging with a handler that can handle Unicode
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('mischief_managed')

# Add a handler that can handle Unicode characters
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Use a cross-platform compatible temp dir
PID_DIR = os.path.join(os.path.expanduser("~"), ".7sisters", "pids")
IPC_PORT = 5555
IPC_ADDRESS = f"tcp://127.0.0.1:{IPC_PORT}"

SISTER_FAREWELLS = {
    "Seven": "🧠 Seven: Disengaging uplink. Goodbye, meatbags.",
    "Harley": "🎉 Harley: Boo! Fine, I'll go... but I'm taking the glitter.",
    "Alice": "🐇 Alice: Back to the tea party I go.",
    "Marla": "☁️ Marla: It's only after we've lost everything that we're free.",
    "Luna": "🌙 Luna: Farewell... unless you're a wrackspurt.",
    "Lisbeth": "🕶️ Lisbeth: Logs purged. Shadow restored.",
    "Bride": "⚔️ Bride: Vengeance paused. Blade sheathed."
}

def cleanup_sockets():
    """Clean up any lingering ZMQ sockets."""
    try:
        logger.info("Cleaning up ZMQ sockets...")
        context = zmq.Context()
        
        # Try to connect to the socket to see if it's in use
        try:
            socket = context.socket(zmq.PUB)
            socket.setsockopt(zmq.LINGER, 0)
            socket.connect(IPC_ADDRESS)
            socket.close()
            logger.info("ZMQ socket was in use, now cleaned up")
        except Exception as e:
            logger.info(f"ZMQ socket not in use or already cleaned up: {e}")
        
        # Terminate the context
        context.term()
        logger.info("ZMQ context terminated")
    except Exception as e:
        logger.error(f"Error cleaning up ZMQ sockets: {e}")

def kill_process_on_port(port):
    """Kill any process using the specified port."""
    try:
        # Use a more compatible approach to find processes using the port
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # Check if the process has any network connections
                connections = proc.connections()
                for conn in connections:
                    if hasattr(conn, 'laddr') and conn.laddr.port == port:
                        logger.info(f"Killing process {proc.pid} using port {port}")
                        os.kill(proc.pid, signal.SIGTERM)
                        time.sleep(0.5)  # Give it time to terminate
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, AttributeError):
                # Skip processes we can't access or that don't have the expected attributes
                pass
    except Exception as e:
        logger.error(f"Error killing process on port {port}: {e}")

def cleanup_temp_files():
    """Clean up any temporary files created by the sisters."""
    try:
        logger.info("Cleaning up temporary files...")
        sisters_dir = os.path.join(os.path.expanduser("~"), ".7sisters")
        
        if os.path.exists(sisters_dir):
            # Remove PID files
            if os.path.exists(PID_DIR):
                shutil.rmtree(PID_DIR)
                logger.info(f"Removed PID directory: {PID_DIR}")
            
            # Remove any other temporary files
            for root, dirs, files in os.walk(sisters_dir):
                for file in files:
                    if file.endswith(".tmp") or file.endswith(".log"):
                        try:
                            os.remove(os.path.join(root, file))
                            logger.info(f"Removed temporary file: {file}")
                        except Exception as e:
                            logger.warning(f"Could not remove file {file}: {e}")
    except Exception as e:
        logger.error(f"Error cleaning up temporary files: {e}")

def close_sister_terminals():
    """Close all sister terminals except for Seven's."""
    try:
        logger.info("Closing sister terminals...")
        
        # Get all running processes
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Check if this is a sister process
                cmdline = proc.info.get('cmdline', [])
                if not cmdline:
                    continue
                
                # Convert cmdline to string for easier checking
                cmdline_str = ' '.join(cmdline).lower()
                
                # Check if this is a sister process (but not Seven)
                if 'python' in cmdline_str and any(sister.lower() in cmdline_str for sister in ['alice', 'luna', 'harley', 'marla', 'lisbeth', 'bride']):
                    # This is a sister process, close its terminal
                    logger.info(f"Closing terminal for process: {proc.info['name']} (PID: {proc.info['pid']})")
                    
                    # On Windows, we need to find the parent process (the terminal)
                    if os.name == 'nt':
                        parent = psutil.Process(proc.info['pid']).parent()
                        if parent:
                            # Send a close signal to the parent (terminal)
                            parent.terminate()
                    else:
                        # On Unix-like systems, we can send a SIGTERM to the process
                        os.kill(proc.info['pid'], signal.SIGTERM)
                    
                    time.sleep(0.2)  # Give it time to close
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Skip processes we can't access
                pass
    except Exception as e:
        logger.error(f"Error closing sister terminals: {e}")

def shutdown_sisters():
    """Shutdown all sisters and clean up resources."""
    print("Mischief Managed: Shutting down the Sisterhood...")
    logger.info("Shutting down the Sisterhood...")
    
    # First, kill any processes using our IPC port
    kill_process_on_port(IPC_PORT)
    
    # Clean up ZMQ sockets
    cleanup_sockets()
    
    # Now shut down the sisters
    if not os.path.exists(PID_DIR):
        logger.info("No sisters summoned. The room is empty.")
        return

    for pid_file in os.listdir(PID_DIR):
        if not pid_file.endswith(".pid"):
            continue

        sister = pid_file.replace(".pid", "")
        pid_path = os.path.join(PID_DIR, pid_file)

        try:
            with open(pid_path, "r") as f:
                pid = int(f.read().strip())
            
            # Try SIGTERM first (graceful shutdown)
            try:
                os.kill(pid, signal.SIGTERM)
                logger.info(f"Sent SIGTERM to {sister} (PID: {pid})")
                time.sleep(1)  # Give it time to shut down gracefully
                
                # Check if process is still running
                try:
                    os.kill(pid, 0)
                    # If we get here, process is still running, use SIGKILL
                    logger.info(f"Process still running, sending SIGKILL to {sister}")
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    # Process is already gone
                    pass
            except ProcessLookupError:
                # Process already terminated
                pass
                
            print(SISTER_FAREWELLS.get(sister, f"{sister} vanished into the mist..."))
            os.remove(pid_path)
            time.sleep(0.3)

        except Exception as e:
            logger.error(f"Couldn't shut down {sister}: {e}")
    
    # Close sister terminals
    close_sister_terminals()
    
    # Final cleanup
    cleanup_temp_files()
    logger.info("Shutdown complete. All sisters have been dismissed.")

if __name__ == "__main__":
    shutdown_sisters()
