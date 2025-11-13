"""
Vision Tools - Consolidated computer vision and camera operations for AI agents
Provides unified vision system for camera control and image analysis.
"""
from typing import Any, Dict, List
import os
import tempfile
import platform
import subprocess
import json

def vision_system(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Universal vision system - replaces capture_camera_image, start_camera_stream, stop_camera_stream, detect_faces, detect_objects, analyze_scene
    
    Args:
        action (str): Action to perform - 'capture', 'start_stream', 'stop_stream', 'detect_faces', 'detect_objects', 'analyze_scene', 'list_cameras'
        camera_index (int): Camera index (default: 0)
        output_path (str): Output file path for captures
        width (int): Image width (default: 640)
        height (int): Image height (default: 480)
        image_path (str): Path to image file for analysis
        confidence_threshold (float): Detection confidence threshold (default: 0.5)
        source (str): Source type - 'camera', 'file', 'stream'
        
    Returns:
        Dict with operation result
    """
    if not args or "action" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: action"}
    
    action = args["action"]
    
    try:
        if action == "capture":
            return _capture_camera_impl(args)
        elif action == "start_stream":
            return _start_camera_stream_impl(args)
        elif action == "stop_stream":
            return _stop_camera_stream_impl(args)
        elif action == "detect_faces":
            return _detect_faces_impl(args)
        elif action == "detect_objects":
            return _detect_objects_impl(args)
        elif action == "analyze_scene":
            return _analyze_scene_impl(args)
        elif action == "list_cameras":
            return _list_cameras_impl(args)
        else:
            return {
                "success": False,
                "result": None,
                "error": f"Unknown action: {action}. Use: capture, start_stream, stop_stream, detect_faces, detect_objects, analyze_scene, list_cameras"
            }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Vision operation failed: {str(e)}"}

# Implementation helpers
def _capture_camera_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Capture image from camera implementation"""
    try:
        camera_index = args.get("camera_index", 0)
        width = args.get("width", 640)
        height = args.get("height", 480)
        output_path = args.get("output_path")
        
        if not output_path:
            output_path = os.path.join(tempfile.gettempdir(), f"camera_capture_{camera_index}.jpg")
        
        # Try OpenCV first (most reliable)
        try:
            import cv2
            
            # Initialize camera
            cap = cv2.VideoCapture(camera_index)
            if not cap.isOpened():
                return {"success": False, "result": None, "error": f"Cannot open camera {camera_index}"}
            
            # Set resolution
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            # Capture frame
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return {"success": False, "result": None, "error": "Failed to capture frame"}
            
            # Save image
            cv2.imwrite(output_path, frame)
            
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                return {
                    "success": True,
                    "result": {
                        "output_path": output_path,
                        "camera_index": camera_index,
                        "width": width,
                        "height": height,
                        "file_size": file_size,
                        "method": "opencv_capture"
                    },
                    "error": None
                }
            else:
                return {"success": False, "result": None, "error": "Failed to save captured image"}
        
        except ImportError:
            # Fallback to system commands
            return _capture_with_system_commands(camera_index, output_path, width, height)
        
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to capture camera image: {str(e)}"}

def _capture_with_system_commands(camera_index: int, output_path: str, width: int, height: int) -> Dict[str, Any]:
    """Fallback camera capture using system commands"""
    try:
        system = platform.system()
        
        if system == "Linux":
            # Try fswebcam, ffmpeg, or v4l2
            capture_commands = [
                ["fswebcam", "-r", f"{width}x{height}", "--no-banner", output_path],
                ["ffmpeg", "-f", "v4l2", "-i", f"/dev/video{camera_index}", "-vframes", "1", "-s", f"{width}x{height}", output_path, "-y"],
                ["v4l2-ctl", "--device", f"/dev/video{camera_index}", "--set-fmt-video=width={width},height={height}", "--stream-mmap", "--stream-count=1", "--stream-to=" + output_path]
            ]
            
            for cmd in capture_commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0 and os.path.exists(output_path):
                        file_size = os.path.getsize(output_path)
                        return {
                            "success": True,
                            "result": {
                                "output_path": output_path,
                                "camera_index": camera_index,
                                "width": width,
                                "height": height,
                                "file_size": file_size,
                                "method": f"system_command_{cmd[0]}"
                            },
                            "error": None
                        }
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            
            return {"success": False, "result": None, "error": "No camera capture tool found (install opencv-python, fswebcam, or ffmpeg)"}
        
        elif system == "Darwin":  # macOS
            # Use imagesnap
            cmd = ["imagesnap", "-w", "2", output_path]  # -w 2 waits 2 seconds for camera warmup
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                return {
                    "success": True,
                    "result": {
                        "output_path": output_path,
                        "camera_index": camera_index,
                        "width": width,
                        "height": height,
                        "file_size": file_size,
                        "method": "imagesnap"
                    },
                    "error": None
                }
            else:
                return {"success": False, "result": None, "error": "Camera capture failed (install imagesnap: brew install imagesnap)"}
        
        elif system == "Windows":
            # Use PowerShell with Windows.Media.Capture
            return {"success": False, "result": None, "error": "Windows camera capture requires additional setup (install opencv-python or use Windows Camera app)"}
        
        else:
            return {"success": False, "result": None, "error": f"Unsupported platform: {system}"}
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"System command capture failed: {str(e)}"}

def _start_camera_stream_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Start camera stream implementation"""
    try:
        camera_index = args.get("camera_index", 0)
        width = args.get("width", 640)
        height = args.get("height", 480)
        
        # This would typically start a background process or thread
        # For now, return a placeholder implementation
        return {
            "success": False,
            "result": None,
            "error": "Camera streaming requires additional setup (implement with opencv, gstreamer, or ffmpeg)"
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to start camera stream: {str(e)}"}

def _stop_camera_stream_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Stop camera stream implementation"""
    try:
        # This would typically stop a background process or thread
        return {
            "success": False,
            "result": None,
            "error": "Camera streaming control not yet implemented"
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to stop camera stream: {str(e)}"}

def _detect_faces_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Face detection implementation"""
    try:
        image_path = args.get("image_path")
        source = args.get("source", "file")
        confidence_threshold = args.get("confidence_threshold", 0.5)
        
        if source == "file" and not image_path:
            return {"success": False, "result": None, "error": "Missing required argument: image_path"}
        
        if source == "file" and not os.path.exists(image_path):
            return {"success": False, "result": None, "error": f"Image file not found: {image_path}"}
        
        # Try OpenCV face detection
        try:
            import cv2
            
            # Load image
            if source == "file":
                image = cv2.imread(image_path)
            elif source == "camera":
                # Capture from camera first
                camera_index = args.get("camera_index", 0)
                cap = cv2.VideoCapture(camera_index)
                if not cap.isOpened():
                    return {"success": False, "result": None, "error": f"Cannot open camera {camera_index}"}
                ret, image = cap.read()
                cap.release()
                if not ret:
                    return {"success": False, "result": None, "error": "Failed to capture from camera"}
            else:
                return {"success": False, "result": None, "error": f"Unsupported source: {source}"}
            
            if image is None:
                return {"success": False, "result": None, "error": "Failed to load image"}
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Load face cascade classifier
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            # Convert to list of dictionaries
            face_list = []
            for (x, y, w, h) in faces:
                face_list.append({
                    "x": int(x),
                    "y": int(y),
                    "width": int(w),
                    "height": int(h),
                    "confidence": 1.0  # Haar cascades don't provide confidence scores
                })
            
            return {
                "success": True,
                "result": {
                    "faces": face_list,
                    "count": len(face_list),
                    "image_path": image_path if source == "file" else "camera",
                    "source": source,
                    "method": "opencv_haar_cascade"
                },
                "error": None
            }
        
        except ImportError:
            return {"success": False, "result": None, "error": "Face detection requires opencv-python (pip install opencv-python)"}
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to detect faces: {str(e)}"}

def _detect_objects_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Object detection implementation"""
    try:
        image_path = args.get("image_path")
        source = args.get("source", "file")
        confidence_threshold = args.get("confidence_threshold", 0.5)
        
        if source == "file" and not image_path:
            return {"success": False, "result": None, "error": "Missing required argument: image_path"}
        
        # Object detection requires more advanced ML models (YOLO, SSD, etc.)
        return {
            "success": False,
            "result": None,
            "error": "Object detection requires AI/ML libraries (yolo, tensorflow, pytorch, etc.)"
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to detect objects: {str(e)}"}

def _analyze_scene_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Scene analysis implementation"""
    try:
        image_path = args.get("image_path")
        source = args.get("source", "file")
        
        if source == "file" and not image_path:
            return {"success": False, "result": None, "error": "Missing required argument: image_path"}
        
        # Scene analysis requires advanced computer vision models
        return {
            "success": False,
            "result": None,
            "error": "Scene analysis requires AI/ML libraries (tensorflow, pytorch, transformers, etc.)"
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to analyze scene: {str(e)}"}

def _list_cameras_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """List available cameras implementation"""
    try:
        cameras = []
        
        # Try OpenCV to enumerate cameras
        try:
            import cv2
            
            # Test camera indices 0-9
            for i in range(10):
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    # Get camera properties
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = int(cap.get(cv2.CAP_PROP_FPS))
                    
                    cameras.append({
                        "index": i,
                        "name": f"Camera {i}",
                        "width": width,
                        "height": height,
                        "fps": fps,
                        "available": True
                    })
                    cap.release()
                else:
                    break  # Stop at first unavailable camera
        
        except ImportError:
            # Fallback to system commands
            system = platform.system()
            
            if system == "Linux":
                # List video devices
                try:
                    result = subprocess.run(["ls", "/dev/video*"], capture_output=True, text=True)
                    if result.returncode == 0:
                        for line in result.stdout.strip().split('\n'):
                            if line.startswith('/dev/video'):
                                index = line.replace('/dev/video', '')
                                cameras.append({
                                    "index": int(index) if index.isdigit() else 0,
                                    "name": f"Video Device {index}",
                                    "device": line,
                                    "available": True
                                })
                except:
                    pass
            
            elif system == "Darwin":  # macOS
                # Use system_profiler
                try:
                    result = subprocess.run(["system_profiler", "SPCameraDataType"], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        # Parse camera info (simplified)
                        cameras.append({
                            "index": 0,
                            "name": "Built-in Camera",
                            "available": True
                        })
                except:
                    pass
            
            elif system == "Windows":
                # Use PowerShell
                try:
                    ps_script = "Get-WmiObject -Class Win32_PnPEntity | Where-Object {$_.Name -match 'camera|webcam'} | Select-Object Name"
                    result = subprocess.run(["powershell", "-c", ps_script], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        for i, line in enumerate(result.stdout.strip().split('\n')):
                            if line.strip() and 'Name' not in line and '---' not in line:
                                cameras.append({
                                    "index": i,
                                    "name": line.strip(),
                                    "available": True
                                })
                except:
                    pass
        
        return {
            "success": True,
            "result": {
                "cameras": cameras,
                "count": len(cameras),
                "method": "camera_enumeration"
            },
            "error": None
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to list cameras: {str(e)}"}

# Legacy function aliases for backward compatibility
def capture_camera_image(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use vision_system instead"""
    return vision_system(args={"action": "capture", **(args or {})})

def start_camera_stream(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use vision_system instead"""
    return vision_system(args={"action": "start_stream", **(args or {})})

def stop_camera_stream(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use vision_system instead"""
    return vision_system(args={"action": "stop_stream", **(args or {})})

def detect_faces(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use vision_system instead"""
    return vision_system(args={"action": "detect_faces", **(args or {})})

def detect_objects(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use vision_system instead"""
    return vision_system(args={"action": "detect_objects", **(args or {})})

def analyze_scene(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use vision_system instead"""
    return vision_system(args={"action": "analyze_scene", **(args or {})})
