# 2026-10-10 home PC, real headset (Quest 3 via Virtual Desktop, worn by nobody: sensor covered)

- OpenXR: "Device is: Meta Quest 3", session running, frames to the headset at ~72/s (6301 -> 7201 in 12.5 s)
  `[verified-live 2026-10-10, n=1]`.
- Stereo NEVER MATCHED with the dev PC's MatchXS/YS (0.915689/1.627892). The home PC's live camera signature is
  xs=1.208792 ys=2.148964 (c0/c7/c192, ys/xs 1.7778): a narrower game FOV here. With those values (numpad 7 live
  reload) the edit applies (~80k edits/s) `[verified-live 2026-10-10, n=1]`.
- BUT with the edit ON the picture breaks: Alan's model disappears, the street-light cones and fog go, trees behind
  the fog show (aw_cmp.png top = off, bottom = on). Same with HeadTrack=0 written before the reload (aw_cmp2.png),
  if HeadTrack is reloaded live at all `[hypothesis]`. Readback: every check "overwritten" (c192 shared).
  Suspect: the signature now also matches passes that share the camera's projection (fog/volumetric/character),
  or the FOV-dependent constants differ from the dev PC's run `[hypothesis]`.
- The ini on the home PC now carries the home values (d3d9_proxy.home.ini). Video:
  MEGA Videos/alan-wake-vr/headset first look_2026-10-10_21-35-51.mp4 (flat window).
