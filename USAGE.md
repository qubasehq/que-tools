# QUE CORE Usage Guide

This guide provides comprehensive examples and usage patterns for QUE CORE tools.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [System Tools](#system-tools)
3. [File Operations](#file-operations)
4. [Automation](#automation)
5. [Network Operations](#network-operations)
6. [Security Operations](#security-operations)
7. [Development Tools](#development-tools)
8. [Data Processing](#data-processing)
9. [Document Processing](#document-processing)
10. [Audio & Media](#audio--media)
11. [Computer Vision](#computer-vision)
12. [Context Awareness](#context-awareness)
13. [Application Control](#application-control)
14. [Shell Operations](#shell-operations)
15. [System Settings](#system-settings)
16. [API Server Usage](#api-server-usage)
17. [Error Handling](#error-handling)

## Basic Usage

All QUE CORE tools follow a consistent interface pattern:

```python
from que_core.tools.module_name import tool_function

result = tool_function(args={
    'action': 'specific_action',
    'parameter1': 'value1',
    'parameter2': 'value2'
})

if result['success']:
    print("Operation successful:", result['result'])
else:
    print("Operation failed:", result['error'])
```

## System Tools

### Get System Information

```python
from que_core.tools.system_tools import system_query

# Get system overview
result = system_query(args={'what': 'overview'})
print(f"OS: {result['result']['os']}")
print(f"CPU Cores: {result['result']['cpu_count']}")
print(f"Memory: {result['result']['memory']['total_gb']}GB")

# Get battery status
result = system_query(args={'what': 'battery'})
if result['result']['has_battery']:
    print(f"Battery: {result['result']['primary_level']}%")
    print(f"Status: {result['result']['primary_status']}")

# Get memory details
result = system_query(args={'what': 'memory'})
print(f"Used: {result['result']['used_percent']}%")
print(f"Available: {result['result']['available_gb']}GB")

# Get CPU information
result = system_query(args={'what': 'cpu'})
print(f"CPU Usage: {result['result']['usage_percent']}%")
```

### System Control

```python
from que_core.tools.system_tools import system_control

# Set volume
system_control(args={'action': 'volume', 'level': 50})

# Lock screen
system_control(args={'action': 'lock'})

# Shutdown (requires confirmation)
system_control(args={'action': 'shutdown', 'confirm': True})
```

### Process Management

```python
from que_core.tools.system_tools import process_manager

# List all processes
result = process_manager(args={'action': 'list'})
for process in result['result']['processes'][:5]:
    print(f"{process['name']}: {process['memory_mb']}MB")

# Find processes by name
result = process_manager(args={'action': 'find', 'name': 'python'})

# Kill process by PID
process_manager(args={'action': 'kill', 'pid': 1234})

# List GUI applications
result = process_manager(args={'action': 'apps'})
```

## File Operations

### File Management

```python
from que_core.tools.file_tools import file_manager

# Create a file
file_manager(args={
    'action': 'create',
    'path': '/tmp/test.txt',
    'content': 'Hello World'
})

# Read file
result = file_manager(args={'action': 'read', 'path': '/tmp/test.txt'})
print(result['result']['content'])

# Copy file
file_manager(args={
    'action': 'copy',
    'source': '/tmp/test.txt',
    'destination': '/tmp/test_copy.txt'
})

# Move file
file_manager(args={
    'action': 'move',
    'source': '/tmp/test_copy.txt',
    'destination': '/tmp/moved.txt'
})

# Delete file
file_manager(args={'action': 'delete', 'path': '/tmp/moved.txt'})

# Get file info
result = file_manager(args={'action': 'info', 'path': '/tmp/test.txt'})
print(f"Size: {result['result']['size']} bytes")
print(f"Modified: {result['result']['modified']}")
```

### File Search

```python
from que_core.tools.file_tools import file_search

# Search by name
result = file_search(args={
    'action': 'name',
    'directory': '/home/user',
    'pattern': '*.py'
})

# Search by content
result = file_search(args={
    'action': 'content',
    'directory': '/home/user/projects',
    'query': 'def main'
})

# Search by size
result = file_search(args={
    'action': 'size',
    'directory': '/tmp',
    'min_size': 1000000  # 1MB
})
```

## Automation

### Mouse and Keyboard Control

```python
from que_core.tools.automation_tools import interact

# Move mouse
interact(args={'action': 'move', 'x': 500, 'y': 300})

# Click
interact(args={'action': 'click', 'x': 500, 'y': 300})

# Right click
interact(args={'action': 'right_click', 'x': 500, 'y': 300})

# Double click
interact(args={'action': 'double_click', 'x': 500, 'y': 300})

# Type text
interact(args={'action': 'type', 'text': 'Hello World'})

# Press hotkey
interact(args={'action': 'hotkey', 'keys': 'ctrl+c'})

# Scroll
interact(args={'action': 'scroll', 'x': 500, 'y': 300, 'direction': 'up', 'clicks': 3})

# Drag
interact(args={
    'action': 'drag',
    'start_x': 100, 'start_y': 100,
    'end_x': 200, 'end_y': 200
})
```

### Automation Sequences

```python
from que_core.tools.automation_tools import automation_sequence

# Execute sequence of actions
steps = [
    {'action': 'move', 'x': 100, 'y': 100},
    {'action': 'click', 'x': 100, 'y': 100},
    {'action': 'type', 'text': 'Hello'},
    {'action': 'key', 'key': 'enter'}
]

automation_sequence(args={'action': 'execute', 'steps': steps})

# Record macro
automation_sequence(args={'action': 'record', 'name': 'my_macro'})
# ... perform actions ...
automation_sequence(args={'action': 'stop_record'})

# Play macro
automation_sequence(args={'action': 'play', 'name': 'my_macro'})
```

## Network Operations

### Network Tools

```python
from que_core.tools.network_tools import network_tools

# Ping host
result = network_tools(args={'action': 'ping', 'host': 'google.com'})
print(f"Ping time: {result['result']['avg_time']}ms")

# HTTP request
result = network_tools(args={
    'action': 'http',
    'url': 'https://api.github.com/users/octocat',
    'method': 'GET'
})

# Download file
network_tools(args={
    'action': 'download',
    'url': 'https://example.com/file.zip',
    'path': '/tmp/downloaded.zip'
})

# Check internet connectivity
result = network_tools(args={'action': 'check_internet'})
print(f"Connected: {result['result']['connected']}")
```

### Web Browser Control

```python
from que_core.tools.network_tools import web_browser

# Open URL
web_browser(args={'action': 'open', 'url': 'https://github.com'})

# Navigate
web_browser(args={'action': 'navigate', 'url': 'https://google.com'})

# Get page title
result = web_browser(args={'action': 'title'})
print(result['result']['title'])

# Take screenshot
web_browser(args={'action': 'screenshot', 'path': '/tmp/page.png'})
```

## Security Operations

```python
from que_core.tools.security_tools import security_manager

# Generate password
result = security_manager(args={
    'action': 'generate_password',
    'length': 16,
    'complexity': 'complex'
})
print(f"Password: {result['result']['passwords'][0]}")

# Hash text
result = security_manager(args={
    'action': 'hash',
    'text': 'Hello World',
    'algorithm': 'sha256'
})
print(f"Hash: {result['result']['hash']}")

# Encrypt file
security_manager(args={
    'action': 'encrypt',
    'file': '/tmp/secret.txt',
    'password': 'mypassword'
})

# Decrypt file
security_manager(args={
    'action': 'decrypt',
    'file': '/tmp/secret.txt.encrypted',
    'password': 'mypassword'
})

# Clear temp files
result = security_manager(args={'action': 'clear_temp'})
print(f"Cleaned {result['result']['files_deleted']} files")
```

## Development Tools

### Development Assistant

```python
from que_core.tools.dev_tools import dev_assistant

# Git status
result = dev_assistant(args={'action': 'git_status'})
print(f"Modified files: {len(result['result']['files']['modified'])}")

# Run Python script
result = dev_assistant(args={
    'action': 'run_python',
    'script': 'test.py',
    'args': ['--verbose']
})

# Run tests
result = dev_assistant(args={
    'action': 'run_tests',
    'framework': 'pytest'
})
print(f"Tests passed: {result['result']['passed']}")

# Build project
dev_assistant(args={'action': 'build', 'project_type': 'rust'})
```

### Code Management

```python
from que_core.tools.dev_tools import code_manager

# Lint code
result = code_manager(args={
    'action': 'lint',
    'language': 'python',
    'path': 'src/'
})

# Format code
code_manager(args={
    'action': 'format',
    'language': 'python',
    'path': 'main.py'
})

# Analyze code
result = code_manager(args={'action': 'analyze', 'path': 'project/'})
print(f"Files: {result['result']['analysis']['files']}")
print(f"Lines: {result['result']['analysis']['lines']}")
```

## Data Processing

```python
from que_core.tools.data_tools import data_processor

# Load CSV
result = data_processor(args={'action': 'load', 'file': 'data.csv'})
print(f"Loaded {result['result']['rows']} rows")

# Describe data
result = data_processor(args={'action': 'describe', 'file': 'data.csv'})

# Plot chart
data_processor(args={
    'action': 'plot',
    'file': 'data.csv',
    'plot_type': 'bar',
    'x_column': 'name',
    'y_column': 'value',
    'output_path': 'chart.png'
})

# Export data
data_processor(args={
    'action': 'export',
    'file': 'data.csv',
    'format': 'json',
    'output_path': 'data.json'
})
```

## Document Processing

### Document Processor

```python
from que_core.tools.document_tools import document_processor

# Extract text from PDF
result = document_processor(args={
    'action': 'extract_pdf',
    'file': 'document.pdf'
})
print(result['result']['text'][:200])

# Summarize text
result = document_processor(args={
    'action': 'summarize',
    'text': 'Long text to summarize...',
    'max_sentences': 3
})
print(result['result']['summary'])

# Convert document
document_processor(args={
    'action': 'convert',
    'file': 'document.pdf',
    'output_format': 'txt'
})
```

### Text Analyzer

```python
from que_core.tools.document_tools import text_analyzer

# Analyze sentiment
result = text_analyzer(args={
    'action': 'sentiment',
    'text': 'I love this product!'
})
print(f"Sentiment: {result['result']['sentiment']}")

# Get text statistics
result = text_analyzer(args={
    'action': 'stats',
    'text': 'Sample text for analysis'
})
print(f"Words: {result['result']['word_count']}")
print(f"Reading time: {result['result']['reading_time_minutes']} min")

# Extract keywords
result = text_analyzer(args={
    'action': 'extract_keywords',
    'text': 'Text with important keywords',
    'max_keywords': 5
})
```

## Audio & Media

### Audio Control

```python
from que_core.tools.audio_tools import audio_control

# Record audio
audio_control(args={
    'action': 'record',
    'duration': 5,
    'output_path': 'recording.wav'
})

# Play audio
audio_control(args={'action': 'play', 'file': 'recording.wav'})

# Set volume
audio_control(args={'action': 'set_volume', 'volume': 75})

# Get volume
result = audio_control(args={'action': 'get_volume'})
print(f"Volume: {result['result']['volume']}%")

# List audio devices
result = audio_control(args={'action': 'list_devices'})
```

### Media Processor

```python
from que_core.tools.audio_tools import media_processor

# Text to speech
media_processor(args={
    'action': 'speak',
    'text': 'Hello World',
    'output_path': 'speech.wav'
})

# Transcribe audio
result = media_processor(args={
    'action': 'transcribe',
    'file': 'recording.wav'
})
print(result['result']['text'])
```

## Computer Vision

```python
from que_core.tools.vision_tools import vision_system

# Capture image
vision_system(args={
    'action': 'capture',
    'output_path': 'photo.jpg'
})

# Start camera stream
vision_system(args={'action': 'start_stream'})

# Detect faces
result = vision_system(args={
    'action': 'detect_faces',
    'image_path': 'photo.jpg'
})
print(f"Found {len(result['result']['faces'])} faces")

# Analyze scene
result = vision_system(args={
    'action': 'analyze_scene',
    'image_path': 'photo.jpg'
})
```

## Context Awareness

### Context Get

```python
from que_core.tools.context_tools import context_get

# Get window info
result = context_get(args={'what': 'window'})
print(f"Active window: {result['result']['title']}")

# Get cursor position
result = context_get(args={'what': 'cursor'})
print(f"Cursor at: ({result['result']['x']}, {result['result']['y']})")

# Get clipboard
result = context_get(args={'what': 'clipboard'})
print(f"Clipboard: {result['result']['text']}")

# Get display info
result = context_get(args={'what': 'display'})
print(f"Resolution: {result['result']['width']}x{result['result']['height']}")
```

### Context Capture

```python
from que_core.tools.context_tools import context_capture

# Take screenshot
context_capture(args={
    'action': 'screenshot',
    'output_path': 'screen.png'
})

# Screen OCR
result = context_capture(args={
    'action': 'ocr',
    'image_path': 'screen.png'
})
print(result['result']['text'])
```

## Application Control

### App Manager

```python
from que_core.tools.app_tools import app_manager

# Launch application
app_manager(args={'action': 'launch', 'app': 'firefox'})

# List running apps
result = app_manager(args={'action': 'list'})
for app in result['result']['apps']:
    print(f"{app['name']}: PID {app['pid']}")

# Close application
app_manager(args={'action': 'close', 'app': 'firefox'})

# Switch to app
app_manager(args={'action': 'switch', 'app': 'terminal'})
```

### Window Control

```python
from que_core.tools.app_tools import window_control

# Get active window
result = window_control(args={'action': 'get_active'})
print(f"Active: {result['result']['title']}")

# Resize window
window_control(args={
    'action': 'resize',
    'width': 800,
    'height': 600
})

# Move window
window_control(args={'action': 'move', 'x': 100, 'y': 100})

# Minimize window
window_control(args={'action': 'minimize'})

# Maximize window
window_control(args={'action': 'maximize'})
```

## Shell Operations

### Shell Execute

```python
from que_core.tools.shell_tools import shell_execute

# Run command
result = shell_execute(args={'command': 'ls -la'})
print(result['result']['stdout'])

# Run with timeout
result = shell_execute(args={
    'command': 'ping -c 3 google.com',
    'timeout': 10
})

# Run in specific directory
result = shell_execute(args={
    'command': 'pwd',
    'cwd': '/tmp'
})
```

### Environment Manager

```python
from que_core.tools.shell_tools import environment_manager

# Get environment variables
result = environment_manager(args={'action': 'get_vars'})
print(result['result']['PATH'])

# Set environment variable
environment_manager(args={
    'action': 'set_var',
    'name': 'MY_VAR',
    'value': 'test_value'
})

# Create virtual environment
environment_manager(args={
    'action': 'create_venv',
    'path': '/tmp/myenv'
})
```

## System Settings

```python
from que_core.tools.settings_tools import settings_manager

# Change wallpaper
settings_manager(args={
    'action': 'wallpaper',
    'path': '/path/to/image.jpg'
})

# Set theme
settings_manager(args={'action': 'theme', 'mode': 'dark'})

# Get installed fonts
result = settings_manager(args={'action': 'fonts'})
print(f"Found {result['result']['font_count']} fonts")

# WiFi status
result = settings_manager(args={
    'action': 'wifi',
    'operation': 'status'
})

# Bluetooth status
result = settings_manager(args={
    'action': 'bluetooth',
    'operation': 'status'
})
```

## API Server Usage

### Starting the Server

```python
from que_core.api.server import start_server

# Start with default settings
start_server()

# Start with custom settings
start_server(host='127.0.0.1', port=8080)
```

### HTTP API Examples

```bash
# List all tools
curl http://localhost:8000/tools

# Call a tool
curl -X POST http://localhost:8000/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "system_query",
    "args": {"what": "battery"}
  }'

# Get consolidated tools only
curl http://localhost:8000/tools/consolidated
```

### WebSocket Usage

```python
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # Send tool request
        request = {
            "tool_name": "system_query",
            "args": {"what": "overview"}
        }
        await websocket.send(json.dumps(request))
        
        # Receive response
        response = await websocket.recv()
        result = json.loads(response)
        print(result)

asyncio.run(test_websocket())
```

## Error Handling

### Standard Error Handling

```python
from que_core.tools.system_tools import system_query

result = system_query(args={'what': 'battery'})

if result['success']:
    # Operation succeeded
    data = result['result']
    print(f"Battery level: {data['primary_level']}%")
else:
    # Operation failed
    error = result['error']
    print(f"Error: {error}")
```

### Exception Handling

```python
try:
    result = system_query(args={'what': 'invalid'})
    if not result['success']:
        raise Exception(result['error'])
except Exception as e:
    print(f"Tool execution failed: {e}")
```

### Validation

```python
def safe_tool_call(tool_func, args):
    """Safely call a tool with validation"""
    if not isinstance(args, dict):
        return {'success': False, 'error': 'Args must be a dictionary'}
    
    try:
        result = tool_func(args=args)
        return result
    except Exception as e:
        return {'success': False, 'error': str(e)}

# Usage
result = safe_tool_call(system_query, {'what': 'battery'})
```

## Best Practices

1. **Always check success status** before using results
2. **Handle errors gracefully** with appropriate fallbacks
3. **Use appropriate timeouts** for long-running operations
4. **Validate inputs** before passing to tools
5. **Log operations** for debugging and auditing
6. **Use consolidated tools** for better performance
7. **Batch operations** when possible to reduce overhead
8. **Clean up resources** (files, processes) after use

## Performance Tips

1. **Use Rust-backed tools** when available for better performance
2. **Avoid frequent small operations** - batch when possible
3. **Cache results** for expensive operations
4. **Use async patterns** for concurrent operations
5. **Monitor memory usage** for large data operations
6. **Set appropriate timeouts** to prevent hanging
7. **Use streaming** for large file operations
