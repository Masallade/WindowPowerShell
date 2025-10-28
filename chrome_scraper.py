import time
import psutil
import win32gui
import win32process
import re
from datetime import datetime

# Helper to get all Chrome processes

def get_chrome_processes():
    chrome_procs = []
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] and 'chrome' in proc.info['name'].lower():
            chrome_procs.append(proc)
    return chrome_procs

# Helper to get window title and PID

def enum_windows():
    windows = []
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            title = win32gui.GetWindowText(hwnd)
            if title and 'chrome' in title.lower():
                windows.append((hwnd, pid, title))
    win32gui.EnumWindows(callback, None)
    return windows

# Try to extract URL from Chrome window title (works for most tabs)
def extract_url_from_title(title):
    # Chrome window titles are usually: "Page Title - Site.com"
    # This is a best-effort guess, as Chrome does not expose URLs in window titles
    # For more accurate results, Chrome extension or remote debugging is needed
    # Here, we just return the title as a placeholder
    return title

# Track when a tab was first seen
open_tabs = {}

while True:
    windows = enum_windows()
    now = datetime.now()
    current_tabs = {}
    for hwnd, pid, title in windows:
        url_guess = extract_url_from_title(title)
        if url_guess not in open_tabs:
            open_tabs[url_guess] = now
        current_tabs[url_guess] = open_tabs[url_guess]

    # Remove closed tabs from tracking
    to_remove = [tab for tab in open_tabs if tab not in current_tabs]
    for tab in to_remove:
        del open_tabs[tab]

    print("\nCurrently open Chrome tabs:")
    for url, since in current_tabs.items():
        duration = (now - since).total_seconds()
        print(f"Tab: {url} | Open since: {since.strftime('%Y-%m-%d %H:%M:%S')} | Open for: {int(duration)} seconds")

    print("\n--- Refreshing in 10 seconds ---")
    time.sleep(10)

# Note: This script uses window titles as a proxy for URLs. For exact URLs, Chrome remote debugging or an extension is required. 