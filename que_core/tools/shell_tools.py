"""
Shell Tools - Consolidated command execution and environment management for AI agents
Provides unified shell operations and development environment control.
"""
from typing import Any, Dict, List
import subprocess
import os
import platform
import shlex
import psutil
import json

# Try to import Rust engine for high-performance shell operations
try:
    from que_core_engine import rust_shell_execute, rust_environment_manager
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False

def shell_execute(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Universal shell executor - replaces run_command, install_package, kill_process_by_pid, which_command
    
    Args:
        action (str): Action to perform - 'run', 'install', 'kill', 'which', 'ps'
        command (str): Command to run (for 'run' action)
        package (str): Package to install (for 'install' action)
        pid (int): Process ID to kill (for 'kill' action)
        program (str): Program to locate (for 'which' action)
        
    Returns:
        Dict with operation result
    """
    if not args:
        return {"success": False, "result": None, "error": "Missing required arguments"}
    
    action = args.get("action", "run")
    
    # Try Rust implementation first for performance
    if RUST_AVAILABLE:
        try:
            command = args.get("command")
            package = args.get("package")
            pid = args.get("pid")
            program = args.get("program")
            
            result_json = rust_shell_execute(action, command, package, pid, program)
            return json.loads(result_json)
        except Exception:
            # Fall back to Python implementation
            pass
    
    # Python fallback implementation
    try:
        if action == "run":
            return _run_command_impl(args)
        elif action == "install":
            return _install_package_impl(args)
        elif action == "kill":
            return _kill_process_impl(args)
        elif action == "which":
            return _which_command_impl(args)
        elif action == "ps":
            return _list_processes_impl(args)
        else:
            return {
                "success": False,
                "result": None,
                "error": f"Unknown action: {action}. Use: run, install, kill, which, ps"
            }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Shell operation failed: {str(e)}"}

def environment_manager(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Development environment manager - replaces get_env_vars, set_env_var, get_current_directory, change_directory, create_virtual_env
    
    Args:
        action (str): Action to perform - 'get_env', 'set_env', 'get_cwd', 'change_dir', 'create_venv', 'list_env'
        key (str): Environment variable name
        value (str): Environment variable value
        path (str): Directory path
        name (str): Virtual environment name
        
    Returns:
        Dict with operation result
    """
    if not args or "action" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: action"}
    
    action = args["action"]
    
    # Try Rust implementation first for performance
    if RUST_AVAILABLE:
        try:
            key = args.get("key")
            value = args.get("value")
            path = args.get("path")
            
            result_json = rust_environment_manager(action, key, value, path)
            return json.loads(result_json)
        except Exception:
            # Fall back to Python implementation
            pass
    
    # Python fallback implementation
    try:
        if action == "get_env":
            return _get_env_var_impl(args)
        elif action == "set_env":
            return _set_env_var_impl(args)
        elif action == "list_env":
            return _list_env_vars_impl(args)
        elif action == "get_cwd":
            return _get_current_directory_impl(args)
        elif action == "change_dir":
            return _change_directory_impl(args)
        elif action == "create_venv":
            return _create_virtual_env_impl(args)
        else:
            return {
                "success": False,
                "result": None,
                "error": f"Unknown action: {action}. Use: get_env, set_env, list_env, get_cwd, change_dir, create_venv"
            }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Environment operation failed: {str(e)}"}

# Implementation helpers
def _run_command_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Run command implementation"""
    command = args.get("command")
    if not command:
        return {"success": False, "result": None, "error": "Missing required argument: command"}
    
    try:
        timeout = args.get("timeout", 30)
        cwd = args.get("cwd", None)
        shell = args.get("shell", True)
        capture_output = args.get("capture_output", True)
        
        # Security: Basic command validation
        dangerous_commands = ['rm -rf /', 'dd if=', 'mkfs', 'fdisk', 'format', 'sudo rm -rf']
        if any(dangerous in command.lower() for dangerous in dangerous_commands):
            return {"success": False, "result": None, "error": "Dangerous command blocked for safety"}
        
        # Run the command
        if shell:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                cwd=cwd
            )
        else:
            # Split command for non-shell execution
            cmd_parts = shlex.split(command)
            result = subprocess.run(
                cmd_parts,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                cwd=cwd
            )
        
        return {
            "success": result.returncode == 0,
            "result": {
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout if capture_output else None,
                "stderr": result.stderr if capture_output else None,
                "cwd": cwd,
                "method": "shell_execute"
            },
            "error": result.stderr if result.returncode != 0 and capture_output else None
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "result": None, "error": f"Command timed out after {timeout} seconds"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to run command: {str(e)}"}

def _install_package_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Install package implementation"""
    package = args.get("package")
    if not package:
        return {"success": False, "result": None, "error": "Missing required argument: package"}
    
    try:
        package_manager = args.get("package_manager", "auto")
        system = platform.system()
        
        # Determine package manager
        if package_manager == "auto":
            if system == "Linux":
                # Check which package manager is available
                if os.path.exists("/usr/bin/apt"):
                    package_manager = "apt"
                elif os.path.exists("/usr/bin/yum"):
                    package_manager = "yum"
                elif os.path.exists("/usr/bin/pacman"):
                    package_manager = "pacman"
                elif os.path.exists("/usr/bin/dnf"):
                    package_manager = "dnf"
                else:
                    package_manager = "pip"
            elif system == "Darwin":
                package_manager = "brew"
            elif system == "Windows":
                package_manager = "pip"
            else:
                package_manager = "pip"
        
        # Build install command
        if package_manager == "apt":
            command = f"sudo apt update && sudo apt install -y {package}"
        elif package_manager == "yum":
            command = f"sudo yum install -y {package}"
        elif package_manager == "dnf":
            command = f"sudo dnf install -y {package}"
        elif package_manager == "pacman":
            command = f"sudo pacman -S --noconfirm {package}"
        elif package_manager == "brew":
            command = f"brew install {package}"
        elif package_manager == "pip":
            command = f"pip install {package}"
        elif package_manager == "pip3":
            command = f"pip3 install {package}"
        else:
            return {"success": False, "result": None, "error": f"Unsupported package manager: {package_manager}"}
        
        # Execute install command
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes for package installation
        )
        
        return {
            "success": result.returncode == 0,
            "result": {
                "package": package,
                "package_manager": package_manager,
                "command": command,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "method": "package_install"
            },
            "error": result.stderr if result.returncode != 0 else None
        }
        
    except subprocess.TimeoutExpired:
        return {"success": False, "result": None, "error": "Package installation timed out after 5 minutes"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to install package: {str(e)}"}

def _kill_process_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Kill process implementation"""
    pid = args.get("pid")
    name = args.get("name")
    
    if not pid and not name:
        return {"success": False, "result": None, "error": "Missing required argument: pid or name"}
    
    try:
        killed_processes = []
        
        if pid:
            # Kill by PID
            try:
                process = psutil.Process(pid)
                process_info = {
                    "pid": process.pid,
                    "name": process.name(),
                    "cmdline": " ".join(process.cmdline())
                }
                process.terminate()
                killed_processes.append(process_info)
            except psutil.NoSuchProcess:
                return {"success": False, "result": None, "error": f"Process with PID {pid} not found"}
            except psutil.AccessDenied:
                return {"success": False, "result": None, "error": f"Access denied to process {pid}"}
        
        elif name:
            # Kill by name
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if name.lower() in proc.info['name'].lower():
                        proc.terminate()
                        killed_processes.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "cmdline": " ".join(proc.info['cmdline'] or [])
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        if killed_processes:
            return {
                "success": True,
                "result": {
                    "killed_processes": killed_processes,
                    "count": len(killed_processes),
                    "method": "process_kill"
                },
                "error": None
            }
        else:
            return {"success": False, "result": None, "error": f"No processes found to kill"}
        
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to kill process: {str(e)}"}

def _which_command_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Which command implementation"""
    program = args.get("program")
    if not program:
        return {"success": False, "result": None, "error": "Missing required argument: program"}
    
    try:
        import shutil
        
        # Use shutil.which for cross-platform compatibility
        path = shutil.which(program)
        
        if path:
            # Get additional info about the executable
            stat_info = os.stat(path)
            
            return {
                "success": True,
                "result": {
                    "program": program,
                    "path": path,
                    "exists": True,
                    "executable": os.access(path, os.X_OK),
                    "size": stat_info.st_size,
                    "method": "which_locate"
                },
                "error": None
            }
        else:
            return {
                "success": False,
                "result": {
                    "program": program,
                    "path": None,
                    "exists": False
                },
                "error": f"Program '{program}' not found in PATH"
            }
        
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to locate program: {str(e)}"}

def _list_processes_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """List processes implementation"""
    try:
        filter_name = args.get("filter", "")
        limit = args.get("limit", 20)
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent', 'status']):
            try:
                if not filter_name or filter_name.lower() in proc.info['name'].lower():
                    processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "memory_mb": round(proc.info['memory_info'].rss / 1024 / 1024, 1),
                        "cpu_percent": proc.info['cpu_percent'],
                        "status": proc.info['status']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort by memory usage
        processes.sort(key=lambda x: x['memory_mb'], reverse=True)
        
        return {
            "success": True,
            "result": {
                "processes": processes[:limit],
                "total_found": len(processes),
                "filter": filter_name,
                "method": "process_list"
            },
            "error": None
        }
        
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to list processes: {str(e)}"}

def _get_env_var_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get environment variable implementation"""
    key = args.get("key")
    if not key:
        return {"success": False, "result": None, "error": "Missing required argument: key"}
    
    try:
        value = os.environ.get(key)
        
        return {
            "success": True,
            "result": {
                "key": key,
                "value": value,
                "exists": value is not None,
                "method": "env_get"
            },
            "error": None
        }
        
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to get environment variable: {str(e)}"}

def _set_env_var_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Set environment variable implementation"""
    key = args.get("key")
    value = args.get("value")
    
    if not key:
        return {"success": False, "result": None, "error": "Missing required argument: key"}
    
    try:
        # Set for current process
        if value is not None:
            os.environ[key] = str(value)
        else:
            # Remove if value is None
            if key in os.environ:
                del os.environ[key]
        
        return {
            "success": True,
            "result": {
                "key": key,
                "value": value,
                "action": "removed" if value is None else "set",
                "method": "env_set"
            },
            "error": None
        }
        
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to set environment variable: {str(e)}"}

def _list_env_vars_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """List environment variables implementation"""
    try:
        filter_key = args.get("filter", "")
        
        env_vars = {}
        for key, value in os.environ.items():
            if not filter_key or filter_key.lower() in key.lower():
                env_vars[key] = value
        
        return {
            "success": True,
            "result": {
                "environment_variables": env_vars,
                "count": len(env_vars),
                "filter": filter_key,
                "method": "env_list"
            },
            "error": None
        }
        
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to list environment variables: {str(e)}"}

def _get_current_directory_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get current directory implementation"""
    try:
        cwd = os.getcwd()
        
        return {
            "success": True,
            "result": {
                "current_directory": cwd,
                "absolute_path": os.path.abspath(cwd),
                "exists": os.path.exists(cwd),
                "method": "cwd_get"
            },
            "error": None
        }
        
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to get current directory: {str(e)}"}

def _change_directory_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Change directory implementation"""
    path = args.get("path")
    if not path:
        return {"success": False, "result": None, "error": "Missing required argument: path"}
    
    try:
        old_cwd = os.getcwd()
        
        # Expand user path
        path = os.path.expanduser(path)
        
        if not os.path.exists(path):
            return {"success": False, "result": None, "error": f"Directory does not exist: {path}"}
        
        if not os.path.isdir(path):
            return {"success": False, "result": None, "error": f"Path is not a directory: {path}"}
        
        os.chdir(path)
        new_cwd = os.getcwd()
        
        return {
            "success": True,
            "result": {
                "old_directory": old_cwd,
                "new_directory": new_cwd,
                "changed": True,
                "method": "cwd_change"
            },
            "error": None
        }
        
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to change directory: {str(e)}"}

def _create_virtual_env_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Create virtual environment implementation"""
    name = args.get("name")
    if not name:
        return {"success": False, "result": None, "error": "Missing required argument: name"}
    
    try:
        path = args.get("path", ".")
        python_version = args.get("python_version", "python3")
        
        # Create full path for venv
        venv_path = os.path.join(path, name)
        
        if os.path.exists(venv_path):
            return {"success": False, "result": None, "error": f"Virtual environment already exists: {venv_path}"}
        
        # Create virtual environment
        command = f"{python_version} -m venv {venv_path}"
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            # Get activation script path
            if platform.system() == "Windows":
                activate_script = os.path.join(venv_path, "Scripts", "activate.bat")
            else:
                activate_script = os.path.join(venv_path, "bin", "activate")
            
            return {
                "success": True,
                "result": {
                    "name": name,
                    "path": venv_path,
                    "activate_script": activate_script,
                    "python_version": python_version,
                    "created": True,
                    "method": "venv_create"
                },
                "error": None
            }
        else:
            return {"success": False, "result": None, "error": f"Failed to create virtual environment: {result.stderr}"}
        
    except subprocess.TimeoutExpired:
        return {"success": False, "result": None, "error": "Virtual environment creation timed out"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to create virtual environment: {str(e)}"}

# Legacy function aliases for backward compatibility
def run_command(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use shell_execute instead"""
    return shell_execute(args={"action": "run", **(args or {})})

def install_package(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use shell_execute instead"""
    return shell_execute(args={"action": "install", **(args or {})})

def kill_process_by_pid(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use shell_execute instead"""
    return shell_execute(args={"action": "kill", **(args or {})})

def get_env_vars(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use environment_manager instead"""
    return environment_manager(args={"action": "list_env", **(args or {})})

def set_env_var(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use environment_manager instead"""
    return environment_manager(args={"action": "set_env", **(args or {})})

def start_shell_session(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use shell_execute instead"""
    return {"success": False, "result": None, "error": "Interactive shell sessions not supported. Use shell_execute for commands."}
