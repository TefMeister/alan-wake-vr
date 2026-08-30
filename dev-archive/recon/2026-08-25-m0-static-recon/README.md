# M0 static recon — 2026-08-25

Pure file-based static analysis of `AlanWake.exe` and its module DLLs — no process was
launched or attached to. Tools: `file`, `objdump`/`strings` (llvm-mingw, i686 target — 32-bit).

## PE header / sections (AlanWake.exe)
```
file format coff-i386
PE32 executable for MS Windows 5.00 (GUI), Intel i386, 4 sections

Idx Name          Size     VMA      Type
  0 .text         0022cfc7 00401000 TEXT
  1 .rdata        0006d1a0 0062e000 DATA
  2 .data         00021200 0069c000 DATA
  3 .rsrc         000286d8 00777000 DATA
```
Unusually small/simple — 4 sections, consistent with a thin loader.

## Import table (AlanWake.exe)
```
d3dx9_43.dll, binkw32.dll, steam_api.dll, KERNEL32.dll, USER32.dll, GDI32.dll, COMDLG32.dll,
SHELL32.dll, ole32.dll, XINPUT1_3.dll, app_sf_Win32.dll, physics_sf_Win32.dll,
grph_sf_Win32.dll, d3d_sf_Win32.dll, snd_sf_Win32.dll, rl_sf_Win32.dll, ai_sf_Win32.dll,
loc_sf_Win32.dll, renderer_sf_Win32.dll, MSVCP90.dll, MSVCR90.dll, dbghelp.dll
```
No direct `d3d9.dll` import — this exe imports its own set of `*_sf_Win32.dll` modules
instead, one per engine subsystem. `steam_api.dll` is a direct static import (Steamworks
built into the main exe, unlike Burnout Paradise).

## Where D3D9 actually gets loaded

Checked all ten binaries (`AlanWake.exe` + the nine `_sf_Win32.dll` modules) for a static
`d3d9.dll` import entry — **zero found anywhere**. Instead, `d3d_sf_Win32.dll` contains the
literal strings:
```
Direct3DCreate9
Direct3DCreate failed
```
side by side — the classic `LoadLibraryA("d3d9.dll")` + `GetProcAddress(..., "Direct3DCreate9")`
dynamic-lookup pattern with a graceful failure/error-log path, not a static PE import.

**No other D3D9 exports referenced** — checked specifically for `D3DPERF_*` strings across all
ten binaries after the lesson learned on Alice: Madness Returns (whose exe needed a second,
non-obvious static import). Only `Direct3DCreate9` is looked up here.

## Renderer strings (d3d_sf_Win32.dll)
```
Direct3DCreate9
Direct3DCreate failed
D3DXCreateTexture, D3DXCreateTextureFromFileEx, D3DXCreateCubeTextureFromFileExA,
D3DXCreateVolumeTextureFromFileExA, D3DXCreateTextureFromFileInMemoryEx  (all from
  d3dx9_43.dll, a real static import of this module)
```

## Engine / developer identification strings
```
Remedy Entertainment
Remedy\
```

## Console / cheat strings
```
?dumpToConsole@GameObject@r@@UAEXXZ   (mangled C++ method name)
"Dump to console"
cheat_receive_flashlight
cheat_receive_weapons
cheat_unlock_levels
cheat_unlock_nightmare
```

## DRM search — all negative
```
denuvo / securom / starforce / link2ea / activation required -> no hits anywhere
```

## What this means for the project

D3D9 confirmed but loaded dynamically (not statically imported) from a separate module DLL —
a meaningfully different architecture from every other project in this portfolio, where the
renderer entry point lives directly in (or is statically imported by) the main exe. No DRM
found. A real console/cheat command system exists in the binary. Full synthesis in
`ENGINE-DOSSIER.md`.

## Gap noted, not a finding
No `/game-research` external-research sweep has run for this project yet.
