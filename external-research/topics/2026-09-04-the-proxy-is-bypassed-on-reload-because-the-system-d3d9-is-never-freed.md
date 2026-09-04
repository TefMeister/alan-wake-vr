# The proxy is bypassed on the reload because it never frees the system `d3d9.dll` — ReShade hit the same wall in this exact game and fixed it with one `FreeLibrary`

**Date:** 2026-09-04 · **Status:** 🆕 new · **Answers:** the board's `[PD]` row *"where does the
REAL render device's `IDirect3D9` come from?"*

## The row this addresses

> our proxy's hook only ever sees that one short-lived, throwaway-looking call, never a second one
> for the persistent device. Static look: a second unhooked path to the system `d3d9.dll`? the
> engine reusing the one returned pointer for the whole session?

Neither. The game does load `d3d9.dll` a second time, for real — and that second load resolves to
the **system** copy because our own proxy left it in memory.

## The evidence, in order

1. **The game probes and unloads.** Every run in `alanwake_vr_proxy_log` is the same three lines:
   proxy loaded → `Direct3DCreate9` returns a valid object → *6 ms later* the proxy unloads
   (`DLL_PROCESS_DETACH`), 131 ms after load. `[measured 2026-08-25 and 2026-09-03, n=3 launches]`
   A `FreeLibrary` that soon after a successful create is a capability probe, not a renderer.
2. **The proxy loads the real DLL by full path and never releases it.** `proxy.c`'s
   `load_real_dll()` calls `LoadLibraryA("C:\Windows\system32\d3d9.dll")`; `DllMain`'s
   `DLL_PROCESS_DETACH` closes the log and does nothing else — no `FreeLibrary(real_d3d9)`.
   `[inferred-static 2026-09-04, from the source]` So when the game frees *our* module, the system
   `d3d9.dll` stays mapped with a dangling reference count.
3. **Windows resolves a bare module name to whatever is already loaded under that name.** Microsoft's
   `LoadLibrary` remarks: *"When no path is specified, the function searches for loaded modules
   whose base name matches the base name of the module to be loaded. If the name matches, the load
   succeeds. Otherwise, the function searches for the file."* `[reported, first-party]` The game's
   renderer module calls `LoadLibraryA("d3d9.dll")` (the dossier's §3 string evidence). The loader
   finds the resident **system** `d3d9.dll`, returns it, never touches the game folder — and our
   proxy is never asked again. Gameplay then runs on the real runtime, which is why the game works
   and the log stops.
4. **ReShade fixed exactly this, for exactly this game.** Commit `74347b91d` (2019-12-19, shipped
   in 4.5.2 as *"Fixed hooking in Alan Wake"*) adds one thing: on hook uninstall, *"Free reference
   to the module loaded for export hooks (this is necessary for Alan Wake to work)"* —
   `FreeLibrary(s_export_module_handle)`. ReShade's export-hook path loads the system DLL by
   absolute path just as ours does; without releasing it, ReShade did not work in Alan Wake.
   `[reported 2026-09-04, primary source]`

The same fact explains why every other local wrapper is known to work on this title — Helix Mod's
3D Vision fix and ReShade both live in a `d3d9.dll` in the game folder and see the real device.
A "second unhooked path to the system DLL" does exist, but *we* create it.

## The fix — `[PD]`, one line, and one thing to verify after it

In `DllMain`, on `DLL_PROCESS_DETACH`, `FreeLibrary(real_d3d9)` before closing the log (and null
the pointer). With the reference dropped, the system DLL unloads together with the proxy, the
game's second `LoadLibraryA("d3d9.dll")` finds nothing resident, searches the game folder, and
loads the proxy again — this time for the device that matters. Expect the log to show a **second**
"proxy loaded" block in the same PID, then `CreateDevice`.

Two cautions:

- If anything *else* in the process holds the system `d3d9.dll` (an overlay that loaded it by
  path before the game's second call), the same bypass happens regardless of our fix. The log
  distinguishes the cases: no second load block → something else pins it; enumerate modules at
  detach to name it.
- The M0 build's `install_createdevice_hook()` is marked *"CONFIRMED BROKEN — DO NOT CALL"* in the
  source. That was diagnosed against a proxy that only ever saw the probe object. Re-test it after
  this change before trusting that verdict; it may have been a symptom of the same bypass.

## Sources

- [crosire/reshade commit 74347b91d — "Fix hooking in Alan Wake" (2019-12-19)](https://github.com/crosire/reshade/commit/74347b91d)
  and the [ReShade 4.5 release notes](https://reshade.me/releases/6048-4-5) (4.5.2: *"Fixed hooking
  in Alan Wake"*). Read online; nothing copied.
- [LoadLibraryA — Microsoft Learn, Remarks](https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibrarya)
  — the already-loaded-module rule and the per-process reference count.
- [Alan Wake care package (Nexus Mods)](https://www.nexusmods.com/alanwake/mods/9) — practical
  confirmation that a game-folder `d3d9.dll` (Helix) hosts the real device on this title.
- Our own `staging/alan-wake-vr/proxy-d3d9/src/proxy.c` and
  `dev-archive/recon/2026-09-03-proxy-startup-question/`.

## Cross-project note

Every proxy in the estate that loads its real DLL by system path and skips `FreeLibrary` on detach
(`alice-madness-returns-vr`, `prince-of-persia-2008-vr`, `manhunt-2003-vr`, `mad-max-vr`,
`burnout-paradise-vr` by a grep of `staging/`, `[inferred-static 2026-09-04]`) carries the same
latent bypass. It only bites where the game probes-and-reloads, which so far is Alan Wake alone —
but it costs one line to close everywhere. Filed to `flat-to-vr-cross-engine-research/inbox/`.
