# 2026-09-01 (b) — Stereo is NVAPI-gated, but loaded *dynamically*; and the switch list I published was incomplete

**Supersedes:** `2026-09-01-native-stereo-confirmed-in-the-binaries.md` §2 (the command-line switch
table, which was incomplete) and its "Next" item (the NVAPI-gating question, now answered).

**Date:** 2026-09-01, dev machine, `/pd` pass. **The game was never launched.** Static analysis of
shipped binaries; nothing modified, nothing run.

---

## 1. ⚠️ Correction: my switch list was incomplete, and `/gr` was right

The earlier note today listed the command-line switches as
`keys · rigidcamera · showfps · verbose · developermenu · largeshadowmaps · noblur · forcesurround ·
forcestereo · cleanaccount · cleancloud · novsync · nosound · window · locale`.

**That list was missing entries**, including **`freecamera`** — which this project's
`external-research` had already flagged as very high priority (patch v1.04, toggled with the right
thumbstick). My scan found `rigidcamera` and printed a window of context that started *after* the
earlier entries, so I read a truncated table and published it as the table.

**The full run, in binary order:**

```
shaders · SENSSCALE=/sensscale= · GPUCOUNT=/gpucount= · freecamera · directaiming ·
nativekeys · rigidcamera · showfps · verbose · developermenu · largeshadowmaps · noblur ·
forcesurround · forcestereo · cleanaccount · cleancloud · novsync · nosound · window ·
LOCALE=/locale=
```

**Confidence upgraded, too.** The string immediately preceding the run is
**`Unknown command line option "%s"`** — a parser's error path. So these are definitively
command-line options with a table and a rejection message, not merely suggestive strings. That moves
the earlier hedge ("that they are parsed is very likely") to established.

**Method lesson worth keeping:** when reading a string table out of a binary, **find its boundaries
before quoting it**. A context window anchored on one hit shows what is near that hit, not the whole
table — and a truncated list published as complete is worse than no list, because it reads as
evidence of absence. The cross-lane check is what caught it: `/gr` had `freecamera` from community
sources, my binary read did not, and the disagreement was the signal.

Newly visible and interesting: **`directaiming`** and **`nativekeys`** — both input-path switches,
which matter for a VR conversion, and neither previously recorded anywhere in this project.

## 2. The deferred question, answered: NVAPI is loaded DYNAMICALLY

The earlier note left this as the next static step — is stereo activation NVAPI-gated, or is there
an internal path? Answer: **NVAPI-gated, and dynamically loaded.**

`[inferred-static 2026-09-01]`

`renderer_sf_Win32.dll`'s import table is:

```
d3dx9_43.dll · KERNEL32.dll · grph_sf_Win32.dll · d3d_sf_Win32.dll · rl_sf_Win32.dll ·
MSVCP90.dll · MSVCR90.dll
```

**No `nvapi.dll`.** But the module contains the strings `nvapi.dll`, `nvapi_QueryInterface` and
`nvapi_pepQueryInterface` — the signature of a runtime `LoadLibrary` + `GetProcAddress` pair, which
is how NVAPI is normally consumed. Its wrapper even logs per call:
`ANvApi: %s Succeeded` / `NvApi: %s Failed: %i` / `NvApi: %s Failed: %s`.

**Why this is the good outcome rather than the bad one.** A *statically* imported NVAPI would make
the whole subsystem hostage to a discontinued driver stack with nothing we could do about it. A
*dynamically* loaded one is **interceptable from a proxy** — `LoadLibrary`/`GetProcAddress` are ours
to answer. That converts "3D Vision is dead, so this is probably inert" into a concrete, testable
route.

## 3. The full stereo symbol set, and what it implies

Contiguous in `renderer_sf_Win32.dll`:

```
Get SLI State · Set Stereo Mode · Activate Stereo · Deactivate Stereo
g_sStereoBuffer · g_vStereo_Separation_Convergence · Stereo Texture · NvidiaSpecificData
Stereo Rendering:Override · Stereo Rendering:Enable · Stereo Rendering:Separation
Stereo Rendering:Convergence · Stereo Rendering:Eye Separation
```

Two readings, both load-bearing:

* **The game applies stereo in its OWN shaders.** `g_vStereo_Separation_Convergence` is a shader
  constant and `g_sStereoBuffer` a shader resource, with a `Stereo Texture` beside them. That is the
  classic NVIDIA arrangement where the driver publishes separation/convergence into a small texture
  and **the application's shaders do the per-eye offset**. If so this is **real geometry stereo, not
  driver reprojection** — which is the difference between a usable shortcut and a curiosity.
* **`Stereo Rendering:*` are settings entries, and one of them is `Override`.** The `Category:Item`
  naming matches `SSAO:Temporal Antialiasing` a few bytes earlier, which is unmistakably a settings
  item. So the renderer exposes **Enable, Separation, Convergence, Eye Separation and an Override**
  as tunables — and `Override` is exactly the affordance needed to supply values ourselves rather
  than take the driver's. **`-developermenu` is the obvious way these are reached.**

### ⚠️ What is NOT established

* **That the shaders, not the driver, do the offset.** The arrangement is consistent with it and the
  symbol names point that way, but no shader has been read. `[hypothesis]` until one is.
* **That `Stereo Rendering:Override` overrides what it sounds like.** Name-based inference.
* **That anything activates at all on a modern driver.** `Activate Stereo` may simply fail — and its
  failure would be logged, which is useful.
* Whether faking NVAPI is sufficient, or whether the driver must also cooperate to produce the
  stereo texture. This is the crux and it is not answerable statically.

## 4. The route this makes concrete

In increasing order of effort, each step informative even if the next is not reached:

1. **`-forcestereo -developermenu`** on a launch. Look for `Stereo Rendering:*` in the menu, and for
   `NvApi: ... Failed` / `... Succeeded` in the log. **This is now a cheap, high-information test**
   where before it was a shot in the dark.
2. If NVAPI fails: intercept `LoadLibrary("nvapi.dll")` / `GetProcAddress` from the proxy and answer
   the stereo queries ourselves, so `Activate Stereo` succeeds.
3. Then drive `g_vStereo_Separation_Convergence` (or the `Override` setting) per eye and submit to a
   headset.

**Still the real blocker, unchanged:** why the `CreateDevice` vtable hook broke startup. Steps 2–3
need a working injection foothold, and that is the thing to fix first.

## 5. Credit where it is due

`external-research`'s `2026-08-25-native-freecamera-developermenu-launch-flags.md` had `freecamera`
from community sources before this binary read did, and finding it *absent* in my truncated table is
what exposed the truncation. The two lanes disagreeing is exactly the mechanism working. A verdict
file has been dropped into that lane's inbox.

🤖 Static analysis of shipped binaries only. The game was not launched and nothing was modified.
