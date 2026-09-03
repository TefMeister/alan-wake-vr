# Engine Dossier — Alan Wake (Remedy proprietary in-house engine)

> One consolidated, living reference for this game's engine, filled in as the
> `PLAYBOOK.md` phases are worked. Chronological blow-by-blow belongs in the
> `-dev-archive` / `-modding-notes` repos; this file is the *distilled current
> truth*. Update it whenever a fact changes; correct false leads in place.

**Status (2026-09-03):** **§6 is answered statically — the hard question is no longer open.** The shipped shader bank is pre-compiled with CTAB intact (9,971 constant tables), and the engine delivers **projection separately from view** (`g_mViewToClip` / `g_mLocalToView`), which is the best matrix shape in this portfolio for stereo. The game-side camera is one static global (`[0x0076C5D8]`, FOV at `+0x214`) and **the exe has no ASLR**, so every address here is permanent. **The critical path is now injection depth, not knowledge:** all of it needs `SetVertexShaderConstantF` interception, i.e. device-level hooking, which is exactly what the unexplained 2026-08-25 `CreateDevice` vtable-hook failure blocks (§4, §11). ⚠️ **And the M0 proxy's "live-verified" status is itself in doubt** — the only log on disk shows two launches ending 131 ms in (§4); settle that with the first launch of the next flat session. Older status line, kept for continuity: M0 done — static recon complete, external research folded in. No DRM found (GFWL history checked specifically, confirmed absent). Unusual, modular DLL architecture confirmed — matters for injection planning (see §4). **Two real Remedy-shipped dev tools exist**: `-freecamera` and `-developermenu` launch flags, plus reported native NVIDIA 3D Vision support with live separation hotkeys. · **VR-readiness verdict:** TBD, no environmental blockers found, and a real chance the native stereo support (once verified live) shortcuts §6's hardest question — vorpX signal alone is weaker here than other fronts (Cinema mode only), so the native-stereo lead matters more for this project specifically. A from-scratch `d3d9.dll` proxy is built, **deployed, and live-verified** (2026-08-25, after a real diagnostic detour — see §4) — the game runs cleanly with it, no compatibility flags needed.

## 1. Identity
- Game / build / version: Alan Wake (2010, Remedy Entertainment, published by Microsoft Game Studios/Remedy), Steam release (`AlanWake.exe`, 32-bit).
- Platform & store; unofficial port? (extra fragility/legal notes): PC via Steam. Not a known unofficial port. **Steamworks is directly, statically linked into the main exe** (`steam_api.dll` in the exe's own import table) — unlike Burnout Paradise, no separate launcher-handoff pattern expected.
- Legitimacy: owned copy confirmed.

## 2. Engine lineage
- Family / base engine and how it was modified: Remedy Entertainment's own proprietary in-house engine for this title — confirmed via the literal string `Remedy Entertainment` in the exe — a predecessor to the studio's later, publicly-named **Northlight** engine (which debuted with *Quantum Break*, 2016). This earlier engine has no confirmed public name. **Distinctive, unusually modular architecture (confirmed via imports, see §3): the main exe is a thin loader that dynamically pulls in separately-named module DLLs** — `app_sf_Win32.dll`, `physics_sf_Win32.dll`, `grph_sf_Win32.dll`, `d3d_sf_Win32.dll`, `snd_sf_Win32.dll`, `rl_sf_Win32.dll` ("resource loader"? unconfirmed), `ai_sf_Win32.dll`, `loc_sf_Win32.dll` (localization), `renderer_sf_Win32.dll` — one per engine subsystem (`_sf_` likely "sub-framework" or similar, unconfirmed). This is meaningfully different from every other project in this portfolio, where the renderer/D3D calls live directly in (or are statically imported by) the main exe.
- Middleware (animation, audio, physics, megatexture, CUDA, etc.): **Bink** (`binkw32.dll`, video — same middleware as Mad Max/Prince of Persia/Alice). Compiled with **VS2008** (`MSVCP90.dll`/`MSVCR90.dll`).
- Distinctive file formats / build tags / symbol naming: not yet investigated.

## 3. Binary & memory
- 32/64-bit, size, module base, ASLR behaviour (stable base? relocations?): **32-bit** (PE32, `coff-i386`). `AlanWake.exe` itself is unusually small (only 4 sections: `.text`/`.rdata`/`.data`/`.rsrc`) — consistent with it being a thin loader/orchestrator, with the real engine code living in the separate `_sf_Win32.dll` modules. **✅ NO ASLR (2026-09-03, `/pd`): `DllCharacteristics = 0x8000` — `DYNAMIC_BASE` is not set and there is no `.reloc` section at all, so the image is always at `ImageBase 0x400000` and every static address recorded for this game is permanent.** `[inferred-static 2026-09-03]` No rebase re-check is ever needed here — contrast doom-2016-vr, where the ringcam address still owes a post-reboot ASLR test. Section map: `.text 0x00401000 (0x22D000)` · `.rdata 0x0062E000` · `.data 0x0069C000` · `.rsrc 0x00777000`.
- Renderer API (D3D11/12, DXGI, GL, Vulkan) with evidence: **Direct3D 9 confirmed, but NOT statically imported anywhere.** `d3d9.dll` does not appear in the static import table of `AlanWake.exe` or any of its module DLLs (checked all ten). Instead, `d3d_sf_Win32.dll` contains the literal strings `Direct3DCreate9` and `Direct3DCreate failed` side by side — the classic pattern of a **dynamic `LoadLibraryA("d3d9.dll")` + `GetProcAddress(..., "Direct3DCreate9")`** call with a graceful failure path, not a static PE import. **Confirmed only one D3D9 function is looked up this way** (`Direct3DCreate9` — no `D3DPERF_*` or other D3D9 exports referenced anywhere across all ten binaries, checked specifically after the lesson learned on Alice: Madness Returns). Practical upshot: a same-named `d3d9.dll` proxy placed in the game's root directory should still work (Windows' `LoadLibraryA` follows the same app-directory-first search order as static imports), and since this is a dynamic lookup rather than a static import, a missing export here would fail *gracefully* (the game's own logged "Direct3DCreate failed" error path) rather than silently killing the whole process the way Alice's missing static import did.
- Developer console / cvar system present? how opened?: **A real console and cheat system both appear to exist.** Strings found: `?dumpToConsole@GameObject@r@@UAEXXZ` (a C++-mangled `dumpToConsole` method), `"Dump to console"`, and real cheat command names: `cheat_receive_flashlight`, `cheat_receive_weapons`, `cheat_unlock_levels`, `cheat_unlock_nightmare`. How the console itself is opened in-game is not yet confirmed.

## 4. DRM / anti-debug & injection foothold
- DRM (CEG/Denuvo/GOG/none); launch-time-debugger behaviour: **No DRM found — checked specifically, not just assumed clean.** Zero hits for Denuvo, SecuROM, StarForce, or any activation/launcher-handoff string. **The original 2010/2012 PC release shipped on Games for Windows Live (GFWL)** (external-research, 2026-08-25), Microsoft's now-defunct online-activation/achievement platform — no precisely dated confirmation of when the Steam build was migrated off it was found publicly (unlike the clean, dated Jan-2022-patch stories for Prince of Persia 2008 and Alice: Madness Returns), so this was worth checking directly rather than assuming. **Follow-up check on the actually-installed Steam build: zero `xlive`/GFWL-related files anywhere in the install directory, and zero `xlive`/GFWL strings across all ten binaries (the exe + all nine module DLLs)** — this build appears to have been fully migrated off GFWL. Not yet tested live.
- Attach workflow that works: not yet tested live, but no static evidence predicts a block.
- Injection vector that works (proxy DLL name / injector / framework): **✅ LIVE-VERIFIED (2026-08-25), a from-scratch `d3d9.dll` proxy exporting only `Direct3DCreate9`**, matching this portfolio's Psychonauts/Prince of Persia/Alice precedent. **A real diagnostic detour along the way, worth recording precisely** (full story in `staging/alan-wake-vr/proxy-d3d9/README.md`): the plain proxy alone crashed the game outright the first time (`STATUS_ACCESS_VIOLATION` in `ntdll.dll`, confirmed via Windows' Application Error event log; a control test with the proxy removed launched fine). Added a diagnostic `IDirect3D9::CreateDevice` vtable hook (slot 16) to see further — **but the hook itself turned out to be the actual problem, not a diagnostic tool for it**: with it installed, the game reliably failed (first the same access violation, then, after trying a Windows Fault-Tolerant Heap compatibility flag out of caution, a silent crash-report-free exit instead; Steam Overlay conflicts were also checked and ruled out). A clean test — hook disabled, otherwise identical — launched and ran the game with zero issues; removing the FTH flag afterward made no difference either way. **Net conclusion: FTH was never actually needed, and this game needs no special compatibility flag at all.** The actual cause of the vtable-hook failure isn't understood yet — the hook code stays in the proxy source, deliberately disabled, until it's properly investigated (don't re-enable without understanding why it broke startup first).

- **⚠️ 2026-09-03 (`/pd`): the "live-verified working" status above is NOT supported by the evidence currently on disk.** The deployed `d3d9.dll` (56.5 KB, 2026-08-25) contains **no** hook code — it is the plain forwarding build `[inferred-static 2026-09-03]`. But `alanwake_vr_proxy_log.txt`, the only run evidence on this disk, records **two launches that both ended ~131 ms after `Direct3DCreate9` returned** (PIDs 10660 and 28072, one load/unload cycle each, nothing after) `[measured 2026-09-03, from the log file]`. That is not a game that reached gameplay, and the log appends across runs, so a later successful run would still be present. **This does not prove the proxy is broken** — it means the recorded status and the surviving evidence disagree, and static data cannot reconcile them. `[hypothesis 2026-09-03]` **Settle it with the first launch of any flat session on this game, before testing anything else:** game reaches the menu ⇒ the recorded status is right; game exits immediately ⇒ rename `d3d9.dll` aside, relaunch, and note that this also re-opens the 2026-08-25 "the vtable hook was the problem" conclusion, which was drawn while the plain proxy was believed to work.
- **A second dynamic-load seam exists beside NVAPI, but it is NOT `d3dcompiler`.** All three modules that mention shader compilation reference **`d3dx9_43.dll`** and call **`D3DXCompileShader` / `D3DXCompileShaderFromFileA`** — the D3DX9 entry points, not `d3dcompiler_43.dll`'s `D3DCompile`. `[inferred-static 2026-09-03]` See §11 for why a `d3dcompiler_43.dll` proxy is the wrong seam here.

## 5. Threading & frame structure
- Immediate context only, or deferred contexts + command lists?:
- Which thread(s) do what; render-thread name(s):
- One-frame walkthrough (record → replay → present):

## 6. Camera & projection delivery (the crucial section)

### ✅ ANSWERED 2026-09-03 (`/pd`, no launch) — the shader bank ships PRE-COMPILED with CTAB intact, and the engine keeps projection SEPARATE from view.

`shaders\build\pc\*.obj` — 62 `RFX ` containers, ~16 MB — hold pre-compiled D3D9 bytecode with the
`CTAB` constant table **intact**: **9,971 tables, 691 distinct layouts**, every constant named with
the register it lands on. `[inferred-static 2026-09-03, n=9971 tables]`

| constant | stage | register(s) | shaders | meaning |
| --- | --- | --- | --- | --- |
| `g_mViewToClip` | `vs_3_0` | `c0 x4` (2238) · `c192 x4` (2084) · `c4` (128) · `c7` (17) | 4,467 | **the projection matrix, standalone** |
| `g_mLocalToView` | `vs_3_0` | `c4 x3` · `c196 x3` · `c7 x3` · `c199 x3` | 4,553 | object → view (4x3) |
| `g_mViewToWorld` | `vs`+`ps` | `ps c7`, `vs c4`/`c196` | 2,788 | view → world |
| `GPU_skinning_matrices` | `vs_3_0` | `c0 x192` | 1,958 | skinning palette |

**This is the best matrix shape in the portfolio.** Unlike Mad Max's fused `WorldViewProjMatrix` or
Enslaved's fused `c0`, projection arrives **separately from view**, so stereo is two independent
single-constant writes: eye separation into `g_mLocalToView`, asymmetric frustum into
`g_mViewToClip`. Nothing has to be un-fused or inverted.

**⚠️ The projection register is NOT fixed.** The `c0`/`c192` split is the skinning palette:
`GPU_skinning_matrices` occupies `c0..c191`, so skinned shaders push the camera block to `c192`.
Tested per shader: **skinning implies `c192` with zero counter-examples (n=1,954)**; the converse
fails (130 unskinned shaders also sit at `c192`), so the register does not identify a skinned
shader. **A proxy must therefore resolve the register per shader, not assume `c0`** — parse the
CTAB out of the bytecode at `CreateVertexShader` and build a shader-to-register map.

**Coverage:** 4,982 of 5,103 vertex shaders (97.6%) carry some `*ToClip` matrix. The 121 that do
not are spread over **22 files, every one a screen-space, fullscreen or effect pass** (Godray 17,
SSAO 16, BloomX86 12, DeferredLight 11, VolumetricLight 11, ShadowBuffer 10, Velocity 8, Blur 6,
BilateralFilter 5, and 13 smaller — complete list in the recon folder), and correctly should not be
offset. Three real gaps a naive implementation would miss:
`g_mWorldToClip` (264) / `g_mLocalToClip` (251) bypass view space; `g_mClipToView` (90) and pixel-
stage `g_mViewToWorld` (`ps c7`) rebuild position from depth for deferred lighting; and
`g_mCurrentLocalToClip` / `g_mPreviousLocalToClip` drive motion blur — **the exact trap enslaved-vr
hit on 2026-09-02** — so use `-noblur` when judging a stereo run.

Full inventory and reproduction scripts: `dev-archive/recon/2026-09-03-shader-ctab-inventory/`.
Write-up: `modding-notes/2026-09-03-the-shader-bank-ships-precompiled-with-ctab-and-section-6-opens.md`.

### ✅ MATRIX CONVENTION SETTLED, and the per-eye maths is two single-float edits (2026-09-03, `/pd`, no launch)

Established **two independent ways**, because a transpose error here compiles fine and is visible
only in a headset:

1. **CTAB type metadata:** every camera matrix is `D3DXPC_MATRIX_ROWS` — register *i* holds **row**
   *i*. `g_mLocalToView` declares a `4x4` type but occupies **3 registers**, which is only
   consistent with the 4th row being `[0,0,0,1]` and elided.
2. **The shipped bytecode agrees** (`TerrainMesh.obj`, disassembled):
   ```
   dp4 r1.x, c4, r0     ; view.x = dot(row0 of g_mLocalToView, local)
   dp4 r1.y, c5, r0
   dp4 r1.z, c6, r0
   mov r1.w, v0.w       ; 4th row elided, w carried through
   dp4 r0.x, c0, r1     ; clip.x = dot(row0 of g_mViewToClip, view)
   dp4 r0.w, c3, r1
   ```
   **`dp4`** — the full 4-component dot — is decisive: each row's `.w` participates, so **the
   translation lives in the `.w` of each row.** (`Sky.obj` shows the `x4` variant where the 4th
   register is present and supplies `w`; both layouts occur, and `ctab.c` reports which.)

**Verdict:** column-vector (`view = M·local`, `clip = P·view`), registers are rows, translation in
`.w`. `[inferred-static 2026-09-03, two independent reads]`

**Consequence — a physically correct off-axis pair, in two single-float edits:**

```
separation   g_mLocalToView.row0.w -= eye_dx          (eye_dx = ±ipd/2 along view +X)
convergence  g_mViewToClip.row0.z  += g_mViewToClip.row0.x * eye_dx / C
```

The convergence shear is expressed via the projection's **own `row0.x`**, so the game's FOV, near
and far never have to be recovered — and it stays correct when the game changes FOV at runtime
(cutscenes, aiming, and the FOV-dependent shadow behaviour in §8). Because the engine hands over a
real view matrix, this is a **true eye translation plus frustum shear**, not the clip-space
approximation alice-madness-returns-vr is forced into — so per-eye depth and view-dependent shading
are correct rather than approximately right. The two are the same family algebraically (with
`w = z`, NVIDIA's `x' = x + S(w−C)` is a shear plus a constant).

**Verified numerically** against ground truth built a *different* way (explicit off-axis frustum +
physically translated eye) over **1,080 configurations × 8 points**, plus the convergence property,
parallax sign and falloff, an `eye_dx = 0` bit-identical no-op, and fail-closed degenerate input.
`[verified-numerically 2026-09-03, n=1080 configurations]` A five-mutant mutation test confirms the
suite discriminates (all caught; control passes) — including `row0.z = (l+r)/(r-l)`, which is
correct for a *symmetric* frustum and would therefore have passed every mono check while breaking
only stereo. Code and full account: `staging/alan-wake-vr/proxy-d3d9/README-stereo.md`.

⚠️ **Not established until something runs:** that `g_mViewToClip` is left-handed with
`clip.w = view.z` and `row3 = [0,0,1,0]` (assumed from the `dp4 r0.w, c3, r1` pattern plus D3D
convention, not measured); which engine unit the IPD should be expressed in; and that no second
path rewrites these registers after we do. **Diagnostics:** vertical separation instead of
horizontal ⇒ the matrix is transposed from this derivation; identical eyes at any IPD ⇒ the write
is not reaching the shader (registry miss, or one of the 515 fused `g_mWorldToClip` /
`g_mLocalToClip` shaders that bypass view space); separation correct but depth inverted ⇒ only the
`eye_dx` sign, a one-line fix and **not** evidence against the derivation.

### ✅ The game-side camera is ONE static global, and this exe has no ASLR (2026-09-03, `/pd`)

`/gr`'s FOV byte pattern (`D9 80 14 02 00 00 D9 5C 24 10 E8`, from an older build) **ports to our
build and matches exactly once**, at `0x0043F533`:

```
0x0043F52E  call 0x005B5800          ; the accessor
0x0043F533  fld  dword [eax+0x214]   ; FOV
```

`0x005B5800` is `mov eax, [0x0076C5D8]` / `ret`. So **the camera object is behind one static global
`[0x0076C5D8]`, and FOV is `[[0x0076C5D8] + 0x214]`.** `[inferred-static 2026-09-03]`
Corroborated by **151 direct callers** of the getter, and by the global's own 7 references (getter,
a writer cluster at `0x005B7AA6`–`0x005B7EB4`, and a `mov dword [0x0076C5D8], 0` teardown).

**No ASLR: `DllCharacteristics = 0x8000`, no `DYNAMIC_BASE`, no `.reloc` section.** The image is
fixed at `0x400000`, so **every static address in this project is permanent** — no rebase check is
ever needed here (contrast doom-2016-vr's ringcam). `[inferred-static 2026-09-03]`

Weaker, kept separate: reads off the camera object cluster in `+0x138`–`+0x164` (all on a 4-byte
grid inside a 48-byte span, **consistent with** a 4x3 transform at `+0x138`) and `+0x200`–`+0x214`;
`+0x210` is written with an immediate at four sites. `[hypothesis 2026-09-03]` The check that would
disprove it: read the 12 floats at `+0x138` live and test row orthonormality. The `fmul 0.4` /
`fadd 0.8` after the FOV read is a linear remap, **not** a degrees-to-radians conversion, and the
call site has **not** been established as the projection build — it remains `/gr`'s candidate.

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

> #### ✅ CLOSED 2026-09-01 by `/gr` — the mapping is confirmed, so the verdict above stands.
>
> All six IDs were checked against **NVIDIA's own published `nvapi_interface.h`** (the very table
> `nvapi_QueryInterface` dispatches through) and corroborated by an independent third-party ID
> list: `NvAPI_Initialize 0x0150E828` · `Stereo_CreateHandleFromIUnknown 0xAC7E37F4` ·
> `Stereo_Activate 0xF6A1AD68` · `Stereo_SetSeparation 0x5C069FA3` · `Stereo_Enable 0x239C4545` ·
> **`Stereo_SetDriverMode 0x5E8F0BEC`**. `[reported 2026-09-01]` The lookup was sanity-checked
> against the negative-evidence rule — it was also asked for a seventh name whose ID it had not
> been given (`Stereo_GetSeparation` → `0x451f2134`) and returned it, so the table was genuinely
> readable rather than truncated.
>
> **Nothing in §6 needs to change**, and the inversion risk is retired. One refinement:
> `Stereo_Enable`'s zero caller count is **expected** and is not evidence of anything — it is a
> persistent, driver-wide setting rather than a per-session call. Source:
> `external-research/topics/2026-09-01-nvapi-function-ids-confirmed-against-nvidias-own-table.md`.

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
- **D3D9 float constant registers — there are no constant buffers.** `vs_3_0`/`ps_3_0` throughout,
  so the mechanism is `SetVertexShaderConstantF` / `SetPixelShaderConstantF` against the register
  map in §6. This is the same shape as psychonauts-vr / alice-madness-returns-vr / enslaved-vr, and
  much simpler than the D3D11 projects' cbuffer work. `[inferred-static 2026-09-03]`
- **Can source contents be read cheaply?** Yes — the values pass through the proxy as plain floats
  on the way to the device. No staging read-back, no captured CPU pointer needed.
- **The chosen override patch point:** `IDirect3DDevice9::SetVertexShaderConstantF`, with the
  target register resolved **per shader** from the CTAB parsed at `CreateVertexShader` (§6 — the
  register is not fixed; `c0` vs `c192` depends on the skinning palette).
- **✅ The register map is BUILT and validated (2026-09-03, `/pd`, no launch):**
  `staging/alan-wake-vr/proxy-d3d9/src/ctab.{h,c}` — a dependency-free CTAB parser plus a
  pointer-keyed registry. Validated by running it over all 62 shipped containers and comparing
  against `d3d9-ctab.py`, an independent implementation in another language that locates tables a
  **different way** (fourcc scan vs. token walk): **all 9,971 shaders agree on every bucket**.
  `[verified-numerically 2026-09-03, n=9971]` `[compile-verified 2026-09-03]` for host and
  `i686-w64-mingw32` under `-Wall -Wextra -Wpedantic -Wshadow -Wconversion`. Registry and
  hostile-input tests included — the parser must be bounds-safe because `CreateVertexShader` passes
  no length. **It is deliberately not wired into `proxy.c`** (see `README-ctab.md`): that needs the
  device hook, and altering the deployed binary would invalidate the queued one-launch test in §4.
- ⚠️ **This requires device-level interception, which is the project's live blocker** — the
  2026-08-25 `CreateDevice` vtable-hook failure (§4, §11) is now on the critical path rather than
  being a footnote, because every route to per-eye rendering goes through it.

## 8. Pass inventory (by render target)
- Main scene (res/formats): not yet enumerated live. The shader bank names the passes though —
  `StandardMaterial`, `Character`, `Taken`, `Skin`, `Chrome`, `Glass`, `Water`, `River`, `Terrain`,
  `FoliagePRT`, `Grass`, `Particle`, `CustomParticle` are the geometry banks (§6).
- Shadow passes (depth-only sizes): `ShadowBuffer.obj`, plus `g_mSunLightProjectionMatrix`
  (`ps`, `c9`/`c11`/`c12`/`c15`, x2) and `g_sSunLightProjectionMap` in **1,520** shaders.
  ⚠️ **Design constraint from the 3D Vision fixer** (`/gr`, `[reported 2026-09-02]`): v1.06's shadow
  shaders are **FOV-dependent** — Neovad's HelixMod fix required setting the FOV slider to 17/20 to
  get correct shadows and torch lights. **Whatever supplies the per-eye projection must reach the
  shadow path too**, or shadows and torch lights will be wrong per-eye. The main shadow VS is hash
  `2B37CDBA`, in which `c0` carries a projection-shaped term (`dp3 r1.x, c0.xyww, r0`).
- Post / AA chain: `SSAA`, `SSAO`, `BilateralFilter`, `Blur`, `BloomX86`, `Godray`,
  `VolumetricLight`, `VectorBlur`, `Velocity`, `AutoExposure`, `ConvertToLinearDepth`. These are the
  121 vertex shaders carrying **no** `*ToClip` matrix (§6) — screen-space, and correctly not to be
  offset. **`Velocity.obj` is the exception that does need per-eye treatment**
  (`g_mCurrentLocalToClip` / `g_mPreviousLocalToClip`); `-noblur` sidesteps it while testing.
- UI / HUD (how it's kept separate): not yet investigated.

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
- **⏱️ A global time-scale float, located in OUR build (2026-09-03, `/pd`): `0x0069C628`
  (`AlanWake.exe + 0x29C628`).** `[inferred-static 2026-09-03]` `/gr` reported `+0x29D628` from a
  public cheat table built against an older build; scanning our exe for that drop's byte pattern
  (`D9 05 ?? ?? ?? ?? DE CB D9 C9`) returns exactly two sites, and the one at `0x0040AAED` reads
  `fld dword [0x0069C628]` — **one page (0x1000) from the predicted address, with an initial value
  of exactly `1.0`**, matching the reported semantics (`1` = normal, `0.0001` = frozen). The other
  match points into a non-raw (BSS) address and is not a candidate.
  **Why it is worth having:** a frozen world with the render loop still running is the ideal state
  for reading camera/projection values back repeatedly — it makes the §6 live checks (camera-basis
  orthonormality at `+0x138`, the `g_mViewToClip` register map) stable instead of racing the frame.
  Not yet exercised; the value has not been written.

## 11. Dead ends & false leads (save future time)
- **A `d3dcompiler_43.dll` proxy is the WRONG seam for this build — do not build one.** `[inferred-static 2026-09-03, `/pd`]` It was proposed on the reasoning that the game ships `D3DCompiler_42`/`43` cabs and aborts with a "could not process hlsl shader" error, so it must compile HLSL at runtime and a compiler proxy would hand over the whole shader corpus with names. Three things are wrong with that here, each independently sufficient:
  1. **The cabs are not evidence about this game.** `thirdparty\DirectX\` is the **complete stock June-2010 DirectX redistributable — 154 cabs**, spanning Apr-2005 onward (XACT, XInput, X3DAudio, MDX, `d3dx10_*`, `d3dx9_24` through `_43`, `D3DCompiler_42`/`43`). Every DX9-era game ships this. It describes the redist, not the renderer.
  2. **The game's call site is D3DX9, not D3DCompiler.** `renderer_sf_Win32.dll`, `d3d_sf_Win32.dll` and `AlanWake.exe` all reference **`d3dx9_43.dll`** and use `D3DXCompileShader` / `D3DXCompileShaderFromFileA`.
  3. **There is nothing to compile.** No `.rfx`, `.hlsl`, `.fx` or `.h` shader source ships anywhere in the install, and the entry point used is the `...FromFileA` (file-based) variant. The strings `Could not preprocess HLSL shader` / `Could not compile HLSL shader` do exist in the renderer, so the path is real — but it is a **developer/fallback path with no inputs in a retail install**.

  **And it is unnecessary anyway**, which is the point that actually matters: the retail shader corpus ships **pre-compiled with CTAB intact** (§6), so the constant map is readable off disk today, with names, with no launch and no proxy. The claim that "runtime compilation implies no pre-compiled cache, so the CTAB-off-disk method does not transfer here" is **`[disproved 2026-09-03]`** — it transfers, and yields 9,971 tables.

- **Windows Fault-Tolerant Heap compatibility flag — tried, not actually needed.** When a `CreateDevice` vtable hook (see §4) caused the game to fail, the first working theory was a pre-existing heap bug in the original 2010 game code being exposed by the extra DLL. FTH (Windows' own shim for exactly that failure class) was applied and briefly seemed to help. It turned out to be a red herring — removing the vtable hook alone (without FTH) fixed the game cleanly, and removing FTH afterward made no difference. **Don't reach for FTH again for this project without re-confirming it's actually needed** — the real cause of that whole episode was the vtable hook itself, not an environmental/OS-level issue.
- **A naive `IDirect3D9::CreateDevice` vtable hook (slot 16) reliably breaks this game's startup, for a reason not yet understood.** The hook code itself (patch technique, logging) looks correct and matches the same pattern documented as working elsewhere in this portfolio (see the enslaved-vr cross-project reference in Alice: Madness Returns' dossier). Something about applying it to *this* game specifically causes a crash (first an access violation, later a silent exit once FTH was tried) — worth real investigation (live debugger, since this game has no DRM and should be attachable) before CreateDevice-level hooking is needed for real camera/projection work (§6/§7).

## 12. Open risks toward the North Star
- **vorpX feasibility signal is real but weaker than this portfolio's stronger fronts (external-research, 2026-08-25): only confirmed in Cinema mode** (vorpX's lowest-fidelity mode — a flat virtual screen in a virtual room, no stereoscopic depth reconstruction, no head-tracked world-relative camera) for the *original* 2010/2012 release specifically. No confirmation of Geometry 3D or full head-tracked/FullVR mode for this exact build (separate vorpX threads exist for Alan Wake Remastered and Alan Wake 2 — different games/builds, not to be conflated with this project's target). This is meaningfully weaker than Mad Max (Geometry 3D + head tracking) or Alice: Madness Returns (Geometry 3D + motion-controller emulation) — the native 3D Vision support (§6) is this project's actually-strongest evidence that per-eye camera work is tractable here, not the vorpX result.
