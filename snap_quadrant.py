"""
Snap window to quadrant using SendInput mouse drag.
Drags title bar to top-center to trigger Windows 11 Snap Layout flyout,
then drops on the target zone.
Usage: python snap_quadrant.py "WindowTitle" 1|2|3|4
"""
import ctypes, sys, time
from ctypes import wintypes

user32 = ctypes.windll.user32
ABSOLUTE = 0x8000
MOVE = 0x0001
DOWN = 0x0002
UP = 0x0004

def mouse(flags, x, y, sw, sh):
    buf = ctypes.create_string_buffer(28)
    ctypes.memmove(buf, ctypes.byref(ctypes.c_ulong(0)), 4)  # type=INPUT_MOUSE
    ax = int(x * 65535 / sw)
    ay = int(y * 65535 / sh)
    ctypes.memmove(buf[4:], ctypes.byref(ctypes.c_long(ax)), 4)
    ctypes.memmove(buf[8:], ctypes.byref(ctypes.c_long(ay)), 4)
    ctypes.memmove(buf[12:], ctypes.byref(ctypes.c_ulong(flags)), 4)
    user32.SendInput(1, buf, 28)

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

def find(part):
    results = []
    def cb(hwnd, lp):
        if user32.IsWindowVisible(hwnd):
            l = user32.GetWindowTextLengthW(hwnd) + 1
            b = ctypes.create_unicode_buffer(l)
            user32.GetWindowTextW(hwnd, b, l)
            if part.lower() in b.value.lower():
                r = wintypes.RECT()
                user32.GetWindowRect(hwnd, ctypes.byref(r))
                results.append((hwnd, b.value, r))
        return True
    user32.EnumWindows(WNDENUMPROC(cb), 0)
    return results

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python snap_quadrant.py \"Title\" Q1|Q2|Q3|Q4")
        sys.exit(1)
    
    title = sys.argv[1]
    quad = sys.argv[2].upper()
    sw, sh = 1920, 1080  # actual display size
    # Also get from API for verification
    sw_api, sh_api = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    
    wins = find(title)
    if not wins:
        print(f"'{title}' not found")
        sys.exit(1)
    
    hwnd, name, rect = wins[0]
    cx = rect.left + (rect.right - rect.left) // 2
    cy = rect.top + 15
    print(f"{name} title=({cx},{cy}) screen={sw}x{sh}")
    
    # Focus window
    user32.ShowWindow(hwnd, 1)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.5)
    
    # Move cursor to title bar
    mouse(MOVE | ABSOLUTE, cx, cy, sw, sh)
    time.sleep(0.1)
    # Press and hold
    mouse(DOWN | ABSOLUTE, cx, cy, sw, sh)
    time.sleep(0.05)
    # Drag to top-center to trigger snap layout flyout
    mouse(MOVE | ABSOLUTE, sw // 2, 0, sw, sh)
    time.sleep(0.5)
    
    # Quadrant zones in the 2x2 grid flyout (approximate positions)
    zones = {
        "Q1": (sw // 2 - 80, 100),  # top-left
        "Q2": (sw // 2 + 80, 100),  # top-right
        "Q3": (sw // 2 - 80, 180),  # bottom-left
        "Q4": (sw // 2 + 80, 180),  # bottom-right
    }
    
    if quad in zones:
        zx, zy = zones[quad]
        mouse(MOVE | ABSOLUTE, zx, zy, sw, sh)
        time.sleep(0.3)
        mouse(UP | ABSOLUTE, zx, zy, sw, sh)
        print(f"Dropped on {quad} zone ({zx},{zy})")
    else:
        mouse(UP | ABSOLUTE, sw // 2, 0, sw, sh)
    
    time.sleep(0.5)
    r = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(r))
    print(f"Result: ({r.left},{r.top})-({r.right},{r.bottom})")
