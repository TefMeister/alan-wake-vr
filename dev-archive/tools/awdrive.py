"""
awdrive.py - drive Alan Wake (2012 PC) from outside, for the /lm lane.

Mechanism from flat-to-vr-RE-toolkit/tools/game-harness.py (BitBlt capture, scancode keys,
focus first). Game-specific facts from ai-game-control-profiles/profiles/alan-wake.json:
  - window title "Alan Wake - v<version>": match on the substring
  - title screen takes SPACE ("Press any key to play"); main menu: Down x5 = Quit, Enter,
    "Are you sure" -> Enter
  - the proxy log is <game folder>\\alanwake_vr_proxy_log.txt
  - NEVER send Alt+Enter (minimises an exclusive-fullscreen build); if IsIconic, restore

Usage:
    python awdrive.py shot out.png
    python awdrive.py key space|enter|down|esc [--repeat N]
    python awdrive.py restore            # SW_RESTORE + foreground if minimised
    python awdrive.py state              # window rect / iconic / running
    python awdrive.py log [N]            # last N lines of the proxy log
"""
import ctypes, ctypes.wintypes as w, importlib.util, os, sys, time

TOOLKIT = r"C:\Users\TD3KX\github-backups\flat-to-vr-RE-toolkit\tools\game-harness.py"
GAME = r"C:\Steam\steamapps\common\Alan Wake"
LOG = os.path.join(GAME, "alanwake_vr_proxy_log.txt")
WINDOW = "Alan Wake"

spec = importlib.util.spec_from_file_location("harness", TOOLKIT)
H = importlib.util.module_from_spec(spec); spec.loader.exec_module(H)
u = ctypes.windll.user32


def restore(hwnd):
    if u.IsIconic(hwnd):
        u.ShowWindow(hwnd, 9)  # SW_RESTORE
        time.sleep(0.5)
    H.focus(hwnd)


if __name__ == "__main__":
    cmd, rest = sys.argv[1], sys.argv[2:]
    if cmd == "log":
        n = int(rest[0]) if rest else 60
        try:
            lines = open(LOG, "r", encoding="utf-8", errors="replace").read().splitlines()
        except OSError:
            lines = ["(no log file)"]
        print("\n".join(lines[-n:])); sys.exit()
    # the profile says the title is exactly "Alan Wake - v<version>"; a terminal whose title merely
    # mentions the game matched the toolkit's substring search first on 2026-09-05, so match the prefix
    import ctypes.wintypes as _w
    _found = []
    @ctypes.WINFUNCTYPE(ctypes.c_bool, _w.HWND, _w.LPARAM)
    def _cb(h, l):
        n = u.GetWindowTextLengthW(h)
        if n and u.IsWindowVisible(h):
            b = ctypes.create_unicode_buffer(n + 1); u.GetWindowTextW(h, b, n + 1)
            if b.value.startswith("Alan Wake"): _found.append((h, b.value))
        return True
    u.EnumWindows(_cb, 0)
    if not _found: raise SystemExit("no window titled Alan Wake - v...")
    hwnd, title = _found[0]
    if cmd == "state":
        r = w.RECT(); u.GetWindowRect(hwnd, ctypes.byref(r))
        print("title=%r rect=(%d,%d)-(%d,%d) iconic=%d" % (title, r.left, r.top, r.right, r.bottom, u.IsIconic(hwnd))); sys.exit()
    restore(hwnd)
    if cmd == "restore":
        print("restored/focused", title)
    elif cmd == "shot":
        H.grab(hwnd).save(rest[0]); print("saved", rest[0])
    elif cmd == "key":
        rep = int(rest[rest.index("--repeat") + 1]) if "--repeat" in rest else 1
        for _ in range(rep): H.tap(rest[0], settle=0.6)
        print("tapped", rest[0], "x", rep)
    else:
        raise SystemExit("unknown command " + cmd)
