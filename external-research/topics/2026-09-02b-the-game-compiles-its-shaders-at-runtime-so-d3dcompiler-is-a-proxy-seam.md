# The game compiles its shaders at runtime — so `d3dcompiler_43.dll` is a proxy seam that hands us the constant map with names

**Status:** 🆕 new · **Priority:** ⭐ high — it attacks the board's main line (*"answer §6 the ordinary
way — locate the camera and projection delivery"*) with a route that needs no launch to design and no
disassembly to read, and it explains why the sibling projects' off-disk trick does not apply here.

## The evidence

Alan Wake ships **DirectX shader-compiler redistributables inside its own install** — 
`third party\directx\aug2009_d3dcompiler_42_x86.cab` and `jun2010_d3dcompiler_43_x86.cab` — and a
well-known launch failure on some systems is the game aborting with **"could not process hlsl
shader"**, fixed by extracting `d3dcompiler_42.dll` / `d3dcompiler_43.dll` from those cabs into the
game directory. `[reported 2026-09-02, community troubleshooting threads, n=2 sources]`

A game does not need a shader **compiler** at runtime unless it compiles shaders at runtime. So:

**Alan Wake compiles HLSL when it loads, rather than shipping a pre-compiled shader cache.**
`[inferred-static 2026-09-02, n=1 — from the redistributable and the error string; not yet confirmed
against the archives]`

## Why that changes the plan for §6

The two sibling UE3/D3D9 projects on this account answered the same question by reading **compiled**
shaders off disk: `d3d9-ctab.py` parses the `CTAB` block that compiled D3D9 bytecode carries, which
names every constant and its register. Alice's shader cache gave 45,832 tables; Enslaved's gave
34,046.

**That technique does not transfer to Alan Wake as-is**, because there is no compiled cache to read —
the bytecode does not exist until the game makes it. What replaces it is better, not worse:

- **HLSL source names its constants in plain text.** Whatever the view-projection is called in this
  engine, it is a readable identifier, not a register index to be inferred.
- **The compile call is a chokepoint we can own.** The game reaches `D3DCompile` /
  `D3DXCompileShader` in `d3dcompiler_4x.dll` **by name, from a DLL sitting in the game's own
  folder** — the same shape as the NVAPI finding that is already on the board (`renderer_sf_Win32.dll`
  loads NVAPI dynamically by string, so the stereo path *"is ours to answer from a proxy"*). A
  **`d3dcompiler_43.dll` proxy** would see every shader's source text, its entry point and its
  defines as they are compiled, and could log the lot on one run.

That is the same technique the board already sanctions for `nvapi.dll`, aimed at a different DLL, and
it yields the whole shader corpus with names intact instead of a register map inferred from bytecode.

## What it also opens, beyond reading

A compiler proxy is not only an observation instrument. It sits **upstream of the bytecode**, so it
could in principle hand back modified source — the cleanest possible place to add a per-eye term,
with no bytecode patching and no register guessing. That is a much later step and is recorded here as
a consequence, not a plan: correctness of the per-eye maths still has to be settled first, and
modifying shipped shaders is a bigger commitment than overriding a constant.

## The static alternative, if a launch is not wanted

The game's archives are publicly readable. **AWTools** (Nostritius) provides `unrmdp` / `unbin` for
Alan Wake's `.bin`/`.rmdp` pairs, and **neat** (TomEvin) unpacks the same archives; **OpenAWE**
(GPL-3.0) is a full open-source reimplementation of this engine that loads the original game's data
directory. `[reported 2026-09-02]` If the HLSL ships inside those archives, the constant names are
readable with no launch at all — worth one look before building a proxy.

OpenAWE also shows how this engine organises materials: as **"techniques"** with permutation
**property flags** (`PROP_NORMAL_MAP`, `PROP_SPECULAR_MAP`, `PROP_GLOB_SKINNED`, `PROP_GLOB_ALPHA_TEST`
…) selected per material and stage (`material`, `depth`). `[reported]` A technique-plus-flags model is
exactly the design that makes runtime compilation necessary — the engine builds the permutation it
needs when it needs it — which corroborates the reading above from a second direction.

**Important limit on OpenAWE as a source:** it is a *reimplementation*, so its own camera and renderer
code is its authors' design, not a description of `renderer_sf_Win32.dll`'s layout. It is useful for
the engine's **concepts and data formats**, never as evidence about the retail binary's structures.
It is GPL-3.0 — study only, nothing copied.

## Concrete next steps, cheapest first

1. **Static:** unpack the game's archives with a public tool and look for HLSL. If present, grep for
   the view-projection identifier — §6 answered with no launch.
2. **Static:** dump the export table of the shipped `d3dcompiler_43.dll` — that is the forwarding list
   a proxy needs, exactly as the `d3d9.dll` proxy work on Alice established (check the *actual*
   per-function imports, not just the DLL name).
3. **Then one run:** the proxy logs every compiled shader's source, entry point and defines. Pair it
   with the FOV read site from the 2026-09-02 topic (`fld [eax+0x214]`) and §6 is answered from both
   ends — where the value comes from, and where it lands.

## Sources

- https://steamcommunity.com/app/108710/discussions/0/864977025688898181/ — the "could not process hlsl shader" failure and the `third party\directx\` cabs
- https://github.com/OpenAWE-Project/OpenAWE — open-source reimplementation of this engine (GPL-3.0); `techniques/*.json` permutation model
- https://github.com/Nostritius/AWTools — `unrmdp` / `unbin` for Alan Wake's archives
- https://github.com/TomEvin/neat — archive unpacker for the same engine family
