# 2026-09-08e — the read-back settles the fork, and a blatant probe closes the third possibility the fork did not list

*Session: `/lm alan-wake-vr`, dev PC (DESKTOP-V8GTSIR), two launches, fully autonomous.
The `/pd` that ran between 09-08c and this session built AND deployed the read-back; this session
ran it, found the fork was under-specified, built the discriminator, and ran that too.*

**Result: the D3D9 vertex-shader constant path is NOT the lever for this game.** That is now
supported by an edit too blatant to be missed, not just by a subtle shear that moved nothing.

---

## 1. The read-back ran, and PUREDEVICE did not bite

The build warned at `CreateDevice`:

```
BehaviorFlags=0x54  <-- PUREDEVICE: D3D9 refuses Get* on shader constants on a pure device,
                        so the constant read-back cannot answer here
readback: Get=73725480 DrawPrimitive=hooked DrawIndexedPrimitive=hooked.
          The device is PURE, so Get is expected to REFUSE; the first check will say so.
```

`0x54` = `HARDWARE_VERTEXPROCESSING | PUREDEVICE | MULTITHREADED`, so the warning was correctly
raised. **It did not happen** — `unavailable=0` across 11 701 checks
`[verified-live 2026-09-08, n=1 launch]`. The compile-time expectation was pessimistic;
`GetVertexShaderConstantF` answered fine on this device. Worth recording so nobody stands the
instrument down on that basis.

⚠️ At the menu the first summary read `readback: 0 check(s) over 1088 draw(s) — NEVER CHECKED` and
`stereo: 0 edit(s) — NEVER MATCHED`. That is **expected, not a failure**: the camera projection is
not uploaded at the menu. Do not read the menu summary as a verdict; reach gameplay.

## 2. The verdict, in gameplay

```
readback: 11701 check(s) over 12806104 draw(s) - survived=4992 restored=0 overwritten=6709 unavailable=0
stereo:   2018199 edit(s) applied in total, 0 upload(s) refused as oversize
```

Individual first-sightings: `SURVIVED at c7`, `OVERWRITTEN at c0`.

- **`restored=0`, exactly, over 11 701 checks ⇒ candidate (1) is DISPROVED**
  `[verified-numerically 2026-09-08, n=1 launch, 11701 checks]`. Nothing ever puts the engine's
  original matrix back. There is no re-upload by a second path, no state-block `Apply` restoring it.
- **`survived=4992` (42.7 %)** — in those draws the device demonstrably held **our** sheared matrix
  at draw time.
- **`overwritten=6709` (57.3 %)** — a third value. Consistent with `c0` being a shared register
  block that many passes rewrite; the last writer before a given draw is often someone else. This is
  about register reuse, not about the engine defending its camera.

And the frame was unchanged, again: far `+0 px` (corr 0.87), mid `+0 px`, near `+0 px` (corr 0.92)
against the stereo-OFF baseline at the same save point — now **n=3 launches**.

## 3. ⚠️ The fork was under-specified, and I nearly wrote the wrong conclusion

The board's reading table said `SURVIVED ⇒ candidate 2, the wrong buffer entirely`. That does not
follow, and the gap matters:

> **The read-back proves our BYTES are in the device at draw time. It does not prove they were the
> RIGHT BYTES to change.** If `stereo.c`'s shear writes an element that does not affect the image
> under this matrix's real layout, then *survived + nothing moves* is exactly what the **correct**
> buffer would look like too.

So "survived" is consistent with **two** stories, not one:

1. the buffer is not what the screen uses (candidate 2), or
2. the buffer IS live and the shear was writing a dead element — which would make it a `stereo.c`
   layout bug, and a **much better** outcome, because the lever would exist.

## 4. The discriminator, and the answer

Separating them is cheap, because there is one element whose location is **not** in doubt: `p[0]`,
the value the matcher itself keys on. Scaling it changes the horizontal FOV and cannot depend on
getting the layout right.

Built `aw_stereo_probe_block()` + `[stereo] ProbeScaleXS` (diagnostic, off unless set). Deployed
`da469d74bc5b`, 224 256 B, stamped, with `ProbeScaleXS=0.5`. Self-tests re-run: all pass.

```
stereo: PROBE MODE - scaling p[0] by 0.500 instead of shearing.
stereo: 2298221 edit(s) applied in total, 0 upload(s) refused as oversize
```

**Result: no geometric change whatsoever** `[verified-numerically 2026-09-08, n=1 launch]`:

| test | result |
| --- | --- |
| horizontal **scale** search, 0.50 → 2.25 | **best f = 1.00** (corr 0.855). A halved `p[0]` doubles `tan(hfov/2)`; nothing. |
| horizontal **shift**, far band | `+0 px` (corr 0.854) |
| horizontal **shift**, mid band | `+0 px` (corr 0.730) |
| horizontal **shift**, near band | `+0 px` (corr 0.962) |

⚠️ **I read this frame as "it changed!" by eye first, and was wrong — for the second time today.**
The probe frame *looks* different because the scene's lighting and Alan's pose differ between runs;
geometrically it is identical. The scale search is what settled it. The standing "judge by eye"
guidance is about *decisive* observations; when the alternative hypothesis predicts a scene that
also looks different, the eye is not decisive and a number is.

**⇒ Candidate (2) confirmed.** Story 2 is eliminated: the element we scaled is the one we match on,
so it cannot have been the wrong element. 2.3 M edits to the matched windows, provably resident at
draw time, produce no change on screen. **These vertex-shader constants are not what produces the
on-screen transform in Alan Wake.**

## 5. What that closes, and what it costs

- **Stop editing this buffer.** The whole `SetVertexShaderConstantF` line — 09-07's wiring, 09-08c's
  signature hunt, 09-08d's read-back — has produced a definite negative. The instrument work was not
  wasted (it is what made the negative *provable*), but the lever is elsewhere.
- **`-developermenu` is now the live row**, and it is the only remaining flat row that never depended
  on the constant path. `/gr` reported `Stereo Rendering:Override / Enable / Separation /
  Convergence / Eye Separation` behind it `[reported]`.
- **NOT established: where the transform actually is.** Candidates not yet examined: a preshader or
  shader-internal recomputation; constants uploaded by a path that is not
  `SetVertexShaderConstantF`; or the engine's own stereo settings being the intended entry point.

## 6. Automation

| capability | status |
| --- | --- |
| 1. menu → gameplay | ✅ proven, `n=2` more loads this session |
| 2. console / exec commands | **N/A** — no console; the ini is read at load only, so every config change costs a relaunch |
| 3. character + camera | ✅ proven 09-08c; not needed this session |
| 4. self-close | ✅ proven, `n=2` this session, graceful, no `taskkill` |

The 09-08c click-before-every-key rule held throughout both launches; `awkeys.py` drove every menu
step and every destructive step was capture-verified before Enter.

## 7. What to run next time

**`-developermenu`**: add the flag to the launch, and look for
`Stereo Rendering:Override / Enable / Separation / Convergence / Eye Separation`. If those exist and
respond, the game ships its own stereo path and this project changes shape entirely. If the menu
does not appear, that closes the last cheap flat row and the project needs a new idea rather than a
new probe.

To go back to the shear at any point, set `[stereo] ProbeScaleXS=0` — the probe is diagnostic only.

Evidence: `dev-archive/recon/2026-09-08e-the-readback-answers-the-fork-and-the-blatant-probe-confirms-it/`.
