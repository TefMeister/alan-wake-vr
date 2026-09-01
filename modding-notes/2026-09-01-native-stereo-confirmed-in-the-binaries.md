# 2026-09-01 — Native stereo rendering is real, and the switch list is in the exe

**Date:** 2026-09-01, dev machine. **The game was never launched** (a parallel session owns the
machine's one "game may run" slot). Static analysis of shipped binaries; nothing modified.

**The queued next step was "try `Ctrl+F3`/`Ctrl+F4` early as a fast way to confirm native stereo
support". That question is answered without launching: the stereo path is real, it is NVIDIA
3D-Vision-style, and it has a shader-level separation/convergence uniform.**

---

## 1. `renderer_sf_Win32.dll` contains a complete stereo subsystem

Symbols and log strings, sitting adjacent in the module:

```
Set Stereo Mode · Activate Stereo · Deactivate Stereo
g_sStereoBuffer
g_vStereo_Separation_Convergence
Stereo Texture
NvidiaSpecificData · Get SLI State · numAFRGroups
Stereo Rendering:Overr…
```

`[inferred-static 2026-09-01]` — present in the shipped module; not observed running.

Two things stand out:

* **`g_vStereo_Separation_Convergence` is a shader global**, i.e. separation and convergence are fed
  to shaders as a vector uniform. That is the classic 3D-Vision-style formulation, and it means the
  per-eye maths already exists inside the renderer rather than needing to be built.
* The surrounding `NvidiaSpecificData` / SLI / AFR strings place this in an **NVAPI** integration —
  so activation historically went through the 3D Vision driver stack, not a plain in-game toggle.
  That is the thing to be careful about (see §3).

## 2. The executable carries a command-line switch list

Found as a contiguous run of switch names in `AlanWake.exe`:

```
keys · rigidcamera · showfps · verbose · developermenu · largeshadowmaps
noblur · forcesurround · forcestereo · cleanaccount · cleancloud
novsync · nosound · window · locale
```

Four of these are directly useful to this project:

| Switch | Why it matters |
|---|---|
| **`forcestereo`** | forces the stereo path on, independent of whatever normally gates it |
| **`developermenu`** | a developer menu in the shipping build — the Psychonauts precedent says these are worth taking seriously |
| **`rigidcamera`** | a camera mode; unknown semantics, but camera-affecting switches are rare and cheap to try |
| **`window`** | windowed mode, which every other project in this portfolio needed and had to fight for |

`[inferred-static 2026-09-01]` — these are strings in a switch table. **That they are parsed is very
likely; that each still does something is not established.** The exact prefix convention (`-`, `--`,
`/`) is also not established from the strings alone.

## 3. What this does NOT mean

* **It does not mean stereo can simply be switched on.** An NVAPI/3D-Vision integration typically
  requires the driver stereo stack to be active, and 3D Vision was discontinued — the game asking
  NVAPI to "Activate Stereo" on a modern driver may well fail. **`forcestereo` might do nothing at
  all, and that would be an unremarkable outcome, not evidence the subsystem is absent.**
* **It does not replace the VR work.** Even if it activates, 3D-Vision stereo is two eyes on a flat
  screen, not headset submission with head tracking. What it would give is enormous: a renderer that
  already knows how to draw the scene twice with a per-eye offset, and a named uniform where that
  offset lives.
* The real prize is `g_vStereo_Separation_Convergence`. **If the renderer's stereo path can be made
  to run at all, driving that uniform is a far shorter road than building per-eye rendering from
  scratch.** If it cannot be activated, the same symbol still tells us where the renderer *would*
  apply an eye offset, which is a strong hint for where to inject one.

## Next

**No launch needed for the first step:** find `g_vStereo_Separation_Convergence`'s xrefs in
`renderer_sf_Win32.dll` and see what writes it and what gates the "Activate Stereo" call — that
establishes whether activation is NVAPI-gated or has an internal path, which decides whether
`forcestereo` is worth a launch at all. The module is a plain DLL, so
`flat-to-vr-RE-toolkit/tools/static-disasm.py` handles it directly.

Then, on a live session: `forcestereo` and `developermenu`, watching the proxy log.

**Also still open from the last session** and unaffected by this: why the `CreateDevice` vtable hook
broke startup. That remains the real blocker for the injection route.

**Version note:** the queued task also said "check installed version against 1.06.18.1326".
`AlanWake.exe` here carries **no version resource at all** (`FileVersion`, `ProductVersion` and
`FileDescription` are all empty), so that check cannot be done this way and needs a different
identifier — file hash or a build string — if it still matters.

🤖 Static analysis of shipped binaries only. The game was not launched and nothing was modified.
