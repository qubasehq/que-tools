"""
Security Tools - Consolidated security and privacy operations for AI agents
Provides unified encryption, password generation, and privacy management.
"""
from typing import Any, Dict, List
import os
import hashlib
import secrets
import string
import tempfile
import shutil
import platform
import json

def security_manager(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Universal security manager - replaces encrypt_file, decrypt_file, generate_password, hash_text, clear_temp_files
    
    Args:
        action (str): Action to perform - 'encrypt', 'decrypt', 'generate_password', 'hash', 'clear_temp', 'secure_delete'
        file (str): File path (for encrypt/decrypt/secure_delete actions)
        password (str): Password for encryption/decryption
        text (str): Text to hash
        algorithm (str): Hash algorithm - 'md5', 'sha1', 'sha256', 'sha512' (for hash action)
        length (int): Password length (for generate_password action)
        complexity (str): Password complexity - 'simple', 'medium', 'complex' (for generate_password action)
        output_path (str): Output file path (optional)
        
    Returns:
        Dict with security operation result
    """
    if not args or "action" not in args:
        return {"success": False, "result": None, "error": "Missing required argument: action"}
    
    action = args["action"]
    
    try:
        if action == "encrypt":
            return _encrypt_file_impl(args)
        elif action == "decrypt":
            return _decrypt_file_impl(args)
        elif action == "generate_password":
            return _generate_password_impl(args)
        elif action == "hash":
            return _hash_text_impl(args)
        elif action == "clear_temp":
            return _clear_temp_files_impl(args)
        elif action == "secure_delete":
            return _secure_delete_impl(args)
        else:
            return {
                "success": False,
                "result": None,
                "error": f"Unknown action: {action}. Use: encrypt, decrypt, generate_password, hash, clear_temp, secure_delete"
            }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Security operation failed: {str(e)}"}

# Security Manager Implementation Helpers
def _encrypt_file_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """File encryption implementation"""
    try:
        file_path = args.get("file")
        password = args.get("password")
        
        if not file_path or not password:
            return {"success": False, "result": None, "error": "Missing required arguments: file, password"}
        
        if not os.path.exists(file_path):
            return {"success": False, "result": None, "error": f"File not found: {file_path}"}
        
        output_path = args.get("output_path", file_path + ".encrypted")
        
        # Try cryptography library first
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            import base64
            
            # Generate salt and derive key
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            fernet = Fernet(key)
            
            # Read and encrypt file
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            encrypted_data = fernet.encrypt(file_data)
            
            # Write encrypted file with salt prepended
            with open(output_path, 'wb') as f:
                f.write(salt + encrypted_data)
            
            file_size = os.path.getsize(output_path)
            original_size = os.path.getsize(file_path)
            
            return {
                "success": True,
                "result": {
                    "input_file": file_path,
                    "output_file": output_path,
                    "original_size": original_size,
                    "encrypted_size": file_size,
                    "algorithm": "Fernet (AES 128)",
                    "encrypted": True,
                    "method": "cryptography_fernet"
                },
                "error": None
            }
        
        except ImportError:
            # Fallback to simple XOR encryption (not secure for production!)
            return _simple_encrypt_impl(file_path, password, output_path)
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to encrypt file: {str(e)}"}

def _decrypt_file_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """File decryption implementation"""
    try:
        file_path = args.get("file")
        password = args.get("password")
        
        if not file_path or not password:
            return {"success": False, "result": None, "error": "Missing required arguments: file, password"}
        
        if not os.path.exists(file_path):
            return {"success": False, "result": None, "error": f"File not found: {file_path}"}
        
        output_path = args.get("output_path")
        if not output_path:
            if file_path.endswith(".encrypted"):
                output_path = file_path[:-10]  # Remove .encrypted
            else:
                output_path = file_path + ".decrypted"
        
        # Try cryptography library first
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            import base64
            
            # Read encrypted file
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Extract salt and encrypted content
            salt = encrypted_data[:16]
            encrypted_content = encrypted_data[16:]
            
            # Derive key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            fernet = Fernet(key)
            
            # Decrypt
            decrypted_data = fernet.decrypt(encrypted_content)
            
            # Write decrypted file
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            file_size = os.path.getsize(output_path)
            encrypted_size = os.path.getsize(file_path)
            
            return {
                "success": True,
                "result": {
                    "input_file": file_path,
                    "output_file": output_path,
                    "encrypted_size": encrypted_size,
                    "decrypted_size": file_size,
                    "algorithm": "Fernet (AES 128)",
                    "decrypted": True,
                    "method": "cryptography_fernet"
                },
                "error": None
            }
        
        except ImportError:
            return {"success": False, "result": None, "error": "Decryption requires cryptography library (pip install cryptography)"}
        except Exception as decrypt_error:
            return {"success": False, "result": None, "error": f"Decryption failed - wrong password or corrupted file: {str(decrypt_error)}"}
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to decrypt file: {str(e)}"}

def _simple_encrypt_impl(file_path: str, password: str, output_path: str) -> Dict[str, Any]:
    """Simple XOR encryption fallback (NOT SECURE - for demo only)"""
    try:
        # Generate key from password
        key = hashlib.sha256(password.encode()).digest()
        
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # XOR encryption
        encrypted = bytearray()
        for i, byte in enumerate(data):
            encrypted.append(byte ^ key[i % len(key)])
        
        with open(output_path, 'wb') as f:
            f.write(encrypted)
        
        return {
            "success": True,
            "result": {
                "input_file": file_path,
                "output_file": output_path,
                "algorithm": "XOR (NOT SECURE - demo only)",
                "encrypted": True,
                "method": "simple_xor",
                "warning": "This is NOT secure encryption - install cryptography library for real security"
            },
            "error": None
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Simple encryption failed: {str(e)}"}

def _generate_password_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Password generation implementation"""
    try:
        length = args.get("length", 12)
        complexity = args.get("complexity", "medium")
        count = args.get("count", 1)
        
        if length < 4:
            return {"success": False, "result": None, "error": "Password length must be at least 4 characters"}
        
        if length > 128:
            return {"success": False, "result": None, "error": "Password length cannot exceed 128 characters"}
        
        # Define character sets based on complexity
        if complexity == "simple":
            chars = string.ascii_letters + string.digits
        elif complexity == "medium":
            chars = string.ascii_letters + string.digits + "!@#$%^&*"
        elif complexity == "complex":
            chars = string.ascii_letters + string.digits + string.punctuation
        else:
            return {"success": False, "result": None, "error": f"Unknown complexity: {complexity}. Use: simple, medium, complex"}
        
        # Generate passwords
        passwords = []
        for _ in range(count):
            password = ''.join(secrets.choice(chars) for _ in range(length))
            
            # Ensure password meets complexity requirements
            if complexity in ["medium", "complex"]:
                # Ensure at least one uppercase, lowercase, digit, and special char
                has_upper = any(c.isupper() for c in password)
                has_lower = any(c.islower() for c in password)
                has_digit = any(c.isdigit() for c in password)
                has_special = any(c in string.punctuation for c in password)
                
                # Regenerate if requirements not met (simple approach)
                attempts = 0
                while not all([has_upper, has_lower, has_digit, has_special]) and attempts < 10:
                    password = ''.join(secrets.choice(chars) for _ in range(length))
                    has_upper = any(c.isupper() for c in password)
                    has_lower = any(c.islower() for c in password)
                    has_digit = any(c.isdigit() for c in password)
                    has_special = any(c in string.punctuation for c in password)
                    attempts += 1
            
            passwords.append(password)
        
        # Calculate password strength
        strength_score = 0
        if length >= 8:
            strength_score += 1
        if length >= 12:
            strength_score += 1
        if complexity == "medium":
            strength_score += 1
        elif complexity == "complex":
            strength_score += 2
        
        strength_levels = ["Very Weak", "Weak", "Fair", "Good", "Strong"]
        strength = strength_levels[min(strength_score, 4)]
        
        return {
            "success": True,
            "result": {
                "passwords": passwords,
                "count": len(passwords),
                "length": length,
                "complexity": complexity,
                "strength": strength,
                "character_set_size": len(chars),
                "entropy_bits": round(length * (len(chars).bit_length() - 1), 1),
                "method": "cryptographically_secure"
            },
            "error": None
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to generate password: {str(e)}"}

def _hash_text_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Text hashing implementation"""
    try:
        text = args.get("text")
        if not text:
            return {"success": False, "result": None, "error": "Missing required argument: text"}
        
        algorithm = args.get("algorithm", "sha256").lower()
        
        # Convert text to bytes
        text_bytes = text.encode('utf-8')
        
        # Hash based on algorithm
        if algorithm == "md5":
            hash_obj = hashlib.md5(text_bytes)
        elif algorithm == "sha1":
            hash_obj = hashlib.sha1(text_bytes)
        elif algorithm == "sha256":
            hash_obj = hashlib.sha256(text_bytes)
        elif algorithm == "sha512":
            hash_obj = hashlib.sha512(text_bytes)
        else:
            return {"success": False, "result": None, "error": f"Unsupported algorithm: {algorithm}. Use: md5, sha1, sha256, sha512"}
        
        hash_hex = hash_obj.hexdigest()
        
        # Calculate additional info
        text_length = len(text)
        hash_length = len(hash_hex)
        
        return {
            "success": True,
            "result": {
                "text": text,
                "hash": hash_hex,
                "algorithm": algorithm.upper(),
                "text_length": text_length,
                "hash_length": hash_length,
                "method": "hashlib"
            },
            "error": None
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to hash text: {str(e)}"}

def _clear_temp_files_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Clear temporary files implementation"""
    try:
        temp_dir = args.get("temp_dir", tempfile.gettempdir())
        pattern = args.get("pattern", "*")
        older_than_hours = args.get("older_than_hours", 24)
        dry_run = args.get("dry_run", False)
        
        if not os.path.exists(temp_dir):
            return {"success": False, "result": None, "error": f"Temp directory not found: {temp_dir}"}
        
        import glob
        import time
        
        # Find files to delete
        if pattern == "*":
            # Get all files in temp directory
            files_to_delete = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        # Check if file is older than specified hours
                        file_age_hours = (time.time() - os.path.getmtime(file_path)) / 3600
                        if file_age_hours > older_than_hours:
                            files_to_delete.append(file_path)
                    except (OSError, IOError):
                        continue  # Skip files we can't access
        else:
            # Use pattern matching
            search_pattern = os.path.join(temp_dir, pattern)
            files_to_delete = glob.glob(search_pattern)
        
        # Filter by age if specified
        if older_than_hours > 0:
            filtered_files = []
            for file_path in files_to_delete:
                try:
                    file_age_hours = (time.time() - os.path.getmtime(file_path)) / 3600
                    if file_age_hours > older_than_hours:
                        filtered_files.append(file_path)
                except (OSError, IOError):
                    continue
            files_to_delete = filtered_files
        
        # Delete files (or simulate if dry run)
        deleted_files = []
        deleted_size = 0
        errors = []
        
        for file_path in files_to_delete:
            try:
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    
                    if not dry_run:
                        os.remove(file_path)
                    
                    deleted_files.append(file_path)
                    deleted_size += file_size
            except (OSError, IOError) as e:
                errors.append(f"{file_path}: {str(e)}")
        
        return {
            "success": True,
            "result": {
                "temp_directory": temp_dir,
                "files_found": len(files_to_delete),
                "files_deleted": len(deleted_files),
                "total_size_mb": round(deleted_size / 1024 / 1024, 2),
                "errors": errors,
                "dry_run": dry_run,
                "older_than_hours": older_than_hours,
                "method": "temp_cleanup"
            },
            "error": None
        }
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to clear temp files: {str(e)}"}

def _secure_delete_impl(args: Dict[str, Any]) -> Dict[str, Any]:
    """Secure file deletion implementation"""
    try:
        file_path = args.get("file")
        if not file_path:
            return {"success": False, "result": None, "error": "Missing required argument: file"}
        
        if not os.path.exists(file_path):
            return {"success": False, "result": None, "error": f"File not found: {file_path}"}
        
        passes = args.get("passes", 3)
        
        # Get file info before deletion
        file_size = os.path.getsize(file_path)
        
        # Secure deletion by overwriting with random data
        try:
            with open(file_path, 'r+b') as f:
                for pass_num in range(passes):
                    f.seek(0)
                    # Overwrite with random data
                    random_data = os.urandom(file_size)
                    f.write(random_data)
                    f.flush()
                    os.fsync(f.fileno())  # Force write to disk
            
            # Finally delete the file
            os.remove(file_path)
            
            return {
                "success": True,
                "result": {
                    "file_path": file_path,
                    "file_size": file_size,
                    "overwrite_passes": passes,
                    "securely_deleted": True,
                    "method": "overwrite_and_delete"
                },
                "error": None
            }
        
        except PermissionError:
            return {"success": False, "result": None, "error": f"Permission denied: {file_path}"}
    
    except Exception as e:
        return {"success": False, "result": None, "error": f"Failed to securely delete file: {str(e)}"}

# Legacy function aliases for backward compatibility
def encrypt_file(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use security_manager instead"""
    return security_manager(args={"action": "encrypt", **(args or {})})

def decrypt_file(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use security_manager instead"""
    return security_manager(args={"action": "decrypt", **(args or {})})

def generate_password(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use security_manager instead"""
    return security_manager(args={"action": "generate_password", **(args or {})})

def hash_text(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use security_manager instead"""
    return security_manager(args={"action": "hash", **(args or {})})

def clear_temp_files(*, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """Legacy function - use security_manager instead"""
    return security_manager(args={"action": "clear_temp", **(args or {})})
