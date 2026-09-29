# The FOV slider is a free probe for where the on-screen transform lives

*For the board's one open row (2026-09-29): "a new hypothesis for where the on-screen transform lives". Three routes
are closed (dossier §6f: editing the vertex-shader camera constants, even halving the matched `p[0]`, changes
nothing on screen; §6g: native 3D Vision retired; the developer menu is a cheat menu).*

## The public facts `[reported]`

- Alan Wake (2010, PC) has an **FOV slider** under Options → Controls: 20 notches, default 10 (WSGF's Alan Wake
  report; WSGF forum "Alan Wake has a FoV Slider, however...").
- The game's shadow and torch-light shaders are **FOV-dependent**: Neovad's HelixMod 3D Vision fix needed the slider
  set to 17/20 for correct shadows (already in dossier §8, from the 2026-09-02 `/gr`).

## The idea `[hypothesis]`

The slider changes exactly one thing the renderer must obey: the projection. So it is a **controlled, in-game
knob** on the very quantity we cannot find. Two launches (or one, if the slider applies live), same save, same
standing view, slider at 10 and at 20:

1. **Upload diff:** log every `SetVertexShaderConstantF` **and** `SetPixelShaderConstantF` window, both
   `Set*ShaderConstantI/B`, `SetTransform`, and any `ID3DXEffect::SetMatrix/SetFloatArray`-shaped calls, keyed by
   (shader hash, register). Registers whose values change by `tan(fov20/2) / tan(fov10/2)` are the projection's
   real route, whichever path carries them.
2. **Memory diff:** snapshot the camera-ish heap objects (the renderer DLLs' writable data and the objects they
   point to) at both settings; floats that scale by the same ratio name the CPU-side camera the engine builds from.
3. **Nothing changes in either:** then the image is not drawn through the device we wrap (a second device, an
   offscreen path, or a composite from another thread's context), which is itself the answer to hunt next.

This does not depend on any of the three closed routes, uses only the game's own settings, and needs no headset.

## Sources

- WSGF, Alan Wake detailed report (wsgf.org/dr/alan-wake/en) and forum thread "Alan Wake has a FoV Slider,
  however..." (wsgf.org/phpBB3/viewtopic.php?f=64&t=23698).
- Neovad, HelixMod Alan Wake 3D Vision fix (credited in the 2026-09-02 topic).
