# 2026-10-11 (dev PC, `/pd`, Opus on a Fable row, NO LAUNCH): the scene is two halves, and only one was edited

**The game was not launched, and nothing here has been run.**

## What the home headset run showed (2026-10-10)

With the camera edit on, Alan, the street-light cones and the fog vanished, while the road, the lamps and the trees
stayed exactly where they were (`dev-archive/recon/2026-10-10-home-headset/aw_cmp.png`). The board's question was why
the home PC's camera match "breaks those passes".

## What it actually is

**1. The world is drawn on two different camera paths, and only one of them was being edited.**
`[inferred-static 2026-10-11]` from the dossier's shader census plus two archived pictures.

- The split path (`g_mViewToClip`, matched by `MatchXS/MatchYS`) draws Alan, rocks, signs and the light volumes.
- The fused path (`g_mWorldToClip` / `g_mLocalToClip`, 515 shaders: Particle, FoliagePRT, Terrain, Grass,
  FoliageBillboard) draws the road, terrain, trees and particles. It never receives `g_mViewToClip`, so the edit
  never reached it.
- Evidence in our own archive: the 2026-10-06 squeeze probe (`probe-squeeze-off-on-off.png`) squeezed **Alan only**;
  on a gridded crop the street lamp, both road edges and the yellow line sit at the same pixels in the "off" and "on"
  frames `[measured 2026-10-11, n=1 picture, by eye on a 40 px grid]`. ⚠️ This corrects dossier §6h's "ON squeezes
  the whole scene, world and Alan".
- With a 3 cm eye shift the two halves only drift slightly apart, which is why the dev PC's stereo looked right. With
  a head turn the split half is thrown across the screen while the fused half stays put: that is the home picture.

**2. The head turn was the headset's raw heading, never re-centred.** `[inferred-static 2026-10-11]` (code read).
The rotation came straight from the runtime's tracking origin, so a headset lying on a desk, facing anywhere, turned
the whole split half away. The simulator always started at "straight ahead", so it could not show this.

**3. The "HeadTrack=0" picture was not a HeadTrack=0 test.** `[inferred-static 2026-10-11]` (code read). `[vr]`
settings were read once at start; numpad 7 re-read only `[stereo]`. The second home picture had head turning on.

The home FOV values (xs 1.208792 vs the dev PC's 0.915689) are a different in-game FOV setting, not a cause.

## What was built (compile-verified, self-tests pass, installed on the dev PC, NOT run)

- **`fused.c`** (`[stereo] Fused=1`): finds every fused camera matrix in an upload by splitting it as
  `P^-1 * M` with the camera projection the split path matched, and rebuilds it with the split path's own edited
  projection, so shear, eye lens and head turn all carry over with no second derivation. Attribution (the old KNOWN
  GAP): a window is only taken when `P^-1 * M` comes out as a real camera transform: depth row equals the camera's
  near/far, and the 3x3 columns are orthogonal (true for any rotation and per-axis object scale, false for another
  FOV or aspect). `fused_test.c`: 2,934 checks, 1,130 on-screen points compared against the split path's own result;
  decoys left alone: zero padding, P itself, orthographic shadow, square spot light, the camera FOV with another near
  plane, the camera at a 3% wider FOV, a local-to-view followed by other data. Six planted mistakes: three caught,
  three that cannot occur with this game's symmetric projection (explained in the test run, not hidden)
  `[verified-numerically 2026-10-11]`.
- **Re-centring:** the head's heading when the view starts (and on every numpad 7 switch-on) becomes the game's
  forward; pitch and roll stay measured from gravity. 64 extra checks; two planted mistakes caught
  `[verified-numerically 2026-10-11]`.
- **Live reload** now re-reads `[vr] HeadTrack` and `Layers` too.
- Installed on the dev PC: `d3d9.dll` `038c168ed96d` (old `95512af70511` kept beside it as a dated backup), ini gets
  `Fused=1` (still off until numpad 7). Stamped.

## NOT established

- That the fused matrices are uploaded in the same register blocks this hook sees (the census says they are vertex
  constants, so they should be). The log line `fused: N fused camera matrices` answers it on the first run.
- That no spot-light shadow passes the camera test. The residual case is a light with the camera's near plane that
  looks exactly along a world axis; the tell would be shadows that swim or split between the eyes.
- The fog and light-cone deferred passes: they also read `g_mClipToView`, which already gets the matching inverse;
  whether that is enough is a live question.

## The one test that decides it (flat, dev PC, no headset needed)

Launch with the installed build, walk to the "Get to the lighthouse" road, press numpad 7:
- road, trees and Alan all shift together, the log shows `fused: N` growing → the two halves are joined;
- `fused: 0 ... NONE FOUND` → the fused matrices are not reaching this hook (then the census register list is next);
- trees or particles jump while Alan is right → a fused window was mis-split (send the log line and a picture).
