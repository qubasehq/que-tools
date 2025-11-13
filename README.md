# QUE CORE

QUE CORE is a hybrid Rust + Python runtime engine designed for AI agents to control computers. It provides 121 tools consolidated into 26 powerful functions for system control, automation, file management, networking, security, and more.

## Overview

QUE CORE serves as the foundational layer between AI agents and operating systems, enabling computer use agents to perceive system state and perform real actions. The hybrid architecture combines Rust's performance for system operations with Python's flexibility for orchestration and AI integration.

## Architecture

- **Rust Engine**: High-performance system integration (battery monitoring, process management, shell execution)
- **Python Layer**: Tool orchestration, API server, plugin system
- **FastAPI Server**: REST and WebSocket endpoints for AI agent communication
- **Cross-Platform**: Windows, macOS, Linux support

## Installation

### Python Package (Recommended)

```bash
pip install que-core
```

### With Optional Features

```bash
# AI/ML capabilities
pip install que-core[ai]

# Computer vision
pip install que-core[vision]

# Audio processing
pip install que-core[audio]

# Data science tools
pip install que-core[datascience]

# All features
pip install que-core[all]
```

### Rust Package

```bash
cargo add que_core
```

## Quick Start

### Command Line Usage

```bash
# Start the API server
que-server

# Run the main runtime
que-core
```

### Python API

```python
from que_core.tools.system_tools import system_query
from que_core.tools.automation_tools import interact

# Get system information
result = system_query(args={'what': 'overview'})
print(f"OS: {result['result']['os']}")
print(f"Memory: {result['result']['memory']['total_gb']}GB")

# Control mouse
interact(args={'action': 'move', 'x': 500, 'y': 300})
interact(args={'action': 'click', 'x': 500, 'y': 300})
```

### API Server

```python
from que_core.api.server import start_server

# Start server on localhost:8000
start_server()
```

## Tool Categories

QUE CORE consolidates 100+ individual tools into 26 powerful functions:

### System Tools (3 functions)
- `system_query`: Get system information, battery status, memory, CPU
- `system_control`: Volume control, screen lock, shutdown, restart
- `process_manager`: List, find, kill processes and applications

### File System (2 functions)
- `file_manager`: Create, read, write, delete, copy, move files
- `file_search`: Search files by name, content, metadata

### Automation (2 functions)
- `interact`: Mouse clicks, keyboard input, scrolling, hotkeys
- `automation_sequence`: Execute multi-step automation workflows

### Network & Web (3 functions)
- `network_tools`: Ping, HTTP requests, download files
- `web_browser`: Open URLs, web automation
- `auto_web_search`: Automated web searching

### Security (1 function)
- `security_manager`: File encryption, password generation, hashing

### Development (2 functions)
- `dev_assistant`: Git operations, Python scripts, testing, building
- `code_manager`: Code linting, formatting, analysis

### Data Processing (1 function)
- `data_processor`: CSV/JSON/Excel processing, plotting, analysis

### Documents (2 functions)
- `document_processor`: PDF extraction, document conversion
- `text_analyzer`: Sentiment analysis, spell checking, text statistics

### Audio & Media (2 functions)
- `audio_control`: Recording, playback, volume control
- `media_processor`: Audio transcription, text-to-speech

### Vision (1 function)
- `vision_system`: Camera capture, image processing, object detection

### Context Awareness (2 functions)
- `context_get`: Window info, cursor position, clipboard, screen state
- `context_capture`: Screenshots, screen recording, OCR

### App Control (2 functions)
- `app_manager`: Launch, close, switch applications
- `window_control`: Resize, move, manage windows

### Shell & Commands (2 functions)
- `shell_execute`: Run system commands, manage processes
- `environment_manager`: Environment variables, virtual environments

### System Settings (1 function)
- `settings_manager`: Wallpaper, themes, WiFi, Bluetooth, fonts

## API Reference

All tools follow a consistent interface:

```python
result = tool_function(args={
    'action': 'specific_action',
    'param1': 'value1',
    'param2': 'value2'
})

# Response format
{
    'success': True/False,
    'result': {...},  # Tool-specific data
    'error': None or "error message"
}
```

### HTTP API

```bash
# List all tools
GET /tools

# Call a tool
POST /call
{
    "tool_name": "system_query",
    "args": {"what": "battery"}
}
```

### WebSocket API

Connect to `ws://localhost:8000/ws` for real-time tool calling.

## Configuration

### Environment Variables

- `QUE_CORE_HOST`: API server host (default: 0.0.0.0)
- `QUE_CORE_PORT`: API server port (default: 8000)
- `QUE_CORE_LOG_LEVEL`: Logging level (default: INFO)

### Python Configuration

```python
from que_core.runtime.main import configure

configure({
    'api_host': '127.0.0.1',
    'api_port': 8080,
    'enable_rust': True,
    'log_level': 'DEBUG'
})
```

## Development

### Building from Source

```bash
# Clone repository
git clone https://github.com/qubasehq/que-tools
cd que-tools

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install development dependencies
pip install -e .[dev]

# Build Rust extension
maturin develop

# Run tests
pytest
```

### Project Structure

```
que-tools/
├── src/                    # Rust source code
│   ├── lib.rs             # Main Rust library
│   ├── system.rs          # System tools
│   ├── shell.rs           # Shell operations
│   └── network.rs         # Network operations
├── que_core/              # Python package
│   ├── tools/             # Tool implementations
│   ├── api/               # FastAPI server
│   └── runtime/           # Runtime engine
├── pyproject.toml         # Python package config
├── Cargo.toml             # Rust package config
└── README.md              # This file
```

## Platform Support

### Linux
- Full functionality
- Requires X11 or Wayland for UI automation
- Audio requires ALSA or PulseAudio

### macOS
- Full functionality
- Uses native macOS APIs
- Requires accessibility permissions for automation

### Windows
- Full functionality
- Uses Win32 APIs
- No additional permissions required

## Performance

- **Rust Engine**: Sub-millisecond system operations
- **Memory Usage**: ~50MB base footprint
- **API Latency**: <10ms for most operations
- **Concurrent Tools**: Supports parallel execution

## Security

- **Local-First**: All operations run locally by default
- **Sandboxed**: Tools operate within user permissions
- **Encrypted**: File encryption using industry-standard algorithms
- **Auditable**: All operations logged and traceable

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## Support

- Issues: https://github.com/qubasehq/que-tools/issues
- Discussions: https://github.com/qubasehq/que-tools/discussions
