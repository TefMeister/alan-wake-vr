# Alan Wake shipped with substantial native NVIDIA 3D Vision support — later patches reportedly need little to no third-party fixing

**Status:** 🆕 new · **Priority:** high — a strong camera/projection prior-art signal for
`ENGINE-DOSSIER.md` §6, in the same family as the native-stereo discoveries already made for Alice:
Madness Returns and (partially) Prince of Persia 2008 elsewhere in this portfolio.

## What was found

Per an NVIDIA GeForce forum discussion on Alan Wake's 3D settings, the game (specifically noted
against version 1.06.18.1326) has **real, driver-level NVIDIA 3D Vision support with in-game
adjustment hotkeys**: convergence changes are enabled via the NVIDIA Control Panel, FOV is set to a
specific value in Options/Controls, and **separation is adjusted live in-game via `Ctrl+F3` /
`Ctrl+F4`** (reported working value: 12 "bars," roughly 20%). Critically, the discussion states that
**"later versions of Alan Wake (1.06) are almost 3D Vision ready out of the box"** with just driver/
in-game setting adjustments — **no HelixMod fix required** for those versions. An older HelixMod DLL
exists and remains useful specifically for **fixing light-clipping issues**, implying earlier game
builds needed more third-party correction than later ones, and the native support matured over the
game's patch history.

## Why this matters

This is the same pattern already found valuable on the Alice: Madness Returns front (a game that
ships its own largely-working native stereo-3D system) — evidence that a real, dev-implemented
per-eye camera/projection path exists inside this game's own code, not something to build from a
mono-rendering assumption. The `Ctrl+F3`/`Ctrl+F4` live separation-adjustment hotkeys are a
particularly concrete, actionable detail: **a working, in-game-adjustable stereo separation control
implies the underlying per-eye offset mechanism is already live, reachable, and not buried behind
anything exotic.**

## Caveats

This research pass's confidence in these specifics comes from a search-engine-summarized read of the
NVIDIA forum thread (a direct fetch of the live page did not return usable content — it returned only
a client-side loading placeholder). The core claims (native 3D Vision support, the `Ctrl+F3`/`Ctrl+F4`
hotkeys, the "almost out of the box on 1.06" framing) are specific enough to be worth recording, but
should be **verified directly against the actually-installed build** before relying on them — confirm
the installed version, and test the hotkeys live, rather than assuming they transfer unchanged.

## Concrete next step

Check the installed game's version against `1.06.18.1326`; if it matches or is newer, try
`Ctrl+F3`/`Ctrl+F4` live early in investigation as a fast, zero-risk way to confirm native stereo
support exists and observe its effect — a strong candidate for directly informing §6's core question
before any independent shader-reflection work begins.

## Sources

- https://www.nvidia.com/en-us/geforce/forums/discover/136359/alan-wake-what-are-the-3d-recommended-settings-/
- https://helixmod.blogspot.com/2017/05/alan-wake.html
