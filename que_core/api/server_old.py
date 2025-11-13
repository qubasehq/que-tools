"""
FastAPI server for Que Core - exposes tool-calling API for AI agents
Provides HTTP and WebSocket endpoints for computer use agents to call tools
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
import asyncio
import uvicorn

# Import tool modules
from que_core.tools import system_tools, context_tools, automation_tools, file_tools, app_tools, shell_tools, network_tools, settings_tools, dev_tools, security_tools, audio_tools, vision_tools, document_tools, data_tools

app = FastAPI(
    title="QUE CORE API",
    description="Tool-calling API for computer use AI agents",
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

# Tool registry - maps tool names to functions
TOOL_REGISTRY = {
    # System tools
    "get_system_info": system_tools.get_system_info,
    "get_battery_status": system_tools.get_battery_status,
    "get_network_info": system_tools.get_network_info,
    "list_processes": system_tools.list_processes,
    "set_volume": system_tools.set_volume,
    "get_volume": system_tools.get_volume,
    "lock_screen": system_tools.lock_screen,
    "shutdown_system": system_tools.shutdown_system,
    
    # Context awareness tools
    "get_active_window_title": context_tools.get_active_window_title,
    "get_cursor_position": context_tools.get_cursor_position,
    "get_clipboard_text": context_tools.get_clipboard_text,
    "set_clipboard_text": context_tools.set_clipboard_text,
    "take_screenshot": context_tools.take_screenshot,
    "detect_idle_state": context_tools.detect_idle_state,
    "get_display_info": context_tools.get_display_info,
    "screen_ocr": context_tools.screen_ocr,
    
    # Automation tools
    "click_at": automation_tools.click_at,
    "type_text": automation_tools.type_text,
    "scroll": automation_tools.scroll,
    "hotkey_press": automation_tools.hotkey_press,
    "drag_to": automation_tools.drag_to,
    "move_mouse": automation_tools.move_mouse,
    "key_press": automation_tools.key_press,
    "double_click": automation_tools.double_click,
    "right_click": automation_tools.right_click,
    "wait_and_click": automation_tools.wait_and_click,
    "safe_terminal_execution": automation_tools.safe_terminal_execution,
    
    # File system tools
    "list_files": file_tools.list_files,
    "read_file": file_tools.read_file,
    "write_file": file_tools.write_file,
    "delete_file": file_tools.delete_file,
    "copy_file": file_tools.copy_file,
    "move_file": file_tools.move_file,
    "get_file_info": file_tools.get_file_info,
    "search_files": file_tools.search_files,
    
    # App control tools
    "open_app": app_tools.open_app,
    "close_app": app_tools.close_app,
    "switch_app": app_tools.switch_app,
    "list_apps": app_tools.list_apps,
    "list_running_apps": app_tools.list_running_apps,
    "get_active_window": app_tools.get_active_window,
    
    # Shell/command tools
    "run_command": shell_tools.run_command,
    "install_package": shell_tools.install_package,
    "get_env_vars": shell_tools.get_env_vars,
    "set_env_var": shell_tools.set_env_var,
    "get_current_directory": shell_tools.get_current_directory,
    "change_directory": shell_tools.change_directory,
    "kill_process_by_pid": shell_tools.kill_process_by_pid,
    "which_command": shell_tools.which_command,
    
    # Network tools
    "ping_host": network_tools.ping_host,
    "download_file": network_tools.download_file,
    "http_request": network_tools.http_request,
    "check_internet": network_tools.check_internet,
    "get_public_ip": network_tools.get_public_ip,
    "open_website": network_tools.open_website,
    
    # System settings tools
    "change_wallpaper": settings_tools.change_wallpaper,
    "set_theme_mode": settings_tools.set_theme_mode,
    "manage_bluetooth": settings_tools.manage_bluetooth,
    "manage_wifi": settings_tools.manage_wifi,
    "set_system_timezone": settings_tools.set_system_timezone,
    "get_installed_fonts": settings_tools.get_installed_fonts,
    
    # Development tools
    "create_virtual_env": dev_tools.create_virtual_env,
    "run_python_script": dev_tools.run_python_script,
    "get_git_status": dev_tools.get_git_status,
    "commit_changes": dev_tools.commit_changes,
    "run_tests": dev_tools.run_tests,
    "build_project": dev_tools.build_project,
    "lint_code": dev_tools.lint_code,
    "format_code": dev_tools.format_code,
    
    # Security and privacy tools
    "encrypt_file": security_tools.encrypt_file,
    "decrypt_file": security_tools.decrypt_file,
    "generate_password": security_tools.generate_password,
    "hash_text": security_tools.hash_text,
    "clear_temp_files": security_tools.clear_temp_files,
    
    # Audio tools
    "record_audio": audio_tools.record_audio,
    "play_audio": audio_tools.play_audio,
    "transcribe_audio": audio_tools.transcribe_audio,
    "speak_text": audio_tools.speak_text,
    "list_audio_devices": audio_tools.list_audio_devices,
    "adjust_mic_gain": audio_tools.adjust_mic_gain,
    "adjust_speaker_volume": audio_tools.adjust_speaker_volume,
    
    # Vision and camera tools
    "capture_camera_image": vision_tools.capture_camera_image,
    "start_camera_stream": vision_tools.start_camera_stream,
    "stop_camera_stream": vision_tools.stop_camera_stream,
    "detect_faces": vision_tools.detect_faces,
    "detect_objects": vision_tools.detect_objects,
    "analyze_scene": vision_tools.analyze_scene,
    
    # Document and text tools
    "summarize_text": document_tools.summarize_text,
    "extract_text_from_pdf": document_tools.extract_text_from_pdf,
    "analyze_sentiment": document_tools.analyze_sentiment,
    "spell_check": document_tools.spell_check,
    "search_text": document_tools.search_text,
    
    # Data and analytics tools
    "load_csv": data_tools.load_csv,
    "describe_data": data_tools.describe_data,
    "plot_chart": data_tools.plot_chart,
    "query_data": data_tools.query_data,
    "export_data": data_tools.export_data,
}

class ToolCall(BaseModel):
    """Tool call request from AI agent"""
    tool_name: str
    args: Optional[Dict[str, Any]] = None

class ToolResponse(BaseModel):
    """Tool execution response"""
    success: bool
    result: Any = None
    error: Optional[str] = None
    tool_name: str

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "QUE CORE API is running", "version": "0.1.0"}

@app.get("/tools")
async def list_tools():
    """List all available tools for AI agents"""
    tools = []
    for tool_name, tool_func in TOOL_REGISTRY.items():
        tools.append({
            "name": tool_name,
            "description": tool_func.__doc__ or "No description available",
            "category": tool_name.split("_")[0] if "_" in tool_name else "misc"
        })
    return {"tools": tools, "total_count": len(tools)}

@app.post("/call_tool", response_model=ToolResponse)
async def call_tool(tool_call: ToolCall):
    """Execute a single tool call"""
    if tool_call.tool_name not in TOOL_REGISTRY:
        raise HTTPException(
            status_code=404, 
            detail=f"Tool '{tool_call.tool_name}' not found"
        )
    
    try:
        tool_func = TOOL_REGISTRY[tool_call.tool_name]
        result = tool_func(args=tool_call.args or {})
        
        return ToolResponse(
            success=result.get("success", False),
            result=result.get("result"),
            error=result.get("error"),
            tool_name=tool_call.tool_name
        )
    except Exception as e:
        return ToolResponse(
            success=False,
            result=None,
            error=f"Tool execution failed: {str(e)}",
            tool_name=tool_call.tool_name
        )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time tool calling"""
    await websocket.accept()
    try:
        while True:
            # Receive tool call from AI agent
            data = await websocket.receive_text()
            try:
                tool_call_data = json.loads(data)
                tool_call = ToolCall(**tool_call_data)
                
                if tool_call.tool_name not in TOOL_REGISTRY:
                    await websocket.send_text(json.dumps({
                        "success": False,
                        "error": f"Tool '{tool_call.tool_name}' not found",
                        "tool_name": tool_call.tool_name
                    }))
                    continue
                
                # Execute tool
                tool_func = TOOL_REGISTRY[tool_call.tool_name]
                result = tool_func(args=tool_call.args or {})
                
                # Send result back to AI agent
                response = {
                    "success": result.get("success", False),
                    "result": result.get("result"),
                    "error": result.get("error"),
                    "tool_name": tool_call.tool_name
                }
                await websocket.send_text(json.dumps(response))
                
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "success": False,
                    "error": "Invalid JSON format",
                    "tool_name": "unknown"
                }))
            except Exception as e:
                await websocket.send_text(json.dumps({
                    "success": False,
                    "error": f"Tool execution failed: {str(e)}",
                    "tool_name": tool_call.tool_name if 'tool_call' in locals() else "unknown"
                }))
                
    except WebSocketDisconnect:
        print("AI agent disconnected from WebSocket")

def start_server(host: str = "127.0.0.1", port: int = 8000):
    """Start the QUE CORE API server"""
    print(f"Starting QUE CORE API server on {host}:{port}")
    print("Available endpoints:")
    print(f"  - Health check: http://{host}:{port}/")
    print(f"  - List tools: http://{host}:{port}/tools")
    print(f"  - Call tool: POST http://{host}:{port}/call_tool")
    print(f"  - WebSocket: ws://{host}:{port}/ws")
    
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()
