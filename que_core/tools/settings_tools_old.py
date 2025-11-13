"""System Settings Tools - OS configuration and theming for AI agents
Cross-platform system settings management
"""
from typing import Any, Dict, List
import os
import platform
import subprocess

def change_wallpaper(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Set desktop wallpaper"""
    if not args or "path" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: path"}
    
    try:
        wallpaper_path = args["path"]
        
        # Check if file exists
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
                ], capture_output=True, text=True)
            elif "kde" in desktop_env or "plasma" in desktop_env:
                # KDE Plasma
                result = subprocess.run([
                    "qdbus", "org.kde.plasmashell", "/PlasmaShell", 
                    "org.kde.PlasmaShell.evaluateScript", 
                    f"var allDesktops = desktops();for (i=0;i<allDesktops.length;i++){{d = allDesktops[i];d.wallpaperPlugin = 'org.kde.image';d.currentConfigGroup = Array('Wallpaper', 'org.kde.image', 'General');d.writeConfig('Image', 'file://{os.path.abspath(wallpaper_path)}');}}"
                ], capture_output=True, text=True)
            else:
                # Generic approach using feh (if available)
                result = subprocess.run(["feh", "--bg-scale", wallpaper_path], capture_output=True, text=True)
        
        elif system == "Darwin":  # macOS
            result = subprocess.run([
                "osascript", "-e", 
                f'tell application "Finder" to set desktop picture to POSIX file "{os.path.abspath(wallpaper_path)}"'
            ], capture_output=True, text=True)
        
        elif system == "Windows":
            import ctypes
            ctypes.windll.user32.SystemParametersInfoW(20, 0, wallpaper_path, 3)
            result = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        
        else:
            return {"success": False, "result": None, "error": f"Unsupported platform: {system}"}
        
        if result.returncode == 0:
            return {
                "success": True,
                "result": {
                    "wallpaper_path": wallpaper_path,
                    "platform": system,
                    "action": "wallpaper_changed"
                },
                "error": None
            }
        else:
            return {"success": False, "result": None, "error": f"Failed to set wallpaper: {result.stderr}"}
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to change wallpaper: {str(e)}"}

def set_theme_mode(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    if not args or "mode" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: mode (dark/light)"}
    
    try:
        mode = args["mode"].lower()
        if mode not in ["dark", "light"]:
            return {"success": False, "result": None, "error": "Mode must be 'dark' or 'light'"}
        
        system = platform.system()
        
        if system == "Linux":
            desktop_env = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
            
            if "gnome" in desktop_env:
                # GNOME theme setting
                theme_value = "prefer-dark" if mode == "dark" else "prefer-light"
                result = subprocess.run([
                    "gsettings", "set", "org.gnome.desktop.interface", "color-scheme", theme_value
                ], capture_output=True, text=True)
            elif "kde" in desktop_env:
                # KDE theme setting
                theme_name = "Breeze Dark" if mode == "dark" else "Breeze"
                result = subprocess.run([
                    "lookandfeeltool", "-a", theme_name
                ], capture_output=True, text=True)
            else:
                return {"success": False, "result": None, "error": f"Theme switching not supported for desktop environment: {desktop_env}"}
        
        elif system == "Darwin":  # macOS
            # macOS dark mode
            appearance = "Dark" if mode == "dark" else "Light"
            result = subprocess.run([
                "osascript", "-e", 
                f'tell application "System Events" to tell appearance preferences to set dark mode to {mode == "dark"}'
            ], capture_output=True, text=True)
        
        elif system == "Windows":
            # Windows theme setting via registry
            import winreg
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                # 0 = dark, 1 = light
                theme_value = 0 if mode == "dark" else 1
                winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, theme_value)
                winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, theme_value)
            
            result = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        
        else:
            return {"success": False, "result": None, "error": f"Unsupported platform: {system}"}
        
        if result.returncode == 0:
            return {
                "success": True,
                "result": {
                    "theme_mode": mode,
                    "platform": system,
                    "action": "theme_changed"
                },
                "error": None
            }
        else:
            return {"success": False, "result": None, "error": f"Failed to set theme: {result.stderr}"}
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to set theme mode: {str(e)}"}

def manage_bluetooth(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    if not args or "action" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: action (enable/disable/status)"}
    
    try:
        action = args["action"].lower()
        system = platform.system()
        
        if system == "Linux":
            if action == "enable":
                result = subprocess.run(["bluetoothctl", "power", "on"], capture_output=True, text=True)
            elif action == "disable":
                result = subprocess.run(["bluetoothctl", "power", "off"], capture_output=True, text=True)
            elif action == "status":
                result = subprocess.run(["bluetoothctl", "show"], capture_output=True, text=True)
            else:
                return {"success": False, "result": None, "error": "Action must be 'enable', 'disable', or 'status'"}
        
        elif system == "Darwin":  # macOS
            if action == "enable":
                result = subprocess.run(["blueutil", "-p", "1"], capture_output=True, text=True)
            elif action == "disable":
                result = subprocess.run(["blueutil", "-p", "0"], capture_output=True, text=True)
            elif action == "status":
                result = subprocess.run(["blueutil", "-p"], capture_output=True, text=True)
            else:
                return {"success": False, "result": None, "error": "Action must be 'enable', 'disable', or 'status'"}
        
        elif system == "Windows":
            # Windows Bluetooth management requires admin privileges
            return {"success": False, "result": None, "error": "Bluetooth management on Windows requires administrative privileges"}
        
        else:
            return {"success": False, "result": None, "error": f"Unsupported platform: {system}"}
        
        return {
            "success": result.returncode == 0,
            "result": {
                "action": action,
                "platform": system,
                "output": result.stdout.strip() if result.returncode == 0 else None
            },
            "error": result.stderr if result.returncode != 0 else None
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to manage Bluetooth: {str(e)}"}

def manage_wifi(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    if not args or "action" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: action (scan/connect/disconnect/status)"}
    
    try:
        action = args["action"].lower()
        system = platform.system()
        
        if system == "Linux":
            if action == "scan":
                result = subprocess.run(["nmcli", "dev", "wifi", "list"], capture_output=True, text=True)
            elif action == "status":
                result = subprocess.run(["nmcli", "dev", "status"], capture_output=True, text=True)
            elif action == "connect":
                ssid = args.get("ssid")
                password = args.get("password")
                if not ssid:
                    return {"success": False, "result": None, "error": "SSID required for connect action"}
                
                if password:
                    result = subprocess.run(["nmcli", "dev", "wifi", "connect", ssid, "password", password], capture_output=True, text=True)
                else:
                    result = subprocess.run(["nmcli", "dev", "wifi", "connect", ssid], capture_output=True, text=True)
            elif action == "disconnect":
                result = subprocess.run(["nmcli", "dev", "disconnect", "wlan0"], capture_output=True, text=True)
            else:
                return {"success": False, "result": None, "error": "Action must be 'scan', 'connect', 'disconnect', or 'status'"}
        
        elif system == "Darwin":  # macOS
            if action == "scan":
                result = subprocess.run(["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-s"], capture_output=True, text=True)
            elif action == "status":
                result = subprocess.run(["networksetup", "-getairportnetwork", "en0"], capture_output=True, text=True)
            else:
                return {"success": False, "result": None, "error": "Only 'scan' and 'status' actions supported on macOS"}
        
        elif system == "Windows":
            if action == "scan":
                result = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output=True, text=True)
            elif action == "status":
                result = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True)
            else:
                return {"success": False, "result": None, "error": "Only 'scan' and 'status' actions supported on Windows"}
        
        else:
            return {"success": False, "result": None, "error": f"Unsupported platform: {system}"}
        
        return {
            "success": result.returncode == 0,
            "result": {
                "action": action,
                "platform": system,
                "output": result.stdout.strip() if result.returncode == 0 else None
            },
            "error": result.stderr if result.returncode != 0 else None
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to manage Wi-Fi: {str(e)}"}

def set_system_timezone(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    if not args or "timezone" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: timezone"}
    
    try:
        timezone = args["timezone"]
        system = platform.system()
        
        if system == "Linux":
            # Use timedatectl on systemd systems
            result = subprocess.run(["timedatectl", "set-timezone", timezone], capture_output=True, text=True)
        
        elif system == "Darwin":  # macOS
            result = subprocess.run(["sudo", "systemsetup", "-settimezone", timezone], capture_output=True, text=True)
        
        elif system == "Windows":
            result = subprocess.run(["tzutil", "/s", timezone], capture_output=True, text=True)
        
        else:
            return {"success": False, "result": None, "error": f"Unsupported platform: {system}"}
        
        if result.returncode == 0:
            return {
                "success": True,
                "result": {
                    "timezone": timezone,
                    "platform": system,
                    "action": "timezone_changed"
                },
                "error": None
            }
        else:
            return {"success": False, "result": None, "error": f"Failed to set timezone: {result.stderr}"}
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to set system timezone: {str(e)}"}

def get_installed_fonts(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    try:
        system = platform.system()
        fonts = []
        
        if system == "Linux":
            # Use fc-list to get fonts
            result = subprocess.run(["fc-list", ":", "family"], capture_output=True, text=True)
            if result.returncode == 0:
                font_lines = result.stdout.strip().split('\n')
                fonts = sorted(list(set([line.split(',')[0].strip() for line in font_lines if line.strip()])))
        
        elif system == "Darwin":  # macOS
            # Use system_profiler to get fonts
            result = subprocess.run(["system_profiler", "SPFontsDataType", "-json"], capture_output=True, text=True)
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                fonts = [font.get('_name', '') for font in data.get('SPFontsDataType', [])]
                fonts = sorted([f for f in fonts if f])
        
        elif system == "Windows":
            # Use PowerShell to get fonts
            ps_script = "Get-ItemProperty 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Fonts' | Select-Object -Property * | ForEach-Object { $_.PSObject.Properties | Where-Object { $_.Name -notlike 'PS*' } | ForEach-Object { $_.Name } }"
            result = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True)
            if result.returncode == 0:
                font_lines = result.stdout.strip().split('\n')
                fonts = sorted(list(set([line.strip() for line in font_lines if line.strip()])))
        
        return {
            "success": True,
            "result": {
                "fonts": fonts,
                "count": len(fonts),
                "platform": system
            },
            "error": None
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to get installed fonts: {str(e)}"}
