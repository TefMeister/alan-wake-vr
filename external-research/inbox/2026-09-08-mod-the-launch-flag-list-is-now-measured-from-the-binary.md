# The launch-flag list is now MEASURED from the shipped binary — please retag and extend INDEX.md

**Filed by:** modding (`/lm alan-wake-vr`), 2026-09-08
**For:** `/gr`, who curates `external-research/`
**Supersedes:** `topics/2026-08-25-native-freecamera-developermenu-launch-flags.md` §the flag list
(the `[reported]` Fandom + fan-reference list). The topic's *other* content stands.

## What changed

`AlanWake.exe` carries the parser's own option table immediately beside the format string
`Unknown command line option "%s"`. Read straight out of the shipped binary `[measured 2026-09-08]`:

```
shaders   SENSSCALE=/sensscale=   GPUCOUNT=/gpucount=   freecamera   directaiming
nativekeys   rigidcamera   showfps   verbose   developermenu   largeshadowmaps
noblur   forcesurround   forcestereo   cleanaccount   cleancloud   novsync
nosound   window   LOCALE=/locale=
```

So the flags can move from `[reported]` to `[measured]`, and the list gains seven entries nobody
had: **`rigidcamera`**, **`noblur`**, `directaiming`, `nativekeys`, `largeshadowmaps`, `verbose`,
`shaders` (plus `gpucount=` and a bare `window`).

⚠️ **One correction to the reported list:** `-w <n>` and `-h <n>` are **not** in the table. Width and
height come from `resolution.xml`. Anyone repeating "use `-w`/`-h`" will get
`Unknown command line option`.

⛔️ **`cleanaccount` and `cleancloud` are in the same table.** Please carry the warning wherever the
list is published: the names say they wipe local account state and Steam Cloud data, nothing has
been run to find out, and nothing should be.

## Why two of them are worth research time

- **`rigidcamera`** — a camera without bob/sway/lag is the most common comfort win in a flat→VR
  port. If any public source describes what it actually does, that is worth a topic.
- **`noblur`** — motion blur off; comfort, and it removes a full-screen pass.

Both are untested here.

## What does NOT change

The `Stereo Rendering:Override / Enable / Separation / Convergence / Eye Separation` entries are
confirmed present in our binary — in **`renderer_sf_Win32.dll`**, not `AlanWake.exe` — alongside
`Activate Stereo`, `NvidiaSpecificData`, `g_vStereo_Separation_Convergence`, and that DLL imports
`nvapi.dll`. **This corroborates your report and does not reopen the route:** the 2026-09-01 topic
already records zero direct callers of `NvAPI_Stereo_SetDriverMode`, making the stereo uniform a
*correction* layer for a driver-made image, and the 2026-09-03 topic records 3D Vision Automatic as
discontinued. Filed so the INDEX can say "confirmed in-binary, still retired" rather than leaving it
as an open `[reported]` lead someone re-chases.

Detail: `engine-research/ENGINE-DOSSIER.md` §6g.
