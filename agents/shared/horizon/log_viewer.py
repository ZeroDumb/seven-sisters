import os
import sys
import time
import curses
import threading
import logging
from typing import List, Optional, Dict
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from agents.shared.horizon.logger import LogEntry, LogLevel, logger

class LogViewer:
    """
    A terminal-based log viewer with real-time updates and filtering capabilities.
    """
    
    def __init__(self):
        """Initialize the log viewer."""
        self.stdscr = None
        self.running = False
        self.filter_category = None
        self.filter_sister = None
        self.filter_level = None
        self.max_lines = 1000
        self.log_entries: List[LogEntry] = []
        self.scroll_position = 0
        self.window_height = 0
        self.window_width = 0
        self.status_message = ""
        self.status_timeout = 0
    
    def _setup_curses(self):
        """Set up the curses environment."""
        self.stdscr = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        
        # Initialize color pairs
        curses.init_pair(1, curses.COLOR_RED, -1)      # ERROR
        curses.init_pair(2, curses.COLOR_YELLOW, -1)   # WARNING
        curses.init_pair(3, curses.COLOR_GREEN, -1)    # INFO
        curses.init_pair(4, curses.COLOR_BLUE, -1)     # DEBUG
        curses.init_pair(5, curses.COLOR_MAGENTA, -1)  # SISTER
        curses.init_pair(6, curses.COLOR_CYAN, -1)     # ACTION
        
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
    
    def _cleanup_curses(self):
        """Clean up the curses environment."""
        if self.stdscr:
            curses.nocbreak()
            self.stdscr.keypad(False)
            curses.echo()
            curses.endwin()
    
    def _get_color_pair(self, level: int) -> int:
        """Get the color pair for a log level."""
        if level >= LogLevel.ERROR:
            return 1
        elif level >= LogLevel.WARNING:
            return 2
        elif level >= LogLevel.INFO:
            return 3
        elif level >= LogLevel.DEBUG:
            return 4
        elif level == LogLevel.SISTER:
            return 5
        elif level == LogLevel.ACTION:
            return 6
        return 0
    
    def _format_log_line(self, entry: LogEntry) -> str:
        """Format a log entry for display."""
        timestamp = datetime.fromtimestamp(entry.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        level_name = entry.level_name.ljust(8)
        sister = f"[{entry.sister}]".ljust(12)
        category = f"({entry.category})" if entry.category != "general" else ""
        return f"{timestamp} {level_name} {sister} {category} {entry.message}"
    
    def _draw_status_bar(self):
        """Draw the status bar with current filters and messages."""
        status = []
        if self.filter_category:
            status.append(f"Category: {self.filter_category}")
        if self.filter_sister:
            status.append(f"Sister: {self.filter_sister}")
        if self.filter_level:
            status.append(f"Level: {logging.getLevelName(self.filter_level)}")
        
        status_str = " | ".join(status) if status else "No filters"
        if self.status_message and time.time() < self.status_timeout:
            status_str = f"{status_str} | {self.status_message}"
        
        self.stdscr.addstr(self.window_height - 1, 0, status_str.ljust(self.window_width))
    
    def _draw_logs(self):
        """Draw the log entries in the main window."""
        self.stdscr.clear()
        
        # Calculate visible range
        start_idx = max(0, len(self.log_entries) - self.window_height + 1)
        visible_entries = self.log_entries[start_idx:]
        
        # Draw log entries
        for i, entry in enumerate(visible_entries):
            if i >= self.window_height - 1:  # Leave room for status bar
                break
            
            line = self._format_log_line(entry)
            color_pair = self._get_color_pair(entry.level)
            self.stdscr.addstr(i, 0, line[:self.window_width], curses.color_pair(color_pair))
        
        self._draw_status_bar()
        self.stdscr.refresh()
    
    def _handle_input(self):
        """Handle user input."""
        try:
            key = self.stdscr.getch()
            
            if key == ord('q'):
                self.running = False
            elif key == ord('h'):
                self._show_help_menu()
            elif key == ord('c'):
                self.filter_category = None
                self.filter_sister = None
                self.filter_level = None
                self._update_logs()
                self._show_status("Filters cleared", 2)
            elif key == ord('f'):
                self._show_filter_menu()
            elif key == ord('r'):
                self._refresh_logs()
                self._show_status("Logs refreshed", 2)
            elif key == ord(' '):
                self._refresh_logs()
            elif key == curses.KEY_UP:
                self.scroll_position = max(0, self.scroll_position - 1)
                self._draw_logs()
            elif key == curses.KEY_DOWN:
                self.scroll_position = min(len(self.log_entries) - 1, self.scroll_position + 1)
                self._draw_logs()
            elif key == curses.KEY_PPAGE:
                self.scroll_position = max(0, self.scroll_position - self.window_height)
                self._draw_logs()
            elif key == curses.KEY_NPAGE:
                self.scroll_position = min(len(self.log_entries) - 1, 
                                         self.scroll_position + self.window_height)
                self._draw_logs()
        except curses.error:
            pass
    
    def _show_filter_menu(self):
        """Show the filter menu."""
        self._cleanup_curses()
        print("\nFilter Menu:")
        print("1. Filter by category")
        print("2. Filter by sister")
        print("3. Filter by level")
        print("4. Clear all filters")
        print("5. Back")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == "1":
            category = input("Enter category (or press Enter to clear): ")
            self.filter_category = category if category else None
        elif choice == "2":
            sister = input("Enter sister name (or press Enter to clear): ")
            self.filter_sister = sister if sister else None
        elif choice == "3":
            print("\nLog Levels:")
            print("1. DEBUG")
            print("2. INFO")
            print("3. WARNING")
            print("4. ERROR")
            print("5. CRITICAL")
            print("6. SISTER")
            print("7. ACTION")
            print("8. Clear level filter")
            
            level_choice = input("\nEnter your choice (1-8): ")
            level_map = {
                "1": LogLevel.DEBUG,
                "2": LogLevel.INFO,
                "3": LogLevel.WARNING,
                "4": LogLevel.ERROR,
                "5": LogLevel.CRITICAL,
                "6": LogLevel.SISTER,
                "7": LogLevel.ACTION
            }
            self.filter_level = level_map.get(level_choice)
        elif choice == "4":
            self.filter_category = None
            self.filter_sister = None
            self.filter_level = None
        
        self._setup_curses()
        self._update_logs()
        self._show_status("Filters updated", 2)
    
    def _show_status(self, message: str, timeout: float = 2.0):
        """Show a status message."""
        self.status_message = message
        self.status_timeout = time.time() + timeout
        self._draw_logs()
    
    def _update_logs(self):
        """Update the log entries based on current filters."""
        self.log_entries = logger.get_recent_logs(
            category=self.filter_category,
            sister=self.filter_sister,
            level=self.filter_level,
            limit=self.max_lines
        )
        self._draw_logs()
    
    def _refresh_logs(self):
        """Refresh the log entries."""
        self._update_logs()
    
    def _log_listener(self, entry: LogEntry):
        """Handle new log entries."""
        # Apply filters
        if self.filter_category and entry.category != self.filter_category:
            return
        if self.filter_sister and entry.sister != self.filter_sister:
            return
        if self.filter_level and entry.level != self.filter_level:
            return
        
        # Add to log entries
        self.log_entries.append(entry)
        if len(self.log_entries) > self.max_lines:
            self.log_entries.pop(0)
        
        # Update display
        self._draw_logs()
    
    def _show_help_menu(self):
        """Show the help menu with command references."""
        self._cleanup_curses()
        print("\nSeven Sisters Log Viewer - Help Menu")
        print("===================================")
        print("\nNavigation:")
        print("  ⬆️ Up Arrow      - Scroll up")
        print("  ⬇️ Down Arrow    - Scroll down")
        print("  Page Up         - Fast scroll up")
        print("  Page Down       - Fast scroll down")
        print("  Home            - Jump to start")
        print("  End             - Jump to end")
        print("\nCommands:")
        print("  /               - Search logs")
        print("  f               - Filter menu")
        print("  s               - Show status")
        print("  h               - Show this help")
        print("  q               - Quit viewer")
        print("\nLog Levels:")
        print("  🔴 ERROR    (40) - Critical errors")
        print("  🟡 WARNING  (30) - Warning messages")
        print("  🟢 INFO     (20) - Information")
        print("  🔵 DEBUG    (10) - Debug messages")
        print("  🟣 SISTER   (25) - Sister-specific")
        print("  🔵 ACTION   (35) - Action-related")
        print("\nFilter Menu Options:")
        print("  1. Filter by category")
        print("  2. Filter by sister")
        print("  3. Filter by level")
        print("  4. Clear all filters")
        print("  5. Back")
        print("\nPress Enter to return to the viewer...")
        input()
        self._setup_curses()
        self._draw_logs()
    
    def run(self):
        """Run the log viewer."""
        try:
            self._setup_curses()
            self.running = True
            
            # Get initial window size
            self.window_height, self.window_width = self.stdscr.getmaxyx()
            
            # Add log listener
            logger.add_realtime_listener(self._log_listener)
            
            # Get initial logs
            self._update_logs()
            
            # Main loop
            while self.running:
                self._handle_input()
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            pass
        finally:
            logger.remove_realtime_listener(self._log_listener)
            self._cleanup_curses()

def main():
    """Main entry point for the log viewer."""
    viewer = LogViewer()
    viewer.run()

if __name__ == "__main__":
    main() 