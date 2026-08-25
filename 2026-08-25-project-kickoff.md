# 2026-08-25 — Project kickoff

Started today. Game: **Alan Wake** (2010, Remedy Entertainment, published by
Microsoft Game Studios / Remedy). Installed via Steam (`AlanWake.exe`).

Engine: Remedy's own proprietary in-house engine for this title. This is a
predecessor to the studio's later, publicly-named **Northlight** engine
(which debuted with *Quantum Break* in 2016) — this earlier engine has no
widely-used public name. Visible module DLLs at install (`renderer_sf_Win32.dll`,
`physics_sf_Win32.dll`, `grph_sf_Win32.dll`, `ai_sf_Win32.dll`, `dm_sf_Win32.dll`,
`rl_sf_Win32.dll`, `loc_sf_Win32.dll`, `snd_sf_Win32.dll`) suggest a modular
subsystem split (renderer / physics / graphics / AI / data management /
resource loading / localization / sound), each compiled as its own DLL —
worth confirming and naming properly once engine research actually begins.

This is the **first look** phase: the six-repo standard has just been
scaffolded per [CONVENTIONS.md](https://github.com/TefMeister/claude-memory/blob/main/CONVENTIONS.md)
in the cross-machine brain repo. No reverse-engineering has started yet —
that begins in a future session, following the
[PLAYBOOK.md](https://github.com/TefMeister/alan-wake-vr-engine-research/blob/main/PLAYBOOK.md)
Phase 0 groundwork (confirm legitimacy, toolchain, first binary read, engine
lineage, DRM/anti-debug recon).
