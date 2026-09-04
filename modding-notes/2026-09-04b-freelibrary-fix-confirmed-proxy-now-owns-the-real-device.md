# 2026-09-04b (`/lm`, dev PC, FULLY AUTONOMOUS) — CONFIRMED: the FreeLibrary fix works, the reload bypass is dead, and the proxy now owns the REAL render device

**One launch, the headline `[FLAT]` row answered decisively.** The user launched from Steam
(already windowed); Claude read the log, drove title → main menu, confirmed the device chain holds,
and quit through the game's own Quit menu. Evidence:
`dev-archive/recon/2026-09-04-freelibrary-fix-proxy-now-in-real-device-chain/`.

---

## 1. The result

For weeks the proxy saw only a throwaway probe device and never the device Alan Wake actually
renders with — because our proxy kept the system `d3d9.dll` resident, so the game's second
`LoadLibraryA("d3d9.dll")` matched the system copy by base name and never searched the game folder
(dossier §4). The 2026-09-04 `/pd` fix — `FreeLibrary(real_d3d9)` at `DLL_PROCESS_DETACH` when
`lpReserved == NULL` — was built and deployed but never run. This launch ran it, and it works.

The log, one PID (5372):

```
=== proxy d3d9.dll loaded, PID=5372 ===
real d3d9.dll loaded ...; Direct3DCreate9=71434B20
Direct3DCreate9 called: SDKVersion=0x20
=== proxy d3d9.dll unloading (reserved=00000000, explicit FreeLibrary) ===
releasing the system d3d9.dll reference so the game's next LoadLibraryA("d3d9.dll") searches the game folder and finds us again
=== proxy d3d9.dll loaded, PID=5372 ===          <-- the SECOND load now finds US
real d3d9.dll loaded ...; Direct3DCreate9=71434B20
Direct3DCreate9 called: SDKVersion=0x20
  -> returned 038DF438
```

`[verified-live 2026-09-04, n=1 launch]`
- The probe load unloaded via **explicit FreeLibrary** (our new detach code, `reserved=00000000`),
  and logged the release of the system reference.
- A **second "proxy loaded" block appeared in the same PID**, and it **never unloaded again** — PID
  5372 has two loads and exactly one unload (the probe's).
- The **title screen and the main menu both rendered through this resident second load** (capture
  deltas > 0 across both). So the game's real device was created on our wrapped `Direct3DCreate9`,
  not the system runtime.

## 2. Why it matters

This is the project's central unblock. Every device-level plan (M1/M2) needs the proxy to be in the
real render chain, and until today it never was — the "camera delivery" work (dossier §6) was all
static because there was no live device to read. Now there is. The reachable next steps:

- **The CreateDevice hook re-enable** (`install_createdevice_hook()`), which the board gated strictly
  *after* this test — now unblocked. It needs the code re-enabled (a rebuild) and its own launch.
- **A live view-to-clip matrix dump** — the handedness falsification (dossier §6, `stereo.c`
  assumes left-handed `clip.w = view.z`, `row3 = [0,0,1,0]`). The current proxy logs only
  `Direct3DCreate9`; reading `g_mViewToClip` from a live frame now needs a dump path built into the
  proxy (intercept the device's constant uploads), which is newly worth building because we finally
  own the device.

## 3. What is NOT established

- **Gameplay** was not loaded — the test only needed the title and menu (both confirm the device
  chain). Whether anything breaks entering a level is untested, but there is no reason to expect it.
- **The loader-lock caveat did not bite:** no hang at the probe unload, the second load, or exit
  (dossier §4 flagged `FreeLibrary`-in-`DllMain` as the suspect if a future launch hangs). Clean
  this launch; `n=1`.
- **No device-level calls are logged yet** — the proxy logs the factory call only, so "we own the
  device" rests on the resident second load + the title/menu rendering through it, not on a logged
  `CreateDevice`/`Present`. A dump path would make it explicit.

## 4. Automation on Alan Wake, scored (§5a)

1. **Menu → gameplay: partial** — title ("Press any key to play", takes Space) → main menu
   (Continue Game / New Game / Episodes / Options / Extras / Quit). Actual level load not exercised.
2. **Commands: N/A this session** — the proxy log is the readout; no console used.
3. **Character + camera: not exercised.**
4. **Self-close: proven** — main menu → Quit (Down x5 from Continue Game) → "Are you sure you want
   to Quit?" → Enter accepts. Process gone. New `process_exit` route recorded in the profile.

## 5. Gate

The headline `[FLAT]` row is done. Newly unblocked and next:
- `[PD]` re-enable `install_createdevice_hook()` (rebuild), then `[FLAT]` a launch of its own to
  confirm the CreateDevice interception now survives (its old "CONFIRMED BROKEN" was a lifetime bug,
  disproved 2026-09-04).
- `[PD]` build a live `g_mViewToClip` dump into the proxy (now that we own the device), then
  `[FLAT]` read it to confirm/falsify the left-handed projection assumption in `stereo.c`.
Nothing needs the headset.
