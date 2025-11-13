//! Shell tools - High-performance command execution and environment management
//! Consolidated shell operations using Rust for maximum performance

use pyo3::prelude::*;
use serde_json::json;
use std::process::Command;
use std::env;
use std::path::Path;

/// Universal shell executor - consolidated command operations
#[pyfunction]
pub fn rust_shell_execute(action: String, command: Option<String>, package: Option<String>, pid: Option<u32>, program: Option<String>) -> PyResult<String> {
    let result = match action.as_str() {
        "run" => {
            let cmd = command.unwrap_or_default();
            if cmd.is_empty() {
                json!({
                    "success": false,
                    "result": serde_json::Value::Null,
                    "error": "Missing required argument: command"
                })
            } else {
                rust_run_command_impl(&cmd)
            }
        },
        "install" => {
            let pkg = package.unwrap_or_default();
            if pkg.is_empty() {
                json!({
                    "success": false,
                    "result": serde_json::Value::Null,
                    "error": "Missing required argument: package"
                })
            } else {
                rust_install_package_impl(&pkg)
            }
        },
        "kill" => {
            if let Some(process_pid) = pid {
                rust_kill_process_impl(process_pid)
            } else {
                json!({
                    "success": false,
                    "result": serde_json::Value::Null,
                    "error": "Missing required argument: pid"
                })
            }
        },
        "which" => {
            let prog = program.unwrap_or_default();
            if prog.is_empty() {
                json!({
                    "success": false,
                    "result": serde_json::Value::Null,
                    "error": "Missing required argument: program"
                })
            } else {
                rust_which_command_impl(&prog)
            }
        },
        "ps" => {
            rust_list_processes_impl()
        },
        _ => {
            json!({
                "success": false,
                "result": serde_json::Value::Null,
                "error": format!("Unknown action: {}. Use: run, install, kill, which, ps", action)
            })
        }
    };
    
    Ok(result.to_string())
}

/// Development environment manager - consolidated environment operations
#[pyfunction]
pub fn rust_environment_manager(action: String, key: Option<String>, value: Option<String>, path: Option<String>) -> PyResult<String> {
    let result = match action.as_str() {
        "get_env" => {
            let env_key = key.unwrap_or_default();
            if env_key.is_empty() {
                json!({
                    "success": false,
                    "result": serde_json::Value::Null,
                    "error": "Missing required argument: key"
                })
            } else {
                rust_get_env_var_impl(&env_key)
            }
        },
        "set_env" => {
            let env_key = key.unwrap_or_default();
            if env_key.is_empty() {
                json!({
                    "success": false,
                    "result": serde_json::Value::Null,
                    "error": "Missing required argument: key"
                })
            } else {
                rust_set_env_var_impl(&env_key, value.as_deref())
            }
        },
        "list_env" => {
            rust_list_env_vars_impl()
        },
        "get_cwd" => {
            rust_get_current_directory_impl()
        },
        "change_dir" => {
            let dir_path = path.unwrap_or_default();
            if dir_path.is_empty() {
                json!({
                    "success": false,
                    "result": serde_json::Value::Null,
                    "error": "Missing required argument: path"
                })
            } else {
                rust_change_directory_impl(&dir_path)
            }
        },
        "create_venv" => {
            let venv_name = key.unwrap_or_default(); // Using key as name for venv
            if venv_name.is_empty() {
                json!({
                    "success": false,
                    "result": serde_json::Value::Null,
                    "error": "Missing required argument: name (use key parameter)"
                })
            } else {
                rust_create_virtual_env_impl(&venv_name, path.as_deref())
            }
        },
        _ => {
            json!({
                "success": false,
                "result": serde_json::Value::Null,
                "error": format!("Unknown action: {}. Use: get_env, set_env, list_env, get_cwd, change_dir, create_venv", action)
            })
        }
    };
    
    Ok(result.to_string())
}

// Implementation helpers
fn rust_run_command_impl(command: &str) -> serde_json::Value {
    // Security: Basic command validation
    let dangerous_commands = ["rm -rf /", "dd if=", "mkfs", "fdisk", "format", "sudo rm -rf"];
    for dangerous in &dangerous_commands {
        if command.to_lowercase().contains(dangerous) {
            return json!({
                "success": false,
                "result": serde_json::Value::Null,
                "error": "Dangerous command blocked for safety"
            });
        }
    }
    
    // Execute command based on platform
    let output = if cfg!(target_os = "windows") {
        Command::new("cmd")
            .args(["/C", command])
            .output()
    } else {
        Command::new("sh")
            .arg("-c")
            .arg(command)
            .output()
    };
    
    match output {
        Ok(result) => {
            let stdout = String::from_utf8_lossy(&result.stdout);
            let stderr = String::from_utf8_lossy(&result.stderr);
            let success = result.status.success();
            
            json!({
                "success": success,
                "result": {
                    "command": command,
                    "return_code": result.status.code().unwrap_or(-1),
                    "stdout": stdout,
                    "stderr": stderr,
                    "method": "rust_shell_execute"
                },
                "error": if success { serde_json::Value::Null } else { json!(stderr) }
            })
        },
        Err(e) => {
            json!({
                "success": false,
                "result": serde_json::Value::Null,
                "error": format!("Failed to execute command: {}", e)
            })
        }
    }
}

fn rust_install_package_impl(package: &str) -> serde_json::Value {
    // Determine package manager based on platform and available tools
    let package_manager = if cfg!(target_os = "windows") {
        "pip"
    } else if cfg!(target_os = "macos") {
        "brew"
    } else {
        // Linux - detect available package manager
        if Path::new("/usr/bin/apt").exists() {
            "apt"
        } else if Path::new("/usr/bin/yum").exists() {
            "yum"
        } else if Path::new("/usr/bin/dnf").exists() {
            "dnf"
        } else if Path::new("/usr/bin/pacman").exists() {
            "pacman"
        } else {
            "pip"
        }
    };
    
    // Build install command
    let command = match package_manager {
        "apt" => format!("sudo apt update && sudo apt install -y {}", package),
        "yum" => format!("sudo yum install -y {}", package),
        "dnf" => format!("sudo dnf install -y {}", package),
        "pacman" => format!("sudo pacman -S --noconfirm {}", package),
        "brew" => format!("brew install {}", package),
        "pip" => format!("pip install {}", package),
        _ => format!("pip install {}", package),
    };
    
    // Execute install command
    let output = if cfg!(target_os = "windows") {
        Command::new("cmd")
            .args(["/C", &command])
            .output()
    } else {
        Command::new("sh")
            .arg("-c")
            .arg(&command)
            .output()
    };
    
    match output {
        Ok(result) => {
            let stdout = String::from_utf8_lossy(&result.stdout);
            let stderr = String::from_utf8_lossy(&result.stderr);
            let success = result.status.success();
            
            json!({
                "success": success,
                "result": {
                    "package": package,
                    "package_manager": package_manager,
                    "command": command,
                    "return_code": result.status.code().unwrap_or(-1),
                    "stdout": stdout,
                    "stderr": stderr,
                    "method": "rust_package_install"
                },
                "error": if success { serde_json::Value::Null } else { json!(stderr) }
            })
        },
        Err(e) => {
            json!({
                "success": false,
                "result": serde_json::Value::Null,
                "error": format!("Failed to install package: {}", e)
            })
        }
    }
}

fn rust_kill_process_impl(pid: u32) -> serde_json::Value {
    // Use platform-specific process killing
    let command = if cfg!(target_os = "windows") {
        format!("taskkill /PID {} /F", pid)
    } else {
        format!("kill -TERM {}", pid)
    };
    
    let output = if cfg!(target_os = "windows") {
        Command::new("cmd")
            .args(["/C", &command])
            .output()
    } else {
        Command::new("sh")
            .arg("-c")
            .arg(&command)
            .output()
    };
    
    match output {
        Ok(result) => {
            let success = result.status.success();
            let stderr = String::from_utf8_lossy(&result.stderr);
            
            json!({
                "success": success,
                "result": {
                    "pid": pid,
                    "command": command,
                    "killed": success,
                    "method": "rust_process_kill"
                },
                "error": if success { serde_json::Value::Null } else { json!(stderr) }
            })
        },
        Err(e) => {
            json!({
                "success": false,
                "result": serde_json::Value::Null,
                "error": format!("Failed to kill process: {}", e)
            })
        }
    }
}

fn rust_which_command_impl(program: &str) -> serde_json::Value {
    // Use platform-specific which command
    let command = if cfg!(target_os = "windows") {
        format!("where {}", program)
    } else {
        format!("which {}", program)
    };
    
    let output = if cfg!(target_os = "windows") {
        Command::new("cmd")
            .args(["/C", &command])
            .output()
    } else {
        Command::new("sh")
            .arg("-c")
            .arg(&command)
            .output()
    };
    
    match output {
        Ok(result) => {
            let success = result.status.success();
            let stdout = String::from_utf8_lossy(&result.stdout).trim().to_string();
            
            if success && !stdout.is_empty() {
                // Get file info if path exists
                let path = Path::new(&stdout);
                let (exists, executable, size) = if path.exists() {
                    let metadata = path.metadata().unwrap_or_else(|_| {
                        std::fs::metadata("/dev/null").unwrap() // Fallback
                    });
                    (true, true, metadata.len()) // Assume executable if found
                } else {
                    (false, false, 0)
                };
                
                json!({
                    "success": true,
                    "result": {
                        "program": program,
                        "path": stdout,
                        "exists": exists,
                        "executable": executable,
                        "size": size,
                        "method": "rust_which_locate"
                    },
                    "error": serde_json::Value::Null
                })
            } else {
                json!({
                    "success": false,
                    "result": {
                        "program": program,
                        "path": serde_json::Value::Null,
                        "exists": false
                    },
                    "error": format!("Program '{}' not found in PATH", program)
                })
            }
        },
        Err(e) => {
            json!({
                "success": false,
                "result": serde_json::Value::Null,
                "error": format!("Failed to locate program: {}", e)
            })
        }
    }
}

fn rust_list_processes_impl() -> serde_json::Value {
    // Use platform-specific process listing
    let command = if cfg!(target_os = "windows") {
        "tasklist /FO CSV"
    } else {
        "ps aux"
    };
    
    let output = if cfg!(target_os = "windows") {
        Command::new("cmd")
            .args(["/C", command])
            .output()
    } else {
        Command::new("sh")
            .arg("-c")
            .arg(command)
            .output()
    };
    
    match output {
        Ok(result) => {
            let success = result.status.success();
            let stdout = String::from_utf8_lossy(&result.stdout);
            
            if success {
                // Parse process list (basic implementation)
                let lines: Vec<&str> = stdout.lines().collect();
                let process_count = lines.len().saturating_sub(1); // Subtract header
                
                json!({
                    "success": true,
                    "result": {
                        "processes": stdout,
                        "total_found": process_count,
                        "method": "rust_process_list",
                        "raw_output": true
                    },
                    "error": serde_json::Value::Null
                })
            } else {
                let stderr = String::from_utf8_lossy(&result.stderr);
                json!({
                    "success": false,
                    "result": serde_json::Value::Null,
                    "error": stderr
                })
            }
        },
        Err(e) => {
            json!({
                "success": false,
                "result": serde_json::Value::Null,
                "error": format!("Failed to list processes: {}", e)
            })
        }
    }
}

fn rust_get_env_var_impl(key: &str) -> serde_json::Value {
    match env::var(key) {
        Ok(value) => {
            json!({
                "success": true,
                "result": {
                    "key": key,
                    "value": value,
                    "exists": true,
                    "method": "rust_env_get"
                },
                "error": serde_json::Value::Null
            })
        },
        Err(_) => {
            json!({
                "success": true,
                "result": {
                    "key": key,
                    "value": serde_json::Value::Null,
                    "exists": false,
                    "method": "rust_env_get"
                },
                "error": serde_json::Value::Null
            })
        }
    }
}

fn rust_set_env_var_impl(key: &str, value: Option<&str>) -> serde_json::Value {
    match value {
        Some(val) => {
            env::set_var(key, val);
            json!({
                "success": true,
                "result": {
                    "key": key,
                    "value": val,
                    "action": "set",
                    "method": "rust_env_set"
                },
                "error": serde_json::Value::Null
            })
        },
        None => {
            env::remove_var(key);
            json!({
                "success": true,
                "result": {
                    "key": key,
                    "value": serde_json::Value::Null,
                    "action": "removed",
                    "method": "rust_env_set"
                },
                "error": serde_json::Value::Null
            })
        }
    }
}

fn rust_list_env_vars_impl() -> serde_json::Value {
    let mut env_vars = std::collections::HashMap::new();
    
    for (key, value) in env::vars() {
        env_vars.insert(key, value);
    }
    
    json!({
        "success": true,
        "result": {
            "environment_variables": env_vars,
            "count": env_vars.len(),
            "method": "rust_env_list"
        },
        "error": serde_json::Value::Null
    })
}

fn rust_get_current_directory_impl() -> serde_json::Value {
    match env::current_dir() {
        Ok(path) => {
            let path_str = path.to_string_lossy().to_string();
            json!({
                "success": true,
                "result": {
                    "current_directory": path_str,
                    "absolute_path": path_str,
                    "exists": path.exists(),
                    "method": "rust_cwd_get"
                },
                "error": serde_json::Value::Null
            })
        },
        Err(e) => {
            json!({
                "success": false,
                "result": serde_json::Value::Null,
                "error": format!("Failed to get current directory: {}", e)
            })
        }
    }
}

fn rust_change_directory_impl(path: &str) -> serde_json::Value {
    let old_cwd = env::current_dir()
        .map(|p| p.to_string_lossy().to_string())
        .unwrap_or_else(|_| "unknown".to_string());
    
    let target_path = Path::new(path);
    
    if !target_path.exists() {
        return json!({
            "success": false,
            "result": serde_json::Value::Null,
            "error": format!("Directory does not exist: {}", path)
        });
    }
    
    if !target_path.is_dir() {
        return json!({
            "success": false,
            "result": serde_json::Value::Null,
            "error": format!("Path is not a directory: {}", path)
        });
    }
    
    match env::set_current_dir(target_path) {
        Ok(_) => {
            let new_cwd = env::current_dir()
                .map(|p| p.to_string_lossy().to_string())
                .unwrap_or_else(|_| path.to_string());
            
            json!({
                "success": true,
                "result": {
                    "old_directory": old_cwd,
                    "new_directory": new_cwd,
                    "changed": true,
                    "method": "rust_cwd_change"
                },
                "error": serde_json::Value::Null
            })
        },
        Err(e) => {
            json!({
                "success": false,
                "result": serde_json::Value::Null,
                "error": format!("Failed to change directory: {}", e)
            })
        }
    }
}

fn rust_create_virtual_env_impl(name: &str, path: Option<&str>) -> serde_json::Value {
    let base_path = path.unwrap_or(".");
    let venv_path = Path::new(base_path).join(name);
    
    if venv_path.exists() {
        return json!({
            "success": false,
            "result": serde_json::Value::Null,
            "error": format!("Virtual environment already exists: {}", venv_path.display())
        });
    }
    
    // Create virtual environment using python -m venv
    let command = format!("python3 -m venv {}", venv_path.display());
    
    let output = if cfg!(target_os = "windows") {
        Command::new("cmd")
            .args(["/C", &command])
            .output()
    } else {
        Command::new("sh")
            .arg("-c")
            .arg(&command)
            .output()
    };
    
    match output {
        Ok(result) => {
            let success = result.status.success();
            
            if success {
                // Determine activation script path
                let activate_script = if cfg!(target_os = "windows") {
                    venv_path.join("Scripts").join("activate.bat")
                } else {
                    venv_path.join("bin").join("activate")
                };
                
                json!({
                    "success": true,
                    "result": {
                        "name": name,
                        "path": venv_path.to_string_lossy(),
                        "activate_script": activate_script.to_string_lossy(),
                        "created": true,
                        "method": "rust_venv_create"
                    },
                    "error": serde_json::Value::Null
                })
            } else {
                let stderr = String::from_utf8_lossy(&result.stderr);
                json!({
                    "success": false,
                    "result": serde_json::Value::Null,
                    "error": format!("Failed to create virtual environment: {}", stderr)
                })
            }
        },
        Err(e) => {
            json!({
                "success": false,
                "result": serde_json::Value::Null,
                "error": format!("Failed to execute venv creation: {}", e)
            })
        }
    }
}
