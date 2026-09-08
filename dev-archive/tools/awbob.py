"""awbob.py - measure Alan Wake's per-frame vertical camera motion while walking.

Why this is a script and not a few lines retyped per run: it is one half of an A/B.
The 2026-09-08f run captured the TREATMENT half (`-rigidcamera` armed) and read
zero bob; the control is a no-flag launch at the same save point. If the two halves
are measured by code typed twice, a difference in the measurement is indistinguishable
from a difference in the game. So both halves run THIS file.

    python awbob.py capture <outdir> [frames]    hold W, grab N frames
    python awbob.py measure <outdir>             per-frame vertical shift + guards

The measure step prints two guards alongside the numbers, because a row of zeros is
worthless on its own:

  * frame-to-frame luma delta - proves the game was rendering and the character was
    moving, rather than the capture being faster than the frame rate.
  * estimator validation - injects known +/-1, +/-3, +/-8 px offsets into a real frame
    and checks each magnitude is recovered. A null from a blind estimator is not a null.

Vertical shift is measured on the UPPER band (sky / treeline / far field). The lower
band is dominated by the road rushing past and by the character, neither of which is
camera motion.

Input note: this game ignores a bare keypress - a left mouse click must precede it,
and the effect does not persist (see dev-archive/tools/awkeys.py). The capture step
clicks once high in the window and then holds W for the whole burst, which is a single
key-down and therefore needs a single click.
"""
import ctypes
import ctypes.wintypes as w
import glob
import importlib.util
import os
import sys
import time

TOOLKIT_CANDIDATES = [
    r"D:\claude video game stuff\github-backups\flat-to-vr-RE-toolkit\tools\game-harness.py",
    r"C:\Users\TD3KX\github-backups\flat-to-vr-RE-toolkit\tools\game-harness.py",
]

BAND = (80, 360)      # upper band, in 720p pixels: sky / treeline / far field
SEARCH = 24           # +/- px searched for the vertical shift


def _toolkit():
    override = os.environ.get("AWBOB_TOOLKIT")
    for c in ([override] if override else TOOLKIT_CANDIDATES):
        if c and os.path.exists(c):
            return c
    raise SystemExit("game-harness.py not found; set AWBOB_TOOLKIT")


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


def _find_window(u):
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


def capture(outdir, frames):
    spec = importlib.util.spec_from_file_location("harness", _toolkit())
    H = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(H)
    u = ctypes.windll.user32

    def send(i):
        u.SendInput(1, ctypes.byref(i), ctypes.sizeof(INPUT))

    hwnd = _find_window(u)
    u.SetForegroundWindow(hwnd)
    time.sleep(0.3)
    r = w.RECT()
    u.GetWindowRect(hwnd, ctypes.byref(r))
    # click high in the window: the menu list lives in the lower third and a click
    # there would select an item
    u.SetCursorPos(int((r.left + r.right) / 2), int(r.top + (r.bottom - r.top) * 0.15))
    time.sleep(0.2)
    for f in (0x0002, 0x0004):
        send(INPUT(0, _U(mi=MI(0, 0, 0, f, 0, None))))
        time.sleep(0.06)
    time.sleep(0.3)

    os.makedirs(outdir, exist_ok=True)
    send(INPUT(1, _U(ki=KI(0x57, 0, 0, 0, None))))          # W down
    try:
        for i in range(frames):
            H.grab(hwnd).save(os.path.join(outdir, "walk%02d.png" % i))
    finally:
        send(INPUT(1, _U(ki=KI(0x57, 0, 0x0002, 0, None))))  # W up
    print("captured %d frames while walking -> %s" % (frames, outdir))


def _shift(a, b, rng=SEARCH):
    import numpy as np
    a = a[BAND[0]:BAND[1]]
    b = b[BAND[0]:BAND[1]]
    a = a - a.mean()
    best = (0, -2.0)
    for d in range(-rng, rng + 1):
        bb = np.roll(b, d, axis=0)
        c = bb - bb.mean()
        den = (np.sqrt((a * a).sum()) * np.sqrt((c * c).sum()))
        if den <= 0:
            continue
        r = float((a * c).sum() / den)
        if r > best[1]:
            best = (d, r)
    return best[0]


def measure(outdir):
    from PIL import Image
    import numpy as np

    fs = sorted(glob.glob(os.path.join(outdir, "walk*.png")))
    if len(fs) < 3:
        raise SystemExit("need at least 3 frames in " + outdir)
    ims = [np.asarray(Image.open(f).convert("L"), dtype=np.float32) for f in fs]

    print("frames: %d   band: rows %d-%d   search: +/-%d px" % (len(ims), BAND[0], BAND[1], SEARCH))
    print()

    print("GUARD 1 - were the frames actually changing?")
    deltas = [float(np.abs(ims[i + 1] - ims[i]).mean()) for i in range(len(ims) - 1)]
    print("  frame-to-frame mean |luma delta|: min %.2f  max %.2f" % (min(deltas), max(deltas)))
    print("  %s" % ("OK - the game was rendering and the character was moving"
                    if min(deltas) > 0.5 else
                    "!! frames are nearly identical - the capture outran the frame rate; the "
                    "shift numbers below mean nothing"))
    print()

    print("GUARD 2 - can the estimator see a shift at all?")
    ok = True
    for truth in (-8, -3, -1, 1, 3, 8):
        got = _shift(ims[0], np.roll(ims[0], truth, axis=0))
        if abs(got) != abs(truth):
            ok = False
        print("    injected %+d px -> recovered %+d px (magnitude %s)"
              % (truth, got, "OK" if abs(got) == abs(truth) else "WRONG"))
    print("  %s" % ("OK - a real shift would have been detected, so a null is a null"
                    if ok else "!! estimator is blind; a null below proves nothing"))
    print()

    seq = [_shift(ims[i], ims[i + 1]) for i in range(len(ims) - 1)]
    print("RESULT - per-frame vertical camera shift (px): %s" % seq)
    print("  mean |dy| = %.2f px   max |dy| = %d px"
          % (sum(abs(x) for x in seq) / len(seq), max(abs(x) for x in seq)))
    print()
    print("This is ONE HALF of an A/B. It says nothing about any launch flag until the")
    print("other half - same save point, same command - has been run and compared.")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "capture":
        capture(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 14)
    elif cmd == "measure":
        measure(sys.argv[2])
    else:
        raise SystemExit("usage: awbob.py capture <outdir> [frames] | measure <outdir>")
