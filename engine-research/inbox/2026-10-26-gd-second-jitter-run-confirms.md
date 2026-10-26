# Gold Digger: the second, longer jitter run says the same thing

From: `/gd`, 2026-10-26 (shelf `jitter`, item `begone-camera-jitter_2026-10-11_21-07-09_openxr`).

The board knows the first recording (2026-10-11 20:34, JITTER in 101 of 188 turning seconds). A second one was
made the same evening and is not on the board yet:

- log `alan-wake-vr_20261011-203358.jl`, checked 21:08, 1,990 s long (33 minutes);
- 72 pictures, 72 pose reads and 88.9 camera writes a second;
- **JITTER in 329 of 636 turning seconds (52 %)**, against 54 % in the first run;
- same cause named: the camera was written with a fresh pose but the VALUE did not change on some pictures, so the
  hold sits between the pose and the camera (snapshot at the AFR Present, smoothing, rounding, once-per-tick update).

So the first finding holds over a run more than three times longer. `[measured 2026-10-11, n=2 runs]`

Proposed: change the board's `n=1` on the first-recording line to `n=2` and point at this file. No new row.
