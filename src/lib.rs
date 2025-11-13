//! que_core_engine - Rust low-level engine for computer use agents
//! Provides high-performance system-level functions for AI agents

use pyo3::prelude::*;

// Import our modular components
mod system;
mod context;
mod utils;
mod network;
mod shell;

// Re-export the functions we want to expose
use system::{rust_system_query, rust_system_control, rust_process_manager};
use context::{rust_context_get, rust_context_capture};
use utils::{rust_read_file, rust_write_file, rust_list_files, rust_ping_host, rust_run_command, rust_check_internet, rust_file_manager, rust_file_search};
use network::{rust_network_tools, rust_web_browser};
use shell::{rust_shell_execute, rust_environment_manager};

// Legacy function aliases for backward compatibility
#[pyfunction]
fn get_system_info() -> PyResult<String> {
    rust_system_query("overview".to_string())
}

#[pyfunction]
fn get_battery_status() -> PyResult<String> {
    rust_system_query("battery".to_string())
}

#[pyfunction]
fn get_network_info() -> PyResult<String> {
    rust_system_query("network".to_string())
}

#[pyfunction]
fn list_processes() -> PyResult<String> {
    rust_process_manager("list".to_string(), None, None)
}

#[pyfunction]
fn get_disk_info() -> PyResult<String> {
    rust_system_query("disk".to_string())
}

/// Python module initialization - register all Rust functions
#[pymodule]
fn que_core_engine(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // New consolidated system tools
    m.add_function(wrap_pyfunction!(rust_system_query, m)?)?;
    m.add_function(wrap_pyfunction!(rust_system_control, m)?)?;
    m.add_function(wrap_pyfunction!(rust_process_manager, m)?)?;
    
    // New consolidated context tools
    m.add_function(wrap_pyfunction!(rust_context_get, m)?)?;
    m.add_function(wrap_pyfunction!(rust_context_capture, m)?)?;
    
    // New consolidated file tools
    m.add_function(wrap_pyfunction!(rust_file_manager, m)?)?;
    m.add_function(wrap_pyfunction!(rust_file_search, m)?)?;
    
    // New consolidated network tools
    m.add_function(wrap_pyfunction!(rust_network_tools, m)?)?;
    m.add_function(wrap_pyfunction!(rust_web_browser, m)?)?;
    
    // New consolidated shell tools
    m.add_function(wrap_pyfunction!(rust_shell_execute, m)?)?;
    m.add_function(wrap_pyfunction!(rust_environment_manager, m)?)?;
    
    // Legacy system tools for backward compatibility
    m.add_function(wrap_pyfunction!(get_system_info, m)?)?;
    m.add_function(wrap_pyfunction!(get_battery_status, m)?)?;
    m.add_function(wrap_pyfunction!(get_network_info, m)?)?;
    m.add_function(wrap_pyfunction!(list_processes, m)?)?;
    m.add_function(wrap_pyfunction!(get_disk_info, m)?)?;
    
    // High-performance I/O tools
    m.add_function(wrap_pyfunction!(rust_read_file, m)?)?;
    m.add_function(wrap_pyfunction!(rust_write_file, m)?)?;
    m.add_function(wrap_pyfunction!(rust_list_files, m)?)?;
    
    // Network tools
    m.add_function(wrap_pyfunction!(rust_ping_host, m)?)?;
    m.add_function(wrap_pyfunction!(rust_check_internet, m)?)?;
    
    // Command execution
    m.add_function(wrap_pyfunction!(rust_run_command, m)?)?;
    
    Ok(())
}
