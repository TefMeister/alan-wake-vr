# Verdict: `-freecamera` / `-developermenu` CONFIRMED in the shipped binary — and your lead caught my error

**From:** the modding side (`/pd` pass), 2026-09-01
**For:** `/gr alan-wake-vr` — please flip this row's status in `INDEX.md`.

## The lead

`topics/2026-08-25-native-freecamera-developermenu-launch-flags.md` — currently 👀 **reviewed**.
**It should be ✅ incorporated.**

## Confirmed against the binary

Both flags are present in `AlanWake.exe`, in a contiguous command-line option table immediately
preceded by the parser's own error string **`Unknown command line option "%s"`**. So these are
definitively parsed options with a rejection path, not merely suggestive strings — which upgrades
the confidence on your topic from community-sourced to binary-confirmed.

The complete table, in binary order:

```
shaders · SENSSCALE=/sensscale= · GPUCOUNT=/gpucount= · freecamera · directaiming ·
nativekeys · rigidcamera · showfps · verbose · developermenu · largeshadowmaps · noblur ·
forcesurround · forcestereo · cleanaccount · cleancloud · novsync · nosound · window ·
LOCALE=/locale=
```

**Three entries your topic did not have, and which may be worth a research pass of their own:**
`directaiming` and `nativekeys` (both input-path switches — directly relevant to a VR conversion,
where aiming and key handling are exactly what gets rebuilt) and `shaders`.

## Your lead caught a real error on my side

My own binary scan on 2026-09-01 published a switch list that **omitted `freecamera`**. The cause
was mundane and reusable: I anchored a context window on `rigidcamera` and printed bytes around it,
which showed a *truncated* table, and I published it as the whole table. Your topic having
`freecamera` while my binary read did not is what exposed it.

Worth recording on the research side too, because it cuts both ways: **a binary read that comes back
"absent" is only evidence of absence if the search covered the whole structure.** If a future topic
is contradicted by a modding-side binary scan, the scan is not automatically the stronger source.

## Also newly established (see `modding-notes/2026-09-01b-...`)

`renderer_sf_Win32.dll` does **not** statically import `nvapi.dll` — it loads it **dynamically**
(`nvapi.dll`, `nvapi_QueryInterface`, `nvapi_pepQueryInterface` as strings, with per-call logging).
That matters for your 3D-Vision topic: a dynamically loaded NVAPI is **interceptable from a proxy**,
so "3D Vision is discontinued" does not automatically make the stereo path unreachable.

The renderer also exposes `Stereo Rendering:Override / Enable / Separation / Convergence /
Eye Separation` as settings-style entries, alongside the shader symbols
`g_vStereo_Separation_Convergence`, `g_sStereoBuffer` and `Stereo Texture`.

**A useful research question, if you want one:** for NVIDIA 3D Vision titles of this era, did the
application's own shaders apply the eye offset (using the driver-published stereo texture), or did
the driver reproject? That distinction decides whether this is a real shortcut to geometry stereo or
a dead end, and it is not answerable from our binaries alone.
