"""
Context Tools - Consolidated context awareness and screen capture for AI agents
Provides unified context information and capture capabilities.
"""
from typing import Any, Dict, List
import base64
import io
import json
import os
import tempfile
import platform
import subprocess
import time

# Try to import Rust engine for high-performance context operations
try:
    from que_core_engine import rust_context_get, rust_context_capture
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False

def context_get(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Universal context information getter - replaces get_active_window_title, get_cursor_position, get_clipboard_text, detect_idle_state, get_display_info, screen_ocr
    
    Args:
        what (str): Type of context to get - 'window', 'cursor', 'clipboard', 'idle', 'display', 'screen_text', 'all'
        include_screenshot (bool): Include screenshot with context (optional)
        
    Returns:
        Dict with requested context information
    """
    if not args:
        args = {}
    
    what = args.get("what", "window")
    
    # Try Rust implementation first for performance
    if RUST_AVAILABLE:
        try:
            result_json = rust_context_get(what)
            return json.loads(result_json)
        except Exception:
            # Fall back to Python implementation
            pass
    
    # Python fallback implementation
    try:
        if what == "window":
            return _get_active_window_impl(args)
        elif what == "cursor":
            return _get_cursor_position_impl(args)
        elif what == "clipboard":
            return _get_clipboard_impl(args)
        elif what == "idle":
            return _detect_idle_state_impl(args)
        elif what == "display":
            return _get_display_info_impl(args)
        elif what == "screen_text":
            return _screen_ocr_impl(args)
        elif what == "all":
            return _get_all_context_impl(args)
        else:
            return {
                "success": False,
                "result": None,
                "error": f"Unknown context type: {what}. Use: window, cursor, clipboard, idle, display, screen_text, all"
            }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Context operation failed: {str(e)}"}

def context_capture(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Universal context capture - replaces take_screenshot, take_window_screenshot, capture_camera_image, record_audio
    
    Args:
        type (str): Type of capture - 'screenshot', 'window_screenshot', 'camera', 'audio'
        output_path (str): Output file path (optional)
        duration (int): Duration for audio recording (optional)
        window_title (str): Window title for window screenshot (optional)
        camera_index (int): Camera index for camera capture (optional)
        
    Returns:
        Dict with capture result
    """
    if not args or "type" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: type"}
    
    capture_type = args["type"]
    
    # Try Rust implementation first for performance
    if RUST_AVAILABLE:
        try:
            output_path = args.get("output_path", "")
            duration = args.get("duration", 0)
            window_title = args.get("window_title", "")
            camera_index = args.get("camera_index", 0)
            
            result_json = rust_context_capture(capture_type, output_path, duration, window_title, camera_index)
            return json.loads(result_json)
        except Exception:
            # Fall back to Python implementation
            pass
    
    # Python fallback implementation
    try:
        if capture_type == "screenshot":
            return _take_screenshot_impl(args)
        elif capture_type == "window_screenshot":
            return _take_window_screenshot_impl(args)
        elif capture_type == "camera":
            return _capture_camera_impl(args)
        elif capture_type == "audio":
            return _record_audio_impl(args)
        else:
            return {
                "success": False,
                "result": None,
                "error": f"Unknown capture type: {capture_type}. Use: screenshot, window_screenshot, camera, audio"
            }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Capture operation failed: {str(e)}"}

# Context Get Implementation Helpers
def _get_active_window_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get active window information implementation"""
    try:
        system = platform.system()
        
        if system == "Linux":
            # Try multiple methods for Linux
            methods = [
                # xdotool method
                ["xdotool", "getactivewindow", "getwindowname"],
                # wmctrl method
                ["wmctrl", "-a", ":ACTIVE:"],
                # xprop method
                ["xprop", "-id", "$(xdotool getactivewindow)", "WM_NAME"]
            ]
            
            for method in methods:
                try:
                    if method[0] == "wmctrl":
                        result = subprocess.run(["wmctrl", "-l"], capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            # Parse wmctrl output to find active window
                            lines = result.stdout.strip().split('\n')
                            if lines:
                                # Get first window as approximation
                                parts = lines[0].split(None, 3)
                                if len(parts) >= 4:
                                    window_title = parts[3]
                                    return {
                                        "success": True,
                                        "result": {
                                            "title": window_title,
                                            "method": "wmctrl",
                                            "platform": system
                                        },
                                        "error": None
                                    }
                    else:
                        result = subprocess.run(method, capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            title = result.stdout.strip()
                            if title:
                                return {
                                    "success": True,
                                    "result": {
                                        "title": title,
                                        "method": method[0],
                                        "platform": system
                                    },
                                    "error": None
                                }
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            
            return {"success": False, "result": None, "error": "No window manager tools found (install xdotool, wmctrl, or xprop)"}
        
        elif system == "Darwin":  # macOS
            # Use AppleScript
            script = 'tell application "System Events" to get name of first application process whose frontmost is true'
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                title = result.stdout.strip()
                return {
                    "success": True,
                    "result": {
                        "title": title,
                        "method": "applescript",
                        "platform": system
                    },
                    "error": None
                }
            else:
                return {"success": False, "result": None, "error": f"AppleScript failed: {result.stderr}"}
        
        elif system == "Windows":
            # Use PowerShell
            ps_script = """
            Add-Type @"
                using System;
                using System.Runtime.InteropServices;
                using System.Text;
                public class Win32 {
                    [DllImport("user32.dll")]
                    public static extern IntPtr GetForegroundWindow();
                    [DllImport("user32.dll")]
                    public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
                }
"@
            $hwnd = [Win32]::GetForegroundWindow()
            $title = New-Object System.Text.StringBuilder 256
            [Win32]::GetWindowText($hwnd, $title, 256)
            $title.ToString()
            """
            result = subprocess.run(["powershell", "-c", ps_script], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                title = result.stdout.strip()
                return {
                    "success": True,
                    "result": {
                        "title": title,
                        "method": "win32api",
                        "platform": system
                    },
                    "error": None
                }
            else:
                return {"success": False, "result": None, "error": f"Windows API failed: {result.stderr}"}
        
        else:
            return {"success": False, "result": None, "error": f"Unsupported platform: {system}"}
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to get active window: {str(e)}"}

def _get_cursor_position_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get cursor position implementation"""
    try:
        import pyautogui
        
        x, y = pyautogui.position()
        screen_width, screen_height = pyautogui.size()
        
        return {
            "success": True,
            "result": {
                "x": x,
                "y": y,
                "screen_width": screen_width,
                "screen_height": screen_height,
                "method": "pyautogui"
            },
            "error": None
        }
    
    except ImportError:
        return {"success": False, "result": None, "error": "Cursor position requires pyautogui (pip install pyautogui)"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to get cursor position: {str(e)}"}

def _get_clipboard_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get clipboard content implementation"""
    try:
        import pyperclip
        
        content = pyperclip.paste()
        content_type = "text"
        
        # Try to detect content type
        if content.startswith("http://") or content.startswith("https://"):
            content_type = "url"
        elif content.startswith("/") or (len(content) > 3 and content[1] == ":"):
            content_type = "path"
        elif content.isdigit():
            content_type = "number"
        
        return {
            "success": True,
            "result": {
                "content": content,
                "length": len(content),
                "type": content_type,
                "method": "pyperclip"
            },
            "error": None
        }
    
    except ImportError:
        return {"success": False, "result": None, "error": "Clipboard access requires pyperclip (pip install pyperclip)"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to get clipboard: {str(e)}"}

def _detect_idle_state_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Detect system idle state implementation"""
    try:
        system = platform.system()
        
        if system == "Linux":
            # Use xprintidle
            try:
                result = subprocess.run(["xprintidle"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    idle_ms = int(result.stdout.strip())
                    idle_seconds = idle_ms / 1000
                    
                    return {
                        "success": True,
                        "result": {
                            "idle_seconds": idle_seconds,
                            "idle_minutes": idle_seconds / 60,
                            "is_idle": idle_seconds > 300,  # 5 minutes
                            "method": "xprintidle"
                        },
                        "error": None
                    }
            except FileNotFoundError:
                pass
            
            return {"success": False, "result": None, "error": "Idle detection requires xprintidle (apt install xprintidle)"}
        
        elif system == "Darwin":  # macOS
            # Use ioreg
            result = subprocess.run(["ioreg", "-c", "IOHIDSystem"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                # Parse ioreg output for HIDIdleTime
                import re
                match = re.search(r'"HIDIdleTime" = (\d+)', result.stdout)
                if match:
                    idle_ns = int(match.group(1))
                    idle_seconds = idle_ns / 1000000000  # Convert nanoseconds to seconds
                    
                    return {
                        "success": True,
                        "result": {
                            "idle_seconds": idle_seconds,
                            "idle_minutes": idle_seconds / 60,
                            "is_idle": idle_seconds > 300,
                            "method": "ioreg"
                        },
                        "error": None
                    }
            
            return {"success": False, "result": None, "error": "Failed to get idle time from ioreg"}
        
        elif system == "Windows":
            # Use PowerShell with Windows API
            ps_script = """
            Add-Type @"
                using System;
                using System.Runtime.InteropServices;
                public class Win32 {
                    [DllImport("user32.dll")]
                    public static extern bool GetLastInputInfo(ref LASTINPUTINFO plii);
                    [StructLayout(LayoutKind.Sequential)]
                    public struct LASTINPUTINFO {
                        public uint cbSize;
                        public uint dwTime;
                    }
                }
"@
            $lii = New-Object Win32+LASTINPUTINFO
            $lii.cbSize = [System.Runtime.InteropServices.Marshal]::SizeOf($lii)
            [Win32]::GetLastInputInfo([ref]$lii)
            $idle_ms = [Environment]::TickCount - $lii.dwTime
            $idle_ms
            """
            result = subprocess.run(["powershell", "-c", ps_script], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                idle_ms = int(result.stdout.strip())
                idle_seconds = idle_ms / 1000
                
                return {
                    "success": True,
                    "result": {
                        "idle_seconds": idle_seconds,
                        "idle_minutes": idle_seconds / 60,
                        "is_idle": idle_seconds > 300,
                        "method": "win32api"
                    },
                    "error": None
                }
            else:
                return {"success": False, "result": None, "error": f"Windows idle detection failed: {result.stderr}"}
        
        else:
            return {"success": False, "result": None, "error": f"Unsupported platform: {system}"}
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to detect idle state: {str(e)}"}

def _get_display_info_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get display information implementation"""
    try:
        import pyautogui
        
        # Get screen size
        screen_width, screen_height = pyautogui.size()
        
        # Try to get additional display info
        displays = []
        system = platform.system()
        
        if system == "Linux":
            try:
                result = subprocess.run(["xrandr"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    # Parse xrandr output
                    import re
                    for line in result.stdout.split('\n'):
                        if ' connected' in line:
                            match = re.search(r'(\w+) connected.*?(\d+)x(\d+)', line)
                            if match:
                                displays.append({
                                    "name": match.group(1),
                                    "width": int(match.group(2)),
                                    "height": int(match.group(3)),
                                    "connected": True
                                })
            except:
                pass
        
        elif system == "Darwin":  # macOS
            try:
                result = subprocess.run(["system_profiler", "SPDisplaysDataType"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    # Basic display info
                    displays.append({
                        "name": "Built-in Display",
                        "width": screen_width,
                        "height": screen_height,
                        "connected": True
                    })
            except:
                pass
        
        elif system == "Windows":
            try:
                ps_script = "Get-WmiObject -Class Win32_VideoController | Select-Object Name, CurrentHorizontalResolution, CurrentVerticalResolution"
                result = subprocess.run(["powershell", "-c", ps_script], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    displays.append({
                        "name": "Primary Display",
                        "width": screen_width,
                        "height": screen_height,
                        "connected": True
                    })
            except:
                pass
        
        # Fallback to basic info
        if not displays:
            displays.append({
                "name": "Primary Display",
                "width": screen_width,
                "height": screen_height,
                "connected": True
            })
        
        return {
            "success": True,
            "result": {
                "primary_display": {
                    "width": screen_width,
                    "height": screen_height
                },
                "displays": displays,
                "display_count": len(displays),
                "method": "pyautogui_system"
            },
            "error": None
        }
    
    except ImportError:
        return {"success": False, "result": None, "error": "Display info requires pyautogui (pip install pyautogui)"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to get display info: {str(e)}"}

def _screen_ocr_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Screen OCR implementation"""
    try:
        # OCR requires additional libraries like pytesseract
        return {
            "success": False,
            "result": None,
            "error": "Screen OCR requires additional setup (install pytesseract and tesseract-ocr)"
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to perform screen OCR: {str(e)}"}

def _get_all_context_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get all context information implementation"""
    try:
        context = {}
        
        # Get window info
        window_result = _get_active_window_impl(args)
        if window_result["success"]:
            context["window"] = window_result["result"]
        
        # Get cursor position
        cursor_result = _get_cursor_position_impl(args)
        if cursor_result["success"]:
            context["cursor"] = cursor_result["result"]
        
        # Get clipboard
        clipboard_result = _get_clipboard_impl(args)
        if clipboard_result["success"]:
            context["clipboard"] = clipboard_result["result"]
        
        # Get display info
        display_result = _get_display_info_impl(args)
        if display_result["success"]:
            context["display"] = display_result["result"]
        
        # Get idle state
        idle_result = _detect_idle_state_impl(args)
        if idle_result["success"]:
            context["idle"] = idle_result["result"]
        
        return {
            "success": True,
            "result": {
                "context": context,
                "timestamp": time.time(),
                "method": "all_context"
            },
            "error": None
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to get all context: {str(e)}"}

# Context Capture Implementation Helpers
def _take_screenshot_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Take screenshot implementation"""
    try:
        import pyautogui
        
        output_path = args.get("output_path")
        if not output_path:
            output_path = os.path.join(tempfile.gettempdir(), f"screenshot_{int(time.time())}.png")
        
        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot.save(output_path)
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            width, height = screenshot.size
            
            return {
                "success": True,
                "result": {
                    "output_path": output_path,
                    "width": width,
                    "height": height,
                    "file_size": file_size,
                    "method": "pyautogui_screenshot"
                },
                "error": None
            }
        else:
            return {"success": False, "result": None, "error": "Failed to save screenshot"}
    
    except ImportError:
        return {"success": False, "result": None, "error": "Screenshot requires pyautogui (pip install pyautogui)"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to take screenshot: {str(e)}"}

def _take_window_screenshot_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Take window screenshot implementation"""
    try:
        # Window screenshot requires more advanced implementation
        # For now, fall back to full screenshot
        return _take_screenshot_impl(args)
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to take window screenshot: {str(e)}"}

def _capture_camera_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Capture camera implementation - delegate to vision system"""
    try:
        from que_core.tools.vision_tools import vision_system
        return vision_system(args={"action": "capture", **args})
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to capture camera: {str(e)}"}

def _record_audio_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Record audio implementation - delegate to audio system"""
    try:
        from que_core.tools.audio_tools import audio_control
        return audio_control(args={"action": "record", **args})
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to record audio: {str(e)}"}

# Legacy function aliases for backward compatibility
def get_active_window_title(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use context_get instead"""
    return context_get(args={"what": "window", **(args or {})})

def get_cursor_position(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use context_get instead"""
    return context_get(args={"what": "cursor", **(args or {})})

def get_clipboard_text(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use context_get instead"""
    return context_get(args={"what": "clipboard", **(args or {})})

def set_clipboard_text(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Set clipboard text - not part of context_get, separate function"""
    try:
        import pyperclip
        
        text = args.get("text", "") if args else ""
        pyperclip.copy(text)
        
        return {
            "success": True,
            "result": {
                "text": text,
                "length": len(text),
                "set": True
            },
            "error": None
        }
    
    except ImportError:
        return {"success": False, "result": None, "error": "Clipboard requires pyperclip (pip install pyperclip)"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to set clipboard: {str(e)}"}

def take_screenshot(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use context_capture instead"""
    return context_capture(args={"type": "screenshot", **(args or {})})

def detect_idle_state(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use context_get instead"""
    return context_get(args={"what": "idle", **(args or {})})

def get_display_info(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use context_get instead"""
    return context_get(args={"what": "display", **(args or {})})

def screen_ocr(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use context_get instead"""
    return context_get(args={"what": "screen_text", **(args or {})})
