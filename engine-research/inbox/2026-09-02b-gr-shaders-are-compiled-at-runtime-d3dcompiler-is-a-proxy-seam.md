# §6: the game compiles HLSL at runtime, so `d3dcompiler_43.dll` is a second proxy seam — and it hands over the constant map with names

Filed by: `/gr`, 2026-09-02
Topic: `external-research/topics/2026-09-02b-the-game-compiles-its-shaders-at-runtime-so-d3dcompiler-is-a-proxy-seam.md`
Dossier sections: §6 (camera & projection delivery — the board's main line), §4 (injection foothold), §7 (constant mechanism)

`[reported 2026-09-02]` / `[inferred-static 2026-09-02, n=1]` — not yet confirmed against the archives.

- **The game ships `d3dcompiler_42`/`43` cabs in `third party\directx\`** and aborts with **"could not process hlsl shader"** when they are missing. A runtime shader **compiler** implies **runtime shader compilation** — so there is **no pre-compiled cache to read**, and the `CTAB`-off-disk method that answered Alice (45,832 tables) and Enslaved (34,046) **does not transfer here**.
- **What replaces it is better:** HLSL names its constants in plain text, and the compile call is a chokepoint in a DLL in the game's own folder. **A `d3dcompiler_43.dll` proxy** — the same technique already sanctioned for `nvapi.dll` — sees every shader's source, entry point and defines as they compile. One run yields the whole corpus with names, instead of a register map inferred from bytecode.
- **A compiler proxy is also upstream of the bytecode**, so it is the cleanest eventual place to add a per-eye term without patching bytecode. Recorded as a consequence, not a plan.
- **Static alternative first:** the archives are publicly readable (`AWTools`' `unrmdp`/`unbin`, `neat`). If the HLSL ships inside them, §6 is answerable with **no launch at all**. Worth one look before building anything.
- **Context, and a caution:** `OpenAWE` (GPL-3.0) is a full open-source reimplementation of this engine; its `techniques/*.json` show a technique-plus-permutation-flag material model (`PROP_GLOB_SKINNED`, `PROP_GLOB_ALPHA_TEST`, stages `material`/`depth`), which is exactly the design that makes runtime compilation necessary. **But it is a reimplementation** — useful for the engine's concepts and data formats, never as evidence about `renderer_sf_Win32.dll`'s layout, and study-only under GPL-3.0.

Suggested dossier change: add to §6 that the projection is decided game-side (FOV at `[camera+0x214]`, earlier drop) and consumed by **runtime-compiled** shaders, with the `d3dcompiler` proxy named as the route to the constant map; note in §4 that this is a second dynamic-load seam beside NVAPI. Check the exe's actual per-function imports before writing the proxy — the Alice lesson.
