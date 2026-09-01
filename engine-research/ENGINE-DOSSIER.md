# Engine Dossier — Alan Wake (Remedy proprietary in-house engine)

> One consolidated, living reference for this game's engine, filled in as the
> `PLAYBOOK.md` phases are worked. Chronological blow-by-blow belongs in the
> `-dev-archive` / `-modding-notes` repos; this file is the *distilled current
> truth*. Update it whenever a fact changes; correct false leads in place.

**Status:** M0 done — static recon complete, external research folded in. No DRM found (GFWL history checked specifically, confirmed absent). Unusual, modular DLL architecture confirmed — matters for injection planning (see §4). **Two real Remedy-shipped dev tools exist**: `-freecamera` and `-developermenu` launch flags, plus reported native NVIDIA 3D Vision support with live separation hotkeys. · **VR-readiness verdict:** TBD, no environmental blockers found, and a real chance the native stereo support (once verified live) shortcuts §6's hardest question — vorpX signal alone is weaker here than other fronts (Cinema mode only), so the native-stereo lead matters more for this project specifically. A from-scratch `d3d9.dll` proxy is built, **deployed, and live-verified** (2026-08-25, after a real diagnostic detour — see §4) — the game runs cleanly with it, no compatibility flags needed.

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
- Injection vector that works (proxy DLL name / injector / framework): **✅ LIVE-VERIFIED (2026-08-25), a from-scratch `d3d9.dll` proxy exporting only `Direct3DCreate9`**, matching this portfolio's Psychonauts/Prince of Persia/Alice precedent. **A real diagnostic detour along the way, worth recording precisely** (full story in `staging/alan-wake-vr/proxy-d3d9/README.md`): the plain proxy alone crashed the game outright the first time (`STATUS_ACCESS_VIOLATION` in `ntdll.dll`, confirmed via Windows' Application Error event log; a control test with the proxy removed launched fine). Added a diagnostic `IDirect3D9::CreateDevice` vtable hook (slot 16) to see further — **but the hook itself turned out to be the actual problem, not a diagnostic tool for it**: with it installed, the game reliably failed (first the same access violation, then, after trying a Windows Fault-Tolerant Heap compatibility flag out of caution, a silent crash-report-free exit instead; Steam Overlay conflicts were also checked and ruled out). A clean test — hook disabled, otherwise identical — launched and ran the game with zero issues; removing the FTH flag afterward made no difference either way. **Net conclusion: FTH was never actually needed, and this game needs no special compatibility flag at all.** The actual cause of the vtable-hook failure isn't understood yet — the hook code stays in the proxy source, deliberately disabled, until it's properly investigated (don't re-enable without understanding why it broke startup first).

## 5. Threading & frame structure
- Immediate context only, or deferred contexts + command lists?:
- Which thread(s) do what; render-thread name(s):
- One-frame walkthrough (record → replay → present):

## 6. Camera & projection delivery (the crucial section)

### ⛔️ SETTLED 2026-09-01 — the game never takes the eyes off the driver. The native-stereo shortcut is DEAD.

**The game was not launched.** `/gr` filed the exact static check that would decide this
(`inbox/2026-09-01-gr-forcestereo-is-audio-and-the-driver-owns-the-eyes.md`): *does
`renderer_sf_Win32.dll`'s stereo path call `NvAPI_Stereo_SetDriverMode`, and with which constant?*
Its own decision rule was: **DIRECT ⇒ a real self-driven two-eye path exists and the shortcut
survives; AUTOMATIC or absent ⇒ the subsystem is a correction layer over a driver that no longer
ships.**

**Answer: absent.** NVAPI resolves entry points by published function ID through
`nvapi_QueryInterface`, so each wrapper is findable as a `push imm32` of its ID. All seven stereo IDs
are present in `renderer_sf_Win32.dll` — but counting **direct callers** of each wrapper separates
what the game *links* from what it *uses*:

| NVAPI wrapper | ID | direct callers |
|---|---|---|
| `NvAPI_Initialize` | `0x0150E828` | 4 |
| `NvAPI_Stereo_CreateHandleFromIUnknown` | `0xAC7E37F4` | 2 |
| `NvAPI_Stereo_Activate` | `0xF6A1AD68` | 1 |
| `NvAPI_Stereo_SetSeparation` | `0x5C069FA3` | 1 |
| **`NvAPI_Stereo_SetDriverMode`** | `0x5E8F0BEC` | **0** |
| `NvAPI_Stereo_Enable` | `0x239C4545` | 0 |

`[inferred-static 2026-09-01]` The wrapper at `0x100D8B50` has **no direct call and no absolute
reference anywhere in the module**, and no wrapper is exported (1,231 exports checked), so no other
module reaches it either.

**Why the zero is meaningful and not just a linker artifact:** unused NVAPI dispatch stubs do get
linked in, so "0 callers" alone would prove nothing. It is the **contrast** that carries the result —
four of the six wrappers *are* called, so unused stubs are plainly distinguishable from used ones in
this binary.

**What it means.** `SetDriverMode` must be called before device creation to hand per-eye rendering to
the application. It is never called, so the driver mode is never switched to DIRECT: Alan Wake used
3D Vision **Automatic**, where the **driver** duplicated the draw calls and appended the clip-space
offset. The game's role was the consumer one — create a stereo handle, activate, set separation. So
`g_vStereo_Separation_Convergence` is a **consumer of driver-published values, not the producer of an
eye offset.** Driving it would change how the game corrects its post-processing and **would move no
camera.**

**⇒ §6 must be answered from scratch**, the ordinary way (find where the view-projection reaches the
GPU and override it). The queued `g_vStereo_Separation_Convergence` xref is **retired** — it maps
where an eye offset *would* go, not a lever.

**What this does NOT establish:** the scan finds `E8` rel32 calls and absolute immediates. A call made
through a runtime-computed pointer would be missed. That is unlikely here — the other four wrappers
are all called directly, so a direct-call convention is established — but it is the one way this
conclusion could be wrong, and it would be settled by a breakpoint on `0x100D8B50` in a live run.

**⚠️ Separate the load-bearing claim from the weaker one it rests on.**

- **Verified on this machine** `[inferred-static 2026-09-01]`: the game references **seven genuine
  NVAPI dispatch IDs** (all seven occur in both `C:\Windows\SysWOW64
vapi.dll` and
  `nvapi64.dll`, so they are real function IDs, not arbitrary constants), and **one of them —
  `0x5E8F0BEC` — has zero callers while four others have callers.** That structural result is solid.
- **NOT verified here** `[reported]`: that `0x5E8F0BEC` is specifically
  `NvAPI_Stereo_SetDriverMode`. The ID→name mapping comes from the published NVAPI ID list. **The
  shipped driver has its id→name table stripped** — the function-name strings are absent from both
  `nvapi.dll` and `nvapi64.dll` — so the mapping could not be confirmed on this machine.
  **If that mapping is wrong, the conclusion above inverts.**

**What supports the mapping short of proof:** the four IDs that *are* called form a coherent NVAPI
stereo initialisation sequence under this mapping — `Initialize` → `CreateHandleFromIUnknown` →
`Activate` → `SetSeparation` — while the two that are *not* called (`SetDriverMode`, `Enable`) are
exactly the two a game using Automatic mode would have no reason to call. A scrambled mapping would
be unlikely to produce a set that coherent. That is consistency, not confirmation.

**Cheapest way to close it:** check the IDs against NVIDIA's published `nvapi.h` / NVAPI SDK
(`NvAPI_Stereo_SetDriverMode`'s ID is a documented constant). That is a research task, not a modding
one — worth a `/gr` drop rather than a launch.

### Corrections that came with it (from the same `/gr` drop)

- **`-forcestereo` is an AUDIO switch** — *"forces stereo 2 channel speaker mode"*, sitting beside
  `-forcesurround` in the public lists and in the binary's own option table.
  `[reported 2026-09-01, n=2 independent sources]` **There is no launch switch that enables stereo
  rendering** — consistent with the finding above.
- **`-rigidcamera`** (Remedy patch-added) **removes camera smoothing** and centres the camera behind
  Alan. `[reported]` Camera smoothing is the comfort hazard a VR conversion usually has to find and
  defeat in the binary; here it has an official off-switch. Add to the standard launch line beside
  `-freecamera -developermenu`, and use it as a **diagnostic** — residual lag with it set means the
  smoothing is somewhere else.
- **`-directaiming`** — 1:1 mouse control, removes mouse acceleration. `[reported]`
- **`-nativekeys`** preserves keyboard layout on exit (worth setting for unattended runs).
  `-shaders` has no public documentation and is left honestly unknown.

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
- **Windows Fault-Tolerant Heap compatibility flag — tried, not actually needed.** When a `CreateDevice` vtable hook (see §4) caused the game to fail, the first working theory was a pre-existing heap bug in the original 2010 game code being exposed by the extra DLL. FTH (Windows' own shim for exactly that failure class) was applied and briefly seemed to help. It turned out to be a red herring — removing the vtable hook alone (without FTH) fixed the game cleanly, and removing FTH afterward made no difference. **Don't reach for FTH again for this project without re-confirming it's actually needed** — the real cause of that whole episode was the vtable hook itself, not an environmental/OS-level issue.
- **A naive `IDirect3D9::CreateDevice` vtable hook (slot 16) reliably breaks this game's startup, for a reason not yet understood.** The hook code itself (patch technique, logging) looks correct and matches the same pattern documented as working elsewhere in this portfolio (see the enslaved-vr cross-project reference in Alice: Madness Returns' dossier). Something about applying it to *this* game specifically causes a crash (first an access violation, later a silent exit once FTH was tried) — worth real investigation (live debugger, since this game has no DRM and should be attachable) before CreateDevice-level hooking is needed for real camera/projection work (§6/§7).

## 12. Open risks toward the North Star
- **vorpX feasibility signal is real but weaker than this portfolio's stronger fronts (external-research, 2026-08-25): only confirmed in Cinema mode** (vorpX's lowest-fidelity mode — a flat virtual screen in a virtual room, no stereoscopic depth reconstruction, no head-tracked world-relative camera) for the *original* 2010/2012 release specifically. No confirmation of Geometry 3D or full head-tracked/FullVR mode for this exact build (separate vorpX threads exist for Alan Wake Remastered and Alan Wake 2 — different games/builds, not to be conflated with this project's target). This is meaningfully weaker than Mad Max (Geometry 3D + head tracking) or Alice: Madness Returns (Geometry 3D + motion-controller emulation) — the native 3D Vision support (§6) is this project's actually-strongest evidence that per-eye camera work is tractable here, not the vorpX result.
