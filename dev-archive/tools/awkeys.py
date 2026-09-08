"""awkeys.py - send keys that Alan Wake actually receives.

THE RULE, measured on the dev PC 2026-09-08 against the main menu (a stable state
that does not auto-advance, so every result is attributable):

    a bare SendInput keypress - VK **or** scancode - does NOT reach this game,
    even with the game's window verified as the foreground window.
    A LEFT MOUSE CLICK IN THE WINDOW IMMEDIATELY BEFORE THE KEY makes it land,
    and the effect does NOT persist: the NEXT key needs its own click.

Evidence (highlight on the main menu, one key each, screenshot after every step):
    VK down, no click .................... highlight did NOT move
    scancode down, no click .............. highlight did NOT move
    cursor moved inside window, no click . highlight did NOT move
    click then VK down ................... highlight MOVED
    VK down again, no click .............. highlight did NOT move

So: click, key, click, key. Why the click is needed is NOT established - a
plausible cause is that each shell command steals foreground and the game never
gets a proper activation back, with the click forcing one. Do not record a cause.

⚠️ Click high in the window (default 15% down) - the menu list is in the lower
third and a click there would SELECT an item. Never click blind near "Quit".

Usage:
    python awkeys.py down enter          # click before each, in order
    python awkeys.py --repeat 5 down
"""
import ctypes, ctypes.wintypes as w, sys, time

u = ctypes.windll.user32
VK = {"space": 0x20, "enter": 0x0D, "down": 0x28, "up": 0x26, "left": 0x25,
      "right": 0x27, "esc": 0x1B, "w": 0x57, "a": 0x41, "s": 0x53, "d": 0x44,
      "e": 0x45, "f": 0x46, "tab": 0x09}
KEYEVENTF_KEYUP = 0x0002
MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP = 0x0002, 0x0004


class KI(ctypes.Structure):
    _fields_ = [("wVk", w.WORD), ("wScan", w.WORD), ("dwFlags", w.DWORD),
                ("time", w.DWORD), ("dwExtraInfo", ctypes.POINTER(w.ULONG))]


class MI(ctypes.Structure):
    _fields_ = [("dx", w.LONG), ("dy", w.LONG), ("mouseData", w.DWORD),
                ("dwFlags", w.DWORD), ("time", w.DWORD),
                ("dwExtraInfo", ctypes.POINTER(w.ULONG))]


class _U(ctypes.Union):
    _fields_ = [("ki", KI), ("mi", MI)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", w.DWORD), ("u", _U)]


def _send(inp):
    u.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))


def find_window():
    found = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, w.HWND, w.LPARAM)
    def cb(h, l):
        n = u.GetWindowTextLengthW(h)
        if n and u.IsWindowVisible(h):
            b = ctypes.create_unicode_buffer(n + 1)
            u.GetWindowTextW(h, b, n + 1)
            if b.value.startswith("Alan Wake"):
                found.append(h)
        return True

    u.EnumWindows(cb, 0)
    if not found:
        raise SystemExit("no window titled 'Alan Wake ...'")
    return found[0]


def activate_click(hwnd, frac=0.15):
    """Foreground the window and click high inside it. The click is what makes the
    NEXT keypress land; frac keeps it clear of the lower-third menu list."""
    u.SetForegroundWindow(hwnd)
    time.sleep(0.25)
    r = w.RECT()
    u.GetWindowRect(hwnd, ctypes.byref(r))
    u.SetCursorPos(int((r.left + r.right) / 2),
                   int(r.top + (r.bottom - r.top) * frac))
    time.sleep(0.20)
    for f in (MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP):
        _send(INPUT(0, _U(mi=MI(0, 0, 0, f, 0, None))))
        time.sleep(0.06)
    time.sleep(0.30)


def tap(hwnd, name, settle=0.7):
    activate_click(hwnd)
    vk = VK[name]
    _send(INPUT(1, _U(ki=KI(vk, 0, 0, 0, None))))
    time.sleep(0.07)
    _send(INPUT(1, _U(ki=KI(vk, 0, KEYEVENTF_KEYUP, 0, None))))
    time.sleep(settle)


if __name__ == "__main__":
    args = sys.argv[1:]
    rep = 1
    if "--repeat" in args:
        i = args.index("--repeat")
        rep = int(args[i + 1])
        del args[i:i + 2]
    hwnd = find_window()
    for name in args:
        for _ in range(rep):
            tap(hwnd, name)
            print("tapped", name)
