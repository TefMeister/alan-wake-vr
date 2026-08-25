# Engine Dossier — Alan Wake (Remedy proprietary in-house engine)

> One consolidated, living reference for this game's engine, filled in as the
> `PLAYBOOK.md` phases are worked. Chronological blow-by-blow belongs in the
> `-dev-archive` / `-modding-notes` repos; this file is the *distilled current
> truth*. Update it whenever a fact changes; correct false leads in place.

**Status:** M0 done — static recon complete, external research folded in. No DRM found (GFWL history checked specifically, confirmed absent). Unusual, modular DLL architecture confirmed — matters for injection planning (see §4). **Two real Remedy-shipped dev tools exist**: `-freecamera` and `-developermenu` launch flags, plus reported native NVIDIA 3D Vision support with live separation hotkeys. · **VR-readiness verdict:** TBD, no environmental blockers found, and a real chance the native stereo support (once verified live) shortcuts §6's hardest question — vorpX signal alone is weaker here than other fronts (Cinema mode only), so the native-stereo lead matters more for this project specifically. A from-scratch `d3d9.dll` proxy is built and **deployed** (`alan-wake-vr-staging/proxy-d3d9/`), not yet tested against a live launch.

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
- DRM (CEG/Denuvo/GOG/none); launch-time-debugger behaviour: **No DRM found — checked specifically, not just assumed clean.** Zero hits for Denuvo, SecuROM, StarForce, or any activation/launcher-handoff string. **The original 2010/2012 PC release shipped on Games for Windows Live (GFWL)** (external-research, 2026-08-25), Microsoft's now-defunct online-activation/achievement platform — no precisely dated confirmation of when the Steam build was migrated off it was found publicly (unlike the clean, dated Jan-2022-patch stories for Prince of Persia 2008 and Alice: Madness Returns), so this was worth checking directly rather than assuming. **Follow-up check on the actually-installed Steam build: zero `xlive`/GFWL-related files anywhere in the install directory, and zero `xlive`/GFWL strings across all ten binaries (the exe + all nine module DLLs)** — this build appears to have been fully migrated off GFWL. Not yet tested live.
- Attach workflow that works: not yet tested live, but no static evidence predicts a block.
- Injection vector that works (proxy DLL name / injector / framework): not yet tested live. **Plan: a from-scratch `d3d9.dll` proxy**, matching this portfolio's Psychonauts/Prince of Persia/Alice precedent — exporting only `Direct3DCreate9` should be sufficient here (unlike Alice, which needed a second export; see §3 for why this game's dynamic-lookup architecture makes that specific failure mode less likely anyway).

## 5. Threading & frame structure
- Immediate context only, or deferred contexts + command lists?:
- Which thread(s) do what; render-thread name(s):
- One-frame walkthrough (record → replay → present):

## 6. Camera & projection delivery (the crucial section)
- How the world transform reaches the GPU (shared VP buffer / per-draw MVP /
  other), with **shader-reflection / disassembly evidence**: (D3D9 note: shader constant registers, not D3D11-style cbuffers — same caveat as the other D3D9 titles in this portfolio.)
- Exact constant-buffer slot, parameter name(s), byte offset(s), layout,
  handedness, row/column convention:
- Where projection `P` / FOV comes from:
- The per-eye override maths (`K_eye = …`):
- **Real, dev-shipped tools to check before any from-scratch work (external-research, 2026-08-25):**
  1. **`-freecamera`** (Steam launch option, added in patch v1.04) — a genuine, official Remedy free-camera tool. In-game: press the right thumbstick to toggle (controller required, no confirmed keyboard/mouse equivalent); left stick moves, right stick rotates, LT/RT scale speed, LB/RB move vertically, X/B cycle speed presets. A safe, zero-injection-risk way to explore the world and observe camera behavior before any hooking work — same category of find as Psychonauts' dormant debug menu elsewhere in this portfolio.
  2. **`-developermenu`** (launch option) — adds a "Developer Menu" to the main menu. Confirmed scope so far: episode/difficulty selection and max ammo/consumables — **not confirmed to include camera/rendering tools**, don't assume further reach without checking live.
  3. **Real, shipped NVIDIA 3D Vision support** — per an NVIDIA forum discussion (version 1.06.18.1326), later game versions are reported "almost 3D Vision ready out of the box" (no HelixMod needed), with **live in-game separation adjustment via `Ctrl+F3`/`Ctrl+F4`** (reported working value: 12 "bars," ~20%) and FOV set via Options/Controls. An older HelixMod fix exists for earlier builds specifically to fix light-clipping. **A working, in-game-adjustable stereo separation control implies the per-eye offset mechanism is already live and reachable, not buried behind anything exotic** — same pattern as Alice: Madness Returns' native stereo find. **Concrete next step: check the installed version against 1.06.18.1326 and try `Ctrl+F3`/`Ctrl+F4` live early** — a fast, zero-risk way to confirm native stereo support before independent shader-reflection work. Not yet confirmed on the actually-installed build.

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
| `-freecamera` (launch option) | enables a real free-camera tool (right-thumbstick toggle, controller-driven) | external-research; the single most useful entry here for §6/§10 |
| `-developermenu` (launch option) | adds a Developer Menu (episode/difficulty/ammo, unconfirmed if more) | external-research |
| `-w <n>` / `-h <n>` / `-window` / `-novsync` / `-showfps` / `-sensscale <n>` / `-locale=xx` / `-forcesurround` / `-forcestereo` | resolution/windowed/vsync/FPS-display/mouse-sensitivity/locale/audio-channel flags | external-research (Fandom wiki + "The Sudden Stop" fan reference); `-window`/`-novsync`/`-showfps` useful for live investigation regardless of camera work |
| `Ctrl+F3` / `Ctrl+F4` | live in-game stereo separation adjustment (reported working value: 12 "bars," ~20%) | external-research, NVIDIA forum — untested on this installed build, see §6 |

## 10. Autonomous harness recipe (this game)
- Launch to a known scene (commands used): candidate — `-developermenu` for episode select, plus the general `-w`/`-h`/`-window`/`-novsync` flags for a controlled test environment (see §9).
- In-process input / camera drive method that worked: candidate — `-freecamera` (see §6) is a real, official free-camera tool; worth using for black-box observation before any hooking work, though it's controller-driven with no confirmed keyboard/mouse equivalent.
- Frame-capture method; where images land: not yet investigated.

## 11. Dead ends & false leads (save future time)
- <what looked true but wasn't, and why>

## 12. Open risks toward the North Star
- **vorpX feasibility signal is real but weaker than this portfolio's stronger fronts (external-research, 2026-08-25): only confirmed in Cinema mode** (vorpX's lowest-fidelity mode — a flat virtual screen in a virtual room, no stereoscopic depth reconstruction, no head-tracked world-relative camera) for the *original* 2010/2012 release specifically. No confirmation of Geometry 3D or full head-tracked/FullVR mode for this exact build (separate vorpX threads exist for Alan Wake Remastered and Alan Wake 2 — different games/builds, not to be conflated with this project's target). This is meaningfully weaker than Mad Max (Geometry 3D + head tracking) or Alice: Madness Returns (Geometry 3D + motion-controller emulation) — the native 3D Vision support (§6) is this project's actually-strongest evidence that per-eye camera work is tractable here, not the vorpX result.
