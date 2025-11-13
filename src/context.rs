//! Context tools - Context awareness and capture
//! Screen awareness, window detection, clipboard, and capture functionality

use pyo3::prelude::*;
use serde_json::json;
use std::process::Command;
use std::time::{SystemTime, UNIX_EPOCH};

/// Universal context getter - consolidated context information tool
#[pyfunction]
pub fn rust_context_get(what: String) -> PyResult<String> {
    let result = match what.as_str() {
        "window" => {
            // Get active window title using system commands
            let output = if cfg!(target_os = "linux") {
                Command::new("xdotool")
                    .args(["getactivewindow", "getwindowname"])
                    .output()
            } else if cfg!(target_os = "macos") {
                Command::new("osascript")
                    .args(["-e", "tell application \"System Events\" to get name of first application process whose frontmost is true"])
                    .output()
            } else {
                return Ok(json!({
                    "success": false,
                    "result": null,
                    "error": "Windows not supported yet"
                }).to_string());
            };
            
            match output {
                Ok(result) if result.status.success() => {
                    let title = String::from_utf8_lossy(&result.stdout).trim().to_string();
                    json!({
                        "success": true,
                        "result": {"title": title, "method": "rust_native"},
                        "error": null
                    })
                },
                _ => {
                    json!({
                        "success": false,
                        "result": null,
                        "error": "Could not get active window"
                    })
                }
            }
        },
        "cursor" => {
            // Cursor position using system commands
            let output = if cfg!(target_os = "linux") {
                Command::new("xdotool")
                    .args(["getmouselocation", "--shell"])
                    .output()
            } else {
                return Ok(json!({
                    "success": false,
                    "result": null,
                    "error": "Cursor position only supported on Linux currently"
                }).to_string());
            };
            
            match output {
                Ok(result) if result.status.success() => {
                    let output_str = String::from_utf8_lossy(&result.stdout);
                    let mut x = 0;
                    let mut y = 0;
                    
                    for line in output_str.lines() {
                        if line.starts_with("X=") {
                            x = line[2..].parse().unwrap_or(0);
                        } else if line.starts_with("Y=") {
                            y = line[2..].parse().unwrap_or(0);
                        }
                    }
                    
                    json!({
                        "success": true,
                        "result": {"x": x, "y": y, "method": "rust_xdotool"},
                        "error": null
                    })
                },
                _ => {
                    json!({
                        "success": false,
                        "result": null,
                        "error": "Could not get cursor position"
                    })
                }
            }
        },
        "clipboard" => {
            // Clipboard access using system commands
            let output = if cfg!(target_os = "linux") {
                Command::new("xclip")
                    .args(["-selection", "clipboard", "-o"])
                    .output()
            } else if cfg!(target_os = "macos") {
                Command::new("pbpaste")
                    .output()
            } else {
                return Ok(json!({
                    "success": false,
                    "result": null,
                    "error": "Windows clipboard not supported yet"
                }).to_string());
            };
            
            match output {
                Ok(result) if result.status.success() => {
                    let text = String::from_utf8_lossy(&result.stdout).to_string();
                    json!({
                        "success": true,
                        "result": {"text": text, "method": "rust_native"},
                        "error": null
                    })
                },
                _ => {
                    json!({
                        "success": false,
                        "result": null,
                        "error": "Could not read clipboard"
                    })
                }
            }
        },
        "idle" => {
            // Idle detection using xprintidle on Linux
            let output = if cfg!(target_os = "linux") {
                Command::new("xprintidle")
                    .output()
            } else {
                return Ok(json!({
                    "success": false,
                    "result": null,
                    "error": "Idle detection only supported on Linux currently"
                }).to_string());
            };
            
            match output {
                Ok(result) if result.status.success() => {
                    let output_str = String::from_utf8_lossy(&result.stdout);
                    let idle_ms_str = output_str.trim();
                    if let Ok(idle_ms) = idle_ms_str.parse::<u64>() {
                        let idle_seconds = idle_ms / 1000;
                        json!({
                            "success": true,
                            "result": {
                                "idle_seconds": idle_seconds,
                                "idle_minutes": idle_seconds / 60,
                                "is_idle": idle_seconds > 300,
                                "method": "rust_xprintidle"
                            },
                            "error": null
                        })
                    } else {
                        json!({
                            "success": false,
                            "result": null,
                            "error": "Could not parse idle time"
                        })
                    }
                },
                _ => {
                    json!({
                        "success": false,
                        "result": null,
                        "error": "Could not get idle time"
                    })
                }
            }
        },
        "display" => {
            // Display info using xrandr on Linux
            let output = if cfg!(target_os = "linux") {
                Command::new("xrandr")
                    .args(["--current"])
                    .output()
            } else {
                return Ok(json!({
                    "success": false,
                    "result": null,
                    "error": "Display info only supported on Linux currently"
                }).to_string());
            };
            
            match output {
                Ok(result) if result.status.success() => {
                    let output_str = String::from_utf8_lossy(&result.stdout);
                    // Parse primary display resolution
                    for line in output_str.lines() {
                        if line.contains("primary") && line.contains("x") {
                            if let Some(resolution_part) = line.split_whitespace().find(|s| s.contains("x")) {
                                let parts: Vec<&str> = resolution_part.split("x").collect();
                                if parts.len() == 2 {
                                    if let (Ok(width), Ok(height)) = (parts[0].parse::<u32>(), parts[1].parse::<u32>()) {
                                        return Ok(json!({
                                            "success": true,
                                            "result": {
                                                "width": width,
                                                "height": height,
                                                "resolution": format!("{}x{}", width, height),
                                                "method": "rust_xrandr"
                                            },
                                            "error": null
                                        }).to_string());
                                    }
                                }
                            }
                        }
                    }
                    json!({
                        "success": false,
                        "result": null,
                        "error": "Could not parse display resolution"
                    })
                },
                _ => {
                    json!({
                        "success": false,
                        "result": null,
                        "error": "Could not get display info"
                    })
                }
            }
        },
        "screen_text" => {
            // OCR would require additional libraries
            json!({
                "success": false,
                "result": null,
                "error": "OCR requires additional libraries - use Python fallback"
            })
        },
        _ => {
            json!({
                "success": false,
                "result": null,
                "error": format!("Unknown context type: {}. Use: window, cursor, clipboard, idle, display, screen_text", what)
            })
        }
    };
    
    Ok(result.to_string())
}

/// Universal context capture - consolidated capture tool
#[pyfunction]
pub fn rust_context_capture(capture_type: String, duration: i32, window_title: String, save_path: String) -> PyResult<String> {
    let result = match capture_type.as_str() {
        "screenshot" => {
            // Screenshot using system commands
            let timestamp = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs();
            
            let final_path = if save_path.is_empty() {
                format!("screenshot_{}.png", timestamp)
            } else {
                save_path
            };
            
            let output = if cfg!(target_os = "linux") {
                Command::new("gnome-screenshot")
                    .args(["-f", &final_path])
                    .output()
            } else if cfg!(target_os = "macos") {
                Command::new("screencapture")
                    .args([&final_path])
                    .output()
            } else {
                return Ok(json!({
                    "success": false,
                    "result": null,
                    "error": "Windows screenshot not supported yet"
                }).to_string());
            };
            
            match output {
                Ok(result) if result.status.success() => {
                    // Get file size if file exists
                    let file_size = std::fs::metadata(&final_path)
                        .map(|m| m.len())
                        .unwrap_or(0);
                    
                    json!({
                        "success": true,
                        "result": {
                            "path": final_path,
                            "file_size_bytes": file_size,
                            "method": "rust_native"
                        },
                        "error": null
                    })
                },
                _ => {
                    json!({
                        "success": false,
                        "result": null,
                        "error": "Could not take screenshot"
                    })
                }
            }
        },
        "window_screenshot" => {
            // Window screenshot using xwininfo + import on Linux
            if !cfg!(target_os = "linux") {
                return Ok(json!({
                    "success": false,
                    "result": null,
                    "error": "Window screenshot only supported on Linux currently"
                }).to_string());
            }
            
            let timestamp = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs();
            
            let final_path = if save_path.is_empty() {
                format!("window_screenshot_{}.png", timestamp)
            } else {
                save_path
            };
            
            // Get window ID first
            let window_output = if !window_title.is_empty() {
                Command::new("xdotool")
                    .args(["search", "--name", &window_title])
                    .output()
            } else {
                Command::new("xdotool")
                    .args(["getactivewindow"])
                    .output()
            };
            
            match window_output {
                Ok(result) if result.status.success() => {
                    let output_str = String::from_utf8_lossy(&result.stdout);
                    let window_id = output_str.trim();
                    
                    // Take screenshot of specific window
                    let screenshot_output = Command::new("import")
                        .args(["-window", window_id, &final_path])
                        .output();
                    
                    match screenshot_output {
                        Ok(result) if result.status.success() => {
                            let file_size = std::fs::metadata(&final_path)
                                .map(|m| m.len())
                                .unwrap_or(0);
                            
                            json!({
                                "success": true,
                                "result": {
                                    "path": final_path,
                                    "window_id": window_id,
                                    "file_size_bytes": file_size,
                                    "method": "rust_import"
                                },
                                "error": null
                            })
                        },
                        _ => {
                            json!({
                                "success": false,
                                "result": null,
                                "error": "Could not capture window screenshot"
                            })
                        }
                    }
                },
                _ => {
                    json!({
                        "success": false,
                        "result": null,
                        "error": "Could not find window"
                    })
                }
            }
        },
        "camera" => {
            // Camera capture using fswebcam on Linux
            if !cfg!(target_os = "linux") {
                return Ok(json!({
                    "success": false,
                    "result": null,
                    "error": "Camera capture only supported on Linux currently"
                }).to_string());
            }
            
            let timestamp = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs();
            
            let final_path = if save_path.is_empty() {
                format!("camera_{}.jpg", timestamp)
            } else {
                save_path
            };
            
            let output = Command::new("fswebcam")
                .args(["-r", "640x480", "--no-banner", &final_path])
                .output();
            
            match output {
                Ok(result) if result.status.success() => {
                    let file_size = std::fs::metadata(&final_path)
                        .map(|m| m.len())
                        .unwrap_or(0);
                    
                    json!({
                        "success": true,
                        "result": {
                            "path": final_path,
                            "resolution": "640x480",
                            "file_size_bytes": file_size,
                            "method": "rust_fswebcam"
                        },
                        "error": null
                    })
                },
                _ => {
                    json!({
                        "success": false,
                        "result": null,
                        "error": "Could not capture from camera - check if fswebcam is installed and camera is available"
                    })
                }
            }
        },
        "audio" => {
            // Audio recording using arecord on Linux
            if !cfg!(target_os = "linux") {
                return Ok(json!({
                    "success": false,
                    "result": null,
                    "error": "Audio recording only supported on Linux currently"
                }).to_string());
            }
            
            let timestamp = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_secs();
            
            let final_path = if save_path.is_empty() {
                format!("audio_{}.wav", timestamp)
            } else {
                save_path
            };
            
            let output = Command::new("arecord")
                .args(["-d", &duration.to_string(), "-f", "cd", &final_path])
                .output();
            
            match output {
                Ok(result) if result.status.success() => {
                    let file_size = std::fs::metadata(&final_path)
                        .map(|m| m.len())
                        .unwrap_or(0);
                    
                    json!({
                        "success": true,
                        "result": {
                            "path": final_path,
                            "duration_seconds": duration,
                            "format": "wav",
                            "file_size_bytes": file_size,
                            "method": "rust_arecord"
                        },
                        "error": null
                    })
                },
                _ => {
                    json!({
                        "success": false,
                        "result": null,
                        "error": "Could not record audio - check if arecord is installed and microphone is available"
                    })
                }
            }
        },
        _ => {
            json!({
                "success": false,
                "result": null,
                "error": format!("Unknown capture type: {}. Use: screenshot, window_screenshot, camera, audio", capture_type)
            })
        }
    };
    
    Ok(result.to_string())
}
