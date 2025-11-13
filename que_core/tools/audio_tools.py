"""
Audio Tools - Consolidated audio operations and media processing for AI agents
Provides unified audio control and media processing capabilities.
"""
from typing import Any, Dict, List
import os
import platform
import subprocess
import tempfile
import json

def audio_control(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Universal audio controller - replaces record_audio, play_audio, transcribe_audio, speak_text, list_audio_devices, adjust_mic_gain, adjust_speaker_volume
    
    Args:
        action (str): Action to perform - 'record', 'play', 'speak', 'transcribe', 'list_devices', 'set_volume', 'get_volume'
        duration (int): Recording duration in seconds (for 'record')
        file (str): Audio file path (for 'play', 'transcribe')
        text (str): Text to speak (for 'speak')
        output_path (str): Output file path (for 'record')
        volume (int): Volume level 0-100 (for 'set_volume')
        device (str): Audio device name (optional)
        
    Returns:
        Dict with operation result
    """
    if not args or "action" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: action"}
    
    action = args["action"]
    
    try:
        if action == "record":
            return _record_audio_impl(args)
        elif action == "play":
            return _play_audio_impl(args)
        elif action == "speak":
            return _speak_text_impl(args)
        elif action == "transcribe":
            return _transcribe_audio_impl(args)
        elif action == "list_devices":
            return _list_audio_devices_impl(args)
        elif action == "set_volume":
            return _set_volume_impl(args)
        elif action == "get_volume":
            return _get_volume_impl(args)
        else:
            return {
                "success": False,
                "result": None,
                "error": f"Unknown action: {action}. Use: record, play, speak, transcribe, list_devices, set_volume, get_volume"
            }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Audio operation failed: {str(e)}"}

def media_processor(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Media processing engine - replaces transcribe_audio, analyze_scene, detect_faces, detect_objects
    
    Args:
        action (str): Action to perform - 'transcribe', 'analyze_scene', 'detect_faces', 'detect_objects', 'extract_audio'
        file (str): Media file path
        image (str): Image file path (for vision tasks)
        language (str): Language for transcription (optional)
        confidence_threshold (float): Detection confidence threshold (optional)
        
    Returns:
        Dict with processing result
    """
    if not args or "action" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: action"}
    
    action = args["action"]
    
    try:
        if action == "transcribe":
            return _transcribe_media_impl(args)
        elif action == "analyze_scene":
            return _analyze_scene_impl(args)
        elif action == "detect_faces":
            return _detect_faces_impl(args)
        elif action == "detect_objects":
            return _detect_objects_impl(args)
        elif action == "extract_audio":
            return _extract_audio_impl(args)
        else:
            return {
                "success": False,
                "result": None,
                "error": f"Unknown action: {action}. Use: transcribe, analyze_scene, detect_faces, detect_objects, extract_audio"
            }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Media processing failed: {str(e)}"}

# Audio Control Implementation Helpers
def _record_audio_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Record audio implementation"""
    duration = args.get("duration")
    if not duration:
        return {"success": False, "result": None, "error": "Missing required argument: duration"}
    
    try:
        output_path = args.get("output_path")
        if not output_path:
            output_path = os.path.join(tempfile.gettempdir(), f"recording_{duration}s.wav")
        
        sample_rate = args.get("sample_rate", 44100)
        channels = args.get("channels", 1)
        system = platform.system()
        
        if system == "Linux":
            # Use arecord (ALSA)
            cmd = [
                "arecord", "-f", "cd", "-t", "wav", "-d", str(duration),
                "-r", str(sample_rate), "-c", str(channels), output_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 10)
            
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                return {
                    "success": True,
                    "result": {
                        "file_path": output_path,
                        "duration": duration,
                        "sample_rate": sample_rate,
                        "channels": channels,
                        "file_size": file_size,
                        "method": "audio_record"
                    },
                    "error": None
                }
            else:
                return {"success": False, "result": None, "error": f"Recording failed: {result.stderr}"}
        
        elif system == "Darwin":  # macOS
            # Use sox or afrecord
            cmd = ["sox", "-t", "coreaudio", "default", "-r", str(sample_rate), "-c", str(channels), output_path, "trim", "0", str(duration)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 10)
            
            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                return {
                    "success": True,
                    "result": {
                        "file_path": output_path,
                        "duration": duration,
                        "sample_rate": sample_rate,
                        "channels": channels,
                        "file_size": file_size,
                        "method": "audio_record"
                    },
                    "error": None
                }
            else:
                return {"success": False, "result": None, "error": f"Recording failed: {result.stderr}"}
        
        elif system == "Windows":
            return {"success": False, "result": None, "error": "Windows audio recording requires additional setup (install SoX or use PowerShell)"}
        
        else:
            return {"success": False, "result": None, "error": f"Unsupported platform: {system}"}
    
    except subprocess.TimeoutExpired:
        return {"success": False, "result": None, "error": f"Recording timed out after {duration} seconds"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to record audio: {str(e)}"}

def _play_audio_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Play audio implementation"""
    file_path = args.get("file")
    if not file_path:
        return {"success": False, "result": None, "error": "Missing required argument: file"}
    
    try:
        if not os.path.exists(file_path):
            return {"success": False, "result": None, "error": f"Audio file not found: {file_path}"}
        
        system = platform.system()
        
        if system == "Linux":
            # Try multiple players
            players = ["aplay", "paplay", "play", "mpg123", "ffplay"]
            for player in players:
                try:
                    if player == "ffplay":
                        cmd = [player, "-nodisp", "-autoexit", file_path]
                    else:
                        cmd = [player, file_path]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        return {
                            "success": True,
                            "result": {
                                "file_path": file_path,
                                "player": player,
                                "played": True,
                                "method": "audio_play"
                            },
                            "error": None
                        }
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            
            return {"success": False, "result": None, "error": "No suitable audio player found (install aplay, paplay, or ffmpeg)"}
        
        elif system == "Darwin":  # macOS
            cmd = ["afplay", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "result": {
                        "file_path": file_path,
                        "player": "afplay",
                        "played": True,
                        "method": "audio_play"
                    },
                    "error": None
                }
            else:
                return {"success": False, "result": None, "error": f"Playback failed: {result.stderr}"}
        
        elif system == "Windows":
            # Use Windows Media Player or PowerShell
            cmd = ["powershell", "-c", f"(New-Object Media.SoundPlayer '{file_path}').PlaySync()"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "result": {
                        "file_path": file_path,
                        "player": "powershell",
                        "played": True,
                        "method": "audio_play"
                    },
                    "error": None
                }
            else:
                return {"success": False, "result": None, "error": f"Playback failed: {result.stderr}"}
        
        else:
            return {"success": False, "result": None, "error": f"Unsupported platform: {system}"}
    
    except subprocess.TimeoutExpired:
        return {"success": False, "result": None, "error": "Audio playback timed out"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to play audio: {str(e)}"}

def _speak_text_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Text-to-speech implementation"""
    text = args.get("text")
    if not text:
        return {"success": False, "result": None, "error": "Missing required argument: text"}
    
    try:
        voice = args.get("voice", "default")
        rate = args.get("rate", 200)  # Words per minute
        system = platform.system()
        
        if system == "Linux":
            # Use espeak or festival
            tts_engines = [
                ["espeak", "-s", str(rate), text],
                ["festival", "--tts"],
                ["spd-say", text]
            ]
            
            for cmd in tts_engines:
                try:
                    if cmd[0] == "festival":
                        result = subprocess.run(cmd, input=text, text=True, capture_output=True, timeout=10)
                    else:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        return {
                            "success": True,
                            "result": {
                                "text": text,
                                "engine": cmd[0],
                                "voice": voice,
                                "rate": rate,
                                "spoken": True,
                                "method": "text_to_speech"
                            },
                            "error": None
                        }
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            
            return {"success": False, "result": None, "error": "No TTS engine found (install espeak, festival, or speech-dispatcher)"}
        
        elif system == "Darwin":  # macOS
            cmd = ["say", "-r", str(rate), text]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "result": {
                        "text": text,
                        "engine": "say",
                        "voice": voice,
                        "rate": rate,
                        "spoken": True,
                        "method": "text_to_speech"
                    },
                    "error": None
                }
            else:
                return {"success": False, "result": None, "error": f"TTS failed: {result.stderr}"}
        
        elif system == "Windows":
            # Use PowerShell with SAPI
            ps_script = f"""
            Add-Type -AssemblyName System.Speech
            $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
            $synth.Rate = {rate // 20}  # Convert to SAPI rate (-10 to 10)
            $synth.Speak('{text}')
            """
            cmd = ["powershell", "-c", ps_script]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "result": {
                        "text": text,
                        "engine": "sapi",
                        "voice": voice,
                        "rate": rate,
                        "spoken": True,
                        "method": "text_to_speech"
                    },
                    "error": None
                }
            else:
                return {"success": False, "result": None, "error": f"TTS failed: {result.stderr}"}
        
        else:
            return {"success": False, "result": None, "error": f"Unsupported platform: {system}"}
    
    except subprocess.TimeoutExpired:
        return {"success": False, "result": None, "error": "Text-to-speech timed out"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to speak text: {str(e)}"}

def _transcribe_audio_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Audio transcription implementation"""
    file_path = args.get("file")
    if not file_path:
        return {"success": False, "result": None, "error": "Missing required argument: file"}
    
    try:
        if not os.path.exists(file_path):
            return {"success": False, "result": None, "error": f"Audio file not found: {file_path}"}
        
        # This would require speech recognition libraries like whisper, vosk, or cloud APIs
        # For now, return a placeholder implementation
        return {
            "success": False,
            "result": None,
            "error": "Audio transcription requires additional setup (install whisper, vosk, or configure cloud API)"
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to transcribe audio: {str(e)}"}

def _list_audio_devices_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """List audio devices implementation"""
    try:
        system = platform.system()
        devices = []
        
        if system == "Linux":
            # Use arecord and aplay to list devices
            try:
                # List capture devices
                result = subprocess.run(["arecord", "-l"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'card' in line and 'device' in line:
                            devices.append({"type": "input", "name": line.strip(), "driver": "alsa"})
                
                # List playback devices
                result = subprocess.run(["aplay", "-l"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'card' in line and 'device' in line:
                            devices.append({"type": "output", "name": line.strip(), "driver": "alsa"})
            except:
                pass
        
        elif system == "Darwin":  # macOS
            # Use system_profiler
            try:
                result = subprocess.run(["system_profiler", "SPAudioDataType"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    # Parse macOS audio device info
                    devices.append({"type": "input", "name": "Built-in Microphone", "driver": "coreaudio"})
                    devices.append({"type": "output", "name": "Built-in Speakers", "driver": "coreaudio"})
            except:
                pass
        
        elif system == "Windows":
            # Use PowerShell to list audio devices
            try:
                ps_script = "Get-WmiObject -Class Win32_SoundDevice | Select-Object Name, Status"
                result = subprocess.run(["powershell", "-c", ps_script], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if line.strip() and 'Name' not in line and '---' not in line:
                            devices.append({"type": "unknown", "name": line.strip(), "driver": "windows"})
            except:
                pass
        
        return {
            "success": True,
            "result": {
                "devices": devices,
                "count": len(devices),
                "platform": system,
                "method": "audio_device_list"
            },
            "error": None
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to list audio devices: {str(e)}"}

def _set_volume_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Set system volume implementation"""
    volume = args.get("volume")
    if volume is None:
        return {"success": False, "result": None, "error": "Missing required argument: volume (0-100)"}
    
    try:
        if not 0 <= volume <= 100:
            return {"success": False, "result": None, "error": "Volume must be between 0 and 100"}
        
        system = platform.system()
        
        if system == "Linux":
            # Use amixer
            cmd = ["amixer", "sset", "Master", f"{volume}%"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "result": {
                        "volume": volume,
                        "set": True,
                        "method": "volume_control"
                    },
                    "error": None
                }
            else:
                return {"success": False, "result": None, "error": f"Volume control failed: {result.stderr}"}
        
        elif system == "Darwin":  # macOS
            # Use osascript
            cmd = ["osascript", "-e", f"set volume output volume {volume}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "result": {
                        "volume": volume,
                        "set": True,
                        "method": "volume_control"
                    },
                    "error": None
                }
            else:
                return {"success": False, "result": None, "error": f"Volume control failed: {result.stderr}"}
        
        elif system == "Windows":
            # Use PowerShell with Windows Audio API
            ps_script = f"""
            Add-Type -TypeDefinition @'
            using System;
            using System.Runtime.InteropServices;
            public class Audio {{
                [DllImport("user32.dll")]
                public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
            }}
'@
            # This is a simplified approach - full implementation would use Windows Audio Session API
            """
            return {"success": False, "result": None, "error": "Windows volume control requires additional setup"}
        
        else:
            return {"success": False, "result": None, "error": f"Unsupported platform: {system}"}
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to set volume: {str(e)}"}

def _get_volume_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Get system volume implementation"""
    try:
        system = platform.system()
        
        if system == "Linux":
            # Use amixer
            cmd = ["amixer", "sget", "Master"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                # Parse amixer output to extract volume percentage
                import re
                match = re.search(r'\[(\d+)%\]', result.stdout)
                if match:
                    volume = int(match.group(1))
                    return {
                        "success": True,
                        "result": {
                            "volume": volume,
                            "muted": "[off]" in result.stdout,
                            "method": "volume_get"
                        },
                        "error": None
                    }
                else:
                    return {"success": False, "result": None, "error": "Could not parse volume from amixer output"}
            else:
                return {"success": False, "result": None, "error": f"Volume query failed: {result.stderr}"}
        
        elif system == "Darwin":  # macOS
            # Use osascript
            cmd = ["osascript", "-e", "output volume of (get volume settings)"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                try:
                    volume = int(result.stdout.strip())
                    return {
                        "success": True,
                        "result": {
                            "volume": volume,
                            "muted": False,  # Would need additional check
                            "method": "volume_get"
                        },
                        "error": None
                    }
                except ValueError:
                    return {"success": False, "result": None, "error": "Could not parse volume from osascript output"}
            else:
                return {"success": False, "result": None, "error": f"Volume query failed: {result.stderr}"}
        
        elif system == "Windows":
            return {"success": False, "result": None, "error": "Windows volume query requires additional setup"}
        
        else:
            return {"success": False, "result": None, "error": f"Unsupported platform: {system}"}
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to get volume: {str(e)}"}

# Media Processing Implementation Helpers
def _transcribe_media_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Media transcription implementation"""
    return {"success": False, "result": None, "error": "Media transcription requires AI/ML libraries (whisper, vosk, etc.)"}

def _analyze_scene_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Scene analysis implementation"""
    return {"success": False, "result": None, "error": "Scene analysis requires computer vision libraries (opencv, tensorflow, etc.)"}

def _detect_faces_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Face detection implementation"""
    return {"success": False, "result": None, "error": "Face detection requires computer vision libraries (opencv, dlib, etc.)"}

def _detect_objects_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Object detection implementation"""
    return {"success": False, "result": None, "error": "Object detection requires AI/ML libraries (yolo, tensorflow, etc.)"}

def _extract_audio_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Audio extraction from video implementation"""
    file_path = args.get("file")
    if not file_path:
        return {"success": False, "result": None, "error": "Missing required argument: file"}
    
    try:
        if not os.path.exists(file_path):
            return {"success": False, "result": None, "error": f"Media file not found: {file_path}"}
        
        output_path = args.get("output_path")
        if not output_path:
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_path = os.path.join(tempfile.gettempdir(), f"{base_name}_audio.wav")
        
        # Use ffmpeg to extract audio
        cmd = ["ffmpeg", "-i", file_path, "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2", output_path, "-y"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            return {
                "success": True,
                "result": {
                    "input_file": file_path,
                    "output_file": output_path,
                    "file_size": file_size,
                    "extracted": True,
                    "method": "audio_extract"
                },
                "error": None
            }
        else:
            return {"success": False, "result": None, "error": f"Audio extraction failed: {result.stderr}"}
    
    except subprocess.TimeoutExpired:
        return {"success": False, "result": None, "error": "Audio extraction timed out"}
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to extract audio: {str(e)}"}

# Legacy function aliases for backward compatibility
def record_audio(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use audio_control instead"""
    return audio_control(args={"action": "record", **(args or {})})

def play_audio(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use audio_control instead"""
    return audio_control(args={"action": "play", **(args or {})})

def speak_text(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use audio_control instead"""
    return audio_control(args={"action": "speak", **(args or {})})

def transcribe_audio(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use audio_control instead"""
    return audio_control(args={"action": "transcribe", **(args or {})})

def list_audio_devices(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use audio_control instead"""
    return audio_control(args={"action": "list_devices", **(args or {})})

def adjust_mic_gain(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use audio_control instead"""
    return {"success": False, "result": None, "error": "Microphone gain adjustment not yet implemented"}

def adjust_speaker_volume(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use audio_control instead"""
    return audio_control(args={"action": "set_volume", **(args or {})})
