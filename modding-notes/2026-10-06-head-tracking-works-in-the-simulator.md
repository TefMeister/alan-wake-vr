# 2026-10-06 (late evening): head tracking works in the simulator

Dev PC, `/lm`, one launch. Tefa pressed OK on Steam's launch-options pop-up (it waits for a person).

## What was tested

Alan Wake with alternate-frame eyes, per-eye lighting, and the new head tracking, sending each eye to the OpenXR
simulator as a full per-eye view (no floating screen any more). The simulated head was turned, tilted up and tilted
sideways.

## What happened

- Head turned 30° right: the world slides left in both eyes.
- Head tilted up 15°: the world moves down in both eyes.
- Head tilted sideways 15°: the world tilts, the HUD stays level.
`[verified-live 2026-10-06, n=1 each]`

All three are the right way round for a headset. One picture taken mid-turn showed a hard-edged bright patch in one
eye; the next picture was clean (probably that eye a frame behind).

## Not established

- How it looks and feels in a real headset (comfort, depth, which way the tilt feels).
- Particles, foliage and some terrain (the "fused" shaders) still ignore the eye shift and head turn.

Evidence: `dev-archive/recon/2026-10-06-head-tracking-in-the-simulator/`.
