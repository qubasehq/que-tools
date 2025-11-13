"""
System Settings Tools - Consolidated system configuration and settings management for AI agents
Provides unified control over wallpapers, themes, connectivity, and system preferences.
"""
from typing import Any, Dict, List
import os
import platform
import subprocess
import json

def settings_manager(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Universal settings manager - replaces change_wallpaper, set_theme_mode, manage_bluetooth, manage_wifi, set_system_timezone, get_installed_fonts
    
    Args:
        action (str): Action to perform - 'wallpaper', 'theme', 'bluetooth', 'wifi', 'timezone', 'fonts', 'display', 'sound'
        path (str): File path (for wallpaper action)
        mode (str): Theme mode - 'light', 'dark', 'auto' (for theme action)
        ssid (str): WiFi network name (for wifi action)
        password (str): WiFi password (for wifi action)
        timezone (str): Timezone string (for timezone action)
        device (str): Bluetooth device address (for bluetooth action)
        enable (bool): Enable/disable setting (for various actions)
        
    Returns:
        Dict with settings operation result
    """
    if not args or "action" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: action"}
    
    action = args["action"]
    
    try:
        if action == "wallpaper":
            return _change_wallpaper_impl(args)
        elif action == "theme":
            return _set_theme_mode_impl(args)
        elif action == "bluetooth":
            return _manage_bluetooth_impl(args)
        elif action == "wifi":
            return _manage_wifi_impl(args)
        elif action == "timezone":
            return _set_timezone_impl(args)
        elif action == "fonts":
            return _get_installed_fonts_impl(args)
        elif action == "display":
            return _manage_display_impl(args)
        elif action == "sound":
            return _manage_sound_impl(args)
        else:
            return {
                "success": False,
                "result": None,
                "error": f"Unknown action: {action}. Use: wallpaper, theme, bluetooth, wifi, timezone, fonts, display, sound"
            }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Settings operation failed: {str(e)}"}

# Settings Manager Implementation Helpers
def _change_wallpaper_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Change wallpaper implementation"""
    try:
        wallpaper_path = args.get("path")
        if not wallpaper_path:
            return {"success": False, "result": None, "error": "Missing required argument: path"}
        
        if not os.path.exists(wallpaper_path):
            return {"success": False, "result": None, "error": f"Wallpaper file not found: {wallpaper_path}"}
        
        system = platform.system()
        
        if system == "Linux":
            # Try different desktop environments
            desktop_env = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
            
            if "gnome" in desktop_env:
                result = subprocess.run([
                    "gsettings", "set", "org.gnome.desktop.background", "picture-uri", 
                    f"file://{os.path.abspath(wallpaper_path)}"
                ], capture_output=True, text=True, timeout=10)
                method = "gnome_gsettings"
            elif "kde" in desktop_env or "plasma" in desktop_env:
                # KDE Plasma
                script = f"""
                var allDesktops = desktops();
                for (i=0;i<allDesktops.length;i++){{
                    d = allDesktops[i];
                    d.wallpaperPlugin = 'org.kde.image';
                    d.currentConfigGroup = Array('Wallpaper', 'org.kde.image', 'General');
                    d.writeConfig('Image', 'file://{os.path.abspath(wallpaper_path)}');
                }}
                """
                result = subprocess.run([
                    "qdbus", "org.kde.plasmashell", "/PlasmaShell", 
                    "org.kde.PlasmaShell.evaluateScript", script
                ], capture_output=True, text=True, timeout=10)
                method = "kde_qdbus"
            else:
                # Generic approach using feh (if available)
                result = subprocess.run(["feh", "--bg-scale", wallpaper_path], capture_output=True, text=True, timeout=10)
                method = "feh"
        
        elif system == "Darwin":  # macOS
            result = subprocess.run([
                "osascript", "-e", 
                f'tell application "Finder" to set desktop picture to POSIX file "{os.path.abspath(wallpaper_path)}"'
            ], capture_output=True, text=True, timeout=10)
            method = "applescript"
        
        elif system == "Windows":
            # Use ctypes to call Windows API
            try:
                import ctypes
                ctypes.windll.user32.SystemParametersInfoW(20, 0, wallpaper_path, 3)
                result = type('Result', (), {'returncode': 0, 'stdout': '', 'stderr': ''})()
                method = "win32api"
            except Exception as e:
                return {"success": False, "result": None, "error": f"Windows wallpaper change failed: {str(e)}"}
        
        else:
            return {"success": False, "result": None, "error": f"Unsupported platform: {system}"}
        
        success = result.returncode == 0
        
        return {
            "success": success,
            "result": {
                "wallpaper_path": wallpaper_path,
                "platform": system,
                "method": method,
                "changed": success
            },
            "error": result.stderr if not success else None
        }
    
    except subprocess.TimeoutExpired:
        return {"success": False, "result": None, "error": "Wallpaper change timed out"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to change wallpaper: {str(e)}"}

def _set_theme_mode_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Set theme mode implementation"""
    try:
        mode = args.get("mode", "auto")
        if mode not in ["light", "dark", "auto"]:
            return {"success": False, "result": None, "error": "Mode must be 'light', 'dark', or 'auto'"}
        
        system = platform.system()
        
        if system == "Linux":
            desktop_env = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
            
            if "gnome" in desktop_env:
                # GNOME theme setting
                theme_value = "prefer-dark" if mode == "dark" else "default"
                result = subprocess.run([
                    "gsettings", "set", "org.gnome.desktop.interface", "color-scheme", theme_value
                ], capture_output=True, text=True, timeout=10)
                method = "gnome_gsettings"
            elif "kde" in desktop_env:
                # KDE theme setting (simplified)
                return {"success": False, "result": None, "error": "KDE theme switching not yet implemented"}
            else:
                return {"success": False, "result": None, "error": f"Theme switching not supported for desktop environment: {desktop_env}"}
        
        elif system == "Darwin":  # macOS
            # macOS dark mode
            appearance = "Dark" if mode == "dark" else "Light"
            result = subprocess.run([
                "osascript", "-e", 
                f'tell application "System Events" to tell appearance preferences to set dark mode to {mode == "dark"}'
            ], capture_output=True, text=True, timeout=10)
            method = "applescript"
        
        elif system == "Windows":
            # Windows theme setting via registry
            try:
                import winreg
                key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                    # 0 = dark, 1 = light
                    theme_value = 0 if mode == "dark" else 1
                    winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, theme_value)
                    winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, theme_value)
                
                result = type('Result', (), {'returncode': 0, 'stdout': '', 'stderr': ''})()
                method = "windows_registry"
            except ImportError:
                return {"success": False, "result": None, "error": "Windows theme change requires winreg module"}
            except Exception as e:
                return {"success": False, "result": None, "error": f"Windows theme change failed: {str(e)}"}
        
        else:
            return {"success": False, "result": None, "error": f"Unsupported platform: {system}"}
        
        success = result.returncode == 0
        
        return {
            "success": success,
            "result": {
                "theme_mode": mode,
                "platform": system,
                "method": method,
                "changed": success
            },
            "error": result.stderr if not success else None
        }
    
    except subprocess.TimeoutExpired:
        return {"success": False, "result": None, "error": "Theme change timed out"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to set theme mode: {str(e)}"}

def _manage_bluetooth_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Manage Bluetooth implementation"""
    try:
        operation = args.get("operation", "status")  # status, enable, disable, scan, pair
        device = args.get("device")  # Bluetooth device address
        
        system = platform.system()
        
        if system == "Linux":
            if operation == "status":
                result = subprocess.run(["bluetoothctl", "show"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    powered = "Powered: yes" in result.stdout
                    discoverable = "Discoverable: yes" in result.stdout
                    return {
                        "success": True,
                        "result": {
                            "powered": powered,
                            "discoverable": discoverable,
                            "method": "bluetoothctl"
                        },
                        "error": None
                    }
            elif operation == "enable":
                result = subprocess.run(["bluetoothctl", "power", "on"], capture_output=True, text=True, timeout=10)
            elif operation == "disable":
                result = subprocess.run(["bluetoothctl", "power", "off"], capture_output=True, text=True, timeout=10)
            elif operation == "scan":
                result = subprocess.run(["bluetoothctl", "scan", "on"], capture_output=True, text=True, timeout=5)
                # Stop scan after brief period
                subprocess.run(["bluetoothctl", "scan", "off"], capture_output=True, text=True, timeout=5)
            else:
                return {"success": False, "result": None, "error": f"Unsupported Bluetooth operation: {operation}"}
            
            method = "bluetoothctl"
        
        elif system == "Darwin":  # macOS
            if operation == "status":
                result = subprocess.run(["system_profiler", "SPBluetoothDataType"], capture_output=True, text=True, timeout=10)
                method = "system_profiler"
            else:
                return {"success": False, "result": None, "error": "macOS Bluetooth control not yet implemented"}
        
        elif system == "Windows":
            return {"success": False, "result": None, "error": "Windows Bluetooth control not yet implemented"}
        
        else:
            return {"success": False, "result": None, "error": f"Unsupported platform: {system}"}
        
        success = result.returncode == 0
        
        return {
            "success": success,
            "result": {
                "operation": operation,
                "platform": system,
                "method": method,
                "output": result.stdout if success else None
            },
            "error": result.stderr if not success else None
        }
    
    except subprocess.TimeoutExpired:
        return {"success": False, "result": None, "error": "Bluetooth operation timed out"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to manage Bluetooth: {str(e)}"}

def _manage_wifi_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Manage WiFi implementation"""
    try:
        operation = args.get("operation", "status")  # status, scan, connect, disconnect
        ssid = args.get("ssid")
        password = args.get("password")
        
        system = platform.system()
        
        if system == "Linux":
            if operation == "status":
                result = subprocess.run(["nmcli", "dev", "wifi"], capture_output=True, text=True, timeout=10)
                method = "nmcli"
            elif operation == "scan":
                result = subprocess.run(["nmcli", "dev", "wifi", "rescan"], capture_output=True, text=True, timeout=15)
                if result.returncode == 0:
                    # Get scan results
                    scan_result = subprocess.run(["nmcli", "dev", "wifi", "list"], capture_output=True, text=True, timeout=10)
                    result = scan_result
                method = "nmcli"
            elif operation == "connect":
                if not ssid:
                    return {"success": False, "result": None, "error": "SSID required for WiFi connection"}
                if password:
                    result = subprocess.run(["nmcli", "dev", "wifi", "connect", ssid, "password", password], capture_output=True, text=True, timeout=20)
                else:
                    result = subprocess.run(["nmcli", "dev", "wifi", "connect", ssid], capture_output=True, text=True, timeout=20)
                method = "nmcli"
            else:
                return {"success": False, "result": None, "error": f"Unsupported WiFi operation: {operation}"}
        
        elif system == "Darwin":  # macOS
            if operation == "status":
                result = subprocess.run(["networksetup", "-getairportnetwork", "en0"], capture_output=True, text=True, timeout=10)
                method = "networksetup"
            elif operation == "scan":
                result = subprocess.run(["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-s"], capture_output=True, text=True, timeout=15)
                method = "airport"
            else:
                return {"success": False, "result": None, "error": "macOS WiFi control limited to status and scan"}
        
        elif system == "Windows":
            if operation == "status":
                result = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output=True, text=True, timeout=10)
                method = "netsh"
            else:
                return {"success": False, "result": None, "error": "Windows WiFi control not yet fully implemented"}
        
        else:
            return {"success": False, "result": None, "error": f"Unsupported platform: {system}"}
        
        success = result.returncode == 0
        
        return {
            "success": success,
            "result": {
                "operation": operation,
                "ssid": ssid,
                "platform": system,
                "method": method,
                "output": result.stdout if success else None
            },
            "error": result.stderr if not success else None
        }
    
    except subprocess.TimeoutExpired:
        return {"success": False, "result": None, "error": "WiFi operation timed out"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to manage WiFi: {str(e)}"}

def _set_timezone_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Set system timezone implementation"""
    try:
        timezone = args.get("timezone")
        if not timezone:
            return {"success": False, "result": None, "error": "Missing required argument: timezone"}
        
        system = platform.system()
        
        if system == "Linux":
            # Use timedatectl on systemd systems
            result = subprocess.run(["timedatectl", "set-timezone", timezone], capture_output=True, text=True, timeout=10)
            method = "timedatectl"
        
        elif system == "Darwin":  # macOS
            result = subprocess.run(["sudo", "systemsetup", "-settimezone", timezone], capture_output=True, text=True, timeout=10)
            method = "systemsetup"
        
        elif system == "Windows":
            result = subprocess.run(["tzutil", "/s", timezone], capture_output=True, text=True, timeout=10)
            method = "tzutil"
        
        else:
            return {"success": False, "result": None, "error": f"Unsupported platform: {system}"}
        
        success = result.returncode == 0
        
        return {
            "success": success,
            "result": {
                "timezone": timezone,
                "platform": system,
                "method": method,
                "changed": success
            },
            "error": result.stderr if not success else None
        }
    
    except subprocess.TimeoutExpired:
        return {"success": False, "result": None, "error": "Timezone change timed out"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to set timezone: {str(e)}"}

def _get_installed_fonts_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get installed fonts implementation"""
    try:
        system = platform.system()
        fonts = []
        
        if system == "Linux":
            # Use fc-list to get fonts
            result = subprocess.run(["fc-list", ":", "family"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                font_lines = result.stdout.strip().split('\n')
                fonts = list(set([line.split(':')[0].strip() for line in font_lines if line.strip()]))
                fonts.sort()
            method = "fontconfig"
        
        elif system == "Darwin":  # macOS
            # Use system_profiler to get fonts
            result = subprocess.run(["system_profiler", "SPFontsDataType"], capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                # Parse font names from output (simplified)
                import re
                font_matches = re.findall(r'^\s+([^:]+):', result.stdout, re.MULTILINE)
                fonts = list(set(font_matches))
                fonts.sort()
            method = "system_profiler"
        
        elif system == "Windows":
            # Use PowerShell to get fonts
            ps_script = """
            Add-Type -AssemblyName System.Drawing
            $fonts = New-Object System.Drawing.Text.InstalledFontCollection
            $fonts.Families | ForEach-Object { $_.Name }
            """
            result = subprocess.run(["powershell", "-c", ps_script], capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                fonts = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
                fonts.sort()
            method = "powershell"
        
        else:
            return {"success": False, "result": None, "error": f"Unsupported platform: {system}"}
        
        return {
            "success": True,
            "result": {
                "fonts": fonts,
                "font_count": len(fonts),
                "platform": system,
                "method": method,
                "sample_fonts": fonts[:10] if fonts else []
            },
            "error": None
        }
    
    except subprocess.TimeoutExpired:
        return {"success": False, "result": None, "error": "Font enumeration timed out"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to get installed fonts: {str(e)}"}

def _manage_display_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Manage display settings implementation"""
    try:
        operation = args.get("operation", "info")  # info, brightness, resolution
        
        system = platform.system()
        
        if system == "Linux":
            if operation == "info":
                result = subprocess.run(["xrandr"], capture_output=True, text=True, timeout=10)
                method = "xrandr"
            else:
                return {"success": False, "result": None, "error": f"Display operation '{operation}' not yet implemented for Linux"}
        
        elif system == "Darwin":  # macOS
            if operation == "info":
                result = subprocess.run(["system_profiler", "SPDisplaysDataType"], capture_output=True, text=True, timeout=10)
                method = "system_profiler"
            else:
                return {"success": False, "result": None, "error": f"Display operation '{operation}' not yet implemented for macOS"}
        
        elif system == "Windows":
            return {"success": False, "result": None, "error": "Windows display management not yet implemented"}
        
        else:
            return {"success": False, "result": None, "error": f"Unsupported platform: {system}"}
        
        success = result.returncode == 0
        
        return {
            "success": success,
            "result": {
                "operation": operation,
                "platform": system,
                "method": method,
                "output": result.stdout if success else None
            },
            "error": result.stderr if not success else None
        }
    
    except subprocess.TimeoutExpired:
        return {"success": False, "result": None, "error": "Display operation timed out"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to manage display: {str(e)}"}

def _manage_sound_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Manage sound settings implementation"""
    try:
        operation = args.get("operation", "info")  # info, volume, mute
        volume = args.get("volume")
        
        # Delegate to existing audio tools for sound management
        from que_core.tools.audio_tools import audio_control
        
        if operation == "volume" and volume is not None:
            return audio_control(args={"action": "set_volume", "volume": volume})
        elif operation == "info":
            return audio_control(args={"action": "get_volume"})
        else:
            return {"success": False, "result": None, "error": f"Sound operation '{operation}' not supported"}
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to manage sound: {str(e)}"}

# Legacy function aliases for backward compatibility
def change_wallpaper(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use settings_manager instead"""
    return settings_manager(args={"action": "wallpaper", **(args or {})})

def set_theme_mode(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use settings_manager instead"""
    return settings_manager(args={"action": "theme", **(args or {})})

def manage_bluetooth(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use settings_manager instead"""
    return settings_manager(args={"action": "bluetooth", **(args or {})})

def manage_wifi(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use settings_manager instead"""
    return settings_manager(args={"action": "wifi", **(args or {})})

def set_system_timezone(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use settings_manager instead"""
    return settings_manager(args={"action": "timezone", **(args or {})})

def get_installed_fonts(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use settings_manager instead"""
    return settings_manager(args={"action": "fonts", **(args or {})})
