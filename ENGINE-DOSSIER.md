# Engine Dossier — Alan Wake (Remedy proprietary in-house engine)

> One consolidated, living reference for this game's engine, filled in as the
> `PLAYBOOK.md` phases are worked. Chronological blow-by-blow belongs in the
> `-dev-archive` / `-modding-notes` repos; this file is the *distilled current
> truth*. Update it whenever a fact changes; correct false leads in place.

**Status:** M0 done — static recon complete, no external research yet (flagged as a gap). No DRM found. Unusual, modular DLL architecture confirmed — matters for injection planning (see §4). · **VR-readiness verdict:** TBD, no environmental blockers found

## 1. Identity
- Game / build / version: Alan Wake (2010, Remedy Entertainment, published by Microsoft Game Studios/Remedy), Steam release (`AlanWake.exe`, 32-bit).
- Platform & store; unofficial port? (extra fragility/legal notes): PC via Steam. Not a known unofficial port. **Steamworks is directly, statically linked into the main exe** (`steam_api.dll` in the exe's own import table) — unlike Burnout Paradise, no separate launcher-handoff pattern expected.
- Legitimacy: owned copy confirmed.

## 2. Engine lineage
- Family / base engine and how it was modified: Remedy Entertainment's own proprietary in-house engine for this title — confirmed via the literal string `Remedy Entertainment` in the exe — a predecessor to the studio's later, publicly-named **Northlight** engine (which debuted with *Quantum Break*, 2016). This earlier engine has no confirmed public name. **Distinctive, unusually modular architecture (confirmed via imports, see §3): the main exe is a thin loader that dynamically pulls in separately-named module DLLs** — `app_sf_Win32.dll`, `physics_sf_Win32.dll`, `grph_sf_Win32.dll`, `d3d_sf_Win32.dll`, `snd_sf_Win32.dll`, `rl_sf_Win32.dll` ("resource loader"? unconfirmed), `ai_sf_Win32.dll`, `loc_sf_Win32.dll` (localization), `renderer_sf_Win32.dll` — one per engine subsystem (`_sf_` likely "sub-framework" or similar, unconfirmed). This is meaningfully different from every other project in this portfolio, where the renderer/D3D calls live directly in (or are statically imported by) the main exe.
- Middleware (animation, audio, physics, megatexture, CUDA, etc.): **Bink** (`binkw32.dll`, video — same middleware as Mad Max/Prince of Persia/Alice). Compiled with **VS2008** (`MSVCP90.dll`/`MSVCR90.dll`).
- Distinctive file formats / build tags / symbol naming: not yet investigated.

## 3. Binary & memory
- 32/64-bit, size, module base, ASLR behaviour (stable base? relocations?): **32-bit** (PE32, `coff-i386`). `AlanWake.exe` itself is unusually small (only 4 sections: `.text`/`.rdata`/`.data`/`.rsrc`) — consistent with it being a thin loader/orchestrator, with the real engine code living in the separate `_sf_Win32.dll` modules.
- Renderer API (D3D11/12, DXGI, GL, Vulkan) with evidence: **Direct3D 9 confirmed, but NOT statically imported anywhere.** `d3d9.dll` does not appear in the static import table of `AlanWake.exe` or any of its module DLLs (checked all ten). Instead, `d3d_sf_Win32.dll` contains the literal strings `Direct3DCreate9` and `Direct3DCreate failed` side by side — the classic pattern of a **dynamic `LoadLibraryA("d3d9.dll")` + `GetProcAddress(..., "Direct3DCreate9")`** call with a graceful failure path, not a static PE import. **Confirmed only one D3D9 function is looked up this way** (`Direct3DCreate9` — no `D3DPERF_*` or other D3D9 exports referenced anywhere across all ten binaries, checked specifically after the lesson learned on Alice: Madness Returns). Practical upshot: a same-named `d3d9.dll` proxy placed in the game's root directory should still work (Windows' `LoadLibraryA` follows the same app-directory-first search order as static imports), and since this is a dynamic lookup rather than a static import, a missing export here would fail *gracefully* (the game's own logged "Direct3DCreate failed" error path) rather than silently killing the whole process the way Alice's missing static import did.
- Developer console / cvar system present? how opened?: **A real console and cheat system both appear to exist.** Strings found: `?dumpToConsole@GameObject@r@@UAEXXZ` (a C++-mangled `dumpToConsole` method), `"Dump to console"`, and real cheat command names: `cheat_receive_flashlight`, `cheat_receive_weapons`, `cheat_unlock_levels`, `cheat_unlock_nightmare`. How the console itself is opened in-game is not yet confirmed.

## 4. DRM / anti-debug & injection foothold
- DRM (CEG/Denuvo/GOG/none); launch-time-debugger behaviour: **No DRM found.** Zero hits for Denuvo, SecuROM, StarForce, or any activation/launcher-handoff string. Not yet tested live.
- Attach workflow that works: not yet tested live, but no static evidence predicts a block.
- Injection vector that works (proxy DLL name / injector / framework): not yet tested live. **Plan: a from-scratch `d3d9.dll` proxy**, matching this portfolio's Psychonauts/Prince of Persia/Alice precedent — exporting only `Direct3DCreate9` should be sufficient here (unlike Alice, which needed a second export; see §3 for why this game's dynamic-lookup architecture makes that specific failure mode less likely anyway).

## 5. Threading & frame structure
- Immediate context only, or deferred contexts + command lists?:
- Which thread(s) do what; render-thread name(s):
- One-frame walkthrough (record → replay → present):

## 6. Camera & projection delivery (the crucial section)
- How the world transform reaches the GPU (shared VP buffer / per-draw MVP /
  other), with **shader-reflection / disassembly evidence**:
- Exact constant-buffer slot, parameter name(s), byte offset(s), layout,
  handedness, row/column convention:
- Where projection `P` / FOV comes from:
- The per-eye override maths (`K_eye = …`):

## 7. Constant-buffer fill mechanism
- Map/DISCARD ring / UpdateSubresource / D3D11.1 offset / **persistent map +
  memcpy** (trap):
- Can source contents be read cheaply (captured CPU pointer) or need staging
  read-back?:
- The chosen override patch point and why:

## 8. Pass inventory (by render target)
- Main scene (res/formats):
- Shadow passes (depth-only sizes):
- Post / AA chain (SMAA/TAA/motion vectors; downscale sizes):
- UI / HUD (how it's kept separate):

## 9. cvar / console cheat sheet
| command / cvar | effect | use |
|---|---|---|
| `cheat_receive_flashlight` | grants the flashlight (core gameplay mechanic) | found via exe strings; console-access method unconfirmed |
| `cheat_receive_weapons` | grants weapons | same source |
| `cheat_unlock_levels` | unlocks levels | same source — useful for the autonomous harness recipe (§10), jumping straight to a target scene |
| `cheat_unlock_nightmare` | unlocks Nightmare difficulty | same source |

## 10. Autonomous harness recipe (this game)
- Launch to a known scene (commands used):
- In-process input / camera drive method that worked:
- Frame-capture method; where images land:

## 11. Dead ends & false leads (save future time)
- <what looked true but wasn't, and why>

## 12. Open risks toward the North Star
- <what could still block VR + head tracking>
