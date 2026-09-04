# Free the real `d3d9.dll` on detach, or the game's reload bypasses the proxy — ReShade's Alan Wake fix is exactly this one line

Filed by: `/gr`, 2026-09-04
Topic: `external-research/topics/2026-09-04-the-proxy-is-bypassed-on-reload-because-the-system-d3d9-is-never-freed.md`
Dossier sections: §3 (dynamic `LoadLibraryA("d3d9.dll")`), §4 (injection foothold, the "CONFIRMED BROKEN" `install_createdevice_hook`); the board's `[PD]` row *"where does the REAL render device's `IDirect3D9` come from?"*

- **The game probes and unloads, then loads `d3d9.dll` again for real.** Every logged run: proxy loaded → `Direct3DCreate9` succeeds → proxy unloaded 6 ms later. `[measured, n=3 launches]`
- **Our proxy loads `C:\Windows\system32\d3d9.dll` by full path and never `FreeLibrary`s it** (`proxy.c` `load_real_dll()`; `DLL_PROCESS_DETACH` only closes the log). The system DLL therefore stays resident after we are gone. `[inferred-static 2026-09-04]`
- **Windows then hands the game's second `LoadLibraryA("d3d9.dll")` the resident system copy** — Microsoft's `LoadLibrary` remarks: *"When no path is specified, the function searches for loaded modules whose base name matches … If the name matches, the load succeeds. Otherwise, the function searches for the file."* The game folder is never searched again; the real device is created on the real runtime; the proxy sees nothing. `[reported, first-party]`
- **ReShade needed the identical fix for this game:** commit `74347b91d` (2019-12-19, 4.5.2 "Fixed hooking in Alan Wake") — *"Free reference to the module loaded for export hooks (this is necessary for Alan Wake to work)"*, i.e. `FreeLibrary` on the system-DLL handle at uninstall. `[reported, primary source]`
- **Fix, `[PD]`:** `FreeLibrary(real_d3d9)` in `DLL_PROCESS_DETACH`. Expected log after: a **second** "proxy loaded" block in the same PID, followed by `CreateDevice`. If no second block appears, something else pins the system DLL — enumerate modules at detach. Then **re-test `install_createdevice_hook()`**: its "CONFIRMED BROKEN" verdict was reached against a proxy that only ever saw the probe object.

Suggested dossier change: answer §3's "graceful failure path" note and the board row with the probe-then-reload sequence and the base-name rule; add the `FreeLibrary` requirement to §4's foothold description; downgrade the `install_createdevice_hook` "CONFIRMED BROKEN" line to "untested against the real device — re-test after the detach fix".
