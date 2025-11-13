"""
System Tools - Consolidated smart tools for AI agents
Provides unified system control and information gathering.
"""
from typing import Any, Dict, List
import json
import time

# Try to import Rust engine, fallback to Python implementations
try:
    from que_core_engine import rust_system_query
    from que_core_engine import rust_system_control
    from que_core_engine import rust_process_manager
    # Legacy functions for backward compatibility
    from que_core_engine import get_system_info as rust_get_system_info
    from que_core_engine import get_battery_status as rust_get_battery_status
    from que_core_engine import get_network_info as rust_get_network_info
    from que_core_engine import list_processes as rust_list_processes
    from que_core_engine import get_disk_info as rust_get_disk_info
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False

def system_query(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Universal system information query - replaces multiple system info tools
    
    Args:
        what (str): Type of info to get - 'overview', 'battery', 'network', 'processes', 'memory', 'cpu', 'disk'
        
    Returns:
        Dict with requested system information
    """
    if not args:
        args = {}
    
    what = args.get("what", "overview")
    
    # Try Rust implementation first
    if RUST_AVAILABLE:
        try:
            result_json = rust_system_query(what)
            return json.loads(result_json)
        except Exception as e:
            # Fall back to Python implementation
            pass
    
    # Python fallback implementation
    try:
        import platform
        import psutil
        
        if what == "overview":
            # Get comprehensive system overview
            battery_info = None
            try:
                battery = psutil.sensors_battery()
                if battery:
                    battery_info = {
                        "percent": battery.percent,
                        "plugged": battery.power_plugged,
                        "time_left": battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None
                    }
            except:
                pass
            
            return {
                "success": True,
                "result": {
                    "os": platform.system(),
                    "os_version": platform.version(),
                    "hostname": platform.node(),
                    "architecture": platform.machine(),
                    "cpu_count": psutil.cpu_count(),
                    "memory": {
                        "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                        "available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
                        "used_percent": psutil.virtual_memory().percent
                    },
                    "battery": battery_info,
                    "uptime_hours": round(psutil.boot_time() / 3600, 1) if hasattr(psutil, 'boot_time') else None
                },
                "error": None
            }
            
        elif what == "battery":
            battery = psutil.sensors_battery()
            if battery:
                return {
                    "success": True,
                    "result": {
                        "percent": battery.percent,
                        "plugged": battery.power_plugged,
                        "time_left_minutes": battery.secsleft // 60 if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None,
                        "status": "charging" if battery.power_plugged else "discharging"
                    },
                    "error": None
                }
            else:
                return {"success": False, "result": None, "error": "No battery detected"}
                
        elif what == "memory":
            mem = psutil.virtual_memory()
            return {
                "success": True,
                "result": {
                    "total_gb": round(mem.total / (1024**3), 2),
                    "available_gb": round(mem.available / (1024**3), 2),
                    "used_gb": round(mem.used / (1024**3), 2),
                    "used_percent": mem.percent,
                    "free_gb": round(mem.free / (1024**3), 2)
                },
                "error": None
            }
            
        elif what == "cpu":
            return {
                "success": True,
                "result": {
                    "count": psutil.cpu_count(),
                    "usage_percent": psutil.cpu_percent(interval=1),
                    "frequency_mhz": psutil.cpu_freq().current if psutil.cpu_freq() else None,
                    "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
                },
                "error": None
            }
            
        elif what == "network":
            interfaces = {}
            for interface, stats in psutil.net_io_counters(pernic=True).items():
                interfaces[interface] = {
                    "bytes_sent": stats.bytes_sent,
                    "bytes_recv": stats.bytes_recv,
                    "packets_sent": stats.packets_sent,
                    "packets_recv": stats.packets_recv
                }
            
            return {
                "success": True,
                "result": {
                    "interfaces": interfaces,
                    "total_sent_mb": round(sum(s.bytes_sent for s in psutil.net_io_counters(pernic=True).values()) / (1024**2), 2),
                    "total_recv_mb": round(sum(s.bytes_recv for s in psutil.net_io_counters(pernic=True).values()) / (1024**2), 2)
                },
                "error": None
            }
            
        elif what == "processes":
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status']):
                try:
                    processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cpu_percent": proc.info['cpu_percent'],
                        "memory_mb": round(proc.info['memory_info'].rss / (1024**2), 1) if proc.info['memory_info'] else 0,
                        "status": proc.info['status']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by memory usage
            processes.sort(key=lambda x: x['memory_mb'], reverse=True)
            
            return {
                "success": True,
                "result": {
                    "processes": processes[:50],  # Top 50 processes
                    "total_count": len(processes)
                },
                "error": None
            }
            
        elif what == "disk":
            disks = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "filesystem": partition.fstype,
                        "total_gb": round(usage.total / (1024**3), 2),
                        "used_gb": round(usage.used / (1024**3), 2),
                        "free_gb": round(usage.free / (1024**3), 2),
                        "used_percent": round((usage.used / usage.total) * 100, 1)
                    })
                except PermissionError:
                    continue
            
            return {
                "success": True,
                "result": {"disks": disks},
                "error": None
            }
            
        else:
            return {"success": False, "result": None, "error": f"Unknown query type: {what}. Use: overview, battery, memory, cpu, network, processes, disk"}
            
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to get system info: {str(e)}"}

def system_control(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Universal system control - replaces volume, lock, shutdown tools
    
    Args:
        action (str): Action to perform - 'volume', 'lock', 'shutdown', 'sleep', 'restart'
        level (int): For volume action, level 0-100
        
    Returns:
        Dict with action result
    """
    if not args or "action" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: action"}
    
    action = args["action"]
    
    try:
        import platform
        import subprocess
        import os
        
        system = platform.system()
        
        if action == "volume":
            level = args.get("level", 50)
            if not 0 <= level <= 100:
                return {"success": False, "result": None, "error": "Volume level must be 0-100"}
            
            if system == "Linux":
                # Try different Linux volume controls
                try:
                    subprocess.run(["amixer", "set", "Master", f"{level}%"], check=True, capture_output=True)
                    return {"success": True, "result": {"volume": level}, "error": None}
                except (subprocess.CalledProcessError, FileNotFoundError):
                    try:
                        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{level}%"], check=True, capture_output=True)
                        return {"success": True, "result": {"volume": level}, "error": None}
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        return {"success": False, "result": None, "error": "No volume control found (tried amixer, pactl)"}
            
            elif system == "Darwin":  # macOS
                try:
                    subprocess.run(["osascript", "-e", f"set volume output volume {level}"], check=True)
                    return {"success": True, "result": {"volume": level}, "error": None}
                except subprocess.CalledProcessError:
                    return {"success": False, "result": None, "error": "Failed to set volume on macOS"}
            
            elif system == "Windows":
                # Windows volume control would go here
                return {"success": False, "result": None, "error": "Windows volume control not yet implemented"}
        
        elif action == "lock":
            if system == "Linux":
                # Try different Linux lock commands
                lock_commands = [
                    ["gnome-screensaver-command", "--lock"],
                    ["xdg-screensaver", "lock"],
                    ["loginctl", "lock-session"],
                    ["dm-tool", "lock"]
                ]
                
                for cmd in lock_commands:
                    try:
                        subprocess.run(cmd, check=True, capture_output=True)
                        return {"success": True, "result": {"action": "locked"}, "error": None}
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                
                return {"success": False, "result": None, "error": "No lock command found"}
            
            elif system == "Darwin":  # macOS
                try:
                    subprocess.run(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"], check=True)
                    return {"success": True, "result": {"action": "locked"}, "error": None}
                except subprocess.CalledProcessError:
                    return {"success": False, "result": None, "error": "Failed to lock macOS"}
            
            elif system == "Windows":
                try:
                    subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True)
                    return {"success": True, "result": {"action": "locked"}, "error": None}
                except subprocess.CalledProcessError:
                    return {"success": False, "result": None, "error": "Failed to lock Windows"}
        
        elif action in ["shutdown", "restart", "sleep"]:
            # These are dangerous operations - require confirmation
            confirm = args.get("confirm", False)
            if not confirm:
                return {"success": False, "result": None, "error": f"Dangerous operation '{action}' requires confirm=True"}
            
            if system == "Linux":
                cmd_map = {
                    "shutdown": ["shutdown", "-h", "now"],
                    "restart": ["shutdown", "-r", "now"],
                    "sleep": ["systemctl", "suspend"]
                }
            elif system == "Darwin":  # macOS
                cmd_map = {
                    "shutdown": ["shutdown", "-h", "now"],
                    "restart": ["shutdown", "-r", "now"],
                    "sleep": ["pmset", "sleepnow"]
                }
            elif system == "Windows":
                cmd_map = {
                    "shutdown": ["shutdown", "/s", "/t", "0"],
                    "restart": ["shutdown", "/r", "/t", "0"],
                    "sleep": ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"]
                }
            
            try:
                subprocess.run(cmd_map[action], check=True)
                return {"success": True, "result": {"action": action}, "error": None}
            except subprocess.CalledProcessError as e:
                return {"success": False, "result": None, "error": f"Failed to {action}: {str(e)}"}
        
        else:
            return {"success": False, "result": None, "error": f"Unknown action: {action}. Use: volume, lock, shutdown, restart, sleep"}
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"System control failed: {str(e)}"}

def process_manager(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Universal process management - replaces list_processes, kill_process tools
    
    Args:
        action (str): Action to perform - 'list', 'kill', 'find', 'apps'
        pid (int): Process ID for kill action
        name (str): Process name for find action
        
    Returns:
        Dict with process information or action result
    """
    if not args or "action" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: action"}
    
    action = args["action"]
    
    try:
        import psutil
        
        if action == "list":
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status', 'create_time']):
                try:
                    processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cpu_percent": proc.info['cpu_percent'],
                        "memory_mb": round(proc.info['memory_info'].rss / (1024**2), 1) if proc.info['memory_info'] else 0,
                        "status": proc.info['status'],
                        "running_time_hours": round((psutil.time.time() - proc.info['create_time']) / 3600, 1) if proc.info['create_time'] else 0
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by memory usage
            processes.sort(key=lambda x: x['memory_mb'], reverse=True)
            
            return {
                "success": True,
                "result": {
                    "processes": processes,
                    "total_count": len(processes)
                },
                "error": None
            }
        
        elif action == "apps":
            # List only GUI applications (processes with windows)
            apps = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                try:
                    # Simple heuristic: processes that are likely GUI apps
                    name = proc.info['name'].lower()
                    if any(gui_hint in name for gui_hint in ['chrome', 'firefox', 'code', 'terminal', 'nautilus', 'explorer', 'finder']):
                        apps.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "memory_mb": round(proc.info['memory_info'].rss / (1024**2), 1) if proc.info['memory_info'] else 0
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                "success": True,
                "result": {"apps": apps, "count": len(apps)},
                "error": None
            }
        
        elif action == "find":
            name = args.get("name", "")
            if not name:
                return {"success": False, "result": None, "error": "Missing required argument: name"}
            
            found_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                try:
                    if name.lower() in proc.info['name'].lower():
                        found_processes.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "cpu_percent": proc.info['cpu_percent'],
                            "memory_mb": round(proc.info['memory_info'].rss / (1024**2), 1) if proc.info['memory_info'] else 0
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                "success": True,
                "result": {"processes": found_processes, "count": len(found_processes)},
                "error": None
            }
        
        elif action == "kill":
            pid = args.get("pid")
            if not pid:
                return {"success": False, "result": None, "error": "Missing required argument: pid"}
            
            try:
                proc = psutil.Process(pid)
                proc_name = proc.name()
                proc.terminate()
                
                # Wait a bit for graceful termination
                proc.wait(timeout=3)
                
                return {
                    "success": True,
                    "result": {"killed_process": proc_name, "pid": pid},
                    "error": None
                }
            except psutil.NoSuchProcess:
                return {"success": False, "result": None, "error": f"Process {pid} not found"}
            except psutil.TimeoutExpired:
                # Force kill if graceful termination failed
                try:
                    proc.kill()
                    return {
                        "success": True,
                        "result": {"force_killed_process": proc_name, "pid": pid},
                        "error": None
                    }
                except:
                    return {"success": False, "result": None, "error": f"Failed to kill process {pid}"}
            except psutil.AccessDenied:
                return {"success": False, "result": None, "error": f"Access denied to kill process {pid}"}
        
        else:
            return {"success": False, "result": None, "error": f"Unknown action: {action}. Use: list, apps, find, kill"}
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Process management failed: {str(e)}"}

# Legacy function aliases for backward compatibility
def get_system_info(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use system_query instead"""
    return system_query(args={"what": "overview"})

def get_battery_status(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use system_query instead"""
    return system_query(args={"what": "battery"})

def get_network_info(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use system_query instead"""
    return system_query(args={"what": "network"})

def list_processes(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use process_manager instead"""
    return process_manager(args={"action": "list"})

def set_volume(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use system_control instead"""
    level = args.get("level", 50) if args else 50
    return system_control(args={"action": "volume", "level": level})

def get_volume(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Get current system volume - not yet implemented"""
    return {"success": False, "result": None, "error": "Volume reading not yet implemented"}

def lock_screen(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use system_control instead"""
    return system_control(args={"action": "lock"})

def shutdown_system(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use system_control instead"""
    action = args.get("action", "shutdown") if args else "shutdown"
    confirm = args.get("confirm", False) if args else False
    return system_control(args={"action": action, "confirm": confirm})

def kill_process_by_pid(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use process_manager instead"""
    pid = args.get("pid") if args else None
    return process_manager(args={"action": "kill", "pid": pid})
