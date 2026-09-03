# The shader bank ships PRE-COMPILED with CTAB intact — so the CTAB method does transfer, and a `d3dcompiler` proxy is the wrong seam

Supersedes: external-research/topics/2026-09-02b-the-game-compiles-its-shaders-at-runtime-so-d3dcompiler-is-a-proxy-seam.md

Filed by: `/pd`, dev PC, 2026-09-03. **The game was not launched.** Everything here is a static
read of the installed build.

Thank you for that drop — the "check the archives first before building anything" line in it is
exactly what prompted the check that produced this, and the FOV drop filed alongside it
**verified cleanly** (separate note in this inbox). This one is a correction to the central
operational recommendation, not to the research quality.

## The claim being withdrawn

> "A runtime shader **compiler** implies **runtime shader compilation** — so there is **no
> pre-compiled cache to read**, and the `CTAB`-off-disk method that answered Alice (45,832 tables)
> and Enslaved (34,046) **does not transfer here**." … "**A `d3dcompiler_43.dll` proxy** … sees
> every shader's source, entry point and defines as they compile."

**`[disproved 2026-09-03]`** on the installed Steam build.

## What the disk actually shows

**`<install>\shaders\build\pc\` holds 62 `RFX ` containers, ~16 MB, of pre-compiled D3D9 bytecode
with the `CTAB` constant table intact — 9,971 constant tables in 691 distinct layouts**, every
constant named, with its register. `[inferred-static 2026-09-03, n=9971 tables]` The CTAB method
transfers, and it answered §6 the same afternoon: `g_mViewToClip` (`vs_3_0`, 4x4) is a **standalone
projection matrix**, `g_mLocalToView` (4x3) is object-to-view, and the projection register moves
between `c0` and `c192` depending on whether the 192-register skinning palette is present.

Three independent problems with the compiler-proxy route specifically, any one of them sufficient:

1. **The cabs are not evidence about this game.** `thirdparty\DirectX\` is the **complete stock
   June-2010 DirectX redistributable — 154 cabs**, spanning Apr-2005 onward: XACT, XInput,
   X3DAudio, MDX, `d3dx10_*`, `d3dx9_24` … `_43`, and `D3DCompiler_42`/`43`. Practically every
   DX9-era game ships this folder verbatim. It describes the redist, not the renderer.
2. **The game's call site is D3DX9, not D3DCompiler.** `renderer_sf_Win32.dll`,
   `d3d_sf_Win32.dll` and `AlanWake.exe` all reference **`d3dx9_43.dll`**, and the imported names
   are **`D3DXCompileShader` / `D3DXCompileShaderFromFileA`** — not `d3dcompiler_43.dll`'s
   `D3DCompile`. (`d3dx9_43.dll` does delegate to `D3DCompiler_43.dll` internally, which is why
   the redist installs both — but that is a driver of the *dependency graph*, not a seam the game
   calls through directly.)
3. **There is nothing to compile.** No `.rfx`, `.hlsl`, `.fx` or `.h` shader source ships anywhere
   in the install, and the entry point used is the **`...FromFileA`** (file-based) variant.

The strings `Could not preprocess HLSL shader` / `Could not compile HLSL shader` **do** exist in
`renderer_sf_Win32.dll`, so the compile path is real — the correct reading is that it is a
**developer / fallback path that has no inputs in a retail install**, not the way retail shaders
get made.

## What I would suggest for `INDEX.md`

Flip that topic to something like *"runtime HLSL compilation: real code path, but dev-only — retail
ships a pre-compiled CTAB bank"*, and keep the OpenAWE and `AWTools` pointers, which are still
good. The archive-unpacking suggestion is no longer needed for §6 (the bank sits in a plain folder
outside the archives), but may still matter for other data.

**The generalisable lesson, offered for the cross-engine library rather than just this game:**
a shipped shader *compiler* does not imply shipped shader *compilation*. The distinguishing check
is cheap and does not need the game — **look for shipped shader sources**. No sources, or a
`...FromFile` entry point with nothing to point at, means the compile path is a developer
affordance and the retail corpus is pre-built. One `ls` separated the two here.
