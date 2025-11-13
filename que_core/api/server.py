"""
FastAPI server for Que Core - exposes consolidated tool-calling API for AI agents
Provides HTTP and WebSocket endpoints for computer use agents to call consolidated tools
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
import asyncio
import uvicorn

# Import consolidated tool modules
from que_core.tools import (
    system_tools, context_tools, automation_tools, file_tools, app_tools, 
    shell_tools, network_tools, settings_tools, dev_tools, security_tools, 
    audio_tools, vision_tools, document_tools, data_tools
)

app = FastAPI(
    title="QUE CORE API",
    description="Consolidated tool-calling API for computer use AI agents",
    version="0.1.0"
)

# Enable CORS for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Consolidated Tool Registry - maps tool names to consolidated functions
CONSOLIDATED_TOOLS = {
    # System tools (3 consolidated tools)
    "system_query": system_tools.system_query,
    "system_control": system_tools.system_control,
    "process_manager": system_tools.process_manager,
    
    # App & Window Control (2 consolidated tools)
    "app_manager": app_tools.app_manager,
    "window_control": app_tools.window_control,
    
    # File System (2 consolidated tools)
    "file_manager": file_tools.file_manager,
    "file_search": file_tools.file_search,
    
    # Network & Web (3 consolidated tools)
    "network_tools": network_tools.network_tools,
    "web_browser": network_tools.web_browser,
    "auto_web_search": network_tools.auto_web_search,
    
    # Shell & Commands (2 consolidated tools)
    "shell_execute": shell_tools.shell_execute,
    "environment_manager": shell_tools.environment_manager,
    
    # Context Awareness (2 consolidated tools)
    "context_get": context_tools.context_get,
    "context_capture": context_tools.context_capture,
    
    # Media & Audio (2 consolidated tools)
    "audio_control": audio_tools.audio_control,
    "media_processor": audio_tools.media_processor,
    
    # Vision & Camera (1 consolidated tool)
    "vision_system": vision_tools.vision_system,
    
    # UI Interaction/Automation (2 consolidated tools)
    "interact": automation_tools.interact,
    "automation_sequence": automation_tools.automation_sequence,
    
    # Documents & Text (2 consolidated tools)
    "document_processor": document_tools.document_processor,
    "text_analyzer": document_tools.text_analyzer,
    
    # Development Tools (2 consolidated tools)
    "dev_assistant": dev_tools.dev_assistant,
    "code_manager": dev_tools.code_manager,
    
    # Data & Analytics (1 consolidated tool)
    "data_processor": data_tools.data_processor,
    
    # Security & Privacy (1 consolidated tool)
    "security_manager": security_tools.security_manager,
    
    # System Settings (1 consolidated tool)
    "settings_manager": settings_tools.settings_manager,
}

# Legacy Tool Registry - for backward compatibility
LEGACY_TOOLS = {
    # Legacy system tools
    "get_system_info": system_tools.get_system_info,
    "get_battery_status": system_tools.get_battery_status,
    "get_network_info": system_tools.get_network_info,
    "list_processes": system_tools.list_processes,
    "set_volume": system_tools.set_volume,
    "get_volume": system_tools.get_volume,
    "lock_screen": system_tools.lock_screen,
    "shutdown_system": system_tools.shutdown_system,
    
    # Legacy context tools
    "get_active_window_title": context_tools.get_active_window_title,
    "get_cursor_position": context_tools.get_cursor_position,
    "get_clipboard_text": context_tools.get_clipboard_text,
    "set_clipboard_text": context_tools.set_clipboard_text,
    "take_screenshot": context_tools.take_screenshot,
    "detect_idle_state": context_tools.detect_idle_state,
    "get_display_info": context_tools.get_display_info,
    "screen_ocr": context_tools.screen_ocr,
    
    # Legacy automation tools
    "click_at": automation_tools.click_at,
    "type_text": automation_tools.type_text,
    "scroll": automation_tools.scroll,
    "hotkey_press": automation_tools.hotkey_press,
    "drag_to": automation_tools.drag_to,
    "move_mouse": automation_tools.move_mouse,
    "key_press": automation_tools.key_press,
    "double_click": automation_tools.double_click,
    "right_click": automation_tools.right_click,
    "run_macro": automation_tools.run_macro,
    "record_macro": automation_tools.record_macro,
    
    # Legacy file tools
    "list_files": file_tools.list_files,
    "read_file": file_tools.read_file,
    "write_file": file_tools.write_file,
    "delete_file": file_tools.delete_file,
    "copy_file": file_tools.copy_file,
    "move_file": file_tools.move_file,
    "get_file_info": file_tools.get_file_info,
    "search_files": file_tools.search_files,
    
    # Legacy app tools
    "open_app": app_tools.open_app,
    "close_app": app_tools.close_app,
    "switch_app": app_tools.switch_app,
    "list_apps": app_tools.list_apps,
    "list_running_apps": app_tools.list_running_apps,
    "get_active_window": app_tools.get_active_window,
    
    # Legacy shell tools
    "run_command": shell_tools.run_command,
    "install_package": shell_tools.install_package,
    "get_env_vars": shell_tools.get_env_vars,
    "set_env_var": shell_tools.set_env_var,
    "kill_process_by_pid": shell_tools.kill_process_by_pid,
    "start_shell_session": shell_tools.start_shell_session,
    
    # Legacy network tools
    "ping_host": network_tools.ping_host,
    "download_file": network_tools.download_file,
    "http_request": network_tools.http_request,
    "check_internet": network_tools.check_internet,
    "get_public_ip": network_tools.get_public_ip,
    "open_website": network_tools.open_website,
    
    # Legacy settings tools
    "change_wallpaper": settings_tools.change_wallpaper,
    "set_theme_mode": settings_tools.set_theme_mode,
    "manage_bluetooth": settings_tools.manage_bluetooth,
    "manage_wifi": settings_tools.manage_wifi,
    "set_system_timezone": settings_tools.set_system_timezone,
    "get_installed_fonts": settings_tools.get_installed_fonts,
    
    # Legacy dev tools
    "create_virtual_env": dev_tools.create_virtual_env,
    "run_python_script": dev_tools.run_python_script,
    "get_git_status": dev_tools.get_git_status,
    "commit_changes": dev_tools.commit_changes,
    "run_tests": dev_tools.run_tests,
    "build_project": dev_tools.build_project,
    "lint_code": dev_tools.lint_code,
    "format_code": dev_tools.format_code,
    
    # Legacy security tools
    "encrypt_file": security_tools.encrypt_file,
    "decrypt_file": security_tools.decrypt_file,
    "generate_password": security_tools.generate_password,
    "hash_text": security_tools.hash_text,
    "clear_temp_files": security_tools.clear_temp_files,
    
    # Legacy audio tools
    "record_audio": audio_tools.record_audio,
    "play_audio": audio_tools.play_audio,
    "speak_text": audio_tools.speak_text,
    "transcribe_audio": audio_tools.transcribe_audio,
    "list_audio_devices": audio_tools.list_audio_devices,
    
    # Legacy vision tools
    "capture_camera_image": vision_tools.capture_camera_image,
    "start_camera_stream": vision_tools.start_camera_stream,
    "stop_camera_stream": vision_tools.stop_camera_stream,
    "detect_faces": vision_tools.detect_faces,
    "detect_objects": vision_tools.detect_objects,
    "analyze_scene": vision_tools.analyze_scene,
    
    # Legacy document tools
    "summarize_text": document_tools.summarize_text,
    "extract_text_from_pdf": document_tools.extract_text_from_pdf,
    "convert_doc_format": document_tools.convert_doc_format,
    "analyze_sentiment": document_tools.analyze_sentiment,
    "spell_check": document_tools.spell_check,
    "translate_text": document_tools.translate_text,
    "search_text": document_tools.search_text,
    
    # Legacy data tools
    "load_csv": data_tools.load_csv,
    "describe_data": data_tools.describe_data,
    "plot_chart": data_tools.plot_chart,
    "query_data": data_tools.query_data,
    "export_data": data_tools.export_data,
}

# Combined registry for all tools
ALL_TOOLS = {**CONSOLIDATED_TOOLS, **LEGACY_TOOLS}

class ToolRequest(BaseModel):
    tool_name: str
    args: Optional[Dict[str, Any]] = None

class ToolResponse(BaseModel):
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    tool_name: str
    execution_time_ms: Optional[float] = None

@app.get("/")
async def root():
    return {
        "message": "QUE CORE API - Computer Use Agent Tool Server",
        "version": "0.1.0",
        "consolidated_tools": len(CONSOLIDATED_TOOLS),
        "legacy_tools": len(LEGACY_TOOLS),
        "total_tools": len(ALL_TOOLS)
    }

@app.get("/tools")
async def list_tools():
    """List all available tools"""
    return {
        "consolidated_tools": list(CONSOLIDATED_TOOLS.keys()),
        "legacy_tools": list(LEGACY_TOOLS.keys()),
        "total_count": len(ALL_TOOLS),
        "recommended": "Use consolidated tools for better performance and fewer API calls"
    }

@app.get("/tools/consolidated")
async def list_consolidated_tools():
    """List only consolidated tools (recommended)"""
    return {
        "tools": list(CONSOLIDATED_TOOLS.keys()),
        "count": len(CONSOLIDATED_TOOLS),
        "description": "These are the new consolidated tools that replace multiple legacy tools"
    }

@app.post("/call", response_model=ToolResponse)
async def call_tool(request: ToolRequest):
    """Call a tool with arguments"""
    import time
    start_time = time.time()
    
    if request.tool_name not in ALL_TOOLS:
        raise HTTPException(
            status_code=404, 
            detail=f"Tool '{request.tool_name}' not found. Available tools: {list(ALL_TOOLS.keys())}"
        )
    
    try:
        tool_function = ALL_TOOLS[request.tool_name]
        result = tool_function(args=request.args or {})
        
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return ToolResponse(
            success=result.get("success", False),
            result=result.get("result"),
            error=result.get("error"),
            tool_name=request.tool_name,
            execution_time_ms=round(execution_time, 2)
        )
    
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        return ToolResponse(
            success=False,
            result=None,
            error=f"Tool execution failed: {str(e)}",
            tool_name=request.tool_name,
            execution_time_ms=round(execution_time, 2)
        )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time tool calling"""
    await websocket.accept()
    
    try:
        while True:
            # Receive tool request
            data = await websocket.receive_text()
            request_data = json.loads(data)
            
            # Create tool request
            request = ToolRequest(**request_data)
            
            # Execute tool
            response = await call_tool(request)
            
            # Send response
            await websocket.send_text(response.json())
    
    except WebSocketDisconnect:
        print("WebSocket client disconnected")
    except Exception as e:
        await websocket.send_text(json.dumps({
            "success": False,
            "error": f"WebSocket error: {str(e)}"
        }))

def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the QUE CORE API server"""
    print(f"🚀 Starting QUE CORE API Server...")
    print(f"📡 Server URL: http://{host}:{port}")
    print(f"🔧 Consolidated Tools: {len(CONSOLIDATED_TOOLS)}")
    print(f"🔄 Legacy Tools: {len(LEGACY_TOOLS)}")
    print(f"📊 Total Tools: {len(ALL_TOOLS)}")
    
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()
