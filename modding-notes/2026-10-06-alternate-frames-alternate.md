# 2026-10-06 (evening): alternate frames alternate

Dev PC, `/lm`, one launch.

## What was tested

The alternate-frame mode built earlier today (one frame for the left eye, the next for the right) was switched on
with a larger-than-real eye distance so the difference is easy to see.

## What happened

- The hook that marks the end of each frame fires about 60 times a second, so the game finishes its frames the way
  the code expected. `[verified-live 2026-10-06, n=1]`
- With the edit on, twelve quick screen grabs fall into two groups. Between them the far fence and road sign sit
  about 160 pixels apart, while Alan, standing about 3 metres away (the focus distance), stays put. HUD fixed.
  That is left eye, right eye, left eye, right eye. `[verified-live 2026-10-06, n=1]`
- On a flat monitor this just looks like flicker; that is expected. It only makes sense in a headset.
- The lamp glow stays the same in both eyes, the known flat-effect gap.

## Next

- Send each eye's frames to the headset (OpenXR).
- The lighting maths per eye (the background helper is building it).

## Not established

- Anything in a headset.
- Comfort at half frame rate per eye.

Evidence: `dev-archive/recon/2026-10-06-alternate-frame-stereo-first-run/`.
