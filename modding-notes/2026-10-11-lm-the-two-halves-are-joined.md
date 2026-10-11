# 2026-10-11 (dev PC, `/lm`, three launches): the two halves are joined

Follows `2026-10-11-pd-the-scene-is-two-halves.md`. Evidence: `dev-archive/recon/2026-10-11-the-two-halves-joined/`.
Videos (game window only): `E:\OBS gameplay videos\alan-wake-vr\` (`two-halves-test`, `two-halves-noblur`,
`head-turn-sim`, `match-by-shape`).

## Results

1. **Flat, numpad 7, 30 cm eye shift, `-noblur`.** Measured sideways shift per region (best correlation against the
   "off" frame). `Fused=0`: the near fence and sign move 47 px, the road edge and treetops 0 px. `Fused=1`: fence 47,
   treetops 51, road 18, Alan (nearer than the 3 m convergence) -7 px the other way. One consistent depth order
   `[measured 2026-10-11, n=2 frames each]`.
2. **At 2 m eye shift, `Fused=0`, Alan vanished**, exactly the home headset picture; `Fused=1` brought him back
   `[verified-live 2026-10-11, n=1]`.
3. **OpenXR simulator.** Head 40° to the side and 20° down when the edit switched on: re-centred, looking straight down
   the road, scene whole. A further 25° turn turned everything together. Control with `Fused=0`, same turn: road
   still, Alan, rocks and sign floating in the sky `[verified-live 2026-10-11, n=1 each]`.
4. **Match by shape** (`MatchAspect=1.7778`, the camera numbers blanked): the mod found the camera on its own
   (xs 0.915689, ys 1.627892) and everything above still worked `[verified-live 2026-10-11, n=1]`. The home PC no
   longer needs its own `MatchXS/MatchYS`.

## The reader (one background helper)

- Job 1: all 515 fused matrices sit in registers the hook sees, in the layout `fused.c` assumes (dossier §6l)
  `[measured 2026-10-11]`.
- Job 2: wrote and tested `MatchAspect` (staging, 7,015 checks); run live in result 4.

## Automation (five capabilities)

- Self-launch: ✅ `steam://run/108710//-noblur/`; Steam's "custom arguments" box appeared on the first two launches
  and was confirmed by clicking Continue (0.581, 0.602 of the Steam window); the third launch had no box.
- Menu → gameplay: ✅ with the recorded route, but its `remedy_logo` checkpoint never matched (the logo passes before
  the check) and `title_press_key` sometimes misses: restart with `--from 2`, `--from 4` or `--from 6` after a look.
  ⚠️ Moving the game window left the mouse pointer over "Episodes", which moved the menu highlight: park the pointer
  outside the window before Enter.
- Commands: N/A (no console). Numpad 7 via SendInput works without a click (GetAsyncKeyState).
- Character + camera: not needed (still camera; head turns came from the simulator).
- Self-close: ✅ `gameplay_to_desktop`, three times.

## NOT established

- Anything in the real headset (home PC).
- The street-lamp glow sprites stayed put through the eye shift and the head turn: a screen-space path, not yet found.
- Whether both eyes alternate correctly in the flat captures (both captures each time caught the same eye).
