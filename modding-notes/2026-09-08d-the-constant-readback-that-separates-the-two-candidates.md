# The constant read-back that separates the two candidates

`/pd`, dev PC, 2026-09-08d. **The game was not launched. Nothing in this note has been run.**

Source: `staging/alan-wake-vr/proxy-d3d9/src/proxy.c`. Deployed `d3d9.dll` md5 `8ad54c58…`,
223,232 B, with a dated backup.

## The question

2026-09-08c left the project at a clean fork. The shear is armed with the correct, live-measured
signature, it applies **1,661,102 times** with `0` oversize refusals, and the rendered frame is
**unchanged** — far and near depth bands both `+0 px` at corr 0.91 against a predicted 351 px
`[verified-numerically 2026-09-08, n=2 launches]`. Two candidates, deliberately not collapsed into
one story:

1. **The engine re-uploads the camera constants after our edit**, by a path that is not
   `SetVertexShaderConstantF`. Our hook would never see it, and the GPU would draw with the
   engine's matrix.
2. **These constants are not what produces the on-screen transform** — the `mad-max-vr` §7 shape,
   *"the transform is in NEITHER buffer"*. Our edit reaches the draw intact and simply does not
   matter.

Both predict exactly the same thing on screen: nothing moves. **The only place they differ is in
what the device holds at draw time**, and that is readable.

## What was built

A read-back instrument. When the shear edits a block, the proxy now remembers three things — the
absolute register it wrote, the sheared 4×4 it put there, and the engine's original 4×4 — and then,
at the next draw, asks the device what that register actually contains.

```
SetVertexShaderConstantF hook  ->  edit applied  ->  arm the read-back
DrawPrimitive / DrawIndexedPrimitive hook  ->  GetVertexShaderConstantF(reg, 4)  ->  verdict
```

Four verdicts, each with a distinct meaning:

| verdict | what the device holds | conclusion |
| --- | --- | --- |
| **`SURVIVED`** | our sheared matrix | the edit reaches the draw ⇒ **candidate (2)**, wrong buffer entirely |
| **`RESTORED`** | the engine's original matrix, exactly | something re-uploaded it ⇒ **candidate (1)**; a state-block `Apply` is the first suspect |
| **`OVERWRITTEN`** | neither | also candidate (1), but the writer is not simply restoring — the register is shared |
| **`UNAVAILABLE`** | `Get` refused | the instrument cannot answer; see the pure-device note below |

Distinguishing `RESTORED` from `OVERWRITTEN` is why the original values are kept as well as ours.
"Not our value" would have collapsed a re-upload and a third-party write into one answer.

### Three design decisions worth stating

**Read *before* the draw is forwarded, not after.** The row asked for a read-back "immediately after
the draw". Reading immediately *before* forwarding is the same device state and is strictly the more
precise instrument, because it is the state **that draw** consumes; nothing between the read and the
real call can change it.

**Exact float comparison, no tolerance.** These are the same bits handed to the runtime moments
earlier, not a recomputation. Any tolerance would only blur the distinction the instrument exists
to draw.

**First occurrence of *each* verdict is logged, and the counts go in the 5 s line.** A mixed result —
some draws survive, some do not — is itself an answer, and would have been hidden by a single
"first verdict" line. This is the same defect that made the 09-08c instrument discard ~3M
observations including the answer: **n=1 decides nothing, and a counter nobody prints is not
evidence.**

## The pure-device caveat, handled rather than discovered later

D3D9 refuses `Get*` on shader constants when the device was created with **`D3DCREATE_PUREDEVICE`**.
That would make this instrument silently useless, so the proxy now records `BehaviorFlags` at
`CreateDevice` and says outright which case it is:

- pure → the `UNAVAILABLE` line names `PUREDEVICE` as the cause and points at the `-developermenu`
  stereo route as the fallback, which does not depend on the constant-buffer path at all;
- not pure → an `UNAVAILABLE` verdict is flagged as **unexpected, and a finding in its own right**
  rather than a limitation to work around.

⚠️ **Which case this game is in is not yet known** — the flags are logged, not predicted. If it is a
pure device, this whole instrument answers nothing and the fallback row becomes the live one.
`[hypothesis]`

## Vtable slots: verified, not assumed — and the check is proven able to fail

The instrument needs three more slots. All four device slots now carry **compile-time assertions**
against the SDK header's own `IDirect3DDevice9Vtbl`, using the negative-array idiom already used in
this file for `IDirect3D9Vtbl` slot 16:

| slot | method |
| --- | --- |
| 81 | `DrawPrimitive` |
| 82 | `DrawIndexedPrimitive` |
| 94 | `SetVertexShaderConstantF` — previously only a *comment* claiming it was verified |
| 95 | `GetVertexShaderConstantF` |

**The assertion was tested by deliberately breaking it**: changing 82 to 83 fails the build with
`'dev_drawindexedprim_slot_check' declared as an array with a negative size`, and restoring it
builds clean. A check that cannot fail is not a check. `[compile-verified 2026-09-08]`

## Cost, and why the 09-08c numbers stay comparable

Both draw entry points are hooked, because a renderer using only `DrawPrimitive` would otherwise be
measured zero times and look like silence rather than a missing hook. Draws are the hottest path in
the renderer, so:

- **When stereo is OFF, nothing is hooked at all.** The instrument-only hot path is byte-for-byte
  the behaviour the 09-08c measurements were taken with, which keeps those numbers comparable.
- When stereo is ON, the check runs on the first **8** draws outright — so a short run still answers —
  then on one draw in **500**. The `Get` never sits on every draw.

Every new hook carries the same foreign-slot guard as the rest of the file, and comes back out of
the vtable on unload under the same lifetime rule — the one whose absence caused the 2026-08-25
crash. A layered hook is refused and logged rather than clobbered.

### One defect this session's own self-review caught

The first version nulled `real_DrawPrim` / `real_DrawIndexedPrim` / `real_GetVSConstF` on unload,
mirroring what `remove_vsconst_hook()` already does for `real_SetVSConstF`. That is wrong here, and
in a way that only shows up in the case the code around it is explicitly written to survive:
**restoring the slot makes our hook unreachable through the vtable, so the only way it can still be
entered is a foreign hook layered on top of it** — precisely the case logged one line earlier — and
in that case the real pointer is exactly what it needs to forward to. Nulling turned "this unload is
not safe" into a **null call on the next draw**. The pointers are now deliberately left in place,
with a comment saying why.

Caught by asking what the new hooks and the existing ones do to each other, which is the only reason
it was found: nothing about it fails a build or a self-test.

## Verification

- Builds clean under `-Wall` for PE32/i386, export table intact `[compile-verified 2026-09-08]`.
- The four vtable assertions pass, and one was proven able to fail.
- The existing host self-test suite (`build-selftest.sh`, `stereo` + `ctab`) still reports
  **ALL CHECKS PASSED** — the regression net over `aw_stereo_apply_block`, which this change does
  not touch.
- **The deployed binary was checked before being overwritten**, the way `CONVENTIONS.md` asks:
  a fresh build of the pre-session source is **md5-identical** to what was installed
  (`0dfdf78b77e9…`), so the stamp was honest and the `--no-insert-timestamp` reproducibility holds.
  `[verified-numerically 2026-09-08]`

**Nothing here has been run in the game.** The instrument is a question, not an answer.

## What the next launch does, and what each outcome means

**No configuration change is needed.** The live `d3d9_proxy.ini` already carries
`Enabled=1 / EyeDx=2.0 / Convergence=5.0 / MatchXS=0.915689 / MatchYS=1.627892`, so the shear arms
and the read-back arms with it. Launch, reach gameplay, quit, read the log.

Look for the `readback:` lines and the `readback:` counts in the 5 s summary:

| log line | what to do next |
| --- | --- |
| `SURVIVED` dominant | **Candidate (2).** Stop editing this buffer. The transform reaching the screen is elsewhere — the `-developermenu` stereo route becomes the live row, and the shipped-shader route is worth re-reading. |
| `RESTORED` dominant | **Candidate (1).** The edit must move later in the frame. Next build hooks the re-upload path; a state-block `Apply` is the first suspect, then `SetVertexShaderConstantI/B`. |
| `OVERWRITTEN` dominant | Candidate (1) with a shared register. Same move, but log the third value to identify the writer. |
| `UNAVAILABLE` + `PUREDEVICE` | The instrument cannot answer here. Fall back to `-developermenu`. |
| `NEVER CHECKED` | Either no edit armed, or no draw came through our hooks — check the `readback: … DrawPrimitive=hooked` install line first. |

⚠️ **Read the counts, not the first line.** A mixed result is a real possibility and is more
informative than either pure answer: it would mean the camera register is re-uploaded on some draws
and not others, which points at a specific pass rather than at the whole frame.

## What is NOT established

- Which candidate is true. That is the launch above.
- Whether the shear is mathematically correct. It still has never had the chance to be wrong on
  screen, and a `SURVIVED` verdict would not vindicate it either.
- Whether the device is pure. Logged, not predicted.
