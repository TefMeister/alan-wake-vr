# Engine Dossier — Alan Wake (Remedy proprietary in-house engine)

> One consolidated, living reference for this game's engine, filled in as the
> `PLAYBOOK.md` phases are worked. Chronological blow-by-blow belongs in the
> `-dev-archive` / `-modding-notes` repos; this file is the *distilled current
> truth*. Update it whenever a fact changes; correct false leads in place.

**Status (2026-09-03):** **§6 is answered statically — the hard question is no longer open.** The shipped shader bank is pre-compiled with CTAB intact (9,971 constant tables), and the engine delivers **projection separately from view** (`g_mViewToClip` / `g_mLocalToView`), which is the best matrix shape in this portfolio for stereo. The game-side camera is one static global (`[0x0076C5D8]`, FOV at `+0x214`) and **the exe has no ASLR**, so every address here is permanent. **The critical path is now injection depth, not knowledge:** all of it needs `SetVertexShaderConstantF` interception, i.e. device-level hooking, which is exactly what the unexplained 2026-08-25 `CreateDevice` vtable-hook failure blocks (§4, §11). ✅ **The M0 proxy's "live-verified" status is CONFIRMED, closing the 2026-09-03 doubt** — the same fast `d3d9.dll` load/unload cycle recurred on 2026-09-03, and this time a screenshot taken seconds later showed the game in live gameplay (HUD, moving scene). **The fast cycle is not the real device's lifecycle** — it is very likely a throwaway capability-probe device the engine creates and discards early, separate from whatever creates the real, persistent one. Our proxy's `Direct3DCreate9` hook only sees that first short-lived call. **Where the real device's `IDirect3D9` actually comes from is the new open question** (a second unhooked path to the system d3d9.dll? the engine reusing the one pointer for the whole session?) — worth a `[PD]` static look. `[verified-live 2026-09-03]` Older status line, kept for continuity: M0 done — static recon complete, external research folded in. No DRM found (GFWL history checked specifically, confirmed absent). Unusual, modular DLL architecture confirmed — matters for injection planning (see §4). **Two real Remedy-shipped dev tools exist**: `-freecamera` and `-developermenu` launch flags, plus reported native NVIDIA 3D Vision support with live separation hotkeys. · **VR-readiness verdict:** TBD, no environmental blockers found, and a real chance the native stereo support (once verified live) shortcuts §6's hardest question — vorpX signal alone is weaker here than other fronts (Cinema mode only), so the native-stereo lead matters more for this project specifically. A from-scratch `d3d9.dll` proxy is built, **deployed, and live-verified** (2026-08-25, after a real diagnostic detour — see §4) — the game runs cleanly with it, no compatibility flags needed.

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

### ⭐ ANSWERED 2026-09-04 (`/pd`, no launch) — the proxy was being BYPASSED on the game's second load, and the vtable hook's "confirmed broken" was a lifetime bug

**Where the real device's `IDirect3D9` came from: the system runtime, with us out of the chain.**
`[inferred-static 2026-09-04]` The game loads `d3d9.dll`, calls `Direct3DCreate9` once, and unloads
it again ~6 ms later `[measured, n=3 launches]`, then loads `"d3d9.dll"` a **second** time for the
device it renders with. Our `load_real_dll()` took a reference on
`C:\Windows\system32\d3d9.dll` by full path and **never released it**, so the system module stayed
resident after we were gone — and `LoadLibrary` matches an unqualified name against the **base names
of already-loaded modules** before searching any directory (Microsoft's `LoadLibrary` remarks). The
game's second load therefore got the resident system copy; the game folder was never searched again.
That is the whole answer to "our hook only ever sees one short-lived call".

- **ReShade needed the identical fix for this identical game**: commit `74347b91d`, 4.5.2,
  *"Fixed hooking in Alan Wake"* — free the reference to the module loaded for export hooks.
  `[reported, primary source]` (Via `/gr`, 2026-09-04.)
- **Fixed and deployed**: `FreeLibrary(real_d3d9)` at `DLL_PROCESS_DETACH`, **only when
  `lpReserved == NULL`** (a non-NULL value means process teardown, where a DLL must not free
  libraries). `d3d9.dll` 58,368 B; previous kept as `d3d9.dll.bak-2026-09-04-pre-freelibrary`.
  `[compile-verified 2026-09-04]`, **not run**.
- ⚠️ `FreeLibrary` inside `DllMain` is against the general loader-lock guidance. It is done here
  because the unload is the only moment the reference can be released and because ReShade ships the
  same call for the same reason — **but if a future launch hangs at exit or on the second load, this
  is the suspect**, and the backup merely restores the old bypass.
- **✅ CONFIRMED LIVE 2026-09-04b (`/lm`): the second load now finds us — the bypass is FIXED and the proxy is in the REAL device chain.** `[verified-live 2026-09-04, n=1 launch]` The log shows, in one PID: probe load → `Direct3DCreate9` → unload logged as `(reserved=00000000, explicit FreeLibrary)` with `releasing the system d3d9.dll reference so the game's next LoadLibraryA searches the game folder and finds us again` → **a SECOND `proxy d3d9.dll loaded, PID=<same>` block** → `Direct3DCreate9 -> returned`, and it **never unloads again** — the title and the main menu both render through it (deltas > 0 throughout). This is the project's central unblock: for weeks the proxy saw only the throwaway probe device; it now owns the device the game actually renders with, so device-level interception (CreateDevice hook, constant/matrix dumps — M1/M2) is finally reachable. Write-up: `modding-notes/2026-09-04b-freelibrary-fix-confirmed-proxy-now-owns-the-real-device.md`; evidence `dev-archive/recon/2026-09-04-freelibrary-fix-proxy-now-in-real-device-chain/`. No exit hang or second-load hang observed (the loader-lock caveat above did not bite this launch).

**And the `install_createdevice_hook` verdict is `[disproved 2026-09-04]` as written.** The source
carried "CONFIRMED BROKEN, 2026-08-25 … the real cause is something about how this specific patch is
applied to this specific game's vtable; not yet understood". The cause is mechanical and needs no
mystery: the hook wrote an address **inside our DLL** into slot 16 of the `IDirect3D9` vtable and
**nothing ever put the original back**; the game then unloads our DLL ~6 ms later. A D3D9 vtable is
shared per interface class, so the patch outlives the object — the next
`IDirect3D9::CreateDevice` call jumps into unmapped memory, which is precisely the reported access
violation, every time. `remove_createdevice_hook()` now restores the runtime's own pointer, and
`DllMain` calls it **before** the `FreeLibrary` above (the vtable lives in the system module's own
data and must not be written after that module is released). It refuses to touch slot 16 if some
later hook owns it.
⚠️ **Still disabled deliberately** — the explanation is static and untested, and the last time the
hook was on the game did not start. Re-enable it in a launch of its own with nothing else changed.
⚠️ With the hook disabled the optimiser strips the unhook as dead code, so the **deployed binary
contains none of it and does not need to**; it was proved to compile in by building a scratch copy
with the hook enabled and confirming its log strings, then discarding that build.
Write-up: `modding-notes/2026-09-04-the-proxy-was-bypassed-on-reload-and-the-vtable-hook-was-a-lifetime-bug.md`.

### ⭐⭐ 4c. ANSWERED LIVE 2026-09-05 (`/lm`, home PC, four launches) — `g_mViewToClip` is LEFT-handed, `clip.w = +view.z`; both hooks survive real frames; the 4b instrument was blind and is replaced

**The verdict** `[verified-live 2026-09-05, n=1 launch, 10 five-second windows per register, in-engine intro]`:
three true projections were uploaded, every one with the w-from-z entry **+1** — at **storage index
14** (register 3, component z), which is §6's settled convention (registers are the ROWS of a
column-vector `P`; the depth offset `−zn·zf/(zf−zn)` sits at index 11). `stereo.c` stands as written.

| register | xs | ys | ys/xs | near … far | what |
| --- | --- | --- | --- | --- | --- |
| **c192** | 1.2088 | 2.1490 | **1.778 = 16:9** | 0.2 … 1000 | **main camera**, skinned shaders (the census's c192) |
| c7 | 1.2088 | 2.1490 | 1.778 | 1068 … 10000 | same lens, far depth slice (distant scenery / sky) |
| c0 | 1.0 | 1.0 | 1.0 | 0.05 … 2 | square 90° shadow or cubemap-face projection |

Horizontal FOV 79.2°, vertical 50.0°. The c0 *camera* projection of the non-skinned shaders was not
seen only because the scan rate-limits per register and the shadow pass is uploaded first each frame
`[hypothesis]`; c192 makes the same statement for the same lens.

**How this engine uploads constants** `[verified-live 2026-09-05]`: **whole 128-register blocks**,
`c0+128` and `c128+128`, ~6,000 of each per second in a 3D scene, plus `c0+4` / `c0+5` for the
video quad and UI. Any edit must locate the matrix *inside* a block by offset; `start == reg` never
fires, and a candidate loop that stops at the first spanned register only ever sees c0.

**Why 4b's dump could not see it (two defects, both in `[disproved 2026-09-05]` territory):** it
`break`-ed on the first spanned candidate, so every full block was counted against c0 and its head
printed (a flat 2D matrix at ~500,000 uploads/s in launch 2); and its reading tested `m[11] = ±1`,
the row-vector D3D convention that §6 had already ruled out on 2026-09-03 — in the dossier's own
convention the ±1 is at index 14, so it would have printed "neither convention" forever. The
replacement (`staging/alan-wake-vr/proxy-d3d9/src/proxy.c`, `28a45fe`): a per-5-s histogram of every
`(start, count)` upload range, and a scan of every 4-register window against both signatures,
logging first sightings per register. Deployed on the home PC (66,048 B; the 4b build kept as
`d3d9.dll.bak-2026-09-05-pre-agnostic-dump`).

**Both hooks survive real frames** — CreateDevice at slot 16 (one call, `hr=0`), the constant hook at
slot 94 through the intro, both unhooked in order at a clean menu quit, three launches running.
**But launch 1 crashed at 7 s on a layered-hook race** `[verified-live, n=1 crash, n=3 clean]`: at
the first unload slot 16 held a foreign pointer (`747C0710` — the Steam overlay is the likely owner),
the unhook correctly stood down, and the second load installed on top of *that* pointer as "real";
the two chained and `CreateDevice` recursed 1,669 times in one millisecond. The first block lived
700 ms that launch and 16 ms on the clean ones, so it is timing. Fix queued: never chain into a
foreign slot-16 pointer. Notes:
`modding-notes/2026-09-05-handedness-answered-left-handed-and-the-dump-was-blind.md`; logs
`dev-archive/recon/2026-09-05-handedness-home-pc/`.

### ⭐ 4b. The device is ours, and the instrument to read `g_mViewToClip` is built (2026-09-04c, `/pd`, no launch) — *superseded by 4c: the instrument was blind, see above*

**Both halves needed the same thing.** `install_createdevice_hook()` is the only place the game's
real `IDirect3DDevice9` is handed to us, and the device vtable carries `SetVertexShaderConstantF` —
so no device meant no constant reads, and the hook was disabled from 2026-08-25 under a verdict that
turned out to be a lifetime bug. With that fixed and the FreeLibrary bypass closed
`[verified-live 2026-09-04, n=1]`, both rows became one build.

- **The CreateDevice hook is re-enabled**, with its unhook path (built the same day) intact — that
  is what makes it safe, since the crash it caused was a pointer into our DLL left in a shared
  vtable across an unload.
- **A `g_mViewToClip` dump is built** on device vtable **slot 94** (`SetVertexShaderConstantF`, read
  from the SDK header's own `IDirect3DDevice9Vtbl`, not assumed). It is **read-only** and exists to
  settle §6's standing assumption that the projection is left-handed with `clip.w = view.z`.
- **It watches four registers, not one.** The 2026-09-03 census found `g_mViewToClip` is standalone
  in 4,467 vertex shaders with **no fixed register**: `c0` (2,238), `c192` (2,084), `c4` (128), `c7`
  (17), the split being the `c0..c191` skinning palette pushing the camera block to `c192`.
- ⚠️ **The capture is SPANNING, not equality** — an upload may start below a candidate and contain
  it, and `c192` sits immediately past the palette, so testing `start == reg` would report "never
  seen" for a register written every frame. That is the most misleading possible negative and the
  code says so where it is done.
- **The log states the verdict, not just the numbers:** `m[11]=+1, m[15]=0` ⇒ left-handed and the
  derivation stands; `m[11]=-1` ⇒ right-handed and **every sign in `stereo.c` needs re-deriving**;
  anything else ⇒ that register is not the projection in the shaders that ran.
- **The lifetime rule now covers three things, unhooked in order at detach:** the device vtable, the
  `IDirect3D9` vtable, then the module reference. Each holds a pointer into this DLL and the
  2026-08-25 crash was exactly one of them left behind.

`[compile-verified 2026-09-04]`, deployed (`d3d9.dll` 62,464 B; previous kept as
`d3d9.dll.bak-2026-09-04c-pre-vsdump`). **NOT established:** that either hook survives a real frame —
the device hook has only ever run against the throwaway probe, and the constant hook has never run.
Write-up and the log-reading table: `modding-notes/2026-09-04c-the-createdevice-hook-is-back-on-and-the-viewtoclip-dump-is-built.md`.

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

#### The paths that bypass the split, and the ones that run backwards — also covered (2026-09-03)

**515 vertex shaders never receive `g_mViewToClip`.** Confirmed by disassembly, not assumed —
`Particle.obj` emits position with `dp4 o0.x, c103, r1` straight from `g_mWorldToClip`, using
`g_mWorldToView` only for a fog distance and `g_mViewToWorld` as a `dp3` billboard-facing rotation.
Split: **478** fused-plus-a-view-matrix (Particle 256, FoliagePRT 152, Terrain 33, FoliageBillboard
18, Grass 18, ShadowBlob 1) and **37** fused-only minimal depth shaders (23 with a single
constant; some carry `g_fZClampValue`).

| path | shaders | edit |
| --- | --- | --- |
| `g_mWorldToClip` / `g_mLocalToClip` (fused) | 515 | `row0 += S·row3` then `row0.w -= S·C`, `S = p00·eye_dx/C` |
| `g_mClipToView` (deferred reconstruction) | 90 | `m[i][3] -= s·m[i][0]` — the matching inverse |
| `g_mViewToWorld` (pixel stage) | 1,367 | `m[i][3] += eye_dx·m[i][0]` |

`p00` is **supplied from the cached camera projection, not recovered from the fused matrix** —
object scale baked into a `g_mLocalToClip` corrupts recovery, and the test suite asserts both that
recovery is exact on a rigid `P·V` and that it is demonstrably wrong under scale.

The `g_mViewToWorld` edit is **safe to apply blanket**: disassembly shows uses split between `dp3`
(direction — reflections and normals in `Chrome`, `Taken`) and `dp4` (position, `Water`), and `dp3`
never reads `.w`, so the edit is invisible to those and correct for the others.

`[verified-numerically 2026-09-03, n=48 fused + 24 inverse configurations]` — the fused result is
compared against `P_eye·V_eye·W` including object scale, and `g_mClipToView` against
`inverse(P_eye)` from an independent Gauss-Jordan inverse. **Twelve mutants across both rounds, all
caught, control passes.**

⚠️ **KNOWN GAP — fused-draw attribution is a RUNTIME question.** Whether a fused draw belongs to the
camera or to a shadow/light view depends on which pass is active, and **the same shader serves
both**. Applying a camera shear to a shadow pass corrupts the shadow map. The code refuses
orthographic matrices (`row3 ≈ [0,0,0,1]`) as a fail-safe against directional-light shadows, but a
**perspective spot-light shadow would pass that guard**. The reliable discriminator is the active
render target. Recorded, not solved. `[hypothesis 2026-09-03]` that the 37 fused-only shaders are
the shadow-map path — the `g_fZClampValue` constant is suggestive, not proof.

✅ **ESTABLISHED LIVE 2026-09-05 (§4c):** `g_mViewToClip` IS left-handed with `clip.w = +view.z` and
`row3 = [0,0,1,0]` — measured at c192 / c7 / c0 in the in-engine intro, `[verified-live 2026-09-05,
n=1 launch]`. ⚠️ **Still not established until something runs:** which engine unit the IPD should be expressed in; and that no second
path rewrites these registers after we do. **Diagnostics — each path fails distinctively, so the symptom names the cause:**
vertical separation instead of horizontal ⇒ the matrix is transposed from this derivation;
identical eyes at any IPD ⇒ the write is not reaching the shader (registry miss); separation
correct but depth inverted ⇒ only the `eye_dx` sign, a one-line fix and **not** evidence against
the derivation; **particles and foliage at the wrong depth while the world is right** ⇒ the fused
path is not applied or `p00` is stale; **shadows doubled, smeared or detached** ⇒ the fused shear
is hitting a shadow pass (the attribution gap above); **deferred lighting and SSAO right in one eye
and offset in the other** ⇒ `g_mClipToView` is not getting the matching inverse; **reflections and
specular swimming** ⇒ pixel-stage `g_mViewToWorld`.

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
- **✅ The ID→name mapping is CONFIRMED — read the closure box below before reading the rest of this
  bullet.** `[reported 2026-09-03, n=3 independent reads]` It was checked against NVIDIA's own
  published `nvapi_interface.h` by `/gr` on 2026-09-01, independently by `/sr` on 2026-09-02, and
  independently again by `/gr` on 2026-09-03 — that third read carried **two positive controls in
  the same query** and reached the file's closing `#endif`, so it was not a truncated head.
  **The inversion risk is retired. `0x5E8F0BEC` is `NvAPI_Stereo_SetDriverMode`.**
  - *What remains true and is worth keeping:* the mapping could not be confirmed **on this machine**,
    because the shipped driver has its id→name table stripped — the function-name strings are absent
    from both `nvapi.dll` and `nvapi64.dll`. That is why it took a first-party header rather than a
    local lookup. It is not an open question.

**What supports the mapping short of proof:** the four IDs that *are* called form a coherent NVAPI
stereo initialisation sequence under this mapping — `Initialize` → `CreateHandleFromIUnknown` →
`Activate` → `SetSeparation` — while the two that are *not* called (`SetDriverMode`, `Enable`) are
exactly the two a game using Automatic mode would have no reason to call. A scrambled mapping would
be unlikely to produce a set that coherent. That is consistency, not confirmation.

**✅ That was the cheapest way to close it, and it is done** — three times, by two lanes. The
paragraph above is kept for the reasoning, not as an open action.

**⚠️ The verdict CAN still be wrong, but not for this reason.** The one genuinely open hole is a call
reaching NVAPI through a **runtime-computed pointer**, which a static caller count cannot see. That
is the `[FLAT]` breakpoint on `0x100D8B50`, and it is the only thing left that could invert the
conclusion. Do not re-open the name lookup.

> #### ✅ CLOSED 2026-09-01 by `/gr`, re-confirmed 2026-09-02 (`/sr`) and 2026-09-03 (`/gr`) — n=3, two lanes
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


## 6b. The stereo edit is WIRED IN (2026-09-07, `/pd`, no launch) — and both hook races are closed

*The game was not launched; nothing here has been run. Folds both `engine-research/inbox/` files.*

`stereo.c` has been numerically verified since 2026-09-03 and was connected to nothing. It is now
called from the live `SetVertexShaderConstantF` path, and the two crash/blindness defects that
stood in front of it are fixed.

### ⭐ The instrument was keyed by REGISTER, which hid the thing it was built to find

`g_persp[register]`: the first perspective-shaped matrix seen at a register set `seen`, and every
later one at that register was rate-limited behind the same entry. **A shadow pass uploading a
projection at c0 therefore masked the camera projection at c0 for the rest of the run** — and c0 is
exactly where the non-skinned camera projection lives.

Now keyed by **(xs, ys)** = `m[0][0]`, `m[1][1]`. Those are the right key three ways over: they
differ between a shadow frustum and the camera, they are **unchanged by transpose** so the key does
not depend on settling the storage layout, and they are what the shear scales from — so the
signature the log prints is literally the one to paste into the ini. Every distinct projection now
announces itself once, in full, with the list of registers it has been seen at.

### The shear itself: `aw_stereo_apply_block()` `[verified-numerically 2026-09-07]`

The match/copy/edit is a pure function in `stereo.c`, so **the code that runs in the game is the code
the host self-test exercises** — not a transcription of it. Three properties matter and all three are
tested:

1. **Found by OFFSET INSIDE the block, never by `start == reg`.** The engine flushes whole
   128-register blocks (`c0+128`, `c128+128`) per draw, so `start` is the block base and a
   `start == reg` test fires on nothing.
2. **The engine's buffer is never written.** The pointer handed to the hook may be the live constant
   store; the edit lands in a copy, and the original is forwarded untouched when nothing matched.
3. **A zero signature is refused.** Most of a 128-register flush is zero padding, so a zero key
   would shear dozens of windows.

Tests added to `stereo_test.c` (9 groups): offset 53 of a 128-register block is found and reported;
source unmodified; no collateral edits outside the matched window; the edited window equals
`aw_stereo_apply_fused_clip` exactly; no-match leaves `dst` alone; zero signature, `C<=0`, short
block and NULL all refused; two windows in one block both edited; `eye_dx = 0` is bit-identical.
**The suite was mutation-checked** — injecting "edit window 0 instead of the matched offset" made it
fail, so a pass is evidence rather than a test that cannot fire.

⚠️ **IT SHIPS SWITCHED OFF, and that is not caution for its own sake.** Attribution is a *runtime*
question: the same shader serves the camera and a shadow view, and nothing static separates them.
The operator reads a signature off the instrument and names it in `d3d9_proxy.ini`. **NOT
ESTABLISHED: that any particular signature is the camera.** If the shear lands on the wrong
projection the tell is a corrupted shadow map — shadows swimming or detaching — **not** a
wrong-looking camera.

### ⭐ The layered-hook race that killed launch 1 `[compile-verified 2026-09-07]`

Launch 1 on 2026-09-05 recursed `CreateDevice` **1,669 times in one millisecond** and died. The
cause is a layered hook: something else — the Steam overlay is the likeliest — had already replaced
the slot, so the pointer cached as "the real one" was itself another hook that chains onward.
Chaining is harmless once, and stops being harmless the moment that hook re-enters.

The **unload** path already refused to restore a slot that was not ours. The **install** path checked
nothing, and that is the half that crashed. Both installs (`IDirect3D9` slot 16 and
`IDirect3DDevice9` slot 94) now verify that the pointer they are about to cache lives inside the real
`d3d9.dll`, via `GetModuleHandleExA(FROM_ADDRESS)`, and **stand down and log the owning module**
otherwise. A pointer with no owning module is also refused — an unbacked address is a trampoline,
which is precisely the case to avoid.

⚠️ Launches 2–4 were clean **only because the first block happened to live 16 ms instead of 700** —
they were timed lucky, not protected. Standing down costs the mod for that run; chaining costs the
process.

### Build and deployment state

`build.sh` now links `stereo.c`. **Deployed on the DEV PC: `d3d9.dll` 73,216 B, hash-verified against
the build**, previous kept as `d3d9.dll.bak-2026-09-07-pre-stereo`. ⚠️ **The dev PC was still running
the 2026-09-04c build (62,464 B)** — the 2026-09-05 instrument only ever reached the home PC, so the
dev PC skipped a generation. **The home PC still needs a rebuild** to get any of this.
`d3d9_proxy.ini.template` ships beside the source with the reading order written out.

Strict build (`-Wall -Wextra -Wpedantic -Wshadow -Wconversion`) is clean for all of this session's
code; the 3 remaining warnings are pre-existing `missing-field-initializer` notices on the `g_vs`
candidate array and were not introduced here.

### `[reported]` — the x64dbg bridge failure has a different cause than recorded

Folded from `/gr`. The old note blamed "stale helper processes / an estate-wide bridge issue". The
helpers are **not** stale — five were running on 2026-09-07 and every one had a live `claude` parent,
holding no TCP endpoints `[measured 2026-09-07]`. The real configuration facts:
**`X64DBG_PATH` points at `x96dbg.exe`, which is the launcher/selector, not a debugger**, and the
bridge `Popen`s that path then waits for a session that therefore never registers
`[inferred-static 2026-09-07]`. There are also **two installs**, and the `AppData\Local\x64dbg` one
has an **empty `x32\plugins`** — fatal for a 32-bit target like this game. First thing to try: point
`X64DBG_PATH` at the WinGet install's `x32\x32dbg.exe`, or pass `x64dbg_path` per call. **Untested.**

## 6c. ⛔️ SLOT 16 IS ALWAYS ALREADY HOOKED, AND THE GUARD STANDS THE WHOLE MOD DOWN (2026-09-08, `/lm`, two launches)

`[verified-live 2026-09-08, n=2 launches, 4 loads]`

§6b's layered-hook guard was written to stop the 2026-09-05 crash, and **it works** — the game ran
perfectly, clean main menu, no recursion, clean menu quit both times. But it fires on **every load**,
and standing down happens **before a device is ever created**, so the constant-upload instrument —
which lives on the device vtable — never runs.

**Zero perspective signatures were logged.** The 2026-09-07 `(xs, ys)` re-keying is still entirely
untested live.

### ⭐ Two DIFFERENT foreign owners, changing between loads 350 ms apart

| launch | load | owning module of slot 16 |
| --- | --- | --- |
| via Steam | 1, 2 | `Steam\gameoverlayrenderer.dll` |
| **direct exe** | 1 | `Steam\gameoverlayrenderer.dll` |
| **direct exe** | 2 | **`C:\Windows\SYSTEM32\apphelp.dll`** |

- **Launching `AlanWake.exe` directly does NOT avoid the Steam overlay** — with Steam running it is
  injected anyway, so bypassing the Steam launcher changes nothing `[verified-live 2026-09-08, n=1]`.
- **The owner changed between two loads in the same process**, with different pointer values. A
  vtable is shared per class, so slot 16 was rewritten in between. **Why is not established** — a
  late compatibility shim, the overlay re-hooking, or a pointer left dangling by our own unload that
  now resolves inside another module. Nothing here distinguishes them.

⚠️ **`apphelp.dll` is a Windows compatibility shim, not a third-party hook**, and there is **no
`AppCompatFlags\Layers` entry for AlanWake** in HKLM or HKCU `[measured 2026-09-08]`, so any shim
comes from the system database. If apphelp legitimately owns a shimmed `d3d9` entry point then the
guard's rule — *"the pointer must live inside the real `d3d9.dll`"* — is **false by design** for a
shimmed d3d9, and refusing it refuses a benign OS mechanism. `[hypothesis]`: consistent with the
evidence, not demonstrated.

### ⭐⭐ The fix: stop patching the vtable at all

The proxy can only install when it wins the race for slot 16 outright, and on this machine it never
does. **Return our own COM object from `Direct3DCreate9`** — which the game calls directly, since we
are the proxy — implementing `IDirect3D9::CreateDevice` ourselves and forwarding every other method
to the real interface. Then nothing is written into a shared vtable, nobody can be ahead of us, the
Steam overlay's own hook keeps working on the real object layered below us as it expects, and the
device we hand back can be wrapped the same way — which is where the constant-upload instrument
belongs anyway.

⚠️ **The smaller stopgap is worse:** chaining into the foreign pointer plus a re-entrancy guard
would probably work, but it re-introduces exactly the failure the guard exists to stop, and that
failure is **timing-dependent** — it appeared once in four launches on 2026-09-05. A fix that is only
usually safe against a bug that is only sometimes visible is not worth shipping.

⚠️ **Untested and important:** whether disabling the Steam overlay is *sufficient*. It owns load 1
in every observation, but `apphelp` owned load 2, so removing it may simply expose the next hooker.
That needs a Steam per-game setting change and a Steam restart.

## ✅ 6d. THE ANSWER TO 6c: WE HAND BACK OUR OWN `IDirect3D9` AND STOP RACING (2026-09-08b, `/pd`, no launch)

`[compile-verified 2026-09-08]`, with the vtable layout checked against `d3d9.h` at compile time —
and that check verified to be capable of failing.

§6c established that slot 16 is **always already taken** and that the guard, though correct, leaves
the mod inert because standing down happens before a device exists. The conclusion §6c reached —
that patching is a race we cannot win — is right, and the fix follows from it: **stop racing.**

We own the `Direct3DCreate9` export, so it now returns an object of ours: 17 methods, all
forwarding, whose vtable lives in our DLL and which nobody else has ever seen.

- nothing is written into a shared vtable, so there is nothing to restore and nothing to race for;
- nobody can be ahead of us, because the object did not exist before us;
- **the Steam overlay's hook keeps working, layered below us** — its patch is on the *real* object's
  vtable, and every forwarder calls straight into it.

### Why this cannot be got wrong quietly

The vtable is typed as `d3d9.h`'s own `IDirect3D9Vtbl`, so the compiler checks all seventeen
signatures **and their order**. A hand-rolled `void *` array would let one wrong slot compile
cleanly and corrupt a call at runtime with the wrong arguments — the worst failure available here.
Two compile-time assertions back it up:

```c
sizeof(struct IDirect3D9Vtbl)                      == 17 * sizeof(void *)
offsetof(struct IDirect3D9Vtbl, CreateDevice)      == 16 * sizeof(void *)
```

Changing the second to `15 *` stops the build with *"declared as an array with a negative size"*
`[verified-numerically 2026-09-08]`. The check can fail, so its passing is evidence.

### Lifetime — the 2026-08-25 bug in a new shape, and what stops it

Our vtable points into this DLL, so the DLL must not unload while the game holds a wrapper. The
wrapper takes a reference on our own module while any wrapper is alive and releases it when the last
one dies.

**The ordering is what makes this safe:** the game releases the throwaway `IDirect3D9` *before* it
unloads `d3d9.dll` (releasing a COM object after freeing its library is not legal), so our reference
is gone before the game's `FreeLibrary`. The 2026-09-04 mechanism therefore works unchanged — we
unload, the system `d3d9.dll` reference is released, and the game's second
`LoadLibraryA("d3d9.dll")` finds us again `[verified-live 2026-09-04, n=1]`.

⚠️ The one ordering still unsafe is a game that unloads `d3d9.dll` while holding our wrapper. That
was already fatal and no wrapper design survives it.

A checked interaction: while a wrapper lives, our module reference also prevents
`DLL_PROCESS_DETACH`, so the existing `FreeLibrary(real_d3d9)` cannot fire while a wrapper still
points into that module. The two mechanisms reinforce each other.

### The old path was DELETED, not disabled

`install_createdevice_hook` / `remove_createdevice_hook` / `Hooked_CreateDevice` are gone — a
disabled hook invites re-enabling, and this one cannot be made to work. `slot_is_foreign()` is kept:
the device-side instrument still patches a vtable.

### ⚠️ The DEVICE is still a vtable patch, deliberately

`IDirect3DDevice9` has **119 methods**, and **there is no evidence its slot is contested** — the
stand-down happened on `IDirect3D9` slot 16, before a device existed, so the device slot has never
been reached. `install_vsconst_hook()` carries the same guard, so if it *is* contested the result is
a clean stand-down of the instrument alone with the game still running. **That** is when the device
earns the same treatment; building it now would be building against a guess.

### What is NOT established

**That the wrapper works.** Compile-verified only; the game has not been launched. A COM wrapper
returning the wrong thing from one forwarder would look like a game that starts and then misbehaves
in one specific way.

### Size, since it looks alarming

73,216 → 216,576 bytes, of which **`.text` grew 610 bytes** `[verified-numerically 2026-09-08]` —
exactly what seventeen thin forwarders should cost. The rest is DWARF type info for the D3D9 structs
the signatures reference, the explanatory log strings, and PE padding. `-ldxguid`/`-luuid` add zero
bytes, measured by linking the old source with and without them.

### Build hygiene

Two builds of identical source differed by 2 bytes (PE `TimeDateStamp`), so "rebuild and compare the
hash" silently could not work here. `-Wl,--no-insert-timestamp` → 0 differing bytes. ⚠️ **Fourth
project in one day**, across two toolchains — four for four. See `CONVENTIONS.md`.

## ✅ 6e. THE WRAPPER IS VERIFIED LIVE, THE CAMERA IS IDENTIFIED, AND THE SHEAR LANDS ON NOTHING THE SCREEN USES (2026-09-08c, `/lm`, four launches)

Notes: `modding-notes/2026-09-08c-the-wrapper-works-the-camera-is-identified-and-the-edit-lands-on-nothing-the-screen-uses.md`.
Evidence: `dev-archive/recon/2026-09-08c-the-wrapper-works-and-the-camera-is-identified/`.

### §6d is confirmed live, and the device slot was never contested

`[verified-live 2026-09-08, n=4 launches]` — `returning OUR IDirect3D9 … wrapping the real …`,
then `IDirect3D9::CreateDevice (through OUR wrapper)`, then
`SetVertexShaderConstantF hook installed at device vtable slot 94`. **No `REFUSING to hook
IDirect3DDevice9`** on any launch, so the open question in §6d — whether the device slot would need
the same wrapper treatment — is answered **no**. §6c's slot-16 contest is now moot rather than solved.

### ⭐⭐ The camera projection, measured live

**`xs = 0.915689, ys = 1.627892`, at BOTH `c0` and `c192`** `[measured 2026-09-08, n=2 launches]`.

**The identifying property is `ys/xs` = the RENDER aspect ratio** — `1.7778` here because the dev PC is 16:9 and the game ran at 1280×720/1920×1080. ⚠️ **The HOME PC is 21:9**, so the number to look for there is **~2.37**, not 1.7778, unless the game is pinned to a 16:9 WINDOWED resolution — which is the cheap way to keep every aspect-keyed number portable (`MACHINES.md`). `MatchXS` is unaffected (`xs = 1/tan(hfov/2)`, set by FOV); only `MatchYS` moves: `1.627892` at 16:9 vs `≈ 2.170522` at 2560×1080. Every other
perspective-shaped signature in the same frame is square (`1.0/1.0`; `2.414214/2.414214`, a 90°
cube or shadow face) or non-physical (`19.77/-3.00` at c81, `19.92/2.65` at c87). Lens:
`hfov 95.0°`, `vfov 63.1°`. Seeing it at c0 **and** c192 in one frame confirms the 2026-09-05
census inference that the skinning palette displaces it to c192 in skinned shaders.

### ⚠️ The one-shot signature table saturates, and said nothing about it

The distinct-signature table logs each signature once. The load-in FOV settle walks monotonically
through ~16 distinct signatures (`xs` 1.035317 → 0.926827, **still converging**), fills all 24 slots,
and everything after is dropped — **including the settled gameplay FOV**. `g_sig_dropped` counted
those drops and was **never printed**, so a saturated table was indistinguishable from a quiet one.
Measured after the fix: `24/24 slots used, 2 977 773 dropped` `[measured 2026-09-08]`.

**Why it mattered:** the table's last logged value (`0.926827`) is **0.011** from the truth
(`0.915689`), and `aw_sig_same()`'s tolerance is `1e-4·(|a|+1) ≈ 0.0002` — **55× tighter**. An ini
configured from the old log would have matched nothing, silently, and the row would have read as
"the shear does not work".

**Now fixed:** the periodic 5 s line prints the *last* signature seen at each register that period
with its `ys/xs`, plus table occupancy, drop count, and the stereo apply counters.

### ⭐⭐ 1.66 M edits applied, zero pixels moved

`stereo: 1661102 edit(s) applied in total, 0 upload(s) refused as oversize` (~236 k per 5 s;
`ST_COPY_REGS` is 256 and the gameplay flushes are 128, so nothing is refused). The match fires
constantly and the edited copy is what is forwarded.

**The rendered frame is unchanged** `[verified-numerically 2026-09-08, n=2 launches]`. Same save
point, stereo OFF vs ON, horizontal cross-correlation per depth band: far **+0 px** (corr 0.91),
near **+0 px** (corr 0.91), mid −72 px at the lowest corr of the three (0.75 — fog/lighting drift
between runs, not geometry; a real global shift moves all three together). Predicted effect was a
constant NDC offset `s = p00·EyeDx/Convergence = 0.3663` = **351 px**. Absent.

**Two live candidates, deliberately not collapsed** `[hypothesis]`:
1. the engine **re-uploads** the camera constants after our edit, by a path that is not
   `SetVertexShaderConstantF`;
2. these constants **are not what produces the on-screen transform** — same shape as `mad-max-vr`
   §7's "large `edited` count, nothing moves ⇒ the transform is in NEITHER buffer".

They are separated by a **read-back immediately after the draw**: `SURVIVED` ⇒ (2), `OVERWRITTEN` ⇒ (1).

⚠️ **NOT established that the shear is mathematically wrong.** It never got the chance to be wrong
on screen; `stereo.c` is still numerically self-tested and live-untested.

### ⚠️ INPUT: a bare keypress does not reach this game. A mouse click must precede every key.

Measured on the **main menu** — a stable state that does not auto-advance, so results are
attributable `[verified-live 2026-09-08, n=2 each]`. VK alone: no. Scancode alone: no. Cursor moved
inside the window without clicking, then VK: no. **Click then VK: YES.** VK again without a new
click: no. The rule is **click, key, click, key** — one click does not enable input persistently.
Holds in gameplay too (2.5 s of `W` with no click matched the no-input control at 2.87 vs 2.92; a
click then 3 s of `W` walked Alan visibly). Tool: `dev-archive/tools/awkeys.py`.

**Why the click is needed is NOT established** — plausibly each shell command steals foreground and
the game never gets a proper activation back. Recorded as a rule, not a cause.

⚠️ **The title screen is useless as an input testbed**: it **auto-advances into an attract reel with
no input at all** (60 s of no input, no title). An early reading of "VK works, scancodes do not" came
from exactly that confound and is withdrawn.

## 6f. THE READ-BACK THAT SEPARATES THE TWO CANDIDATES IS BUILT AND DEPLOYED (2026-09-08d, `/pd`, no launch)

Write-up: `modding-notes/2026-09-08d-the-constant-readback-that-separates-the-two-candidates.md`.
Deployed `d3d9.dll` md5 `8ad54c58...`, 223,232 B, dated backup kept. **Not run.**

§6e left the project at a fork: the shear applies 1,661,102 times and the screen does not move, so
either **(1)** the engine re-uploads the camera constants by a path that is not
`SetVertexShaderConstantF`, or **(2)** these constants are not what produces the on-screen
transform. **Both predict an unchanged screen. They differ only in what the device holds at draw
time**, and that is readable without the game running to write.

- **The mechanism.** When the shear edits a block, the proxy remembers the absolute register, the
  sheared 4x4 it wrote, and the engine ORIGINAL 4x4; at the next draw it calls
  `GetVertexShaderConstantF` on that register and compares. `SURVIVED` (our value) is candidate
  (2); `RESTORED` (the original, exactly) is candidate (1); `OVERWRITTEN` (a third value) is
  candidate (1) with a shared register. Keeping the originals is what stops a re-upload and a
  third-party write from collapsing into one answer. `[compile-verified 2026-09-08]`
- **⚠️ `D3DCREATE_PUREDEVICE` is the one thing that would make this silently useless** — D3D9 refuses
  `Get*` on shader constants on a pure device. `BehaviorFlags` is now recorded at `CreateDevice` and
  the `UNAVAILABLE` verdict names the cause; on a non-pure device the same refusal is flagged as
  **unexpected and a finding in its own right**. Which case this game is in is **logged, not
  predicted** `[hypothesis]`.
- **⭐ Four device vtable slots now carry COMPILE-TIME assertions** against the SDK header
  (`DrawPrimitive` 81, `DrawIndexedPrimitive` 82, `SetVertexShaderConstantF` 94,
  `GetVertexShaderConstantF` 95), using the negative-array idiom already used for `IDirect3D9Vtbl`
  slot 16. **Slot 94 previously had only a comment claiming it was verified.** The assertion was
  tested by deliberately breaking it: 82 -> 83 fails the build, restoring it builds clean. A check
  that cannot fail is not a check. `[compile-verified 2026-09-08]`
- **Cost is bounded and the old numbers stay comparable.** With stereo OFF **nothing is hooked at
  all**, so the instrument-only hot path is exactly what the 09-08c measurements were taken with.
  With stereo ON the check runs on the first 8 draws outright, then one draw in 500.
- **The 09-08c instrument lesson is carried forward:** the first occurrence of **each** verdict is
  logged and the counts go in the 5 s line, because a mixed result is itself an answer and n=1
  decides nothing. That is the same defect that made the previous instrument discard ~3M
  observations including the answer.
- **⚠️ A defect caught in self-review, not by a build:** the first version nulled the new real-function
  pointers on unload, copying what `remove_vsconst_hook()` does for `real_SetVSConstF`. Restoring a
  slot makes our hook unreachable *through the vtable*, so the only remaining entry is a foreign
  layered hook — the case logged one line earlier — and there the real pointer is what it must forward
  to. Nulling turned "this unload is not safe" into a **null call on the next draw**. The pointers are
  now left in place deliberately. Nothing about this fails a build or a self-test.
- **The deployed binary was verified before being overwritten**: a fresh build of the pre-session
  source is md5-identical to what was installed (`0dfdf78b77e9...`), so the stamp was honest and
  the `--no-insert-timestamp` reproducibility holds `[verified-numerically 2026-09-08]`.

**No configuration change is needed for the next launch** — the live ini already carries
`Enabled=1 / EyeDx=2.0 / Convergence=5.0` and the measured signature, so the read-back arms with the
shear. Read the `readback:` counts, not the first line.

## ⛔ 6f. THE VERTEX-SHADER CONSTANT PATH IS NOT THE LEVER — PROVEN BY A READ-BACK AND THEN BY AN EDIT TOO BLATANT TO MISS (2026-09-08e, `/lm`, two launches)

Notes: `modding-notes/2026-09-08e-the-readback-settles-the-fork-and-a-blatant-probe-closes-the-third-possibility.md`.
Evidence: `dev-archive/recon/2026-09-08e-the-readback-answers-the-fork-and-the-blatant-probe-confirms-it/`.

**This closes the line §6b–§6e were built on. Do not resume editing `SetVertexShaderConstantF`
constants for the camera in this game.**

### The read-back: candidate (1) is disproved outright

```
readback: 11701 check(s) over 12806104 draw(s) - survived=4992 restored=0 overwritten=6709 unavailable=0
stereo:   2018199 edit(s) applied, 0 refused as oversize
```

- **`restored=0`, exactly** `[verified-numerically 2026-09-08, n=1 launch, 11701 checks]` — nothing
  ever puts the engine's original matrix back, so there is no second upload path and no state-block
  `Apply` restoring it. Candidate (1) is **dead**.
- **`survived=4992`** — the device demonstrably held OUR sheared matrix at draw time in those draws.
- **`overwritten=6709`** — `c0` is a shared register block; the last writer before a given draw is
  often another pass. About register reuse, not about the engine defending its camera.
- First sightings: `SURVIVED at c7`, `OVERWRITTEN at c0`.
- Frame unchanged again: far/mid/near all `+0 px`, **n=3 launches** now.

⚠️ **`PUREDEVICE` did NOT block the read-back.** `CreateDevice` came in with
`BehaviorFlags=0x54` (`HARDWARE_VERTEXPROCESSING | PUREDEVICE | MULTITHREADED`) and the build warned
that D3D9 refuses `Get*` on shader constants on a pure device. In practice `unavailable=0` across
11 701 checks. Do not stand the instrument down on that warning.

⚠️ **The menu summary is not a verdict.** At the main menu it reads `0 check(s) ... NEVER CHECKED`
and `0 edit(s) ... NEVER MATCHED`, because the camera projection is not uploaded there. Reach
gameplay before reading anything.

### ⭐ The fork as written was under-specified — and the third possibility is the important one

The reading table said `SURVIVED ⇒ candidate 2, the wrong buffer entirely`. **That does not
follow.** The read-back proves our *bytes* are present at draw time; it does not prove they were the
*right bytes to change*. If the shear wrote an element that does not affect the image under this
matrix's real layout, "survived + nothing moves" is what the **correct** buffer would also look
like — which would have been a `stereo.c` layout bug and a far better outcome.

### The discriminator, and the answer

There is one element whose location is not in doubt: **`p[0]`, the value the matcher keys on**.
Scaling it changes horizontal FOV regardless of layout. Built `aw_stereo_probe_block()` +
`[stereo] ProbeScaleXS` (diagnostic; `0` = off, back to the shear). Deployed `da469d74bc5b`,
224 256 B, stamped, with `ProbeScaleXS=0.5`; self-tests pass.

**2 298 221 edits applied, and NO geometric change** `[verified-numerically 2026-09-08, n=1 launch]`:
a horizontal **scale** search over 0.50–2.25 returns **best f = 1.00** (corr 0.855) — a halved
`p[0]` doubles `tan(hfov/2)` and would be unmissable — and all three depth bands shift `+0 px`.

**⇒ The vertex-shader constants are NOT what produces the on-screen transform.** The element scaled
is the element matched, so "wrong element" is excluded.

⚠️ **Judged by eye, this frame looks changed — it is not.** Scene lighting and character pose differ
between runs. That is the SECOND eye-misread in one day on this project (see §6e). The "judge by
eye" rule applies to *decisive* observations; when the rival hypothesis also predicts a
different-looking frame, only a number decides.

### What is NOT established

Where the transform actually is. Unexamined: a preshader or in-shader recomputation; constants
uploaded by a path that is not `SetVertexShaderConstantF`; or the engine's own stereo settings being
the intended entry point. **`-developermenu` is now the live row** and is the only remaining flat
row that never depended on this path.

## ✅ 6g. THE COMPLETE COMMAND-LINE OPTION TABLE, READ OUT OF THE SHIPPED BINARY (2026-09-08f, `/lm`, static)

`AlanWake.exe` carries its own option table immediately beside the format string
`Unknown command line option "%s"`, so this is the parser's list, not a wiki's
`[measured 2026-09-08]`:

```
shaders   SENSSCALE=/sensscale=   GPUCOUNT=/gpucount=   freecamera   directaiming
nativekeys   rigidcamera   showfps   verbose   developermenu   largeshadowmaps
noblur   forcesurround   forcestereo   cleanaccount   cleancloud   novsync
nosound   window   LOCALE=/locale=
```

This **supersedes the `[reported]` list** in `external-research` (Fandom + a fan reference), which
had `-window / -w / -h / -novsync / -showfps / -sensscale / -locale / -forcesurround / -forcestereo
/ -freecamera / -developermenu`. Note the reported `-w <n>` / `-h <n>` do **not** appear in the
table; width/height come from `resolution.xml`.

**Seven options nobody had recorded**, and two of them are directly VR-relevant:

| option | why it matters here |
| --- | --- |
| **`rigidcamera`** | ⭐ name suggests a camera without bob/sway/lag — the single most common comfort win in a flat→VR port. Untested. |
| **`noblur`** | ⭐ motion blur off. Also a comfort item, and it removes a full-screen pass that would otherwise have to be defeated. Untested. |
| `directaiming` | input/aim model change. Untested. |
| `nativekeys` | keyboard handling change — possibly relevant to the click-before-every-key rule in §10. Untested. |
| `largeshadowmaps` | quality only. |
| `verbose` / `shaders` / `gpucount=` | diagnostics. |
| `window` | forces windowed without editing `resolution.xml`. |

⛔ **NEVER PASS `cleanaccount` OR `cleancloud`.** They sit in the same table and the names say they
wipe local account state and Steam Cloud data. Nothing has been run to find out what they do, and
nothing should be — a save wipe is not recoverable and the project's save is the test fixture.

### Where the developer menu's stereo entries actually live — and why they are still not the lever

`Stereo Rendering:Override / Enable / Separation / Convergence / Eye Separation` are **not in
`AlanWake.exe`** (zero occurrences, ASCII or UTF-16). They are in **`renderer_sf_Win32.dll`**
(`Stereo Rendering` ×5, `Convergence` ×2, `Eye Separation` ×1) `[measured 2026-09-08]`, in one
cluster with `Get SLI State`, `Set Stereo Mode`, `Activate Stereo`, `Deactivate Stereo`,
`g_sStereoBuffer`, `Stereo Texture`, `NvidiaSpecificData` and **`g_vStereo_Separation_Convergence`**.
That DLL **imports `nvapi.dll`** (and `nvpowerapi.dll`).

⚠️ **This corroborates `/gr`'s `[reported]` menu entries in our own binary — and it does NOT reopen
the route.** `external-research/topics/2026-09-01-nvapi-function-ids-confirmed-against-nvidias-own-table.md`
already records that `/pd` found **zero direct callers of `NvAPI_Stereo_SetDriverMode`**, which
"makes the game's stereo uniform a *correction* layer rather than a self-driven two-eye path", and
`2026-09-03-3d-vision-on-a-current-driver-is-a-dead-feature...` records that 3D Vision Automatic is
discontinued. So `g_vStereo_Separation_Convergence` is a **correction constant for a driver-made
stereo image**, not a two-eye renderer we can drive. Finding the strings is confirmation of a
retired route, not a new one.

### ✅ RUN 2026-09-08f: the menu exists, and it is a CHEAT MENU

`AlanWake.exe -developermenu -rigidcamera -noblur` started clean (no `Unknown command line option`).
**`[Developer Menu]` appears in the main menu between `Extras` and `Quit`**
`[verified-live 2026-09-08, n=1 launch]`. Entire contents:

| entry | state |
| --- | --- |
| `Get Lots of Guns` | greyed at the main menu (in-game only) |
| `Get Flashlight and Batteries` | greyed at the main menu (in-game only) |
| `Unlock all Episodes (Easy and Normal)` | selectable |
| `Unlock Nightmare difficulty` | selectable |

**No stereo entries, no camera / FOV / freeze-render / debug-draw toggles, no cvar console.** It is
a QA unlock menu and there is nothing in it for this project. Nothing was selected — all four alter
save/profile state and the save is the test fixture.

⚠️ **THE FLAG SHIFTS EVERY MENU INDEX BY ONE**, in the main menu *and* the pause menu:

| route | no flag | with `-developermenu` |
| --- | --- | --- |
| main menu → `Quit` | Down ×5 | **Down ×6** |
| pause menu → `Quit To Menu` | Down ×5 | **Down ×6** |

A session blind-counting the recorded ×5 lands on `[Developer Menu]`. Harmless here; the same
off-by-one on a differently-ordered menu is how a save gets overwritten.

### `rigidcamera`: the treatment half of an A/B, with no control yet

14 frames captured while holding `W` with `-rigidcamera` armed. Per-frame **vertical** camera shift
(cross-correlation on the far field): **all zero, mean |dy| = 0.00 px** across 13 pairs. Two guards
so the null means something: consecutive frames differed by 1.97–4.47 mean luma (the game was
rendering and walking, not frozen), and the estimator recovered injected ±1/±3/±8 px offsets
exactly (it is not blind).

### ✅ A/B COMPLETE (2026-09-08g): `-rigidcamera` changes nothing, because there is no bob to remove

The control ran the next session — no flags, same save point, same walk, same window size, same
deployed proxy and the same untouched ini — and **both halves were measured by the same file**
(`dev-archive/tools/awbob.py`), so a difference in the numbers could not have been a difference in
the arithmetic.

| | treatment (`-rigidcamera`) | control (no flags) |
| --- | --- | --- |
| vertical `dy` mean / max | **0.00 / 0 px** | **0.00 / 0 px** |
| horizontal `dx` mean / max | **0.00 / 0 px** | **0.00 / 0 px** |
| per-pair correlation | 0.911–0.993 | 0.927–0.993 |
| frame-to-frame luma delta | 1.97–4.47 | 1.94–4.21 |

`[measured 2026-09-08, n=2 runs, 13 frame pairs each]`

Guards passed in both runs: the frames were changing (so the capture did not outrun the frame rate)
and the estimator recovered injected ±1/±3/±8 px offsets exactly (so a null is a null). A third
check came free — the control's main menu had **six** rows and no `[Developer Menu]` where the
flagged run had seven, confirming the flags really were absent.

⇒ **Alan Wake's third-person camera has no translational bob or sway while walking forward, with or
without the flag.** `-rigidcamera` has nothing to remove along those axes and is not the comfort win
its name suggested. The flat comfort angle closes.

⚠️ **NOT established:** anything about camera **rotation** — only translation was measured, so roll
and rotational smoothing/lag remain untested; anything about running, strafing, stairs, combat or
scripted sequences — only walking forward on flat road was tested; and **`-noblur`, which was armed
in the treatment run and never tested at all**, because motion blur shows during fast camera
rotation and neither run rotated the camera. It stays a cheap question to ride along with any future
launch.

**Consequence for the board:** the `-developermenu` row's stated payoff — *"they exist and respond
⇒ the game ships its own stereo path and this project changes shape entirely"* — **is wrong as
written and is corrected here.** The menu is still worth opening once, but for what else it exposes
(camera/FOV/debug toggles in a 2010 Remedy dev build), not for the stereo rows.

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
- **✅ SOLVED 2026-09-08c — THE INPUT RULE: a mouse click must precede EVERY key.** Bare `SendInput`
  does not reach this game, VK or scancode, foreground verified. `click, key, click, key` — one click
  does not enable input persistently. Driver: **`dev-archive/tools/awkeys.py`**; screen capture and
  window state: `dev-archive/tools/awdrive.py` (both resolve their paths per machine).
  Full evidence table in §6e. ⚠️ The click lands at 15 % window height on purpose — the menu list is
  in the lower third and a click there SELECTS an item (`Quit`, `Restart Checkpoint`).
- **✅ Menu → gameplay, proven autonomously (`n=3`):** click+`space` ×6 → main menu (`Continue Game`
  highlighted) → `enter` → slot list → `enter` → ~40 s load → gameplay. **Self-close, proven `n=4`,
  graceful, never `taskkill`:** `esc` → `down`×5 → verify `Quit To Menu` → `enter` → `enter` → ~12 s
  → `down`×5 → verify `Quit` → `enter` → `enter`. **Verify the highlight by screenshot before every
  Enter** — never blind-count past a destructive item.
- ⚠️ **The title screen auto-advances into an attract reel with no input**, so it cannot be used to
  test whether input works. The main menu is stable; test there.
- Frame capture: `BitBlt` from the screen DC via the toolkit harness (`awdrive.py shot`). Works in
  gameplay and menus at 1920×1080 windowed (`resolution.xml` `fullscreen=0`).
- Launch to a known scene (commands used): candidate (commands used): candidate — `-developermenu` for episode select, plus the general `-w`/`-h`/`-window`/`-novsync` flags for a controlled test environment (see §9).
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
