import tkinter as tk
from tkinter import ttk
import requests
import json
import os
import sys
import cloudscraper
import certifi
import winreg
import time
import traceback

# Constants
REG_PATH = r"Software\WindowSupport"
REG_NAME = "staff_id"
API_URL = "http://teamspace.baselinepracticesupport.co.uk/return_all_employees.php"

# App data directory used by WindowPowerShellProvider
LOCAL_APPDATA = os.environ.get('LOCALAPPDATA') or os.path.expanduser('~')
APP_DIR = os.path.join(LOCAL_APPDATA, 'WindowSupport')
CONFIG_FILE = os.path.join(APP_DIR, 'config.json')

def ensure_app_dir():
    try:
        os.makedirs(APP_DIR, exist_ok=True)
    except Exception:
        pass

def save_staff_id(staff_id):
    """Save the selected staff ID to HKCU and to config.json for provider fallback"""
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        winreg.SetValueEx(key, REG_NAME, 0, winreg.REG_SZ, staff_id)
        winreg.CloseKey(key)
        try:
            ensure_app_dir()
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump({'staff_id': staff_id}, f)
        except Exception:
            pass
        print(f"Staff ID {staff_id} saved.")
    except Exception as e:
        print(f"Error saving staff ID to registry: {e}")

def get_staff_id():
    """Retrieve the staff ID from the Windows Registry"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        value, _ = winreg.QueryValueEx(key, REG_NAME)
        winreg.CloseKey(key)
        return value
    except FileNotFoundError:
        return ""
    except Exception as e:
        print(f"Error reading staff ID from registry: {e}")
        return ""

def fetch_staff_ids():
    """Fetch staff IDs from the API with timeout and basic retries"""
    try:
        print("Attempting to fetch staff IDs...")
        scraper = cloudscraper.create_scraper()
        for attempt in range(3):
            try:
                response = scraper.get(API_URL, timeout=10, verify=certifi.where())
                print(f"Response Status Code: {response.status_code}")
                if response.status_code != 200:
                    time.sleep(1.5)
                    continue
                clean_response = response.text.lstrip('/').strip()
                data = json.loads(clean_response)
                if data.get('status') == 'success':
                    items = data.get('staff_ids', []) or []
                    # Normalize to list of strings
                    staff_ids = [str(x) for x in items]
                    staff_ids = sorted(staff_ids)
                    print(f"Found {len(staff_ids)} staff IDs")
                    return staff_ids
                else:
                    print(f"API returned non-success status: {data.get('status')}")
                    return []
            except Exception as e:
                print(f"Attempt {attempt+1} failed: {e}")
                time.sleep(1.5)
        return []
    except Exception as e:
        print(f"Error fetching staff IDs: {e}")
        print("Full error traceback:")
        print(traceback.format_exc())
        return []

class StaffIDSelector:
    def __init__(self, root):
        self.root = root
        self.root.title("Select Your Staff ID")
        ensure_app_dir()
        
        # Center the window
        window_width = 520
        window_height = 320
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create and pack widgets
        title = ttk.Label(main_frame, text="Select Your Staff ID", font=('Segoe UI', 14, 'bold'))
        title.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Add a loading label
        self.loading_label = ttk.Label(main_frame, text="Loading staff IDs...", font=('Segoe UI', 10))
        self.loading_label.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)

        # Search box
        ttk.Label(main_frame, text="Search:", font=('Segoe UI', 10)).grid(row=2, column=0, sticky=tk.W)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(main_frame, textvariable=self.search_var, width=40)
        self.search_entry.grid(row=2, column=1, sticky=(tk.W, tk.E))
        self.search_var.trace_add('write', lambda *args: self.filter_ids())
        
        # Create combobox
        self.selected_id = tk.StringVar()
        self.combo = ttk.Combobox(main_frame, textvariable=self.selected_id, width=44, state='readonly')
        self.combo.grid(row=3, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        self.combo.bind('<KeyRelease>', self._combo_typeahead)
        
        # Pre-fill combobox with current staff_id if available
        current_staff_id = get_staff_id()
        if current_staff_id:
            self.selected_id.set(current_staff_id)
        
        # Create save button (disabled until IDs load)
        buttons = ttk.Frame(main_frame)
        buttons.grid(row=4, column=0, columnspan=2, pady=10, sticky=(tk.E))
        self.save_button = ttk.Button(buttons, text="Save", command=self.save_selected_id)
        self.save_button.state(['disabled'])
        self.save_button.grid(row=0, column=1, padx=(8, 0))
        self.refresh_button = ttk.Button(buttons, text="Refresh", command=self.load_staff_ids)
        self.refresh_button.grid(row=0, column=0)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="", font=('Segoe UI', 10))
        self.status_label.grid(row=5, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W))
        
        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Fetch staff IDs after UI is created
        self.root.after(100, self.load_staff_ids)

    def load_staff_ids(self):
        """Load staff IDs in a separate step"""
        try:
            self.staff_ids = fetch_staff_ids()
            if self.staff_ids:
                self.combo['values'] = self.staff_ids
                self.loading_label.config(text=f"Found {len(self.staff_ids)} staff IDs")
                # Preselect current if present
                current = get_staff_id()
                if current and current in self.staff_ids:
                    self.selected_id.set(current)
                # Enable Save
                self.save_button.state(['!disabled'])
            else:
                self.loading_label.config(text="No staff IDs found", foreground="red")
        except Exception as e:
            self.loading_label.config(text=f"Error loading staff IDs: {e}", foreground="red")

    def filter_ids(self):
        try:
            query = (self.search_var.get() or '').strip().lower()
            if not hasattr(self, 'staff_ids') or not self.staff_ids:
                return
            if not query:
                filtered = self.staff_ids
            else:
                filtered = [sid for sid in self.staff_ids if query in str(sid).lower()]
            self.combo['values'] = filtered
            # Keep current selection if still in filtered list
            current = self.selected_id.get()
            if current in filtered:
                self.combo.set(current)
            elif filtered:
                self.combo.set(filtered[0])
            else:
                self.combo.set('')
        except Exception:
            pass

    def _combo_typeahead(self, event):
        # Allow typing to jump within the dropdown values
        try:
            text = self.combo.get().lower()
            values = self.combo['values']
            for v in values:
                if str(v).lower().startswith(text):
                    self.combo.set(v)
                    break
        except Exception:
            pass

    def save_selected_id(self):
        """Save the selected staff ID"""
        selected = self.selected_id.get()
        if selected:
            save_staff_id(selected)
            self.status_label.config(text=f"Staff ID {selected} saved successfully!", foreground="green")
            # Close the window after 2 seconds
            self.root.after(2000, self.root.destroy)
        else:
            self.status_label.config(text="Please select a Staff ID!", foreground="red")

def main():
    root = tk.Tk()
    app = StaffIDSelector(root)
    root.mainloop()

if __name__ == "__main__":
    main() 