"""
Automation Tools - Consolidated UI interaction and automation sequences for AI agents
Provides unified mouse, keyboard, and automation control for computer use agents.
"""
from typing import Any, Dict, List
import time
import json

def interact(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Universal UI interaction - replaces click_at, type_text, scroll, hotkey_press, drag_to, move_mouse, key_press, double_click, right_click
    
    Args:
        action (str): Action to perform - 'click', 'type', 'scroll', 'hotkey', 'drag', 'move', 'key', 'double_click', 'right_click'
        x, y (int): Coordinates for click/move/drag actions
        text (str): Text to type
        direction (str): Scroll direction - 'up', 'down', 'left', 'right'
        amount (int): Scroll amount or click count
        button (str): Mouse button - 'left', 'right', 'middle'
        keys (str/list): Hotkey combination or single key
        to_x, to_y (int): Target coordinates for drag actions
        duration (float): Duration for smooth movements
        
    Returns:
        Dict with action result
    """
    if not args or "action" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: action"}
    
    action = args["action"]
    
    try:
        if action == "click":
            return _click_impl(args)
        elif action == "double_click":
            return _double_click_impl(args)
        elif action == "right_click":
            return _right_click_impl(args)
        elif action == "type":
            return _type_text_impl(args)
        elif action == "scroll":
            return _scroll_impl(args)
        elif action == "hotkey":
            return _hotkey_impl(args)
        elif action == "drag":
            return _drag_impl(args)
        elif action == "move":
            return _move_mouse_impl(args)
        elif action == "key":
            return _key_press_impl(args)
        else:
            return {
                "success": False,
                "result": None,
                "error": f"Unknown action: {action}. Use: click, double_click, right_click, type, scroll, hotkey, drag, move, key"
            }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Interaction failed: {str(e)}"}

def automation_sequence(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Automation sequence executor - replaces wait_and_click, run_macro, record_macro, safe_terminal_execution
    
    Args:
        action (str): Action to perform - 'execute', 'record', 'stop_record', 'save_macro', 'load_macro'
        steps (list): List of interaction steps to execute
        macro_name (str): Name of macro to save/load
        delay (float): Delay between steps (default: 0.1)
        
    Returns:
        Dict with sequence execution result
    """
    if not args or "action" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: action"}
    
    action = args["action"]
    
    try:
        if action == "execute":
            return _execute_sequence_impl(args)
        elif action == "record":
            return _start_recording_impl(args)
        elif action == "stop_record":
            return _stop_recording_impl(args)
        elif action == "save_macro":
            return _save_macro_impl(args)
        elif action == "load_macro":
            return _load_macro_impl(args)
        else:
            return {
                "success": False,
                "result": None,
                "error": f"Unknown action: {action}. Use: execute, record, stop_record, save_macro, load_macro"
            }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Automation sequence failed: {str(e)}"}

# Interaction Implementation Helpers
def _click_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Click implementation"""
    try:
        import pyautogui
        pyautogui.FAILSAFE = True
        
        x = args.get("x")
        y = args.get("y")
        if x is None or y is None:
            return {"success": False, "result": None, "error": "Missing required arguments: x, y"}
        
        button = args.get("button", "left")
        clicks = args.get("clicks", 1)
        duration = args.get("duration", 0.1)
        
        # Validate coordinates
        screen_width, screen_height = pyautogui.size()
        if not (0 <= x <= screen_width and 0 <= y <= screen_height):
            return {
                "success": False,
                "result": None,
                "error": f"Coordinates ({x}, {y}) outside screen bounds ({screen_width}x{screen_height})"
            }
        
        # Perform click
        pyautogui.click(x, y, clicks=clicks, interval=duration, button=button)
        
        return {
            "success": True,
            "result": {
                "action": "click",
                "x": x,
                "y": y,
                "button": button,
                "clicks": clicks,
                "method": "pyautogui"
            },
            "error": None
        }
    
    except ImportError:
        return {"success": False, "result": None, "error": "UI automation requires pyautogui (pip install pyautogui)"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Click failed: {str(e)}"}

def _double_click_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Double click implementation"""
    args["clicks"] = 2
    args["duration"] = 0.05  # Faster for double click
    return _click_impl(args)

def _right_click_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Right click implementation"""
    args["button"] = "right"
    return _click_impl(args)

def _type_text_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Type text implementation"""
    try:
        import pyautogui
        
        text = args.get("text")
        if not text:
            return {"success": False, "result": None, "error": "Missing required argument: text"}
        
        interval = args.get("interval", 0.01)  # Typing speed
        
        # Type the text
        pyautogui.typewrite(text, interval=interval)
        
        return {
            "success": True,
            "result": {
                "action": "type",
                "text": text,
                "length": len(text),
                "interval": interval,
                "method": "pyautogui"
            },
            "error": None
        }
    
    except ImportError:
        return {"success": False, "result": None, "error": "Text typing requires pyautogui (pip install pyautogui)"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Type text failed: {str(e)}"}

def _scroll_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Scroll implementation"""
    try:
        import pyautogui
        
        direction = args.get("direction", "down")
        amount = args.get("amount", 3)
        x = args.get("x")
        y = args.get("y")
        
        # Convert direction to scroll amount
        if direction == "up":
            scroll_amount = amount
        elif direction == "down":
            scroll_amount = -amount
        else:
            return {"success": False, "result": None, "error": f"Unsupported scroll direction: {direction}. Use 'up' or 'down'"}
        
        # Scroll at specific position or current mouse position
        if x is not None and y is not None:
            pyautogui.scroll(scroll_amount, x=x, y=y)
        else:
            pyautogui.scroll(scroll_amount)
        
        return {
            "success": True,
            "result": {
                "action": "scroll",
                "direction": direction,
                "amount": amount,
                "x": x,
                "y": y,
                "method": "pyautogui"
            },
            "error": None
        }
    
    except ImportError:
        return {"success": False, "result": None, "error": "Scrolling requires pyautogui (pip install pyautogui)"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Scroll failed: {str(e)}"}

def _hotkey_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Hotkey implementation"""
    try:
        import pyautogui
        
        keys = args.get("keys")
        if not keys:
            return {"success": False, "result": None, "error": "Missing required argument: keys"}
        
        # Handle different key formats
        if isinstance(keys, str):
            # Split by + for combinations like "ctrl+c"
            key_list = [k.strip() for k in keys.split('+')]
        elif isinstance(keys, list):
            key_list = keys
        else:
            return {"success": False, "result": None, "error": "Keys must be string or list"}
        
        # Execute hotkey
        pyautogui.hotkey(*key_list)
        
        return {
            "success": True,
            "result": {
                "action": "hotkey",
                "keys": key_list,
                "combination": "+".join(key_list),
                "method": "pyautogui"
            },
            "error": None
        }
    
    except ImportError:
        return {"success": False, "result": None, "error": "Hotkeys require pyautogui (pip install pyautogui)"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Hotkey failed: {str(e)}"}

def _drag_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Drag implementation"""
    try:
        import pyautogui
        
        x = args.get("x")
        y = args.get("y")
        to_x = args.get("to_x")
        to_y = args.get("to_y")
        
        if any(coord is None for coord in [x, y, to_x, to_y]):
            return {"success": False, "result": None, "error": "Missing required arguments: x, y, to_x, to_y"}
        
        duration = args.get("duration", 0.5)
        button = args.get("button", "left")
        
        # Validate coordinates
        screen_width, screen_height = pyautogui.size()
        for coord_x, coord_y in [(x, y), (to_x, to_y)]:
            if not (0 <= coord_x <= screen_width and 0 <= coord_y <= screen_height):
                return {
                    "success": False,
                    "result": None,
                    "error": f"Coordinates ({coord_x}, {coord_y}) outside screen bounds"
                }
        
        # Perform drag
        pyautogui.drag(to_x - x, to_y - y, duration=duration, button=button)
        
        return {
            "success": True,
            "result": {
                "action": "drag",
                "from": {"x": x, "y": y},
                "to": {"x": to_x, "y": to_y},
                "distance": ((to_x - x) ** 2 + (to_y - y) ** 2) ** 0.5,
                "duration": duration,
                "button": button,
                "method": "pyautogui"
            },
            "error": None
        }
    
    except ImportError:
        return {"success": False, "result": None, "error": "Dragging requires pyautogui (pip install pyautogui)"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Drag failed: {str(e)}"}

def _move_mouse_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Move mouse implementation"""
    try:
        import pyautogui
        
        x = args.get("x")
        y = args.get("y")
        if x is None or y is None:
            return {"success": False, "result": None, "error": "Missing required arguments: x, y"}
        
        duration = args.get("duration", 0.2)
        
        # Validate coordinates
        screen_width, screen_height = pyautogui.size()
        if not (0 <= x <= screen_width and 0 <= y <= screen_height):
            return {
                "success": False,
                "result": None,
                "error": f"Coordinates ({x}, {y}) outside screen bounds"
            }
        
        # Get current position
        current_x, current_y = pyautogui.position()
        
        # Move mouse
        pyautogui.moveTo(x, y, duration=duration)
        
        return {
            "success": True,
            "result": {
                "action": "move",
                "from": {"x": current_x, "y": current_y},
                "to": {"x": x, "y": y},
                "duration": duration,
                "method": "pyautogui"
            },
            "error": None
        }
    
    except ImportError:
        return {"success": False, "result": None, "error": "Mouse movement requires pyautogui (pip install pyautogui)"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Mouse movement failed: {str(e)}"}

def _key_press_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Key press implementation"""
    try:
        import pyautogui
        
        key = args.get("key")
        if not key:
            return {"success": False, "result": None, "error": "Missing required argument: key"}
        
        presses = args.get("presses", 1)
        interval = args.get("interval", 0.1)
        
        # Press key(s)
        pyautogui.press(key, presses=presses, interval=interval)
        
        return {
            "success": True,
            "result": {
                "action": "key_press",
                "key": key,
                "presses": presses,
                "interval": interval,
                "method": "pyautogui"
            },
            "error": None
        }
    
    except ImportError:
        return {"success": False, "result": None, "error": "Key press requires pyautogui (pip install pyautogui)"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Key press failed: {str(e)}"}

# Automation Sequence Implementation Helpers
def _execute_sequence_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute automation sequence implementation"""
    try:
        steps = args.get("steps")
        if not steps:
            return {"success": False, "result": None, "error": "Missing required argument: steps"}
        
        if not isinstance(steps, list):
            return {"success": False, "result": None, "error": "Steps must be a list"}
        
        delay = args.get("delay", 0.1)
        results = []
        
        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                return {"success": False, "result": None, "error": f"Step {i} must be a dictionary"}
            
            # Execute the step using interact function
            step_result = interact(args=step)
            results.append({
                "step": i,
                "action": step.get("action", "unknown"),
                "success": step_result["success"],
                "error": step_result.get("error")
            })
            
            # Stop on first failure if specified
            if not step_result["success"] and args.get("stop_on_error", True):
                return {
                    "success": False,
                    "result": {
                        "completed_steps": i,
                        "total_steps": len(steps),
                        "results": results,
                        "method": "sequence_execution"
                    },
                    "error": f"Step {i} failed: {step_result['error']}"
                }
            
            # Delay between steps
            if delay > 0 and i < len(steps) - 1:
                time.sleep(delay)
        
        successful_steps = sum(1 for r in results if r["success"])
        
        return {
            "success": True,
            "result": {
                "completed_steps": len(steps),
                "successful_steps": successful_steps,
                "total_steps": len(steps),
                "results": results,
                "method": "sequence_execution"
            },
            "error": None
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Sequence execution failed: {str(e)}"}

def _start_recording_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Start macro recording implementation"""
    try:
        # Macro recording would require event listeners
        # This is a placeholder implementation
        return {
            "success": False,
            "result": None,
            "error": "Macro recording requires additional setup (event listeners, input monitoring)"
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Recording start failed: {str(e)}"}

def _stop_recording_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Stop macro recording implementation"""
    try:
        return {
            "success": False,
            "result": None,
            "error": "Macro recording not yet implemented"
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Recording stop failed: {str(e)}"}

def _save_macro_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Save macro implementation"""
    try:
        macro_name = args.get("macro_name")
        steps = args.get("steps")
        
        if not macro_name:
            return {"success": False, "result": None, "error": "Missing required argument: macro_name"}
        
        if not steps:
            return {"success": False, "result": None, "error": "Missing required argument: steps"}
        
        # Save macro to file (simplified implementation)
        import os
        import tempfile
        
        macro_dir = os.path.join(tempfile.gettempdir(), "que_core_macros")
        os.makedirs(macro_dir, exist_ok=True)
        
        macro_file = os.path.join(macro_dir, f"{macro_name}.json")
        
        macro_data = {
            "name": macro_name,
            "steps": steps,
            "created": time.time(),
            "version": "1.0"
        }
        
        with open(macro_file, 'w') as f:
            json.dump(macro_data, f, indent=2)
        
        return {
            "success": True,
            "result": {
                "macro_name": macro_name,
                "file_path": macro_file,
                "steps_count": len(steps),
                "saved": True,
                "method": "file_save"
            },
            "error": None
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Macro save failed: {str(e)}"}

def _load_macro_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Load macro implementation"""
    try:
        macro_name = args.get("macro_name")
        if not macro_name:
            return {"success": False, "result": None, "error": "Missing required argument: macro_name"}
        
        # Load macro from file
        import os
        import tempfile
        
        macro_dir = os.path.join(tempfile.gettempdir(), "que_core_macros")
        macro_file = os.path.join(macro_dir, f"{macro_name}.json")
        
        if not os.path.exists(macro_file):
            return {"success": False, "result": None, "error": f"Macro '{macro_name}' not found"}
        
        with open(macro_file, 'r') as f:
            macro_data = json.load(f)
        
        return {
            "success": True,
            "result": {
                "macro_name": macro_name,
                "steps": macro_data.get("steps", []),
                "steps_count": len(macro_data.get("steps", [])),
                "created": macro_data.get("created"),
                "loaded": True,
                "method": "file_load"
            },
            "error": None
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Macro load failed: {str(e)}"}

# Legacy function aliases for backward compatibility
def click_at(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use interact instead"""
    return interact(args={"action": "click", **(args or {})})

def type_text(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use interact instead"""
    return interact(args={"action": "type", **(args or {})})

def scroll(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use interact instead"""
    return interact(args={"action": "scroll", **(args or {})})

def hotkey_press(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use interact instead"""
    return interact(args={"action": "hotkey", **(args or {})})

def drag_to(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use interact instead"""
    return interact(args={"action": "drag", **(args or {})})

def move_mouse(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use interact instead"""
    return interact(args={"action": "move", **(args or {})})

def key_press(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use interact instead"""
    return interact(args={"action": "key", **(args or {})})

def double_click(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use interact instead"""
    return interact(args={"action": "double_click", **(args or {})})

def right_click(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use interact instead"""
    return interact(args={"action": "right_click", **(args or {})})

def run_macro(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use automation_sequence instead"""
    macro_name = args.get("macro_name") if args else None
    if macro_name:
        # Load and execute macro
        load_result = automation_sequence(args={"action": "load_macro", "macro_name": macro_name})
        if load_result["success"]:
            steps = load_result["result"]["steps"]
            return automation_sequence(args={"action": "execute", "steps": steps})
        else:
            return load_result
    else:
        return {"success": False, "result": None, "error": "Missing macro_name"}

def record_macro(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use automation_sequence instead"""
    return automation_sequence(args={"action": "record", **(args or {})})

def schedule_task(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - not yet implemented"""
    return {"success": False, "result": None, "error": "Task scheduling not yet implemented"}

def list_scheduled_tasks(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - not yet implemented"""
    return {"success": False, "result": None, "error": "Task scheduling not yet implemented"}

def cancel_scheduled_task(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - not yet implemented"""
    return {"success": False, "result": None, "error": "Task scheduling not yet implemented"}

def trigger_system_event(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - not yet implemented"""
    return {"success": False, "result": None, "error": "System events not yet implemented"}
