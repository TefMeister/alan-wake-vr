# In 3D Vision Automatic, the DRIVER makes the two eyes — the game's stereo uniform only *corrects* effects

**Status:** 🆕 new · **Priority:** high — it answers a question the modding lane asked directly, and
the answer **downgrades** the shortcut this project was hoping for while handing it a better,
driver-independent technique in exchange.

## The question that was asked

From `inbox/2026-09-01-mod-freecamera-lead-confirmed-in-the-binary.md`:

> for NVIDIA 3D Vision titles of this era, did the application's own shaders apply the eye offset
> (using the driver-published stereo texture), or did the driver reproject? That distinction decides
> whether this is a real shortcut to geometry stereo or a dead end.

It is a false dichotomy, and the true third answer is the useful one.

## The answer, from NVIDIA's own developer documentation

**Neither.** The driver does not reproject, and the application's shaders do not apply the eye
offset. In 3D Vision **Automatic**, the driver produces real geometry stereo by rewriting the
*application's* vertex shaders and issuing every draw twice `[reported 2026-09-01, NVIDIA's own
3D Vision Automatic developer documentation]`:

- The driver *"monitors vertex shader creation, and adds a footer to each shader"*, operating in
  **clip space** — chosen because it is *"directly before the perspective divide"*, so shifting `x`
  there changes apparent stereoscopic depth *without* altering the rasterised location or the
  z-buffer depth of the resulting fragments.
- The appended footer is one line:

  ```
  ClipPos.x += Separation * (ClipPos.w - Convergence)
  ```

- *"application issued draw calls are substituted for two separate draw calls — one for the left eye
  and one for the right eye"*, with `Separation` positive for one eye and negative for the other,
  each rendered into its own eye buffer.
- Which draws get this treatment is decided by **driver heuristics plus a per-game profile** built
  during NVIDIA's own QA — not by anything the game asks for.

So it is **true per-eye geometry**, rendered twice — not reprojection of a single image. But the
mechanism lives entirely on the driver's side of the API boundary.

## What, then, is `g_vStereo_Separation_Convergence` / `Stereo Texture` doing in our binary?

It is almost certainly the **`StereoParmsTexture`** pattern from NVIDIA's `nvstereo.h`, and its job
is the *opposite* of what the dossier currently hopes `[hypothesis]` — strongly supported, but not
confirmed against our binary:

Automatic mode gets two effect classes wrong, by NVIDIA's own account: **post-processing** and
**deferred renderers**, both because they *unproject* from window space back to world space, and
that unprojection has to undo a clip-space transform the shader does not know was applied. The
documented fix is that the driver publishes the live `Separation` and `Convergence` into a small
special texture, and **the game's own shaders sample it to invert the stereo transform.**
`nvstereo.h` is the freely-published header that builds and updates that texture.

That makes a renderer symbol named `g_vStereo_Separation_Convergence` a **consumer of values the
driver produced**, not the producer of the eye offset. Alan Wake's `Ctrl+F3` / `Ctrl+F4` separation
hotkeys point the same way: those are the **driver's** Automatic-mode hotkeys, not the game's.

**⚠️ Consequence for `ENGINE-DOSSIER.md` §6/§12.** The framing recorded on 2026-08-25 — *"a working,
in-game-adjustable stereo separation control implies the per-eye offset mechanism is already live and
reachable"* — is too optimistic as written. The control being live implies the **driver's** mechanism
was live on 2010 hardware. Writing our own values into that uniform would change how the game
*corrects* its post-processing, and would move no camera. That is the dead-end half of the answer.

## What the game *could* still be doing — the one live thread

NVAPI has a second mode. `NvAPI_Stereo_SetDriverMode(NVAPI_STEREO_DRIVER_MODE_DIRECT)` turns the
driver's automatic path **off** and hands rendering back to the application, which then renders left,
renders right, and Presents itself `[reported 2026-09-01, NVAPI public headers and NVIDIA developer
forum threads]`. It **must be called before device creation.**

That matters for us specifically because of what `/pd` established statically: `nvapi.dll` is loaded
**dynamically, by string**, from `renderer_sf_Win32.dll`. So the question worth a static xref is
narrow and answerable without launching anything:

> Does the `Activate Stereo` path call `NvAPI_Stereo_SetDriverMode`, and with which mode?

- **DIRECT** ⇒ the game contains a real, self-driven two-eye render path, and `forcestereo` /
  `Stereo Rendering:Override` are its switches. That is the shortcut this project hoped for, intact.
- **AUTOMATIC** (or no such call) ⇒ the stereo subsystem is a correction layer over a driver that no
  longer exists, and the strings are a map of where an eye offset *would* go, not a lever.

`NvAPI_Stereo_SetDriverMode` needing to run before device creation is convenient: it is exactly the
window our `d3d9.dll` proxy already owns.

## The half of this that is worth more than the answer

**We can implement the driver's technique ourselves, and it needs no NVIDIA anything.**

The footer is one line of clip-space arithmetic appended to a vertex shader, with two scalars fed per
eye. That is a complete, first-party-documented recipe for getting **real geometry stereo out of a
D3D9 game without ever locating its view matrix, its projection matrix, or its camera** — the exact
problem §6 is stuck on across several projects in this estate, not just this one. It is also, in
substance, what geo-11 and the HelixMod-lineage fixes do, which the cross-engine library currently
records only as *drivers you use* and not as *a mechanism you can build*.

Its documented weaknesses come free with it, and they are the honest cost: it needs a per-draw
decision about what to stereoise (the driver used heuristics and a hand-built profile), and it breaks
post-processing and deferred unprojection unless those shaders are corrected — which is precisely why
`nvstereo.h` exists.

Filed to the cross-engine library for `/sr`, since it is engine-agnostic:
`flat-to-vr-cross-engine-research/inbox/2026-09-01-gr-clip-space-stereo-footer.md`.

## Concrete next steps

1. **Static, no launch:** xref the `Activate Stereo` path in `renderer_sf_Win32.dll` for
   `NvAPI_Stereo_SetDriverMode` and read the mode constant. This single fact decides whether the
   native path is a shortcut or a museum piece.
2. If AUTOMATIC: stop treating `g_vStereo_Separation_Convergence` as a camera lever, and evaluate the
   clip-space footer as our own technique instead.
3. Either way, `Stereo Rendering:Override` under `-developermenu` is worth looking at live, since an
   *Override* is the affordance that would let us supply values whichever mode is in force.

## Sources

- https://archive.docs.nvidia.com/gameworks/content/technologies/desktop/nv3dva_background.htm
- https://archive.docs.nvidia.com/gameworks/content/technologies/desktop/nv3dva_stereoscopic_issues.htm
- https://help.autodesk.com/cloudhelp/ENU/Scaleform-Help/scaleform_help/3di/stereoscopic/nvidia.html
- https://github.com/NVIDIA/nvapi/blob/main/nvapi_lite_stereo.h
- https://docs.nvidia.com/nvapi/nvapi__lite__stereo_8h.html
