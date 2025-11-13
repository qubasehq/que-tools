"""
File Tools - Consolidated file operations for AI agents
Provides unified file management and smart search capabilities.
"""
from typing import Any, Dict, List
import os
import shutil
import pathlib
import json
import base64

# Try to import Rust engine for high-performance I/O
try:
    from que_core_engine import rust_read_file, rust_write_file, rust_list_files, rust_file_manager, rust_file_search
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False

def file_manager(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Universal file manager - replaces list_files, read_file, write_file, delete_file, copy_file, move_file, get_file_info
    
    Args:
        action (str): Action to perform - 'list', 'read', 'write', 'delete', 'copy', 'move', 'info'
        path (str): Primary file/directory path
        content (str): Content for write operations
        to_path (str): Destination path for copy/move operations
        
    Returns:
        Dict with operation result
    """
    if not args or "action" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: action"}
    
    action = args["action"]
    path = args.get("path", "")
    content = args.get("content")
    to_path = args.get("to_path")
    
    # Try Rust implementation first for performance
    if RUST_AVAILABLE:
        try:
            result_json = rust_file_manager(action, path, content, to_path)
            return json.loads(result_json)
        except Exception:
            # Fall back to Python implementation
            pass
    
    # Python fallback implementation
    try:
        if action == "list":
            return _list_files_impl(args)
        elif action == "read":
            return _read_file_impl(args)
        elif action == "write":
            return _write_file_impl(args)
        elif action == "delete":
            return _delete_file_impl(args)
        elif action == "copy":
            return _copy_file_impl(args)
        elif action == "move":
            return _move_file_impl(args)
        elif action == "info":
            return _get_file_info_impl(args)
        else:
            return {
                "success": False,
                "result": None,
                "error": f"Unknown action: {action}. Use: list, read, write, delete, copy, move, info"
            }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"File operation failed: {str(e)}"}

def file_search(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Smart file search - replaces search_files with AI-powered search
    
    Args:
        query (str): Search query (filename, content, or pattern)
        path (str): Directory to search in (default: current directory)
        search_type (str): Type of search - 'name', 'content', 'both'
        extensions (list): File extensions to include
        
    Returns:
        Dict with search results
    """
    if not args or "query" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: query"}
    
    query = args["query"]
    search_path = args.get("path", ".")
    search_type = args.get("search_type", "both")
    extensions = args.get("extensions", [])
    
    # Try Rust implementation first for performance
    if RUST_AVAILABLE:
        try:
            result_json = rust_file_search(query, search_path, search_type, extensions)
            return json.loads(result_json)
        except Exception:
            # Fall back to Python implementation
            pass
    
    # Python fallback implementation
    try:
        import fnmatch
        import re
        
        results = []
        
        # Walk through directory tree
        for root, dirs, files in os.walk(search_path):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Filter by extensions if specified
                if extensions:
                    file_ext = os.path.splitext(file)[1].lower().lstrip('.')
                    if file_ext not in extensions:
                        continue
                
                match_score = 0
                match_reasons = []
                
                # Search by filename
                if search_type in ["name", "both"]:
                    if query.lower() in file.lower():
                        match_score += 10
                        match_reasons.append("filename_contains")
                    elif fnmatch.fnmatch(file.lower(), f"*{query.lower()}*"):
                        match_score += 5
                        match_reasons.append("filename_pattern")
                
                # Search by content (for text files)
                if search_type in ["content", "both"]:
                    try:
                        # Only search in text files
                        if _is_text_file(file_path):
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if query.lower() in content.lower():
                                    match_score += 15
                                    match_reasons.append("content_contains")
                                    
                                    # Count occurrences
                                    occurrences = len(re.findall(re.escape(query.lower()), content.lower()))
                                    match_score += min(occurrences, 10)  # Cap bonus at 10
                    except (PermissionError, UnicodeDecodeError, OSError):
                        pass
                
                if match_score > 0:
                    file_info = {
                        "path": file_path,
                        "name": file,
                        "directory": root,
                        "size": os.path.getsize(file_path),
                        "modified": os.path.getmtime(file_path),
                        "match_score": match_score,
                        "match_reasons": match_reasons
                    }
                    results.append(file_info)
        
        # Sort by match score (highest first)
        results.sort(key=lambda x: x["match_score"], reverse=True)
        
        return {
            "success": True,
            "result": {
                "query": query,
                "search_path": search_path,
                "search_type": search_type,
                "files_found": len(results),
                "results": results[:50]  # Limit to top 50 results
            },
            "error": None
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Search failed: {str(e)}"}

# Implementation helpers
def _list_files_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """List files implementation"""
    path = args.get("path", ".")
    
    # Try Rust implementation first
    if RUST_AVAILABLE:
        try:
            result_json = rust_list_files(path)
            result = json.loads(result_json)
            
            # Apply filters
            show_hidden = args.get("show_hidden", False)
            file_types_only = args.get("file_types_only", False)
            
            if not show_hidden or file_types_only:
                items = result.get("result", {}).get("items", [])
                filtered_items = []
                
                for item in items:
                    if not show_hidden and item["name"].startswith('.'):
                        continue
                    if file_types_only and item["type"] != "file":
                        continue
                    filtered_items.append(item)
                
                result["result"]["items"] = filtered_items
                result["result"]["total_count"] = len(filtered_items)
            
            return result
        except Exception:
            pass
    
    # Python fallback
    try:
        if not os.path.exists(path):
            return {"success": False, "result": None, "error": f"Path does not exist: {path}"}
        
        if not os.path.isdir(path):
            return {"success": False, "result": None, "error": f"Path is not a directory: {path}"}
        
        show_hidden = args.get("show_hidden", False)
        file_types_only = args.get("file_types_only", False)
        
        items = []
        for item_name in os.listdir(path):
            if not show_hidden and item_name.startswith('.'):
                continue
                
            item_path = os.path.join(path, item_name)
            is_file = os.path.isfile(item_path)
            
            if file_types_only and not is_file:
                continue
            
            items.append({
                "name": item_name,
                "path": item_path,
                "type": "file" if is_file else "directory",
                "size": os.path.getsize(item_path) if is_file else 0,
                "modified": os.path.getmtime(item_path)
            })
        
        return {
            "success": True,
            "result": {
                "path": path,
                "items": items,
                "total_count": len(items)
            },
            "error": None
        }
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to list files: {str(e)}"}

def _read_file_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Read file implementation"""
    path = args.get("path")
    if not path:
        return {"success": False, "result": None, "error": "Missing required argument: path"}
    
    # Try Rust implementation first
    if RUST_AVAILABLE:
        try:
            result_json = rust_read_file(path)
            return json.loads(result_json)
        except Exception:
            pass
    
    # Python fallback
    try:
        if not os.path.exists(path):
            return {"success": False, "result": None, "error": f"File does not exist: {path}"}
        
        if not os.path.isfile(path):
            return {"success": False, "result": None, "error": f"Path is not a file: {path}"}
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "success": True,
            "result": {
                "path": path,
                "content": content,
                "size": len(content),
                "encoding": "utf-8"
            },
            "error": None
        }
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to read file: {str(e)}"}

def _write_file_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Write file implementation"""
    path = args.get("path")
    content = args.get("content", "")
    
    if not path:
        return {"success": False, "result": None, "error": "Missing required argument: path"}
    
    # Try Rust implementation first
    if RUST_AVAILABLE:
        try:
            result_json = rust_write_file(path, content)
            return json.loads(result_json)
        except Exception:
            pass
    
    # Python fallback
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "success": True,
            "result": {
                "path": path,
                "bytes_written": len(content.encode('utf-8')),
                "encoding": "utf-8"
            },
            "error": None
        }
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to write file: {str(e)}"}

def _delete_file_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Delete file implementation"""
    path = args.get("path")
    if not path:
        return {"success": False, "result": None, "error": "Missing required argument: path"}
    
    try:
        if not os.path.exists(path):
            return {"success": False, "result": None, "error": f"Path does not exist: {path}"}
        
        if os.path.isfile(path):
            os.remove(path)
            action = "file_deleted"
        elif os.path.isdir(path):
            shutil.rmtree(path)
            action = "directory_deleted"
        else:
            return {"success": False, "result": None, "error": f"Unknown path type: {path}"}
        
        return {
            "success": True,
            "result": {"path": path, "action": action},
            "error": None
        }
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to delete: {str(e)}"}

def _copy_file_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Copy file implementation"""
    path = args.get("path")
    to_path = args.get("to_path")
    
    if not path or not to_path:
        return {"success": False, "result": None, "error": "Missing required arguments: path, to_path"}
    
    try:
        if not os.path.exists(path):
            return {"success": False, "result": None, "error": f"Source does not exist: {path}"}
        
        # Create destination directory if needed
        os.makedirs(os.path.dirname(to_path), exist_ok=True)
        
        if os.path.isfile(path):
            shutil.copy2(path, to_path)
            action = "file_copied"
        elif os.path.isdir(path):
            shutil.copytree(path, to_path)
            action = "directory_copied"
        else:
            return {"success": False, "result": None, "error": f"Unknown path type: {path}"}
        
        return {
            "success": True,
            "result": {"from": path, "to": to_path, "action": action},
            "error": None
        }
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to copy: {str(e)}"}

def _move_file_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Move file implementation"""
    path = args.get("path")
    to_path = args.get("to_path")
    
    if not path or not to_path:
        return {"success": False, "result": None, "error": "Missing required arguments: path, to_path"}
    
    try:
        if not os.path.exists(path):
            return {"success": False, "result": None, "error": f"Source does not exist: {path}"}
        
        # Create destination directory if needed
        os.makedirs(os.path.dirname(to_path), exist_ok=True)
        
        shutil.move(path, to_path)
        
        return {
            "success": True,
            "result": {"from": path, "to": to_path, "action": "moved"},
            "error": None
        }
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to move: {str(e)}"}

def _get_file_info_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get file info implementation"""
    path = args.get("path")
    if not path:
        return {"success": False, "result": None, "error": "Missing required argument: path"}
    
    try:
        if not os.path.exists(path):
            return {"success": False, "result": None, "error": f"Path does not exist: {path}"}
        
        stat = os.stat(path)
        is_file = os.path.isfile(path)
        
        info = {
            "path": path,
            "name": os.path.basename(path),
            "type": "file" if is_file else "directory",
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "created": stat.st_ctime,
            "permissions": oct(stat.st_mode)[-3:],
            "readable": os.access(path, os.R_OK),
            "writable": os.access(path, os.W_OK),
            "executable": os.access(path, os.X_OK)
        }
        
        if is_file:
            info["extension"] = os.path.splitext(path)[1]
            info["is_text"] = _is_text_file(path)
        
        return {
            "success": True,
            "result": info,
            "error": None
        }
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to get file info: {str(e)}"}

def _is_text_file(file_path: str) -> bool:
    """Check if file is likely a text file"""
    text_extensions = {
        '.txt', '.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml',
        '.md', '.rst', '.log', '.conf', '.cfg', '.ini', '.sh', '.bat', '.sql',
        '.csv', '.tsv', '.c', '.cpp', '.h', '.hpp', '.java', '.php', '.rb',
        '.go', '.rs', '.ts', '.jsx', '.tsx', '.vue', '.svelte'
    }
    
    ext = os.path.splitext(file_path)[1].lower()
    return ext in text_extensions

# Legacy function aliases for backward compatibility
def list_files(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use file_manager instead"""
    return file_manager(args={"action": "list", **(args or {})})

def read_file(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use file_manager instead"""
    return file_manager(args={"action": "read", **(args or {})})

def write_file(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use file_manager instead"""
    return file_manager(args={"action": "write", **(args or {})})

def delete_file(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use file_manager instead"""
    return file_manager(args={"action": "delete", **(args or {})})

def copy_file(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use file_manager instead"""
    return file_manager(args={"action": "copy", **(args or {})})

def move_file(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use file_manager instead"""
    return file_manager(args={"action": "move", **(args or {})})

def get_file_info(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use file_manager instead"""
    return file_manager(args={"action": "info", **(args or {})})

def search_files(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use file_search instead"""
    return file_search(args=args)
