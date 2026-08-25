# 2026-08-25 — First look: an unusual, modular engine architecture

Session type: static file analysis (no game launch).

## What we know for sure

- **The renderer is Direct3D 9**, but this game is structured differently from every other
  project in this portfolio: instead of the main exe (`AlanWake.exe`) linking directly to
  `d3d9.dll`, it's a thin loader that pulls in nine separately-named module DLLs
  (`app_sf_Win32.dll`, `physics_sf_Win32.dll`, `d3d_sf_Win32.dll`, `renderer_sf_Win32.dll`,
  and others), one per engine subsystem. The actual D3D9 device creation happens inside
  `d3d_sf_Win32.dll`, and it's looked up dynamically at runtime rather than being a fixed
  dependency — with its own graceful error-handling path if that lookup ever fails.
- **The engine is Remedy's own proprietary tech** ("Remedy Entertainment" confirmed directly
  in the exe) — the predecessor to their later, publicly-named Northlight engine.
- **No DRM found.**
- **A real console/cheat system exists** — actual cheat command names are visible directly in
  the binary (`cheat_receive_flashlight`, `cheat_unlock_levels`, etc.), though how to open the
  console itself in-game isn't confirmed yet.

## Why the modular structure matters

We double-checked, carefully, for any other D3D9 functions this game might need beyond
`Direct3DCreate9` — a real lesson from Alice: Madness Returns, whose exe unexpectedly needed a
second export we hadn't planned for and which broke the game outright on the first try. Alan
Wake only ever asks for `Direct3DCreate9`, and because it's looked up dynamically (not a hard
requirement baked into the exe at load time), even a missing export here should fail more
gracefully than Alice's case did.

## What's next

A `d3d9.dll` proxy DLL (same direct-proxy pattern as this portfolio's other D3D9 titles) is the
natural M0 injection foothold.

One honest gap: no public-research sweep has happened for this project yet.

Full technical detail: `alan-wake-vr-dev-archive`, `recon/2026-08-25-m0-static-recon/`.
