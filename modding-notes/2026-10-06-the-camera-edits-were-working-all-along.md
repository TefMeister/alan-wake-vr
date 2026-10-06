# 2026-10-06: the camera edits were working all along

Dev PC, `/lm`, run on Opus although the board row asked for Fable (Tefa's instruction for the dev PC).

## The short version

Since 8 September the board said the camera route was a dead end: we edited the camera's lens values more than
two million times and "zero pixels moved". That was wrong. The edits did move the picture. The old tests compared
two separate game launches, and Alan's camera stood somewhere else each time, so the comparison could not see the
difference.

## How it was found

- Looking at the old 8 September pictures by eye: with the "halve the lens width" test on, Alan is half as wide as
  normal compared with his height. Moving the camera cannot do that; only the edit can.
- So I built a key (numpad 7) that switches the edit on and off **while the game runs**, and took pictures a second
  apart from the same spot.

## What it showed

- **Squeeze test on:** the whole world and Alan squeeze toward the middle, the HUD stays put. Off: back to normal.
  Done twice. `[verified-live 2026-10-06, n=2 cycles]`
- **One-eye shift on:** Alan (close) moves left, the far fence and sign move right, the middle distance barely moves.
  That is exactly one eye of a 3D pair. Off: back to normal. `[verified-live 2026-10-06, n=1]`
- **The street-lamp glow did not move.** It is a flat screen effect, a separate job.

## What it means

Alan Wake is back on track. The camera maths written in September works in the game. What is left is the big step:
drawing **two** eyes each frame, plus the flat screen effects, plus sensible eye-distance numbers.

## Also done

- Music muted (Options -> Audio).
- The hotkey re-reads the settings file each time it switches on, so values can be tried without restarting.

## Not established

- How to draw two eyes per frame in this renderer.
- The real-world unit of the eye-distance setting.
- Anything in a headset.

Evidence: `dev-archive/recon/2026-10-06-the-camera-edits-were-working-all-along/`. Dossier §6h.
