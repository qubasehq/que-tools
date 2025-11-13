"""
App Tools - Consolidated application management for AI agents
Provides unified app control and window management capabilities.
"""
from typing import Any, Dict, List
import subprocess
import platform
import os
import signal
import psutil

def app_manager(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Universal app manager - replaces open_app, close_app, switch_app, list_apps, get_active_window, resize_window, pin_window, mute_app_audio
    
    Args:
        action (str): Action to perform - 'open', 'close', 'switch', 'list', 'active', 'resize', 'pin', 'mute'
        name (str): Application name for open/close/switch operations
        pid (int): Process ID for close operations
        width, height (int): Dimensions for resize operations
        
    Returns:
        Dict with operation result
    """
    if not args or "action" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: action"}
    
    action = args["action"]
    
    try:
        if action == "open":
            return _open_app_impl(args)
        elif action == "close":
            return _close_app_impl(args)
        elif action == "switch":
            return _switch_app_impl(args)
        elif action == "list":
            return _list_apps_impl(args)
        elif action == "active":
            return _get_active_window_impl(args)
        elif action == "resize":
            return _resize_window_impl(args)
        elif action == "pin":
            return _pin_window_impl(args)
        elif action == "mute":
            return _mute_app_impl(args)
        else:
            return {
                "success": False,
                "result": None,
                "error": f"Unknown action: {action}. Use: open, close, switch, list, active, resize, pin, mute"
            }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"App operation failed: {str(e)}"}

def window_control(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Advanced window management - replaces resize_window, pin_window, take_window_screenshot, switch_app
    
    Args:
        action (str): Action to perform - 'resize', 'pin', 'screenshot', 'switch', 'move', 'minimize', 'maximize'
        window_title (str): Window title to target
        x, y (int): Position for move operations
        width, height (int): Dimensions for resize operations
        
    Returns:
        Dict with operation result
    """
    if not args or "action" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: action"}
    
    action = args["action"]
    
    try:
        if action == "resize":
            return _resize_window_impl(args)
        elif action == "pin":
            return _pin_window_impl(args)
        elif action == "screenshot":
            return _take_window_screenshot_impl(args)
        elif action == "switch":
            return _switch_window_impl(args)
        elif action == "move":
            return _move_window_impl(args)
        elif action == "minimize":
            return _minimize_window_impl(args)
        elif action == "maximize":
            return _maximize_window_impl(args)
        else:
            return {
                "success": False,
                "result": None,
                "error": f"Unknown action: {action}. Use: resize, pin, screenshot, switch, move, minimize, maximize"
            }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Window operation failed: {str(e)}"}

# Implementation helpers
def _open_app_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Open application implementation"""
    name = args.get("name")
    if not name:
        return {"success": False, "result": None, "error": "Missing required argument: name"}
    
    try:
        wait_for_launch = args.get("wait_for_launch", False)
        system = platform.system()
        
        if system == "Linux":
            # Try different methods to launch apps on Linux
            launch_commands = [
                [name],  # Direct command
                ["gtk-launch", name],  # GTK launcher
                ["/usr/bin/" + name],  # Common bin path
                ["/usr/local/bin/" + name],  # Local bin path
                ["flatpak", "run", name],  # Flatpak apps
                ["snap", "run", name],  # Snap apps
            ]
            
            for cmd in launch_commands:
                try:
                    if wait_for_launch:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                        if result.returncode == 0:
                            return {
                                "success": True,
                                "result": {
                                    "app_name": name,
                                    "command": " ".join(cmd),
                                    "launched": True,
                                    "method": "linux_native"
                                },
                                "error": None
                            }
                    else:
                        # Launch in background
                        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        return {
                            "success": True,
                            "result": {
                                "app_name": name,
                                "command": " ".join(cmd),
                                "launched": True,
                                "method": "linux_background"
                            },
                            "error": None
                        }
                except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
                    continue
                    
        elif system == "Darwin":  # macOS
            try:
                subprocess.run(["open", "-a", name], check=True)
                return {
                    "success": True,
                    "result": {"app_name": name, "launched": True, "method": "macos_open"},
                    "error": None
                }
            except subprocess.CalledProcessError:
                pass
                
        elif system == "Windows":
            try:
                subprocess.run(["start", name], shell=True, check=True)
                return {
                    "success": True,
                    "result": {"app_name": name, "launched": True, "method": "windows_start"},
                    "error": None
                }
            except subprocess.CalledProcessError:
                pass
        
        return {"success": False, "result": None, "error": f"Could not launch application: {name}"}
        
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to open app: {str(e)}"}

def _close_app_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Close application implementation"""
    if "name" not in args and "pid" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: name or pid"}
    
    try:
        force = args.get("force", False)
        
        if "pid" in args:
            # Close by PID
            pid = args["pid"]
            try:
                process = psutil.Process(pid)
                if force:
                    process.kill()
                else:
                    process.terminate()
                    
                return {
                    "success": True,
                    "result": {"pid": pid, "action": "killed" if force else "terminated"},
                    "error": None
                }
            except psutil.NoSuchProcess:
                return {"success": False, "result": None, "error": f"Process with PID {pid} not found"}
            except psutil.AccessDenied:
                return {"success": False, "result": None, "error": f"Access denied to process {pid}"}
        
        elif "name" in args:
            # Close by name
            name = args["name"]
            killed_processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if name.lower() in proc.info['name'].lower():
                        if force:
                            proc.kill()
                        else:
                            proc.terminate()
                        killed_processes.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if killed_processes:
                return {
                    "success": True,
                    "result": {
                        "app_name": name,
                        "processes_closed": killed_processes,
                        "count": len(killed_processes),
                        "action": "killed" if force else "terminated"
                    },
                    "error": None
                }
            else:
                return {"success": False, "result": None, "error": f"No processes found matching: {name}"}
        
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to close app: {str(e)}"}

def _switch_app_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Switch to application implementation"""
    name = args.get("name")
    if not name:
        return {"success": False, "result": None, "error": "Missing required argument: name"}
    
    try:
        system = platform.system()
        
        if system == "Linux":
            # Use wmctrl to switch to window
            try:
                result = subprocess.run(["wmctrl", "-a", name], capture_output=True, text=True)
                if result.returncode == 0:
                    return {
                        "success": True,
                        "result": {"app_name": name, "switched": True, "method": "wmctrl"},
                        "error": None
                    }
            except FileNotFoundError:
                pass
            
            # Try xdotool as fallback
            try:
                result = subprocess.run(["xdotool", "search", "--name", name, "windowactivate"], capture_output=True, text=True)
                if result.returncode == 0:
                    return {
                        "success": True,
                        "result": {"app_name": name, "switched": True, "method": "xdotool"},
                        "error": None
                    }
            except FileNotFoundError:
                pass
                
        elif system == "Darwin":  # macOS
            try:
                script = f'tell application "{name}" to activate'
                subprocess.run(["osascript", "-e", script], check=True)
                return {
                    "success": True,
                    "result": {"app_name": name, "switched": True, "method": "applescript"},
                    "error": None
                }
            except subprocess.CalledProcessError:
                pass
        
        return {"success": False, "result": None, "error": f"Could not switch to application: {name}"}
        
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to switch app: {str(e)}"}

def _list_apps_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """List applications implementation"""
    try:
        running_only = args.get("running_only", True)
        
        if running_only:
            # List running applications
            apps = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
                try:
                    # Simple heuristic for GUI applications
                    name = proc.info['name'].lower()
                    if any(gui_app in name for gui_app in ['chrome', 'firefox', 'code', 'terminal', 'nautilus', 'explorer', 'finder', 'safari']):
                        apps.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "memory_mb": round(proc.info['memory_info'].rss / 1024 / 1024, 1),
                            "cpu_percent": proc.info['cpu_percent']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by memory usage
            apps.sort(key=lambda x: x['memory_mb'], reverse=True)
            
            return {
                "success": True,
                "result": {
                    "apps": apps,
                    "count": len(apps),
                    "type": "running_apps"
                },
                "error": None
            }
        else:
            # List all installed applications (platform-specific)
            return {
                "success": False,
                "result": None,
                "error": "Listing all installed apps not yet implemented"
            }
        
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to list apps: {str(e)}"}

def _get_active_window_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get active window implementation"""
    try:
        system = platform.system()
        
        if system == "Linux":
            # Try xdotool first
            try:
                result = subprocess.run(["xdotool", "getactivewindow", "getwindowname"], capture_output=True, text=True)
                if result.returncode == 0:
                    title = result.stdout.strip()
                    
                    # Get window ID and geometry
                    id_result = subprocess.run(["xdotool", "getactivewindow"], capture_output=True, text=True)
                    window_id = id_result.stdout.strip() if id_result.returncode == 0 else None
                    
                    return {
                        "success": True,
                        "result": {
                            "title": title,
                            "window_id": window_id,
                            "method": "xdotool"
                        },
                        "error": None
                    }
            except FileNotFoundError:
                pass
        
        return {"success": False, "result": None, "error": "Could not get active window"}
        
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to get active window: {str(e)}"}

def _resize_window_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Resize window implementation"""
    width = args.get("width")
    height = args.get("height")
    
    if not width or not height:
        return {"success": False, "result": None, "error": "Missing required arguments: width, height"}
    
    try:
        system = platform.system()
        window_title = args.get("window_title")
        
        if system == "Linux":
            if window_title:
                # Resize specific window
                try:
                    subprocess.run(["wmctrl", "-r", window_title, "-e", f"0,-1,-1,{width},{height}"], check=True)
                    return {
                        "success": True,
                        "result": {"window_title": window_title, "width": width, "height": height, "method": "wmctrl"},
                        "error": None
                    }
                except (FileNotFoundError, subprocess.CalledProcessError):
                    pass
            else:
                # Resize active window
                try:
                    subprocess.run(["xdotool", "getactivewindow", "windowsize", str(width), str(height)], check=True)
                    return {
                        "success": True,
                        "result": {"width": width, "height": height, "method": "xdotool"},
                        "error": None
                    }
                except (FileNotFoundError, subprocess.CalledProcessError):
                    pass
        
        return {"success": False, "result": None, "error": "Could not resize window"}
        
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to resize window: {str(e)}"}

def _pin_window_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Pin window implementation"""
    try:
        return {
            "success": False,
            "result": None,
            "error": "Window pinning not yet implemented"
        }
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to pin window: {str(e)}"}

def _mute_app_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Mute application implementation"""
    try:
        return {
            "success": False,
            "result": None,
            "error": "App audio muting not yet implemented"
        }
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to mute app: {str(e)}"}

def _take_window_screenshot_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Take window screenshot implementation"""
    try:
        # Use context_capture for window screenshots
        from que_core.tools.context_tools import context_capture
        
        window_title = args.get("window_title", "")
        save_path = args.get("save_path", "")
        
        return context_capture(args={
            "type": "window_screenshot",
            "window_title": window_title,
            "save_path": save_path
        })
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to take window screenshot: {str(e)}"}

def _switch_window_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Switch window implementation"""
    return _switch_app_impl(args)

def _move_window_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Move window implementation"""
    x = args.get("x")
    y = args.get("y")
    
    if x is None or y is None:
        return {"success": False, "result": None, "error": "Missing required arguments: x, y"}
    
    try:
        system = platform.system()
        
        if system == "Linux":
            try:
                subprocess.run(["xdotool", "getactivewindow", "windowmove", str(x), str(y)], check=True)
                return {
                    "success": True,
                    "result": {"x": x, "y": y, "method": "xdotool"},
                    "error": None
                }
            except (FileNotFoundError, subprocess.CalledProcessError):
                pass
        
        return {"success": False, "result": None, "error": "Could not move window"}
        
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to move window: {str(e)}"}

def _minimize_window_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Minimize window implementation"""
    try:
        system = platform.system()
        
        if system == "Linux":
            try:
                subprocess.run(["xdotool", "getactivewindow", "windowminimize"], check=True)
                return {
                    "success": True,
                    "result": {"action": "minimized", "method": "xdotool"},
                    "error": None
                }
            except (FileNotFoundError, subprocess.CalledProcessError):
                pass
        
        return {"success": False, "result": None, "error": "Could not minimize window"}
        
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to minimize window: {str(e)}"}

def _maximize_window_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Maximize window implementation"""
    try:
        system = platform.system()
        
        if system == "Linux":
            try:
                subprocess.run(["xdotool", "getactivewindow", "windowmaximize"], check=True)
                return {
                    "success": True,
                    "result": {"action": "maximized", "method": "xdotool"},
                    "error": None
                }
            except (FileNotFoundError, subprocess.CalledProcessError):
                pass
        
        return {"success": False, "result": None, "error": "Could not maximize window"}
        
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to maximize window: {str(e)}"}

# Legacy function aliases for backward compatibility
def open_app(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use app_manager instead"""
    return app_manager(args={"action": "open", **(args or {})})

def close_app(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use app_manager instead"""
    return app_manager(args={"action": "close", **(args or {})})

def switch_app(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use app_manager instead"""
    return app_manager(args={"action": "switch", **(args or {})})

def list_apps(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use app_manager instead"""
    return app_manager(args={"action": "list", **(args or {})})

def get_active_window(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use app_manager instead"""
    return app_manager(args={"action": "active", **(args or {})})

def resize_window(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use window_control instead"""
    return window_control(args={"action": "resize", **(args or {})})

def take_window_screenshot(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use window_control instead"""
    return window_control(args={"action": "screenshot", **(args or {})})

def pin_window(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use window_control instead"""
    return window_control(args={"action": "pin", **(args or {})})

def mute_app_audio(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use app_manager instead"""
    return app_manager(args={"action": "mute", **(args or {})})

def list_running_apps(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use app_manager instead"""
    return app_manager(args={"action": "list", "running_only": True, **(args or {})})
