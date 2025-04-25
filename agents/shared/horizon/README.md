# Seven Sisters Log Viewer

A real-time, interactive log viewer for the Seven Sisters system.

## Features

- Real-time log updates
- Color-coded log levels
- Filtering capabilities
- Interactive navigation
- Status bar with current filters

## Log Levels

- 🔴 ERROR (40)
- 🟡 WARNING (30)
- 🟢 INFO (20)
- 🔵 DEBUG (10)
- 🟣 SISTER (25)
- 🔵 ACTION (35)

## Commands

### Interface Commands

From Seven's interface, you can control the log viewer using these commands:

```python
# Start the log viewer
message = Message(
    type="command",
    data={
        "command": "logs",
        "action": "start"
    }
)

# Stop the log viewer
message = Message(
    type="command",
    data={
        "command": "logs",
        "action": "stop"
    }
)
```

### Viewer Controls

While the log viewer is running, use these keyboard controls:

- ⬆️ Up Arrow: Scroll up
- ⬇️ Down Arrow: Scroll down
- Page Up: Fast scroll up
- Page Down: Fast scroll down
- Home: Jump to start
- End: Jump to end
- /: Search logs
- f: Filter menu
- s: Show status
- q: Quit viewer

### Filter Menu Options

When pressing 'f' in the viewer:

1. Filter by category
2. Filter by sister
3. Filter by level
4. Clear all filters
5. Back

## Integration

The log viewer is integrated with Seven's interface through the `SevenLogViewer` class. It runs in a separate process to avoid interfering with the main interface.

## Log Categories

- general: General system logs
- sister: Sister-specific logs
- action: Action-related logs
- system: System operation logs
- error: Error and warning logs

## Status Bar

The status bar at the bottom of the viewer shows:
- Current filters
- Status messages
- Viewer state

## Error Handling

The viewer includes comprehensive error handling:
- Process monitoring
- Graceful shutdown
- Error reporting
- Automatic cleanup 