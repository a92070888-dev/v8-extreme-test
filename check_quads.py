import ctypes
from ctypes import wintypes

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
user32 = ctypes.windll.user32
EnumWindows = user32.EnumWindows
GetWindowText = user32.GetWindowTextW
GetWindowTextLength = user32.GetWindowTextLengthW
IsWindowVisible = user32.IsWindowVisible
GetWindowRect = user32.GetWindowRect

def get_rect(hwnd):
    r = wintypes.RECT()
    GetWindowRect(hwnd, ctypes.byref(r))
    return r.left, r.top, r.right, r.bottom

results = []
def cb(hwnd, lp):
    if IsWindowVisible(hwnd):
        l = GetWindowTextLength(hwnd) + 1
        b = ctypes.create_unicode_buffer(l)
        GetWindowText(hwnd, b, l)
        t = b.value
        if t:
            x1, y1, x2, y2 = get_rect(hwnd)
            if x2 > 0 and x1 < 2000:
                quad = "??"
                if x1 < 10 and y1 < 10: quad = "Q1-TL"
                elif x1 >= 900 and y1 < 10: quad = "Q2-TR"
                elif x1 < 10 and y1 >= 500: quad = "Q3-BL"
                elif x1 >= 900 and y1 >= 500: quad = "Q4-BR"
                print(f"[{quad}] ({x1},{y1})-({x2},{y2}) {t}")
    return True

EnumWindows(WNDENUMPROC(cb), 0)
