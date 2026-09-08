# 2026-09-08g — `-rigidcamera` changes nothing, because there is no bob to remove

*Session: `/lm alan-wake-vr`, dev PC, one launch (the control half), fully autonomous.*

**The A/B is complete and the answer is a clean, well-scoped negative.** Alan Wake's third-person
camera has **no translational bob or sway while walking forward**, with or without the flag — so
`-rigidcamera` cannot be the comfort win its name suggested, and the flat comfort angle closes.

---

## 1. Both halves, measured by the same code

The two halves were run a session apart, so the measurement itself was made a shared fixture first:
`dev-archive/tools/awbob.py` captures and measures, and **both halves ran that same file**. Without
that, a difference in the numbers could have been a difference in my arithmetic rather than in the
game.

| | treatment (`-rigidcamera`) | control (no flags) |
| --- | --- | --- |
| vertical `dy`, mean / max | **0.00 / 0 px** | **0.00 / 0 px** |
| horizontal `dx`, mean / max | **0.00 / 0 px** | **0.00 / 0 px** |
| per-pair correlation | 0.911 – 0.993 | 0.927 – 0.993 |
| frame-to-frame luma delta | 1.97 – 4.47 | 1.94 – 4.21 |
| frame pairs | 13 | 13 |

`[measured 2026-09-08, n=2 runs, 13 frame pairs each]`

Same save point, same walk (hold `W`), same 14-frame burst, same window size (1280×720), same
deployed proxy and **the same `d3d9_proxy.ini` left untouched** — the two runs differ in the launch
flags and nothing else.

## 2. Why the null is worth believing

A row of zeros is worthless unless it could have been non-zero. `awbob.py` prints two guards
alongside the numbers, and both passed in both runs:

- **The frames were changing.** Consecutive frame-to-frame mean |luma delta| ran 1.94–4.47, so the
  game was rendering and Alan was walking — the capture did not simply outrun the frame rate.
- **The estimator can see a shift.** Injecting known ±1, ±3 and ±8 px offsets into a real frame
  recovered every magnitude exactly. It is not blind.

A third check fell out of the control run for free: **the main menu had six rows and no
`[Developer Menu]`**, where the flagged run had seven. That confirms the flags really were absent
this time, i.e. the control is a control.

## 3. What this does and does not establish

**Established:** no measurable camera *translation* — vertical or horizontal — while walking forward,
in either configuration. So `-rigidcamera` has nothing to remove along those axes, and the "camera
without bob/sway is the commonest comfort win" hypothesis does not apply to this game's walk.

**NOT established, and deliberately not claimed:**

- **Rotation.** Only translation was measured. `-rigidcamera` could still affect camera *roll*, or
  rotational smoothing/lag, and neither was tested.
- **Other motions.** Only walking forward on a flat road. Running, strafing, stairs, combat,
  vehicle sections and scripted set-pieces are untested.
- **`-noblur`** was armed in the treatment run and **never tested at all** — motion blur shows during
  fast camera rotation, and neither run rotated the camera. It remains an open, cheap question.

⚠️ A third-person camera having little translational bob is unsurprising in hindsight — the character
absorbs the gait, not the camera. That is a reason the null is *plausible*, not extra evidence for
it; the evidence is the table above.

## 4. Automation

| capability | status |
| --- | --- |
| 1. menu → gameplay | ✅ proven again (6-row menu this time) |
| 2. console / exec commands | **N/A** — no console on this game |
| 3. character + camera | ✅ character movement drove the capture; camera rotation not exercised |
| 4. self-close | ✅ graceful through the game's own menu, no `taskkill` |

## 5. What is left

Nothing on the flat comfort angle. The two remaining `[FLAT]` rows are both near-retirement (the
Steam-overlay slot-16 curiosity, and a breakpoint blocked behind the x64dbg `[USER]` row), so **this
project now needs a new idea about where the on-screen transform lives** — the constant path is a
proven dead end (§6f), the 3D Vision path is retired (§6g), and the developer menu is a cheat menu.

The one cheap live question still outstanding is `-noblur`, which would ride along with any future
launch rather than justify one of its own.

Evidence: `dev-archive/recon/2026-09-08g-rigidcamera-ab-there-is-no-bob-to-remove/` — the full
`awbob.py` output for both halves, plus the first and last frames of each burst (the middle frames
were dropped to keep the repo small; the measurements are the durable part).
