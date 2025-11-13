//! Utility tools - File I/O, network, and command execution
//! High-performance utility operations using Rust

use pyo3::prelude::*;
use serde_json::json;
use std::fs;
use std::process::Command;
use std::time::{Duration, Instant};

/// Fast file reading in Rust
#[pyfunction]
pub fn rust_read_file(file_path: String) -> PyResult<String> {
    match fs::read_to_string(&file_path) {
        Ok(content) => {
            let result = json!({
                "success": true,
                "result": {
                    "path": file_path,
                    "content": content,
                    "size": content.len(),
                    "type": "text"
                },
                "error": null
            });
            Ok(result.to_string())
        }
        Err(e) => {
            let result = json!({
                "success": false,
                "result": null,
                "error": format!("Failed to read file: {}", e)
            });
            Ok(result.to_string())
        }
    }
}

/// Fast file writing in Rust
#[pyfunction]
pub fn rust_write_file(file_path: String, content: String) -> PyResult<String> {
    match fs::write(&file_path, &content) {
        Ok(_) => {
            let result = json!({
                "success": true,
                "result": {
                    "path": file_path,
                    "bytes_written": content.len(),
                    "type": "text"
                },
                "error": null
            });
            Ok(result.to_string())
        }
        Err(e) => {
            let result = json!({
                "success": false,
                "result": null,
                "error": format!("Failed to write file: {}", e)
            });
            Ok(result.to_string())
        }
    }
}

/// Fast directory listing in Rust
#[pyfunction]
pub fn rust_list_files(dir_path: String) -> PyResult<String> {
    match fs::read_dir(&dir_path) {
        Ok(entries) => {
            let mut files = Vec::new();
            
            for entry in entries {
                if let Ok(entry) = entry {
                    let path = entry.path();
                    let metadata = entry.metadata().unwrap_or_else(|_| {
                        // Create dummy metadata if we can't read it
                        fs::metadata("/dev/null").unwrap()
                    });
                    
                    files.push(json!({
                        "name": path.file_name().unwrap_or_default().to_string_lossy(),
                        "path": path.to_string_lossy(),
                        "type": if path.is_dir() { "directory" } else { "file" },
                        "size": if path.is_file() { metadata.len() } else { 0 },
                        "modified": metadata.modified().ok().map(|t| 
                            t.duration_since(std::time::UNIX_EPOCH).unwrap_or_default().as_secs()
                        )
                    }));
                }
            }
            
            let result = json!({
                "success": true,
                "result": {
                    "path": dir_path,
                    "items": files,
                    "total_count": files.len()
                },
                "error": null
            });
            Ok(result.to_string())
        }
        Err(e) => {
            let result = json!({
                "success": false,
                "result": null,
                "error": format!("Failed to list directory: {}", e)
            });
            Ok(result.to_string())
        }
    }
}

/// Fast network ping in Rust
#[pyfunction]
pub fn rust_ping_host(host: String, count: Option<u32>) -> PyResult<String> {
    let ping_count = count.unwrap_or(4);
    
    // Use system ping command for now (could use pure Rust ping library later)
    let output = Command::new("ping")
        .arg("-c")
        .arg(ping_count.to_string())
        .arg(&host)
        .output();
    
    match output {
        Ok(result) => {
            let stdout = String::from_utf8_lossy(&result.stdout);
            let stderr = String::from_utf8_lossy(&result.stderr);
            
            let response = json!({
                "success": result.status.success(),
                "result": {
                    "host": host,
                    "count": ping_count,
                    "output": stdout,
                    "reachable": result.status.success()
                },
                "error": if result.status.success() { serde_json::Value::Null } else { serde_json::Value::String(stderr.to_string()) }
            });
            Ok(response.to_string())
        }
        Err(e) => {
            let result = json!({
                "success": false,
                "result": null,
                "error": format!("Failed to ping host: {}", e)
            });
            Ok(result.to_string())
        }
    }
}

/// Fast command execution in Rust
#[pyfunction]
pub fn rust_run_command(command: String, timeout_secs: Option<u64>) -> PyResult<String> {
    let _timeout = Duration::from_secs(timeout_secs.unwrap_or(30));
    let start_time = Instant::now();
    
    let output = Command::new("sh")
        .arg("-c")
        .arg(&command)
        .output();
    
    let elapsed = start_time.elapsed();
    
    match output {
        Ok(result) => {
            let stdout = String::from_utf8_lossy(&result.stdout);
            let stderr = String::from_utf8_lossy(&result.stderr);
            
            let response = json!({
                "success": result.status.success(),
                "result": {
                    "command": command,
                    "return_code": result.status.code().unwrap_or(-1),
                    "stdout": stdout,
                    "stderr": stderr,
                    "elapsed_ms": elapsed.as_millis()
                },
                "error": if result.status.success() { serde_json::Value::Null } else { serde_json::Value::String(stderr.to_string()) }
            });
            Ok(response.to_string())
        }
        Err(e) => {
            let result = json!({
                "success": false,
                "result": null,
                "error": format!("Failed to run command: {}", e)
            });
            Ok(result.to_string())
        }
    }
}

/// Check internet connectivity in Rust
#[pyfunction]
pub fn rust_check_internet() -> PyResult<String> {
    // Try to ping common DNS servers
    let test_hosts = vec!["8.8.8.8", "1.1.1.1", "google.com"];
    let mut connected = false;
    let mut results = Vec::new();
    
    for host in test_hosts {
        let output = Command::new("ping")
            .arg("-c")
            .arg("1")
            .arg("-W")
            .arg("3")
            .arg(host)
            .output();
        
        let success = output.map(|o| o.status.success()).unwrap_or(false);
        results.push(json!({
            "host": host,
            "reachable": success
        }));
        
        if success {
            connected = true;
        }
    }
    
    let response = json!({
        "success": true,
        "result": {
            "connected": connected,
            "tests": results
        },
        "error": null
    });
    Ok(response.to_string())
}

/// Universal file manager - consolidated file operations tool
#[pyfunction]
pub fn rust_file_manager(action: String, path: String, content: Option<String>, to_path: Option<String>) -> PyResult<String> {
    let result = match action.as_str() {
        "list" => {
            // List directory contents
            match fs::read_dir(&path) {
                Ok(entries) => {
                    let mut files = Vec::new();
                    
                    for entry in entries {
                        if let Ok(entry) = entry {
                            let entry_path = entry.path();
                            let metadata = entry.metadata().unwrap_or_else(|_| {
                                fs::metadata("/dev/null").unwrap()
                            });
                            
                            files.push(json!({
                                "name": entry_path.file_name().unwrap_or_default().to_string_lossy(),
                                "path": entry_path.to_string_lossy(),
                                "type": if entry_path.is_dir() { "directory" } else { "file" },
                                "size": if entry_path.is_file() { metadata.len() } else { 0 },
                                "modified": metadata.modified().ok().map(|t| 
                                    t.duration_since(std::time::UNIX_EPOCH).unwrap_or_default().as_secs()
                                )
                            }));
                        }
                    }
                    
                    json!({
                        "success": true,
                        "result": {
                            "path": path,
                            "items": files,
                            "total_count": files.len()
                        },
                        "error": null
                    })
                },
                Err(e) => {
                    json!({
                        "success": false,
                        "result": null,
                        "error": format!("Failed to list directory: {}", e)
                    })
                }
            }
        },
        "read" => {
            // Read file contents
            match fs::read_to_string(&path) {
                Ok(content) => {
                    json!({
                        "success": true,
                        "result": {
                            "path": path,
                            "content": content,
                            "size": content.len(),
                            "encoding": "utf-8"
                        },
                        "error": null
                    })
                },
                Err(e) => {
                    json!({
                        "success": false,
                        "result": null,
                        "error": format!("Failed to read file: {}", e)
                    })
                }
            }
        },
        "write" => {
            // Write file contents
            let file_content = content.unwrap_or_default();
            
            // Create parent directories if needed
            if let Some(parent) = std::path::Path::new(&path).parent() {
                let _ = fs::create_dir_all(parent);
            }
            
            match fs::write(&path, &file_content) {
                Ok(_) => {
                    json!({
                        "success": true,
                        "result": {
                            "path": path,
                            "bytes_written": file_content.len(),
                            "encoding": "utf-8"
                        },
                        "error": null
                    })
                },
                Err(e) => {
                    json!({
                        "success": false,
                        "result": null,
                        "error": format!("Failed to write file: {}", e)
                    })
                }
            }
        },
        "delete" => {
            // Delete file or directory
            let path_obj = std::path::Path::new(&path);
            
            if !path_obj.exists() {
                json!({
                    "success": false,
                    "result": null,
                    "error": format!("Path does not exist: {}", path)
                })
            } else if path_obj.is_file() {
                match fs::remove_file(&path) {
                    Ok(_) => {
                        json!({
                            "success": true,
                            "result": {"path": path, "action": "file_deleted"},
                            "error": null
                        })
                    },
                    Err(e) => {
                        json!({
                            "success": false,
                            "result": null,
                            "error": format!("Failed to delete file: {}", e)
                        })
                    }
                }
            } else if path_obj.is_dir() {
                match fs::remove_dir_all(&path) {
                    Ok(_) => {
                        json!({
                            "success": true,
                            "result": {"path": path, "action": "directory_deleted"},
                            "error": null
                        })
                    },
                    Err(e) => {
                        json!({
                            "success": false,
                            "result": null,
                            "error": format!("Failed to delete directory: {}", e)
                        })
                    }
                }
            } else {
                json!({
                    "success": false,
                    "result": null,
                    "error": format!("Unknown path type: {}", path)
                })
            }
        },
        "copy" => {
            // Copy file or directory
            let dest_path = to_path.unwrap_or_default();
            if dest_path.is_empty() {
                json!({
                    "success": false,
                    "result": null,
                    "error": "Missing required argument: to_path"
                })
            } else {
                let source_path = std::path::Path::new(&path);
                let dest_path_obj = std::path::Path::new(&dest_path);
                
                // Create parent directories if needed
                if let Some(parent) = dest_path_obj.parent() {
                    let _ = fs::create_dir_all(parent);
                }
                
                if source_path.is_file() {
                    match fs::copy(&path, &dest_path) {
                        Ok(_) => {
                            json!({
                                "success": true,
                                "result": {"from": path, "to": dest_path, "action": "file_copied"},
                                "error": null
                            })
                        },
                        Err(e) => {
                            json!({
                                "success": false,
                                "result": null,
                                "error": format!("Failed to copy file: {}", e)
                            })
                        }
                    }
                } else {
                    // For directories, we'd need a recursive copy function
                    json!({
                        "success": false,
                        "result": null,
                        "error": "Directory copying not yet implemented in Rust backend"
                    })
                }
            }
        },
        "move" => {
            // Move/rename file or directory
            let dest_path = to_path.unwrap_or_default();
            if dest_path.is_empty() {
                json!({
                    "success": false,
                    "result": null,
                    "error": "Missing required argument: to_path"
                })
            } else {
                // Create parent directories if needed
                if let Some(parent) = std::path::Path::new(&dest_path).parent() {
                    let _ = fs::create_dir_all(parent);
                }
                
                match fs::rename(&path, &dest_path) {
                    Ok(_) => {
                        json!({
                            "success": true,
                            "result": {"from": path, "to": dest_path, "action": "moved"},
                            "error": null
                        })
                    },
                    Err(e) => {
                        json!({
                            "success": false,
                            "result": null,
                            "error": format!("Failed to move: {}", e)
                        })
                    }
                }
            }
        },
        "info" => {
            // Get file information
            let path_obj = std::path::Path::new(&path);
            
            if !path_obj.exists() {
                json!({
                    "success": false,
                    "result": null,
                    "error": format!("Path does not exist: {}", path)
                })
            } else {
                match fs::metadata(&path) {
                    Ok(metadata) => {
                        let is_file = path_obj.is_file();
                        
                        let mut info = json!({
                            "path": path,
                            "name": path_obj.file_name().unwrap_or_default().to_string_lossy(),
                            "type": if is_file { "file" } else { "directory" },
                            "size": metadata.len(),
                            "modified": metadata.modified().ok().map(|t| 
                                t.duration_since(std::time::UNIX_EPOCH).unwrap_or_default().as_secs()
                            ),
                            "created": metadata.created().ok().map(|t| 
                                t.duration_since(std::time::UNIX_EPOCH).unwrap_or_default().as_secs()
                            ),
                            "readonly": metadata.permissions().readonly()
                        });
                        
                        if is_file {
                            if let Some(extension) = path_obj.extension() {
                                info["extension"] = json!(extension.to_string_lossy());
                            }
                        }
                        
                        json!({
                            "success": true,
                            "result": info,
                            "error": null
                        })
                    },
                    Err(e) => {
                        json!({
                            "success": false,
                            "result": null,
                            "error": format!("Failed to get file info: {}", e)
                        })
                    }
                }
            }
        },
        _ => {
            json!({
                "success": false,
                "result": null,
                "error": format!("Unknown action: {}. Use: list, read, write, delete, copy, move, info", action)
            })
        }
    };
    
    Ok(result.to_string())
}

/// Smart file search - consolidated search tool
#[pyfunction]
pub fn rust_file_search(query: String, search_path: String, search_type: String, extensions: Vec<String>) -> PyResult<String> {
    use std::path::Path;
    
    let mut results = Vec::new();
    
    // Walk through directory tree
    fn walk_dir(dir: &Path, query: &str, search_type: &str, extensions: &[String], results: &mut Vec<serde_json::Value>) -> std::io::Result<()> {
        if dir.is_dir() {
            for entry in fs::read_dir(dir)? {
                let entry = entry?;
                let path = entry.path();
                
                if path.is_dir() {
                    walk_dir(&path, query, search_type, extensions, results)?;
                } else if path.is_file() {
                    let file_name = path.file_name().unwrap_or_default().to_string_lossy();
                    
                    // Filter by extensions if specified
                    if !extensions.is_empty() {
                        if let Some(ext) = path.extension() {
                            let file_ext = ext.to_string_lossy().to_lowercase();
                            if !extensions.iter().any(|e| e.to_lowercase() == file_ext) {
                                continue;
                            }
                        } else {
                            continue;
                        }
                    }
                    
                    let mut match_score = 0;
                    let mut match_reasons = Vec::new();
                    
                    // Search by filename
                    if search_type == "name" || search_type == "both" {
                        if file_name.to_lowercase().contains(&query.to_lowercase()) {
                            match_score += 10;
                            match_reasons.push("filename_contains");
                        }
                    }
                    
                    // Search by content (for text files)
                    if search_type == "content" || search_type == "both" {
                        if let Ok(content) = fs::read_to_string(&path) {
                            if content.to_lowercase().contains(&query.to_lowercase()) {
                                match_score += 15;
                                match_reasons.push("content_contains");
                                
                                // Count occurrences
                                let occurrences = content.to_lowercase().matches(&query.to_lowercase()).count();
                                match_score += std::cmp::min(occurrences, 10);
                            }
                        }
                    }
                    
                    if match_score > 0 {
                        let metadata = fs::metadata(&path).ok();
                        let file_info = json!({
                            "path": path.to_string_lossy(),
                            "name": file_name,
                            "directory": path.parent().unwrap_or_else(|| Path::new("")).to_string_lossy(),
                            "size": metadata.as_ref().map(|m| m.len()).unwrap_or(0),
                            "modified": metadata.and_then(|m| m.modified().ok()).map(|t| 
                                t.duration_since(std::time::UNIX_EPOCH).unwrap_or_default().as_secs()
                            ),
                            "match_score": match_score,
                            "match_reasons": match_reasons
                        });
                        results.push(file_info);
                    }
                }
            }
        }
        Ok(())
    }
    
    let search_path_obj = Path::new(&search_path);
    
    if !search_path_obj.exists() {
        return Ok(json!({
            "success": false,
            "result": null,
            "error": format!("Search path does not exist: {}", search_path)
        }).to_string());
    }
    
    if let Err(e) = walk_dir(search_path_obj, &query, &search_type, &extensions, &mut results) {
        return Ok(json!({
            "success": false,
            "result": null,
            "error": format!("Search failed: {}", e)
        }).to_string());
    }
    
    // Sort by match score (highest first)
    results.sort_by(|a, b| {
        let score_a = a["match_score"].as_i64().unwrap_or(0);
        let score_b = b["match_score"].as_i64().unwrap_or(0);
        score_b.cmp(&score_a)
    });
    
    // Limit to top 50 results
    results.truncate(50);
    
    let response = json!({
        "success": true,
        "result": {
            "query": query,
            "search_path": search_path,
            "search_type": search_type,
            "files_found": results.len(),
            "results": results
        },
        "error": null
    });
    
    Ok(response.to_string())
}
