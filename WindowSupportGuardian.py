
"""
WindowSupport Guardian Service
Monitors and restarts WindowPowerShellProvider.exe if it stops
This runs as a Windows Service (system-level)
"""

import os
import sys
import time
import subprocess
import psutil
import win32serviceutil
import win32service
import win32event
import servicemanager
import traceback

class WindowSupportGuardian(win32serviceutil.ServiceFramework):
    _svc_name_ = 'WindowSupportGuardian'
    _svc_display_name_ = 'Window Support Guardian Service'
    _svc_description_ = 'Monitors and restarts WindowPowerShellProvider if stopped'
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.running = True
        self.consecutive_errors = 0
        self.max_consecutive_errors = 10
        
    def SvcStop(self):
        """Called when the service is being stopped"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.running = False
        
    def SvcDoRun(self):
        """Main service loop with ultimate crash protection"""
        try:
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, '')
            )
        except Exception:
            pass
        
        # Ultimate protection: if main() crashes, restart it
        while self.running:
            try:
                self.main()
                break  # Normal exit
            except Exception as e:
                try:
                    tb = traceback.format_exc()
                    self.log(f"CRITICAL: main() crashed: {e}\n{tb}")
                    self.log("Restarting main() in 10 seconds...")
                except Exception:
                    pass
                time.sleep(10)
                if not self.running:
                    break
        
    def log(self, msg):
        """Log message to Windows Event Log"""
        try:
            servicemanager.LogInfoMsg(str(msg))
        except Exception:
            pass  # Fail silently if logging fails
        
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
            
            # Try multiple potential locations
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
            
            exe_path = None
            for loc in locations:
                if os.path.exists(loc):
                    exe_path = loc
                    self.log(f"Found WindowPowerShellProvider at: {exe_path}")
                    break
            
            if not exe_path:
                self.log("WindowPowerShellProvider.exe not found in any of these locations:")
                for loc in locations:
                    self.log(f"  - {loc}")
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
        self.log("Guardian Service started - Monitoring WindowPowerShellProvider")
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
                
                # Wait for next check or stop event
                if win32event.WaitForSingleObject(self.stop_event, check_interval * 1000) == win32event.WAIT_OBJECT_0:
                    break
                    
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
        
        self.log("Guardian Service stopped")

if __name__ == '__main__':
    # Check if running from correct installation location
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
            print("Please install properly using INSTALL_WindowSupport.bat")
            print()
            print("If you want to install this service manually:")
            print(f"  1. Copy to: {expected_location}")
            print(f"  2. Run: {os.path.join(expected_location, 'WindowSupportGuardian', 'WindowSupportGuardian.exe')} install")
            print(f"  3. Run: sc start WindowSupportGuardian")
            print("=" * 70)
            if len(sys.argv) > 1 and sys.argv[1] not in ['install', 'remove', 'update', 'start', 'stop']:
                # Allow service commands to proceed
                pass
            elif len(sys.argv) == 1:
                print("\nPress any key to exit...")
                input()
                sys.exit(1)
    except Exception:
        pass  # Continue anyway if check fails
    
    # Wrap everything in try-except to prevent crashes
    try:
        if len(sys.argv) == 1:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(WindowSupportGuardian)
            servicemanager.StartServiceCtrlDispatcher()
        else:
            win32serviceutil.HandleCommandLine(WindowSupportGuardian)
    except Exception as e:
        try:
            servicemanager.LogErrorMsg(f"Fatal error in Guardian service: {e}")
        except Exception:
            pass
        # Sleep and exit - Windows Service Manager will auto-restart
        time.sleep(5)
        sys.exit(1)


