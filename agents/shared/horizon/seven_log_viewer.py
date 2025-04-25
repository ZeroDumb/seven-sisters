import os
import sys
import subprocess
import threading
from typing import Optional

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from agents.shared.horizon.logger import logger

class SevenLogViewer:
    """
    A wrapper class that integrates the log viewer with Seven's interface.
    """
    
    def __init__(self):
        """Initialize the Seven log viewer."""
        self.viewer_process: Optional[subprocess.Popen] = None
        self.viewer_thread: Optional[threading.Thread] = None
    
    def start_viewer(self):
        """Start the log viewer in a separate process."""
        if self.viewer_process is not None:
            logger.warning("Log viewer is already running")
            return
        
        try:
            # Get the path to the log viewer script
            viewer_script = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "log_viewer.py"
            )
            
            # Start the viewer process
            self.viewer_process = subprocess.Popen(
                [sys.executable, viewer_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Start a thread to monitor the process
            self.viewer_thread = threading.Thread(
                target=self._monitor_viewer,
                daemon=True
            )
            self.viewer_thread.start()
            
            logger.info("Log viewer started successfully")
        
        except Exception as e:
            logger.error(f"Failed to start log viewer: {str(e)}")
            self.viewer_process = None
    
    def stop_viewer(self):
        """Stop the log viewer process."""
        if self.viewer_process is None:
            logger.warning("Log viewer is not running")
            return
        
        try:
            self.viewer_process.terminate()
            self.viewer_process.wait(timeout=5)
            self.viewer_process = None
            logger.info("Log viewer stopped successfully")
        
        except subprocess.TimeoutExpired:
            self.viewer_process.kill()
            self.viewer_process = None
            logger.warning("Log viewer was forcefully terminated")
        
        except Exception as e:
            logger.error(f"Error stopping log viewer: {str(e)}")
    
    def _monitor_viewer(self):
        """Monitor the log viewer process and handle its output."""
        if self.viewer_process is None:
            return
        
        try:
            # Read output until the process ends
            while True:
                output = self.viewer_process.stdout.readline()
                if output == b'' and self.viewer_process.poll() is not None:
                    break
                if output:
                    logger.debug(f"Log viewer: {output.decode().strip()}")
            
            # Check for any errors
            if self.viewer_process.returncode != 0:
                error = self.viewer_process.stderr.read().decode()
                logger.error(f"Log viewer exited with error: {error}")
            
            self.viewer_process = None
        
        except Exception as e:
            logger.error(f"Error monitoring log viewer: {str(e)}")
            self.viewer_process = None

def main():
    """Main entry point for the Seven log viewer."""
    viewer = SevenLogViewer()
    
    try:
        viewer.start_viewer()
        input("Press Enter to stop the log viewer...")
    
    except KeyboardInterrupt:
        pass
    
    finally:
        viewer.stop_viewer()

if __name__ == "__main__":
    main() 