"""
Development Tools - Consolidated development operations and code management for AI agents
Provides unified development workflow and code quality tools.
"""
from typing import Any, Dict, List
import os
import subprocess
import platform
import json
import tempfile

def dev_assistant(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Universal development assistant - replaces run_python_script, get_git_status, commit_changes, run_tests, build_project, lint_code, format_code
    
    Args:
        action (str): Action to perform - 'run_python', 'git_status', 'git_commit', 'run_tests', 'build', 'lint', 'format'
        script (str): Python script path (for 'run_python')
        message (str): Commit message (for 'git_commit')
        framework (str): Test framework - 'pytest', 'unittest', 'nose' (for 'run_tests')
        language (str): Programming language (for 'lint', 'format')
        project_type (str): Project type - 'python', 'rust', 'node', 'go' (for 'build')
        
    Returns:
        Dict with operation result
    """
    if not args or "action" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: action"}
    
    action = args["action"]
    
    try:
        if action == "run_python":
            return _run_python_script_impl(args)
        elif action == "git_status":
            return _git_status_impl(args)
        elif action == "git_commit":
            return _git_commit_impl(args)
        elif action == "run_tests":
            return _run_tests_impl(args)
        elif action == "build":
            return _build_project_impl(args)
        elif action == "lint":
            return _lint_code_impl(args)
        elif action == "format":
            return _format_code_impl(args)
        else:
            return {
                "success": False,
                "result": None,
                "error": f"Unknown action: {action}. Use: run_python, git_status, git_commit, run_tests, build, lint, format"
            }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Development operation failed: {str(e)}"}

def code_manager(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Smart code operations - replaces lint_code, format_code, run_tests, build_project
    
    Args:
        action (str): Action to perform - 'lint', 'format', 'test', 'build', 'analyze', 'check_style'
        language (str): Programming language - 'python', 'rust', 'javascript', 'go', 'java'
        path (str): File or directory path to process
        fix (bool): Auto-fix issues when possible (optional)
        config (str): Configuration file path (optional)
        
    Returns:
        Dict with operation result
    """
    if not args or "action" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: action"}
    
    action = args["action"]
    
    try:
        if action == "lint":
            return _lint_code_impl(args)
        elif action == "format":
            return _format_code_impl(args)
        elif action == "test":
            return _run_tests_impl(args)
        elif action == "build":
            return _build_project_impl(args)
        elif action == "analyze":
            return _analyze_code_impl(args)
        elif action == "check_style":
            return _check_code_style_impl(args)
        else:
            return {
                "success": False,
                "result": None,
                "error": f"Unknown action: {action}. Use: lint, format, test, build, analyze, check_style"
            }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Code management failed: {str(e)}"}

# Development Assistant Implementation Helpers
def _run_python_script_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Run Python script implementation"""
    try:
        script = args.get("script")
        if not script:
            return {"success": False, "result": None, "error": "Missing required argument: script"}
        
        if not os.path.exists(script):
            return {"success": False, "result": None, "error": f"Script not found: {script}"}
        
        # Get script arguments
        script_args = args.get("args", [])
        if isinstance(script_args, str):
            script_args = script_args.split()
        
        # Build command
        python_exe = args.get("python", "python3")
        cmd = [python_exe, script] + script_args
        
        # Set working directory
        cwd = args.get("cwd", os.path.dirname(script))
        
        # Run script
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=args.get("timeout", 60),
            cwd=cwd
        )
        
        return {
            "success": result.returncode == 0,
            "result": {
                "script": script,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(cmd),
                "cwd": cwd,
                "method": "subprocess_run"
            },
            "error": result.stderr if result.returncode != 0 else None
        }
    
    except subprocess.TimeoutExpired:
        return {"success": False, "result": None, "error": f"Script execution timed out"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to run Python script: {str(e)}"}

def _git_status_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Git status implementation"""
    try:
        repo_path = args.get("path", ".")
        
        # Check if it's a git repository
        if not os.path.exists(os.path.join(repo_path, ".git")):
            return {"success": False, "result": None, "error": f"Not a git repository: {repo_path}"}
        
        # Get git status
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=repo_path,
            timeout=10
        )
        
        if result.returncode != 0:
            return {"success": False, "result": None, "error": f"Git status failed: {result.stderr}"}
        
        # Parse status output
        files = {"modified": [], "added": [], "deleted": [], "untracked": [], "renamed": []}
        
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            
            status = line[:2]
            filename = line[3:]
            
            if status == "??":
                files["untracked"].append(filename)
            elif status[0] == "M" or status[1] == "M":
                files["modified"].append(filename)
            elif status[0] == "A" or status[1] == "A":
                files["added"].append(filename)
            elif status[0] == "D" or status[1] == "D":
                files["deleted"].append(filename)
            elif status[0] == "R":
                files["renamed"].append(filename)
        
        # Get current branch
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            cwd=repo_path,
            timeout=5
        )
        
        current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
        
        total_changes = sum(len(file_list) for file_list in files.values())
        
        return {
            "success": True,
            "result": {
                "repository": repo_path,
                "current_branch": current_branch,
                "files": files,
                "total_changes": total_changes,
                "clean": total_changes == 0,
                "method": "git_status"
            },
            "error": None
        }
    
    except subprocess.TimeoutExpired:
        return {"success": False, "result": None, "error": "Git status timed out"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to get git status: {str(e)}"}

def _git_commit_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Git commit implementation"""
    try:
        message = args.get("message")
        if not message:
            return {"success": False, "result": None, "error": "Missing required argument: message"}
        
        repo_path = args.get("path", ".")
        
        # Check if it's a git repository
        if not os.path.exists(os.path.join(repo_path, ".git")):
            return {"success": False, "result": None, "error": f"Not a git repository: {repo_path}"}
        
        # Add files if specified
        files_to_add = args.get("files", [])
        if files_to_add:
            if isinstance(files_to_add, str):
                files_to_add = [files_to_add]
            
            add_result = subprocess.run(
                ["git", "add"] + files_to_add,
                capture_output=True,
                text=True,
                cwd=repo_path,
                timeout=10
            )
            
            if add_result.returncode != 0:
                return {"success": False, "result": None, "error": f"Git add failed: {add_result.stderr}"}
        
        # Commit changes
        commit_result = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True,
            text=True,
            cwd=repo_path,
            timeout=10
        )
        
        if commit_result.returncode != 0:
            return {"success": False, "result": None, "error": f"Git commit failed: {commit_result.stderr}"}
        
        # Get commit hash
        hash_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=repo_path,
            timeout=5
        )
        
        commit_hash = hash_result.stdout.strip()[:8] if hash_result.returncode == 0 else "unknown"
        
        return {
            "success": True,
            "result": {
                "repository": repo_path,
                "message": message,
                "commit_hash": commit_hash,
                "files_added": files_to_add,
                "committed": True,
                "method": "git_commit"
            },
            "error": None
        }
    
    except subprocess.TimeoutExpired:
        return {"success": False, "result": None, "error": "Git commit timed out"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to commit changes: {str(e)}"}

def _run_tests_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Run tests implementation"""
    try:
        framework = args.get("framework", "pytest")
        path = args.get("path", ".")
        
        # Build test command based on framework
        if framework == "pytest":
            cmd = ["pytest", path, "-v"]
            if args.get("coverage", False):
                cmd.extend(["--cov", path])
        elif framework == "unittest":
            cmd = ["python", "-m", "unittest", "discover", "-s", path, "-v"]
        elif framework == "nose":
            cmd = ["nosetests", path, "-v"]
        elif framework == "cargo":  # Rust tests
            cmd = ["cargo", "test"]
        elif framework == "npm":  # Node.js tests
            cmd = ["npm", "test"]
        elif framework == "go":  # Go tests
            cmd = ["go", "test", "./..."]
        else:
            return {"success": False, "result": None, "error": f"Unsupported test framework: {framework}"}
        
        # Run tests
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=path,
            timeout=args.get("timeout", 120)
        )
        
        # Parse test results (basic implementation)
        output = result.stdout + result.stderr
        
        # Extract test counts (framework-specific parsing would be more accurate)
        import re
        
        if framework == "pytest":
            passed_match = re.search(r'(\d+) passed', output)
            failed_match = re.search(r'(\d+) failed', output)
            passed = int(passed_match.group(1)) if passed_match else 0
            failed = int(failed_match.group(1)) if failed_match else 0
        else:
            # Generic parsing
            passed = output.lower().count("pass")
            failed = output.lower().count("fail")
        
        total = passed + failed
        success_rate = (passed / total * 100) if total > 0 else 0
        
        return {
            "success": result.returncode == 0,
            "result": {
                "framework": framework,
                "path": path,
                "total_tests": total,
                "passed": passed,
                "failed": failed,
                "success_rate": round(success_rate, 2),
                "return_code": result.returncode,
                "output": output,
                "method": "test_runner"
            },
            "error": None if result.returncode == 0 else f"Tests failed with {failed} failures"
        }
    
    except subprocess.TimeoutExpired:
        return {"success": False, "result": None, "error": "Test execution timed out"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to run tests: {str(e)}"}

def _build_project_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Build project implementation"""
    try:
        project_type = args.get("project_type", "auto")
        path = args.get("path", ".")
        
        # Auto-detect project type if not specified
        if project_type == "auto":
            if os.path.exists(os.path.join(path, "Cargo.toml")):
                project_type = "rust"
            elif os.path.exists(os.path.join(path, "package.json")):
                project_type = "node"
            elif os.path.exists(os.path.join(path, "go.mod")):
                project_type = "go"
            elif os.path.exists(os.path.join(path, "setup.py")) or os.path.exists(os.path.join(path, "pyproject.toml")):
                project_type = "python"
            else:
                return {"success": False, "result": None, "error": "Could not auto-detect project type"}
        
        # Build command based on project type
        if project_type == "rust":
            cmd = ["cargo", "build"]
            if args.get("release", False):
                cmd.append("--release")
        elif project_type == "node":
            cmd = ["npm", "run", "build"]
        elif project_type == "go":
            cmd = ["go", "build", "./..."]
        elif project_type == "python":
            cmd = ["python", "setup.py", "build"]
        else:
            return {"success": False, "result": None, "error": f"Unsupported project type: {project_type}"}
        
        # Run build
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=path,
            timeout=args.get("timeout", 300)  # 5 minutes for builds
        )
        
        return {
            "success": result.returncode == 0,
            "result": {
                "project_type": project_type,
                "path": path,
                "command": " ".join(cmd),
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "build_time": "unknown",  # Would need timing implementation
                "method": "project_build"
            },
            "error": result.stderr if result.returncode != 0 else None
        }
    
    except subprocess.TimeoutExpired:
        return {"success": False, "result": None, "error": "Build timed out"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to build project: {str(e)}"}

def _lint_code_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Code linting implementation"""
    try:
        language = args.get("language", "auto")
        path = args.get("path", ".")
        
        # Auto-detect language if not specified
        if language == "auto":
            if path.endswith(".py"):
                language = "python"
            elif path.endswith(".rs"):
                language = "rust"
            elif path.endswith(".js") or path.endswith(".ts"):
                language = "javascript"
            elif path.endswith(".go"):
                language = "go"
            else:
                # Try to detect from directory contents
                if any(f.endswith(".py") for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))):
                    language = "python"
                else:
                    return {"success": False, "result": None, "error": "Could not auto-detect language"}
        
        # Build lint command based on language
        if language == "python":
            # Try multiple Python linters
            linters = [
                (["flake8", path], "flake8"),
                (["pylint", path], "pylint"),
                (["pycodestyle", path], "pycodestyle")
            ]
        elif language == "rust":
            linters = [(["cargo", "clippy"], "clippy")]
        elif language == "javascript":
            linters = [(["eslint", path], "eslint")]
        elif language == "go":
            linters = [(["golint", path], "golint")]
        else:
            return {"success": False, "result": None, "error": f"Unsupported language: {language}"}
        
        # Try linters in order
        for cmd, linter_name in linters:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=path if os.path.isdir(path) else os.path.dirname(path),
                    timeout=60
                )
                
                # Count issues (basic implementation)
                output = result.stdout + result.stderr
                issue_count = len([line for line in output.split('\n') if line.strip()])
                
                return {
                    "success": True,
                    "result": {
                        "language": language,
                        "linter": linter_name,
                        "path": path,
                        "issues_found": issue_count,
                        "return_code": result.returncode,
                        "output": output,
                        "clean": issue_count == 0,
                        "method": "code_linting"
                    },
                    "error": None
                }
            
            except FileNotFoundError:
                continue  # Try next linter
        
        return {"success": False, "result": None, "error": f"No suitable linter found for {language}"}
    
    except subprocess.TimeoutExpired:
        return {"success": False, "result": None, "error": "Linting timed out"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to lint code: {str(e)}"}

def _format_code_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Code formatting implementation"""
    try:
        language = args.get("language", "auto")
        path = args.get("path", ".")
        
        # Auto-detect language if not specified
        if language == "auto":
            if path.endswith(".py"):
                language = "python"
            elif path.endswith(".rs"):
                language = "rust"
            elif path.endswith(".js") or path.endswith(".ts"):
                language = "javascript"
            elif path.endswith(".go"):
                language = "go"
            else:
                return {"success": False, "result": None, "error": "Could not auto-detect language"}
        
        # Build format command based on language
        if language == "python":
            formatters = [
                (["black", path], "black"),
                (["autopep8", "--in-place", path], "autopep8")
            ]
        elif language == "rust":
            formatters = [(["cargo", "fmt"], "rustfmt")]
        elif language == "javascript":
            formatters = [(["prettier", "--write", path], "prettier")]
        elif language == "go":
            formatters = [(["gofmt", "-w", path], "gofmt")]
        else:
            return {"success": False, "result": None, "error": f"Unsupported language: {language}"}
        
        # Try formatters in order
        for cmd, formatter_name in formatters:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=path if os.path.isdir(path) else os.path.dirname(path),
                    timeout=60
                )
                
                return {
                    "success": result.returncode == 0,
                    "result": {
                        "language": language,
                        "formatter": formatter_name,
                        "path": path,
                        "return_code": result.returncode,
                        "output": result.stdout,
                        "formatted": result.returncode == 0,
                        "method": "code_formatting"
                    },
                    "error": result.stderr if result.returncode != 0 else None
                }
            
            except FileNotFoundError:
                continue  # Try next formatter
        
        return {"success": False, "result": None, "error": f"No suitable formatter found for {language}"}
    
    except subprocess.TimeoutExpired:
        return {"success": False, "result": None, "error": "Formatting timed out"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to format code: {str(e)}"}

# Code Manager Implementation Helpers
def _analyze_code_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Code analysis implementation"""
    try:
        path = args.get("path", ".")
        
        if not os.path.exists(path):
            return {"success": False, "result": None, "error": f"Path not found: {path}"}
        
        # Basic code analysis
        analysis = {
            "files": 0,
            "lines": 0,
            "languages": {},
            "size_bytes": 0
        }
        
        # Analyze files
        if os.path.isfile(path):
            files_to_analyze = [path]
        else:
            files_to_analyze = []
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(('.py', '.rs', '.js', '.ts', '.go', '.java', '.cpp', '.c', '.h')):
                        files_to_analyze.append(os.path.join(root, file))
        
        for file_path in files_to_analyze:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = len(content.split('\n'))
                    
                    analysis["files"] += 1
                    analysis["lines"] += lines
                    analysis["size_bytes"] += len(content.encode('utf-8'))
                    
                    # Detect language
                    ext = os.path.splitext(file_path)[1]
                    if ext not in analysis["languages"]:
                        analysis["languages"][ext] = {"files": 0, "lines": 0}
                    analysis["languages"][ext]["files"] += 1
                    analysis["languages"][ext]["lines"] += lines
            
            except Exception:
                continue  # Skip files that can't be read
        
        return {
            "success": True,
            "result": {
                "path": path,
                "analysis": analysis,
                "method": "code_analysis"
            },
            "error": None
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to analyze code: {str(e)}"}

def _check_code_style_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Code style check implementation"""
    # This is similar to linting but focuses on style issues
    return _lint_code_impl(args)

# Legacy function aliases for backward compatibility
def create_virtual_env(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use shell_execute or environment_manager instead"""
    from que_core.tools.shell_tools import environment_manager
    return environment_manager(args={"action": "create_venv", **(args or {})})

def run_python_script(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use dev_assistant instead"""
    return dev_assistant(args={"action": "run_python", **(args or {})})

def get_git_status(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use dev_assistant instead"""
    return dev_assistant(args={"action": "git_status", **(args or {})})

def commit_changes(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use dev_assistant instead"""
    return dev_assistant(args={"action": "git_commit", **(args or {})})

def run_tests(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use dev_assistant instead"""
    return dev_assistant(args={"action": "run_tests", **(args or {})})

def build_project(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use dev_assistant instead"""
    return dev_assistant(args={"action": "build", **(args or {})})

def lint_code(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use code_manager instead"""
    return code_manager(args={"action": "lint", **(args or {})})

def format_code(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use code_manager instead"""
    return code_manager(args={"action": "format", **(args or {})})
