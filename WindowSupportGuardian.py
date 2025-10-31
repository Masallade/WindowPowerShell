"""
WindowSupport Guardian - Background Monitor
Monitors and restarts WindowPowerShellProvider.exe if it stops
This runs as a background process (managed by NSSM as a Windows Service)
"""

import os
import sys
import time
import subprocess
import psutil
import traceback
import winreg
from datetime import datetime

class WindowSupportGuardian:
    def __init__(self):
        self.running = True
        self.consecutive_errors = 0
        self.max_consecutive_errors = 10
        self.log_file = self.get_log_file_path()
        
    def get_log_file_path(self):
        """Get path for log file in AppData"""
        try:
            appdata = os.environ.get('LOCALAPPDATA', '')
            log_dir = os.path.join(appdata, 'WindowSupport', 'logs')
            os.makedirs(log_dir, exist_ok=True)
            return os.path.join(log_dir, 'WindowSupportGuardian.log')
        except Exception:
            return 'WindowSupportGuardian.log'
        
    def log(self, msg):
        """Log message to file"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_message = f"[{timestamp}] {msg}\n"
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message)
            print(log_message.strip())  # Also print to console for NSSM to capture
        except Exception:
            pass  # Fail silently if logging fails
        
    def get_provider_path_from_registry(self):
        """Get WindowPowerShellProvider.exe path from Windows Registry"""
        try:
            # Try to read from HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WindowSupport", 0, winreg.KEY_READ)
            provider_path, _ = winreg.QueryValueEx(key, "ProviderExePath")
            winreg.CloseKey(key)
            
            if provider_path and os.path.exists(provider_path):
                self.log(f"Found Provider path in registry: {provider_path}")
                return provider_path
            else:
                self.log(f"Registry path exists but file not found: {provider_path}")
                return None
        except FileNotFoundError:
            self.log("Registry key not found (SOFTWARE\\WindowSupport)")
            return None
        except Exception as e:
            self.log(f"Error reading from registry: {e}")
            return None
    
    def get_current_user(self):
        """Get the currently logged-in user"""
        try:
            # Get all users with active sessions
            for user in psutil.users():
                if user.name and user.terminal:  # Has an active session
                    return user.name
            return None
        except Exception as e:
            self.log(f"Error getting current user: {e}")
            return None
    
    def is_process_running(self, process_name="WindowPowerShellProvider.exe", for_user=None):
        """Check if the target process is running for a specific user"""
        try:
            for proc in psutil.process_iter(['name', 'username']):
                if proc.info['name'] == process_name:
                    # If checking for specific user, verify username matches
                    if for_user:
                        try:
                            proc_username = proc.info.get('username', '').split('\\')[-1].lower()
                            if proc_username == for_user.lower():
                                return True
                        except Exception:
                            continue
                    else:
                        # No user specified, return True if any instance running
                        return True
            return False
        except Exception as e:
            self.log(f"Error checking process: {e}")
            return False
    
    def start_process(self):
        """Start WindowPowerShellProvider.exe for current user"""
        try:
            current_user = self.get_current_user()
            if not current_user:
                self.log("No user logged in, skipping process start")
                return False
            
            # FIRST: Try to get path from Windows Registry (most reliable)
            exe_path = self.get_provider_path_from_registry()
            
            # FALLBACK: If registry not found, try multiple potential locations
            if not exe_path:
                self.log("Registry not found, searching common locations...")
                
                # Note: After PyInstaller --onedir build, the exe is in a subfolder
                guardian_dir = os.path.dirname(os.path.abspath(sys.executable))
                parent_dir = os.path.dirname(guardian_dir)
                
                locations = [
                    # Location when both are in dist\WindowSupport\
                    os.path.join(parent_dir, 'WindowPowerShellProvider', 'WindowPowerShellProvider.exe'),
                    # Location in AppData
                    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'WindowSupport', 'WindowPowerShellProvider', 'WindowPowerShellProvider.exe'),
                    # Location in ProgramData
                    os.path.join(os.environ.get('ProgramData', ''), 'WindowSupport', 'WindowPowerShellProvider', 'WindowPowerShellProvider.exe'),
                    # Same directory as guardian (fallback)
                    os.path.join(guardian_dir, 'WindowPowerShellProvider.exe'),
                    # Old single-file location (backward compatibility)
                    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'WindowSupport', 'WindowPowerShellProvider.exe'),
                ]
                
                for loc in locations:
                    if os.path.exists(loc):
                        exe_path = loc
                        self.log(f"Found WindowPowerShellProvider at: {exe_path}")
                        break
            
            if not exe_path:
                self.log("WindowPowerShellProvider.exe not found!")
                self.log("Checked registry and common installation locations")
                return False
            
            # Start the process using scheduled task (better for user context)
            task_name = "WindowSupportMonitor"
            try:
                result = subprocess.run(
                    f'schtasks /run /tn "{task_name}"',
                    shell=True,
                    capture_output=True,
                    timeout=10,
                    text=True
                )
                if result.returncode == 0:
                    self.log(f"Started via scheduled task: {task_name}")
                    return True
                else:
                    # Fallback: start directly
                    subprocess.Popen([exe_path], shell=False, 
                                   creationflags=subprocess.CREATE_NO_WINDOW)
                    self.log(f"Started process directly: {exe_path}")
                    return True
            except Exception as e:
                self.log(f"Error starting process: {e}")
                return False
                
        except Exception as e:
            self.log(f"Error in start_process: {e}")
            return False
    
    def main(self):
        """Main monitoring loop with robust error handling"""
        self.log("Guardian started - Monitoring WindowPowerShellProvider")
        self.log(f"Log file: {self.log_file}")
        check_interval = 30  # Check every 30 seconds
        
        while self.running:
            try:
                # Check if someone is logged in
                current_user = self.get_current_user()
                
                if current_user:
                    # User is logged in, check if process is running FOR THIS USER
                    if not self.is_process_running(for_user=current_user):
                        self.log(f"Process not running for user {current_user}, attempting restart...")
                        if self.start_process():
                            self.log("Process started successfully")
                            self.consecutive_errors = 0  # Reset error counter
                        else:
                            self.log("Failed to start process")
                            self.consecutive_errors += 1
                    else:
                        self.consecutive_errors = 0  # Process running, reset errors
                else:
                    # No user logged in, skip monitoring
                    self.consecutive_errors = 0
                
                # Check if too many consecutive errors
                if self.consecutive_errors >= self.max_consecutive_errors:
                    self.log(f"Too many consecutive errors ({self.consecutive_errors}), resetting...")
                    self.consecutive_errors = 0
                    time.sleep(60)  # Wait longer before retrying
                
                # Wait for next check (simple sleep since NSSM handles stop signals)
                time.sleep(check_interval)
                    
            except Exception as e:
                self.consecutive_errors += 1
                try:
                    tb = traceback.format_exc()
                    self.log(f"Error in main loop: {e}\n{tb}")
                except Exception:
                    self.log(f"Error in main loop: {e}")
                
                # Exponential backoff on errors
                sleep_time = min(10 * self.consecutive_errors, 120)
                time.sleep(sleep_time)
        
        self.log("Guardian stopped")

def run_guardian():
    """Run the Guardian with crash protection"""
    guardian = WindowSupportGuardian()
    
    # Ultimate protection: if main() crashes, restart it
    while True:
        try:
            guardian.main()
            break  # Normal exit
        except KeyboardInterrupt:
            guardian.log("Guardian stopped by user (Ctrl+C)")
            break
        except Exception as e:
            try:
                tb = traceback.format_exc()
                guardian.log(f"CRITICAL: Guardian crashed: {e}\n{tb}")
                guardian.log("Restarting Guardian in 10 seconds...")
            except Exception:
                pass
            time.sleep(10)

if __name__ == '__main__':
    # Check if running from correct installation location (warning only)
    try:
        exe_path = os.path.abspath(sys.executable)
        expected_location = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'WindowSupport')
        current_location = os.path.dirname(exe_path)
        
        if expected_location.lower() not in current_location.lower():
            print("=" * 70)
            print("WARNING: Guardian not running from installed location!")
            print("=" * 70)
            print(f"Current location: {current_location}")
            print(f"Expected location: {expected_location}")
            print()
            print("For proper installation, use: INSTALL_WindowSupport.bat")
            print("=" * 70)
            print()
    except Exception:
        pass  # Continue anyway if check fails
    
    # Run the Guardian
    print("Starting WindowSupport Guardian...")
    print("This will monitor and restart WindowPowerShellProvider if needed.")
    print("Press Ctrl+C to stop (when testing manually)")
    print()
    
    run_guardian()


