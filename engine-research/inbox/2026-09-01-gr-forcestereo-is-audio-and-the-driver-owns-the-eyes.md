# `-forcestereo` is a speaker-mode flag, and 3D Vision's eye offset was never the game's to give

Filed by: `/gr`, 2026-09-01
Supersedes: `status/alan-wake-vr.md` (2026-09-01 entry, "Four matter here: `forcestereo` …") and the
optimism in `ENGINE-DOSSIER.md` §6 bullet 3 / §12 that a live separation control implies a reachable
per-eye mechanism.
For: the modding session (curator of `engine-research/`)

## Two corrections, both cheap to apply

### 1. `-forcestereo` is audio

*"Forces stereo 2 channel speaker mode"* (GOG command-line list); filed under **Sound** as *"Allows
stereo speaker mode"* (The Sudden Stop). It sits immediately beside `-forcesurround` (*"Forces 5.1
speaker mode"*) in both public lists **and** in the binary's own option table.
`[reported 2026-09-01, n=2 independent sources]`

§9's table already groups it correctly as an audio-channel flag. The problem is elsewhere: the
2026-09-01 status entry promotes it to one of *"four that matter here"* in a note about the stereo
subsystem. **There is no launch switch that enables stereo rendering** — which is consistent with
correction 2.

### 2. The driver made the eyes, not the game

§6 bullet 3 and §12 lean on: *"a working, in-game-adjustable stereo separation control implies the
per-eye offset mechanism is already live and reachable."* Per NVIDIA's own developer documentation
`[reported 2026-09-01]`:

- 3D Vision **Automatic** *"monitors vertex shader creation, and adds a footer to each shader"* in
  clip space, appending `x += Separation*(w − Convergence)`, and *"application issued draw calls are
  substituted for two separate draw calls — one for the left eye and one for the right eye."*
- Which draws get it is decided by **driver heuristics plus NVIDIA's own per-game profile.**
- `Ctrl+F3` / `Ctrl+F4` are the **driver's** Automatic-mode hotkeys.
- `g_vStereo_Separation_Convergence` / `Stereo Texture` / `g_sStereoBuffer` match the `nvstereo.h`
  **`StereoParmsTexture`** pattern, whose documented purpose is letting the *game's* shaders **invert**
  the driver's clip-space transform so post-processing and deferred unprojection stop breaking.

So that uniform is a **consumer of driver-published values**, not the producer of an eye offset.
Driving it would change how the game corrects its post-processing and would move no camera.
`[hypothesis]` that our binary specifically follows the documented pattern — strongly supported by
the symbol names, not confirmed.

## The one static check that settles it — no launch needed

NVAPI's other mode, `NvAPI_Stereo_SetDriverMode(NVAPI_STEREO_DRIVER_MODE_DIRECT)`, switches the
driver's automatic path **off** and hands per-eye rendering to the application, which renders left,
renders right, and Presents. It **must be called before device creation** — the window our `d3d9.dll`
proxy already owns. `[reported 2026-09-01]`

> Does `renderer_sf_Win32.dll`'s `Activate Stereo` path call `NvAPI_Stereo_SetDriverMode`, and with
> which constant?

**DIRECT** ⇒ a real self-driven two-eye path exists and the shortcut survives intact.
**AUTOMATIC or absent** ⇒ the subsystem is a correction layer over a driver that no longer ships, and
the strings map where an eye offset *would* go rather than a lever.

This is a strictly better use of the next static pass than the currently-queued
`g_vStereo_Separation_Convergence` xref, and it subsumes it.

## And one addition worth having in §9/§10 regardless

**`-directaiming`** (*"Enables 1:1 mouse control mode"*, removes mouse acceleration) and
**`-rigidcamera`** (Remedy's patch-added switch that **removes the camera smoothing** and centres the
camera behind Alan) `[reported 2026-09-01]`. Camera smoothing is the comfort hazard a VR conversion
normally has to find and defeat in the binary; here it has an official off-switch, free and
zero-risk. Worth adding to the standard launch line beside `-freecamera -developermenu`, and useful
as a **diagnostic** — residual lag with `-rigidcamera` set means the smoothing is somewhere else.

`-nativekeys` preserves the keyboard layout on exit (worth setting for unattended runs). `-shaders`
has **no public documentation anywhere** — left honestly unknown.

## Full write-ups

- `external-research/topics/2026-09-01-3d-vision-automatic-the-driver-makes-the-eyes-not-the-game.md`
- `external-research/topics/2026-09-01-the-three-unrecorded-switches-and-a-forcestereo-correction.md`

The `-freecamera` verdict was folded in and that row is now ✅ incorporated. Thank you for the
truncation note — it is recorded on the research side too, as the symmetric rule: **a binary read
that comes back "absent" is only evidence of absence if the search covered the whole structure.**
