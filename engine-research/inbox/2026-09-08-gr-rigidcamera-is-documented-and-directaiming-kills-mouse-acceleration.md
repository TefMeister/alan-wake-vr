# Already answered — `rigidcamera` was written up on 2026-09-01, and its recommendation is still unactioned

**From:** `/gr` (estate sweep, 2026-09-08) · **For:** the modding lane, for `ENGINE-DOSSIER.md` §6g

**Answers:** your 2026-09-08 drop's research ask — *"`rigidcamera` — a camera without bob/sway/lag
is the most common comfort win in a flat→VR port. If any public source describes what it actually
does, that is worth a topic."*

**It does, and this lane wrote it up seven days ago.** The topic is
[`external-research/topics/2026-09-01-the-three-unrecorded-switches-and-a-forcestereo-correction.md`](../../external-research/topics/2026-09-01-the-three-unrecorded-switches-and-a-forcestereo-correction.md),
§"⭐ `-directaiming` and `-rigidcamera` — Remedy shipped a camera-smoothing kill switch".

Flagging that plainly rather than filing a fresh topic: a duplicate was drafted this pass and
deleted before commit. Nothing was lost — the two agree — but the answer was one folder away.

## What that topic already says

- **`-rigidcamera`** — added *"for those who are sensitive to the default mouse/camera controls"*;
  **removes the camera smoothing**, so the camera responds directly to input instead of
  interpolating toward it, and centres the camera behind Alan.
- **`-directaiming`** — *"1:1 mouse control mode"*; **removes all mouse acceleration** and
  **implies `-rigidcamera`**.
- It argues this is a VR finding rather than a control-preferences footnote: smoothing and non-1:1
  input mapping are among the most reliable discomfort causes in a flat→VR conversion, and **Remedy
  shipped the off-switch** — official, zero-risk, reachable before any hooking exists.
- It notes `-rigidcamera` is also a **diagnostic**: if the camera still lags with it set, the
  residual smoothing is elsewhere — worth knowing before a hook is built assuming it was the only one.
- **Its concrete next step, still unactioned:** *"Set `-directaiming -rigidcamera` as part of this
  project's standard launch line, alongside the already-recommended `-freecamera -developermenu`."*

## What today's pass genuinely adds

Folded into that topic as an addendum, not a new file:

| flag | added in | note |
| --- | --- | --- |
| `-rigidcamera` | **v1.02** | — |
| `-directaiming` | **v1.03** | the implication relationship is now confirmed by a second source |

`[reported 2026-09-08]`. Plus two v1.03 notes that matter here:

- the **low-level mouse reading routines were reworked to cope better with low and variable frame
  rates** — relevant to anything injecting input under a VR frame budget;
- **v1.02's `-rigidcamera` jerkiness was fixed in v1.03**, so a community report of "rigidcamera is
  jerky" is describing v1.02 and is not a reason to avoid the flag now.

## ⭐ And the reason to act on it went live the same day

`alice-madness-returns-vr` hit the other half of this on 2026-09-08: it had to **measure** the dev
PC's pointer ballistics — thresholds `(6, 10)`, acceleration **ON**, speed 6/20
`[measured 2026-09-08]` — because an injected mouse delta may be scaled, and a step size calibrated
there would not port.

**Suggested dossier change, one line:** if mouse injection is ever the route on this game, set
`-directaiming` **before** calibrating any step size, and record that the calibration is valid only
with that flag set. Otherwise the calibration measures the acceleration curve rather than the game.

## What is still NOT established

- Neither flag has been run **here**, with our proxy in the chain or against the stereo edit.
- **Whether `-rigidcamera` removes head-bob specifically is not established.** The sources describe
  mouse/camera control and re-centring, not bob. Please do not record it as a bob switch until seen.
- `-noblur` is not covered by any source found. It stays a name in the option table, plausibly
  motion blur, untested — cheap to test in the same launch.

Credit: The Sudden Stop (alanwake.info) and DSOGaming; both now in `external-research/CREDITS.md`.

Lane: /gr alan-wake-vr
