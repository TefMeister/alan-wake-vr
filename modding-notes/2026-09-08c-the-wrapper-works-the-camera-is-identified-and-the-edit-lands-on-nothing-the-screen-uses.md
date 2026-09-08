# 2026-09-08c — the wrapper works, the camera is identified, and 1.66 M edits land on something the screen does not use

*Session: `/lm alan-wake-vr`, dev PC (DESKTOP-V8GTSIR), four launches, fully autonomous.
The user launched nothing: they granted "launch and close as you please" for this session only.*

---

## 1. The headline: the blocker is gone

The 2026-09-08b wrapper build was compile-verified only. It is now **verified live**
`[verified-live 2026-09-08, n=4 launches]`. All three lines the board asked for appeared, and the
fourth — the feared one — did not:

```
returning OUR IDirect3D9 06E35C28 wrapping the real 06EADCB0. Nothing was written into a
  shared vtable, so no other hook can be ahead of us ...
IDirect3D9::CreateDevice (through OUR wrapper): Adapter=0 DeviceType=1 ... windowed=1
SetVertexShaderConstantF hook installed at device vtable slot 94 (real=73728CC0)
```

No `REFUSING to hook IDirect3DDevice9 slot …`. **The device vtable slot was not contested**, so the
device does not need the same wrapper treatment — the question 09-08b left open is answered, and
answered the cheap way. `slot_is_foreign()` still guards it and still stood down on nothing.

Every previous launch of this project ended at `REFUSING to hook IDirect3D9 slot 16` (Steam overlay,
then `apphelp.dll`). That whole line of investigation is now **moot rather than solved** — we stopped
competing for the slot instead of winning it.

## 2. The camera is identified, live, and the old instrument could never have found it

```
LIVE perspective signatures this period (reg xs ys ys/xs n):
  [c0   0.915689 1.627892 1.7778 n=163051]
  [c192 0.915689 1.627892 1.7778 n=64149]
```

**`ys/xs = 1.7778` is exactly 16:9, the display aspect — that is what identifies the camera**
`[measured 2026-09-08, n=2 launches]`. The other perspective-shaped signatures in the same frame are
square (`1.000000/1.000000`, `2.414214/2.414214` = a 90° cube/shadow face) or nonsense
(`19.77/-3.00` at c81, `19.92/2.65` at c87). It appears at **both `c0` and `c192`**, which is the
2026-09-05 census finding — the skinning palette pushes it to c192 in skinned shaders — now seen in
a single frame rather than inferred across runs.

Camera lens, for the record: `hfov = 2·atan(1/0.915689) = 95.0°`, `vfov = 63.1°` at 16:9.

### The instrument was silently throwing away three million observations

The distinct-signature table logs each signature **once**. That is right for "which projections
exist" and **wrong for "what is the camera doing now"**: the load-in FOV settle animation walks
monotonically through ~16 distinct signatures (`xs` 1.035317 → 0.926827, still converging),
**fills all 24 slots**, and every signature after that is dropped — including the settled gameplay
FOV, which is the one value the stereo ini needs. `g_sig_dropped` counted the drops and **was never
printed anywhere**, so the log could not even report that it had happened.

Measured after the fix: **`24/24 slots used, 2 977 773 dropped`** `[measured 2026-09-08]`.

The numbers matter, because the old instrument's *last* logged value was `xs=0.926827` and the truth
is `xs=0.915689`. They differ by **0.011**; `aw_sig_same()`'s tolerance is `1e-4·(|a|+1) ≈ 0.0002`,
**55× smaller**. Configuring the ini from the old log would have produced a silent no-match, and the
row would have read as "the shear does not work" when the real fault was the reading.

⚠️ **This is the same defect class the project keeps finding** (the 09-05 register-keyed instrument
that hid c0; the non-reproducible builds). A counter incremented and never printed is a negative
result that cannot be distinguished from an absent one.

**Fix (this session):** the periodic 5 s line now also prints the **last** perspective signature seen
at each register in that period, with `ys/xs`, plus the table's occupancy and drop count.

## 3. The shear arms, lands 1.66 M times, and changes nothing on screen

With `[stereo] Enabled=1 EyeDx=2.0 Convergence=5.0 MatchXS=0.915689 MatchYS=1.627892`
(deliberately exaggerated — the question was "does it move", not "is this comfortable"):

```
stereo: ON  eye_dx=2.000000 convergence=5.000  matching xs=0.915689 ys=1.627892
stereo: FIRST edit applied - block c0+15, matrix at offset +7 (register c7), 1 window(s)
stereo: 1661102 edit(s) applied in total, 0 upload(s) refused as oversize
```

~236 000 edits per 5 s period, **zero** oversize refusals (`ST_COPY_REGS` is 256; the gameplay
flushes are 128). So the match fires constantly and the edited copy is what gets forwarded.

**And the rendered frame is unchanged** `[verified-numerically 2026-09-08, n=2 launches]`. Comparing
the stereo-OFF and stereo-ON frames at the *same* save point, per-depth-band horizontal
cross-correlation:

| band | dx | peak corr |
| --- | --- | --- |
| far — treeline / sky | **+0 px** | 0.91 |
| mid — road bend, fence, sign | −72 px | 0.75 |
| near — road surface + Alan | **+0 px** | 0.91 |

The predicted effect was a constant NDC offset `s = p00·EyeDx/Convergence = 0.3663`, i.e.
**0.183 of screen width = 351 px**. Nothing of the sort is present. The mid band's −72 px at the
*lowest* correlation of the three is fog and lighting drift between runs, not geometry — a real
global shift would move all three bands together, and the two high-confidence bands read exactly
zero.

⚠️ **I got this wrong by eye first.** My first reading of the stereo-ON frame was "Alan has moved
left, it is working" — I was comparing against a screenshot taken *after* I had walked and turned the
camera. The measurement against the correct baseline says zero. Judge by eye where the observation
is decisive; this one was not.

### What that leaves — two candidates, not one

`[hypothesis]`, and they are **not** collapsed into one story:

1. **The engine re-uploads the camera constants after our edit**, by a path that does not go through
   `SetVertexShaderConstantF` — so what we shear is overwritten before the draw.
2. **These constants are not what produces the on-screen transform.** The signature is unmistakably
   the camera projection by shape, but the vertex path that actually reaches the backbuffer may take
   it from somewhere else (a different constant slot, a preshader, or a shader that recomputes it).

This is the same shape as `mad-max-vr` §7's "large `edited` count, nothing moves ⇒ the transform is
in NEITHER buffer". The two are separated by reading the constants **back** immediately after the
draw, which is the next `[PD]` build.

**NOT established:** that the shear is mathematically wrong. It was never given the chance to be
wrong on screen. `stereo.c` remains numerically self-tested and live-untested.

## 4. Automation — the four capabilities, and a genuine surprise

| capability | status |
| --- | --- |
| 1. menu → gameplay | ✅ **PROVEN**, autonomously, `n=3` loads |
| 2. console / exec commands | **N/A** — this game has no console; the ini is read at load |
| 3. character + camera | ✅ **PROVEN for the first time on this project** |
| 4. self-close | ✅ **PROVEN, `n=4`**, graceful through the game's own menu, never `taskkill` |

### ⚠️ THE INPUT RULE: this game ignores a bare keypress. It needs a mouse click first.

Measured on the **main menu**, which is a stable state that does not auto-advance, so every result is
attributable `[verified-live 2026-09-08, n=2 each]`:

| what was sent | did the menu highlight move? |
| --- | --- |
| `SendInput` **VK** `down`, window verified foreground | **no** |
| `SendInput` **scancode** `down` | **no** |
| cursor moved *inside* the window, no click, then VK | **no** |
| **left click in the window, then VK `down`** | **YES** |
| VK `down` again with no new click | **no** |

So: **click, key, click, key.** One click does not enable input persistently — the *next* key needs
its own click. The same rule holds in gameplay: 2.5 s of `W` with no click was indistinguishable from
the no-input control (mean luma delta 2.87 vs 2.92); a click then 3 s of `W` walked Alan visibly down
the road (13.15). Camera: click then relative `MOUSEEVENTF_MOVE` turned the view ~180°.

**Why the click is needed is NOT established.** A plausible cause is that each shell command steals
foreground and the game never receives a proper activation back, with the click forcing one. Do not
record a cause; record the rule. Tool: `dev-archive/tools/awkeys.py`.

⚠️ **This CORRECTS the profile's dev-PC record.** `profiles/alan-wake.json` said scancodes worked
here on 2026-09-04 (`n=1`) and did not work on the home PC on 2026-09-05 (`n=1`). Today, on this same
dev PC, **bare scancodes did nothing and bare VK events did nothing either** — the missing ingredient
in both records may simply have been the click. The old entries are kept, not deleted.

⚠️ **And it nearly produced a false finding.** Early on I reported "VK works, scancodes do not",
because the title screen advanced right after a VK space. Then the no-input control showed the title
**auto-advances into an attract reel on its own** — 60 s of no input, no title. Every transition I
had attributed to a keypress was equally explained by the attract timeout. The attract loop makes the
title useless as a testbed; the main menu is the right one because it is stable.

## 5. Hazards found

- **The attract reel cycles title → videos → title with no input**, so the title screen cannot be
  used to test whether input works. Use the main menu.
- **`awkeys.py` clicks at 15 % window height on purpose** — the menu list lives in the lower third and
  a click there would *select* an item. The main menu's `Quit` and the pause menu's
  `Restart Checkpoint` are both one careless click away.
- Every destructive navigation this session was **capture-verified before Enter** (six times).

## 6. Deployed state

`d3d9.dll` = `6de735faf984`, 217 600 B, stamped on DESKTOP-V8GTSIR. Backups kept:
`d3d9.dll.bak-2026-09-08c-pre-livesig` (the 09-08b wrapper, `a788b9dfb94d`) and
`d3d9.dll.bak-2026-09-08d-pre-applycount`. `d3d9_proxy.ini` is left in place with the measured
camera signature and `Enabled=1`; it is a dev build and the shear is inert on screen, not harmful.

## 7. What to run next time

The next step is **static**, not a launch: make the proxy read the camera constants back immediately
after the draw and log whether our sheared values survive. `SURVIVED` ⇒ candidate 2 (the screen
transform comes from elsewhere); `OVERWRITTEN` ⇒ candidate 1 (the engine re-uploads) and the edit
must move later in the frame.

Evidence: `dev-archive/recon/2026-09-08c-the-wrapper-works-and-the-camera-is-identified/`
(four proxy logs, the ini as tested, and the stereo OFF/ON gameplay pair).
