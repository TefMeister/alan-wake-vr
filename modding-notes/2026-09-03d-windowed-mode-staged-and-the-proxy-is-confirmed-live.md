# 2026-09-03d (`/lm`, dev PC, live) — the M0 proxy IS reaching gameplay; windowed mode staged; a real focus-loss hazard found twice

User launched Alan Wake and handed off. Session covered the board's step-zero question (does
the deployed proxy still let the game start), a user request to switch to windowed mode, and an
attempted live verification of `g_mViewToClip`'s handedness that did not complete.

---

## 1. ✅ ANSWERED — the M0 proxy DOES reach gameplay. The recorded "live-verified" status was right.

`[verified-live 2026-09-03]` The proxy log for this launch shows the same fast
load/unload cycle recorded on 2026-08-25 (`Direct3DCreate9` returns a valid pointer, DLL unloads
~144 ms later) — but this time a screenshot taken seconds later shows Alan Wake standing on the
foggy road outside Cauldron Lake with a live HUD ("Get to the lighthouse" objective, flashlight
battery dial), confirmed rendering via a 4-sample frame-delta check (~1.0-1.6/frame, non-zero).

**This closes the open question from `dev-archive/recon/2026-09-03-proxy-startup-question/`.**
The fast `d3d9.dll` load/unload is NOT the main render device's lifecycle — it is very likely a
capability probe the engine performs early (creates a throwaway `IDirect3D9`, queries something,
tears it down), separate from whatever code path creates the real, persistent device. Our proxy's
`Direct3DCreate9` hook only sees that first, short-lived call; it does not see a second one for the
real device. **Where the real device actually gets its `IDirect3D9` object from is now the open
question** — worth a `[PD]` static look (is there a second, unhooked path to the system d3d9.dll,
or does the engine cache/reuse the one pointer from that first call for the whole session?).

## 2. ✅ Windowed mode — staged via `resolution.xml`, applies on next launch

`~/Documents/Remedy/AlanWake/resolution.xml` (backed up to `resolution.xml.bak-2026-09-03`) had
`<fullscreen value="1"/>`; changed to `<fullscreen value="0"/>` `[verified-live 2026-09-03]`,
byte-for-byte otherwise, CRLF line endings preserved.

**This is a config file the game reads, not a live setting** — this session's already-running
instance stayed fullscreen throughout; it takes effect on the **next launch**.

## 3. ⚠️ A real, twice-reproduced hazard: ANY external focus-steal auto-minimizes this game

`[verified-live 2026-09-03, n=2]` The window runs D3D9 **exclusive fullscreen**
(`resolution.xml`'s `fullscreen=1`, matching), and its `GetWindowRect` reports the Windows
minimized-window sentinel `(-32000,-32000)-(-31840,-31972)`, confirmed via `IsIconic()==True`,
**twice**, from two unrelated causes:

1. Sending `Alt+Enter` (the conventional D3D9 windowed-toggle key combo) — the `ALT` key alone
   generates `WM_SYSKEYDOWN`, which this build appears to treat as "losing exclusive focus" and
   auto-minimizes rather than toggling mode.
2. Launching `x32dbg.exe`'s GUI window nearby — just having another window take the foreground
   momentarily triggered the same auto-minimize, even though no debugger ever attached.

**Both times fully recoverable**, with no lasting effect on the running game: `ShowWindow(hwnd,
SW_RESTORE)` + `SetForegroundWindow` immediately restored the window to `(0,0)-(1920,1080)` and
rendering resumed exactly where it left off (same scene, same HUD, same character position).

**Practical consequence:** do not send `Alt+Enter` to this game live, and expect that alt-tabbing,
opening another app's window, or attaching any external tool will minimize it. Always check
`IsIconic()` before concluding a capture failure means the game crashed — `SW_RESTORE` is the fix,
not `taskkill`.

## 4. ⚠️ CORRECTION, same session: the close was NOT clean — a dump was written

I initially reported the session-end `WM_CLOSE` as a graceful close because the process left
`tasklist` within 4 seconds with no hang. **That was not sufficient evidence and the conclusion was
wrong.** A new crash dump appeared immediately after:
`AlanWake_3372514_20260903-192042_3031040.dmp`, **15,718 bytes**, timestamped 19:20:43 — i.e. right
at the close. `[verified-live 2026-09-03]`

⚠️ **Dump CONTENTS were never copied anywhere** — a minidump is a snapshot of the process's own
memory (compiled game code, possibly loaded assets), which is exactly what the never-commit-game-
files rule protects; only size/timestamp metadata is recorded here.

**One thing softens this finding rather than making it alarming:** that exact size, 15,718 bytes,
also appears on **one** of the nine pre-existing 2026-08-25 dumps
(`AlanWake_3372514_20260825-161801_3031040.dmp`) — the other eight from that day range 216–254 KB,
visibly a different (larger) kind of fault. An identical, small, consistent dump size on two
otherwise-unrelated occasions suggests **this may be a specific, repeatable, likely-benign
exception the game's own shutdown path always trips** — not something distinguishing about
`WM_CLOSE` versus any other termination. It is not established either way this session.
`[hypothesis]`

**What this means for future sessions:** don't claim a close was "graceful" from process-exit speed
alone — check for a fresh dump. A properly-identified in-game quit route (through a menu, once
found) would be worth having and is recorded as untested: `Esc` was tried once mid-session and
produced no visible menu, but the capture happened to land on a transition frame — genuinely
inconclusive, not a "no menu" finding.

## 5. ❌ NOT completed — the `g_mViewToClip` handedness/convention falsification test

Blocked. Two routes were available and neither worked out this session:

- **A purpose-built hook** (intercepting `SetVertexShaderConstantF` at register `c0`) needs new
  proxy code, a build, and a relaunch — real dev work, not doable against the already-running
  instance.
- **x64dbg**, which should have been able to attach live and read the constant register file at a
  breakpoint, could not be used: the MCP bridge never registered a session
  (`list_sessions` returned empty after `start_session` reported a timeout, though `x32dbg.exe`
  did launch and run standalone). Six pre-existing, apparently-stale `x64dbg-automate-mcp.exe`
  helper processes were found already running on this machine before this attempt, suggesting the
  bridge is in a broken state estate-wide, not something specific to this session. The orphaned
  `x32dbg.exe` this session started (which never attached to anything) was closed cleanly;
  the pre-existing stale helper processes were left alone rather than killed blind.

**This is still the single most important open question for §6** (dossier, unchanged): whether
`clip.w = view.z` and `row3 = [0,0,1,0]` hold, which the whole `stereo.c` derivation assumes and
has never measured. It needs either the x64dbg bridge fixed, or a minimal read-only hook DLL built
and deployed on a future launch.

## 6. What is NOT established

- Where the real render device's `IDirect3D9`/`IDirect3DDevice9` actually comes from (§1).
- Whether `Esc` (or any key) opens an in-game menu — one inconclusive attempt only.
- Whether the 15,718-byte dump signature is truly benign or coincidental (§4) — `n=2`, not proven.
- The `g_mViewToClip` handedness/convention (§5) — still open, unchanged from before this session.
- Anything about VR, stereo, or comfort — no rendering changes were made or tested this session.
