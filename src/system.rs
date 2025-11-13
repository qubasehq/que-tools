//! System tools - System information and control
//! High-performance system operations using Rust

use pyo3::prelude::*;
use serde_json::json;
use sysinfo::System;

/// Universal system query - consolidated system information tool
#[pyfunction]
pub fn rust_system_query(what: String) -> PyResult<String> {
    let mut sys = System::new_all();
    sys.refresh_all();
    
    let result = match what.as_str() {
        "overview" => {
            json!({
                "success": true,
                "result": {
                    "os": System::name().unwrap_or_else(|| "Unknown".to_string()),
                    "os_version": System::os_version().unwrap_or_else(|| "Unknown".to_string()),
                    "hostname": System::host_name().unwrap_or_else(|| "Unknown".to_string()),
                    "architecture": std::env::consts::ARCH,
                    "cpu_count": sys.cpus().len(),
                    "memory": {
                        "total_gb": (sys.total_memory() as f64 / (1024.0 * 1024.0 * 1024.0) * 100.0).round() / 100.0,
                        "available_gb": (sys.available_memory() as f64 / (1024.0 * 1024.0 * 1024.0) * 100.0).round() / 100.0,
                        "used_percent": ((sys.used_memory() as f64 / sys.total_memory() as f64) * 100.0).round()
                    },
                    "uptime_hours": (System::uptime() as f64 / 3600.0 * 10.0).round() / 10.0
                },
                "error": null
            })
        },
        "memory" => {
            json!({
                "success": true,
                "result": {
                    "total_gb": (sys.total_memory() as f64 / (1024.0 * 1024.0 * 1024.0) * 100.0).round() / 100.0,
                    "available_gb": (sys.available_memory() as f64 / (1024.0 * 1024.0 * 1024.0) * 100.0).round() / 100.0,
                    "used_gb": (sys.used_memory() as f64 / (1024.0 * 1024.0 * 1024.0) * 100.0).round() / 100.0,
                    "used_percent": ((sys.used_memory() as f64 / sys.total_memory() as f64) * 100.0).round(),
                    "free_gb": ((sys.total_memory() - sys.used_memory()) as f64 / (1024.0 * 1024.0 * 1024.0) * 100.0).round() / 100.0
                },
                "error": null
            })
        },
        "cpu" => {
            json!({
                "success": true,
                "result": {
                    "count": sys.cpus().len(),
                    "brand": sys.cpus().first().map(|cpu| cpu.brand()).unwrap_or("Unknown"),
                    "frequency_mhz": sys.cpus().first().map(|cpu| cpu.frequency()).unwrap_or(0),
                    "usage_percent": sys.global_cpu_info().cpu_usage()
                },
                "error": null
            })
        },
        "processes" => {
            let mut processes = Vec::new();
            for (pid, process) in sys.processes() {
                processes.push(json!({
                    "pid": pid.as_u32(),
                    "name": process.name(),
                    "cpu_percent": process.cpu_usage(),
                    "memory_mb": (process.memory() as f64 / (1024.0 * 1024.0) * 10.0).round() / 10.0,
                    "status": format!("{:?}", process.status())
                }));
            }
            
            // Sort by memory usage (top 50)
            processes.sort_by(|a, b| {
                let mem_a = a["memory_mb"].as_f64().unwrap_or(0.0);
                let mem_b = b["memory_mb"].as_f64().unwrap_or(0.0);
                mem_b.partial_cmp(&mem_a).unwrap_or(std::cmp::Ordering::Equal)
            });
            processes.truncate(50);
            
            json!({
                "success": true,
                "result": {
                    "processes": processes,
                    "total_count": sys.processes().len()
                },
                "error": null
            })
        },
        "battery" => {
            // Get battery information using system commands
            use std::process::Command;
            use std::fs;
            
            // Try Linux battery paths first
            let mut batteries = Vec::new();
            
            // Check /sys/class/power_supply/ for battery info
            if let Ok(entries) = fs::read_dir("/sys/class/power_supply/") {
                for entry in entries.flatten() {
                    let path = entry.path();
                    let name = path.file_name().unwrap().to_string_lossy();
                    
                    if name.starts_with("BAT") {
                        let capacity_path = path.join("capacity");
                        let status_path = path.join("status");
                        
                        let level = fs::read_to_string(&capacity_path)
                            .ok()
                            .and_then(|s| s.trim().parse::<u8>().ok())
                            .unwrap_or(0);
                            
                        let status = fs::read_to_string(&status_path)
                            .ok()
                            .map(|s| s.trim().to_string())
                            .unwrap_or_else(|| "Unknown".to_string());
                        
                        batteries.push(json!({
                            "name": name,
                            "level": level,
                            "status": status,
                            "health": 100, // Default health
                            "method": "linux_sysfs"
                        }));
                    }
                }
            }
            
            // If no batteries found via sysfs, try acpi command
            if batteries.is_empty() {
                if let Ok(output) = Command::new("acpi").arg("-b").output() {
                    if output.status.success() {
                        let acpi_output = String::from_utf8_lossy(&output.stdout);
                        for line in acpi_output.lines() {
                            if line.contains("Battery") {
                                // Parse ACPI output: "Battery 0: Discharging, 85%, 02:15:30 remaining"
                                let parts: Vec<&str> = line.split(',').collect();
                                if parts.len() >= 2 {
                                    let status = if line.contains("Charging") { "Charging" }
                                               else if line.contains("Discharging") { "Discharging" }
                                               else if line.contains("Full") { "Full" }
                                               else { "Unknown" };
                                    
                                    let level = parts[1].trim()
                                        .replace('%', "")
                                        .parse::<u8>()
                                        .unwrap_or(0);
                                    
                                    batteries.push(json!({
                                        "name": "BAT0",
                                        "level": level,
                                        "status": status,
                                        "health": 100,
                                        "method": "linux_acpi"
                                    }));
                                }
                            }
                        }
                    }
                }
            }
            
            if batteries.is_empty() {
                json!({
                    "success": true,
                    "result": {
                        "batteries": [],
                        "count": 0,
                        "has_battery": false,
                        "message": "No battery detected - likely desktop system",
                        "method": "rust_system_commands"
                    },
                    "error": null
                })
            } else {
                let primary_battery = &batteries[0];
                json!({
                    "success": true,
                    "result": {
                        "batteries": batteries,
                        "count": batteries.len(),
                        "has_battery": true,
                        "primary_level": primary_battery["level"],
                        "primary_status": primary_battery["status"],
                        "method": "rust_system_commands"
                    },
                    "error": null
                })
            }
        },
        "network" => {
            json!({
                "success": true,
                "result": {
                    "interfaces": [],
                    "note": "Network interface details not available in current sysinfo version"
                },
                "error": null
            })
        },
        "disk" => {
            json!({
                "success": true,
                "result": {
                    "disks": [],
                    "note": "Disk information not available in current sysinfo version"
                },
                "error": null
            })
        },
        _ => {
            json!({
                "success": false,
                "result": null,
                "error": format!("Unknown query type: {}. Use: overview, battery, memory, cpu, network, processes, disk", what)
            })
        }
    };
    
    Ok(result.to_string())
}

/// Universal system control - consolidated system control tool
#[pyfunction]
pub fn rust_system_control(action: String, level: Option<i32>, confirm: Option<bool>) -> PyResult<String> {
    let result = match action.as_str() {
        "volume" => {
            let vol_level = level.unwrap_or(50);
            if vol_level < 0 || vol_level > 100 {
                json!({
                    "success": false,
                    "result": null,
                    "error": "Volume level must be 0-100"
                })
            } else {
                // Platform-specific volume control would go here
                json!({
                    "success": false,
                    "result": null,
                    "error": "Volume control not yet implemented in Rust backend"
                })
            }
        },
        "lock" => {
            json!({
                "success": false,
                "result": null,
                "error": "Screen lock not yet implemented in Rust backend"
            })
        },
        "shutdown" | "restart" | "sleep" => {
            let confirmed = confirm.unwrap_or(false);
            if !confirmed {
                json!({
                    "success": false,
                    "result": null,
                    "error": format!("Dangerous operation '{}' requires confirm=true", action)
                })
            } else {
                json!({
                    "success": false,
                    "result": null,
                    "error": format!("{} not yet implemented in Rust backend", action)
                })
            }
        },
        _ => {
            json!({
                "success": false,
                "result": null,
                "error": format!("Unknown action: {}. Use: volume, lock, shutdown, restart, sleep", action)
            })
        }
    };
    
    Ok(result.to_string())
}

/// Universal process manager - consolidated process management tool
#[pyfunction]
pub fn rust_process_manager(action: String, pid: Option<u32>, name: Option<String>) -> PyResult<String> {
    let mut sys = System::new_all();
    sys.refresh_processes();
    
    let result = match action.as_str() {
        "list" => {
            let mut processes = Vec::new();
            for (process_pid, process) in sys.processes() {
                processes.push(json!({
                    "pid": process_pid.as_u32(),
                    "name": process.name(),
                    "cpu_percent": process.cpu_usage(),
                    "memory_mb": (process.memory() as f64 / (1024.0 * 1024.0) * 10.0).round() / 10.0,
                    "status": format!("{:?}", process.status()),
                    "running_time_hours": (process.run_time() as f64 / 3600.0 * 10.0).round() / 10.0
                }));
            }
            
            // Sort by memory usage
            processes.sort_by(|a, b| {
                let mem_a = a["memory_mb"].as_f64().unwrap_or(0.0);
                let mem_b = b["memory_mb"].as_f64().unwrap_or(0.0);
                mem_b.partial_cmp(&mem_a).unwrap_or(std::cmp::Ordering::Equal)
            });
            
            json!({
                "success": true,
                "result": {
                    "processes": processes,
                    "total_count": sys.processes().len()
                },
                "error": null
            })
        },
        "find" => {
            let search_name = name.unwrap_or_default();
            if search_name.is_empty() {
                json!({
                    "success": false,
                    "result": null,
                    "error": "Missing required argument: name"
                })
            } else {
                let mut found_processes = Vec::new();
                for (process_pid, process) in sys.processes() {
                    if process.name().to_lowercase().contains(&search_name.to_lowercase()) {
                        found_processes.push(json!({
                            "pid": process_pid.as_u32(),
                            "name": process.name(),
                            "cpu_percent": process.cpu_usage(),
                            "memory_mb": (process.memory() as f64 / (1024.0 * 1024.0) * 10.0).round() / 10.0
                        }));
                    }
                }
                
                json!({
                    "success": true,
                    "result": {
                        "processes": found_processes,
                        "count": found_processes.len()
                    },
                    "error": null
                })
            }
        },
        "kill" => {
            let target_pid = pid.unwrap_or(0);
            if target_pid == 0 {
                json!({
                    "success": false,
                    "result": null,
                    "error": "Missing required argument: pid"
                })
            } else {
                // Process killing would require platform-specific implementation
                json!({
                    "success": false,
                    "result": null,
                    "error": "Process killing not yet implemented in Rust backend"
                })
            }
        },
        "apps" => {
            let mut apps = Vec::new();
            for (process_pid, process) in sys.processes() {
                let name = process.name().to_lowercase();
                // Simple heuristic for GUI applications
                if name.contains("chrome") || name.contains("firefox") || name.contains("code") 
                   || name.contains("terminal") || name.contains("nautilus") || name.contains("explorer") {
                    apps.push(json!({
                        "pid": process_pid.as_u32(),
                        "name": process.name(),
                        "memory_mb": (process.memory() as f64 / (1024.0 * 1024.0) * 10.0).round() / 10.0
                    }));
                }
            }
            
            json!({
                "success": true,
                "result": {
                    "apps": apps,
                    "count": apps.len()
                },
                "error": null
            })
        },
        _ => {
            json!({
                "success": false,
                "result": null,
                "error": format!("Unknown action: {}. Use: list, apps, find, kill", action)
            })
        }
    };
    
    Ok(result.to_string())
}
