//! Network tools - High-performance network operations
//! Consolidated network and web browser operations using Rust

use pyo3::prelude::*;
use serde_json::json;
use std::process::Command;

/// Universal network tools - consolidated network operations
#[pyfunction]
pub fn rust_network_tools(action: String, host: Option<String>, url: Option<String>, path: Option<String>, method: Option<String>, count: Option<i32>) -> PyResult<String> {
    let result = match action.as_str() {
        "ping" => {
            let target_host = host.unwrap_or_default();
            if target_host.is_empty() {
                json!({
                    "success": false,
                    "result": serde_json::Value::Null,
                    "error": "Missing required argument: host"
                })
            } else {
                rust_ping_host_impl(&target_host, count.unwrap_or(4))
            }
        },
        "download" => {
            let target_url = url.unwrap_or_default();
            let target_path = path.unwrap_or_default();
            if target_url.is_empty() || target_path.is_empty() {
                json!({
                    "success": false,
                    "result": serde_json::Value::Null,
                    "error": "Missing required arguments: url, path"
                })
            } else {
                rust_download_file_impl(&target_url, &target_path)
            }
        },
        "request" => {
            let target_url = url.unwrap_or_default();
            if target_url.is_empty() {
                json!({
                    "success": false,
                    "result": serde_json::Value::Null,
                    "error": "Missing required argument: url"
                })
            } else {
                rust_http_request_impl(&target_url, &method.unwrap_or_else(|| "GET".to_string()))
            }
        },
        "check_internet" => {
            rust_check_internet_impl()
        },
        "public_ip" => {
            rust_get_public_ip_impl()
        },
        "open_url" => {
            let target_url = url.unwrap_or_default();
            if target_url.is_empty() {
                json!({
                    "success": false,
                    "result": serde_json::Value::Null,
                    "error": "Missing required argument: url"
                })
            } else {
                rust_open_website_impl(&target_url)
            }
        },
        _ => {
            json!({
                "success": false,
                "result": serde_json::Value::Null,
                "error": format!("Unknown action: {}. Use: ping, download, request, check_internet, public_ip, open_url", action)
            })
        }
    };
    
    Ok(result.to_string())
}

/// Smart web browser control - consolidated browser operations
#[pyfunction]
pub fn rust_web_browser(action: String, url: Option<String>, query: Option<String>, search_engine: Option<String>, browser: Option<String>) -> PyResult<String> {
    let result = match action.as_str() {
        "navigate" => {
            let target_url = url.unwrap_or_default();
            if target_url.is_empty() {
                json!({
                    "success": false,
                    "result": serde_json::Value::Null,
                    "error": "Missing required argument: url"
                })
            } else {
                rust_navigate_browser_impl(&target_url, &browser.unwrap_or_else(|| "default".to_string()))
            }
        },
        "search" => {
            let search_query = query.unwrap_or_default();
            if search_query.is_empty() {
                json!({
                    "success": false,
                    "result": serde_json::Value::Null,
                    "error": "Missing required argument: query"
                })
            } else {
                rust_search_browser_impl(&search_query, &search_engine.unwrap_or_else(|| "google".to_string()))
            }
        },
        "open" => {
            rust_open_browser_impl(&url.unwrap_or_else(|| "about:blank".to_string()), &browser.unwrap_or_else(|| "default".to_string()))
        },
        "close" => {
            json!({
                "success": false,
                "result": serde_json::Value::Null,
                "error": "Browser closing not yet implemented in Rust backend"
            })
        },
        _ => {
            json!({
                "success": false,
                "result": serde_json::Value::Null,
                "error": format!("Unknown action: {}. Use: navigate, search, open, close", action)
            })
        }
    };
    
    Ok(result.to_string())
}

// Implementation helpers
fn rust_ping_host_impl(host: &str, count: i32) -> serde_json::Value {
    use std::process::Command;
    
    // Determine ping command based on OS
    let mut cmd = Command::new("ping");
    
    #[cfg(target_os = "windows")]
    {
        cmd.args(["-n", &count.to_string(), host]);
    }
    
    #[cfg(not(target_os = "windows"))]
    {
        cmd.args(["-c", &count.to_string(), host]);
    }
    
    match cmd.output() {
        Ok(output) => {
            let stdout = String::from_utf8_lossy(&output.stdout);
            let stderr = String::from_utf8_lossy(&output.stderr);
            let success = output.status.success();
            
            // Parse ping statistics
            let mut stats = json!({
                "packets_sent": count,
                "packets_received": 0,
                "packet_loss": 100.0,
                "min_time": null,
                "max_time": null,
                "avg_time": null
            });
            
            // Simple parsing for packet statistics
            let output_str = stdout.to_lowercase();
            if output_str.contains("packets transmitted") || output_str.contains("packets: sent") {
                // Extract received packets count
                for line in stdout.lines() {
                    if line.contains("received") && (line.contains("transmitted") || line.contains("Sent")) {
                        let parts: Vec<&str> = line.split_whitespace().collect();
                        for (i, part) in parts.iter().enumerate() {
                            if part.contains("received") && i > 0 {
                                if let Ok(received) = parts[i-1].parse::<i32>() {
                                    stats["packets_received"] = json!(received);
                                    let loss = ((count - received) as f64 / count as f64) * 100.0;
                                    stats["packet_loss"] = json!(loss);
                                    break;
                                }
                            }
                        }
                    }
                }
            }
            
            json!({
                "success": success,
                "result": {
                    "host": host,
                    "count": count,
                    "statistics": stats,
                    "reachable": success,
                    "output": stdout,
                    "method": "rust_ping"
                },
                "error": if success { serde_json::Value::Null } else { json!(stderr) }
            })
        },
        Err(e) => {
            json!({
                "success": false,
                "result": serde_json::Value::Null,
                "error": format!("Failed to execute ping: {}", e)
            })
        }
    }
}

fn rust_download_file_impl(url: &str, path: &str) -> serde_json::Value {
    // For now, use curl command as Rust HTTP client would require additional dependencies
    use std::fs;
    use std::path::Path;
    
    // Create parent directories if needed
    if let Some(parent) = Path::new(path).parent() {
        let _ = fs::create_dir_all(parent);
    }
    
    // Use curl for downloading
    let output = Command::new("curl")
        .args(["-L", "-o", path, url])
        .output();
    
    match output {
        Ok(result) => {
            if result.status.success() {
                // Get file size
                match fs::metadata(path) {
                    Ok(metadata) => {
                        let file_size = metadata.len();
                        json!({
                            "success": true,
                            "result": {
                                "url": url,
                                "path": path,
                                "size": file_size,
                                "size_mb": (file_size as f64 / (1024.0 * 1024.0) * 100.0).round() / 100.0,
                                "action": "downloaded",
                                "method": "rust_curl"
                            },
                            "error": serde_json::Value::Null
                        })
                    },
                    Err(e) => {
                        json!({
                            "success": false,
                            "result": serde_json::Value::Null,
                            "error": format!("File downloaded but could not get size: {}", e)
                        })
                    }
                }
            } else {
                let stderr = String::from_utf8_lossy(&result.stderr);
                json!({
                    "success": false,
                    "result": serde_json::Value::Null,
                    "error": format!("Download failed: {}", stderr)
                })
            }
        },
        Err(e) => {
            json!({
                "success": false,
                "result": serde_json::Value::Null,
                "error": format!("Failed to execute curl: {}", e)
            })
        }
    }
}

fn rust_http_request_impl(url: &str, method: &str) -> serde_json::Value {
    // Use curl for HTTP requests
    let mut cmd = Command::new("curl");
    cmd.args(["-s", "-i", "-X", method, url]);
    
    match cmd.output() {
        Ok(output) => {
            let response = String::from_utf8_lossy(&output.stdout);
            let success = output.status.success();
            
            if success {
                // Parse response (simple parsing)
                let mut headers = std::collections::HashMap::new();
                let mut content = String::new();
                let mut status_code = 200;
                let mut in_headers = true;
                
                for line in response.lines() {
                    if in_headers {
                        if line.is_empty() {
                            in_headers = false;
                        } else if line.starts_with("HTTP/") {
                            // Extract status code
                            let parts: Vec<&str> = line.split_whitespace().collect();
                            if parts.len() >= 2 {
                                status_code = parts[1].parse().unwrap_or(200);
                            }
                        } else if line.contains(':') {
                            let parts: Vec<&str> = line.splitn(2, ':').collect();
                            if parts.len() == 2 {
                                headers.insert(parts[0].trim().to_string(), parts[1].trim().to_string());
                            }
                        }
                    } else {
                        content.push_str(line);
                        content.push('\n');
                    }
                }
                
                json!({
                    "success": true,
                    "result": {
                        "url": url,
                        "method": method,
                        "status_code": status_code,
                        "headers": headers,
                        "content": content.trim(),
                        "content_length": content.len(),
                        "method": "rust_curl"
                    },
                    "error": null
                })
            } else {
                let stderr = String::from_utf8_lossy(&output.stderr);
                json!({
                    "success": false,
                    "result": serde_json::Value::Null,
                    "error": format!("HTTP request failed: {}", stderr)
                })
            }
        },
        Err(e) => {
            json!({
                "success": false,
                "result": serde_json::Value::Null,
                "error": format!("Failed to execute curl: {}", e)
            })
        }
    }
}

fn rust_check_internet_impl() -> serde_json::Value {
    let test_hosts = vec!["8.8.8.8", "1.1.1.1", "google.com"];
    let mut connected = false;
    let mut results = Vec::new();
    
    for host in test_hosts {
        let mut cmd = Command::new("ping");
        
        #[cfg(target_os = "windows")]
        {
            cmd.args(["-n", "1", "-w", "3000", host]);
        }
        
        #[cfg(not(target_os = "windows"))]
        {
            cmd.args(["-c", "1", "-W", "3", host]);
        }
        
        let success = cmd.output()
            .map(|output| output.status.success())
            .unwrap_or(false);
        
        results.push(json!({
            "host": host,
            "reachable": success
        }));
        
        if success {
            connected = true;
        }
    }
    
    json!({
        "success": true,
        "result": {
            "connected": connected,
            "tests": results,
            "method": "rust_ping_test"
        },
        "error": null
    })
}

fn rust_get_public_ip_impl() -> serde_json::Value {
    let ip_services = vec![
        "https://api.ipify.org",
        "https://ipinfo.io/ip",
        "https://icanhazip.com"
    ];
    
    for service in ip_services {
        let output = Command::new("curl")
            .args(["-s", "--max-time", "10", service])
            .output();
        
        if let Ok(result) = output {
            if result.status.success() {
                let ip = String::from_utf8_lossy(&result.stdout).trim().to_string();
                if !ip.is_empty() && ip.chars().all(|c| c.is_ascii_digit() || c == '.') {
                    return json!({
                        "success": true,
                        "result": {
                            "public_ip": ip,
                            "service": service,
                            "method": "rust_curl"
                        },
                        "error": null
                    });
                }
            }
        }
    }
    
    json!({
        "success": false,
        "result": null,
        "error": "Could not determine public IP"
    })
}

fn rust_open_website_impl(url: &str) -> serde_json::Value {
    // Add protocol if missing
    let final_url = if url.starts_with("http://") || url.starts_with("https://") {
        url.to_string()
    } else {
        format!("https://{}", url)
    };
    
    // Use platform-specific commands to open URL
    let result = if cfg!(target_os = "windows") {
        Command::new("cmd")
            .args(["/C", "start", &final_url])
            .output()
    } else if cfg!(target_os = "macos") {
        Command::new("open")
            .arg(&final_url)
            .output()
    } else {
        // Linux - try xdg-open
        Command::new("xdg-open")
            .arg(&final_url)
            .output()
    };
    
    match result {
        Ok(output) => {
            if output.status.success() {
                json!({
                    "success": true,
                    "result": {
                        "url": final_url,
                        "action": "opened_in_browser",
                        "method": "rust_system_open"
                    },
                    "error": null
                })
            } else {
                let stderr = String::from_utf8_lossy(&output.stderr);
                json!({
                    "success": false,
                    "result": serde_json::Value::Null,
                    "error": format!("Failed to open URL: {}", stderr)
                })
            }
        },
        Err(e) => {
            json!({
                "success": false,
                "result": serde_json::Value::Null,
                "error": format!("Failed to execute open command: {}", e)
            })
        }
    }
}

fn rust_navigate_browser_impl(url: &str, browser: &str) -> serde_json::Value {
    // For now, just use the same implementation as open_website
    // In the future, could add browser-specific commands
    let final_url = if url.starts_with("http://") || url.starts_with("https://") {
        url.to_string()
    } else {
        format!("https://{}", url)
    };
    
    let result = rust_open_website_impl(&final_url);
    
    // Modify result to include browser info
    if let serde_json::Value::Object(mut obj) = result {
        if let Some(serde_json::Value::Object(ref mut result_obj)) = obj.get_mut("result") {
            result_obj.insert("browser".to_string(), json!(browser));
            result_obj.insert("action".to_string(), json!("navigated"));
        }
        serde_json::Value::Object(obj)
    } else {
        result
    }
}

fn rust_search_browser_impl(query: &str, search_engine: &str) -> serde_json::Value {
    // Build search URL
    let search_url = match search_engine {
        "google" => format!("https://www.google.com/search?q={}", urlencoding::encode(query)),
        "bing" => format!("https://www.bing.com/search?q={}", urlencoding::encode(query)),
        "duckduckgo" => format!("https://duckduckgo.com/?q={}", urlencoding::encode(query)),
        _ => format!("https://www.google.com/search?q={}", urlencoding::encode(query)),
    };
    
    let result = rust_open_website_impl(&search_url);
    
    // Modify result to include search info
    if let serde_json::Value::Object(mut obj) = result {
        if let Some(serde_json::Value::Object(ref mut result_obj)) = obj.get_mut("result") {
            result_obj.insert("query".to_string(), json!(query));
            result_obj.insert("search_engine".to_string(), json!(search_engine));
            result_obj.insert("search_url".to_string(), json!(search_url));
            result_obj.insert("action".to_string(), json!("search_opened"));
        }
        serde_json::Value::Object(obj)
    } else {
        result
    }
}

fn rust_open_browser_impl(url: &str, browser: &str) -> serde_json::Value {
    let result = rust_open_website_impl(url);
    
    // Modify result to include browser info
    if let serde_json::Value::Object(mut obj) = result {
        if let Some(serde_json::Value::Object(ref mut result_obj)) = obj.get_mut("result") {
            result_obj.insert("browser".to_string(), json!(browser));
            result_obj.insert("action".to_string(), json!("browser_opened"));
        }
        serde_json::Value::Object(obj)
    } else {
        result
    }
}

// URL encoding helper (simple implementation)
mod urlencoding {
    pub fn encode(input: &str) -> String {
        input
            .chars()
            .map(|c| match c {
                'A'..='Z' | 'a'..='z' | '0'..='9' | '-' | '_' | '.' | '~' => c.to_string(),
                ' ' => "+".to_string(),
                _ => format!("%{:02X}", c as u8),
            })
            .collect()
    }
}
