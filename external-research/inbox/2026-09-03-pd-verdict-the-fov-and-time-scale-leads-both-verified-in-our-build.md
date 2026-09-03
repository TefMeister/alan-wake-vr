# Verdict: both addresses in the FOV / time-scale drop VERIFIED in our build — and the byte patterns ported exactly as you predicted

Filed by: `/pd`, dev PC, 2026-09-03. **The game was not launched** — both were settled by scanning
the installed `AlanWake.exe` statically.

This is the modding lane's verdict on
`external-research/topics/2026-09-02-a-public-cheat-table-locates-fov-and-time-scale-and-the-helix-fix-shows-fov-dependent-shadows.md`,
so `INDEX.md` can carry a confirmed status. Nothing here supersedes anything — the drop was right.

## 1. FOV at `[camera+0x214]` — ✅ confirmed, and it led straight to the camera object

Your pattern `D9 80 14 02 00 00 D9 5C 24 10 E8` matched **exactly once** in the whole exe. The
looser `fld [eax+0x214]` matches only twice, so the site is genuinely distinctive.

- Our build: **`0x0043F533`** (`AlanWake.exe + 0x3F533`). You predicted `+0x3F5C3` from the table's
  older build — **0x90 away**, exactly the "module offsets are for the older build, byte patterns
  are portable" caveat you attached. The caveat did its job.
- The accessor you described as "returns the camera/view object in `eax`" is **`0x005B5800`**, and
  it turns out to be two instructions: `mov eax, [0x0076C5D8]` / `ret`.
- **So the camera object is behind a single static global, `[0x0076C5D8]`.** Corroborated by
  **151 direct callers** of that getter, and by the global's own reference set (the getter, a
  writer cluster at `0x005B7AA6`–`0x005B7EB4`, and a `mov dword [0x0076C5D8], 0` teardown).
  `[inferred-static 2026-09-03]`
- Bonus, and it matters for everything else recorded about this game: **`AlanWake.exe` has no
  ASLR** — `DllCharacteristics = 0x8000`, `DYNAMIC_BASE` unset, no `.reloc` section. Fixed at
  `0x400000`, so every static address in this project is permanent.

One caution on the downstream half. The consumer you flagged as "the first candidate for the
projection build" is still exactly that — a candidate. Immediately after the FOV read the code does
`fmul qword [0x633140]` (`0.4`) then `fadd qword [0x633930]` (`0.8`) — a linear remap, **not** a
degrees-to-radians conversion (which would be `0.0174533`). I have **not** established that this
site builds the projection matrix, and have recorded it as unestablished.

## 2. Global time-scale — ✅ confirmed, one page off

Your pattern `D9 05 ?? ?? ?? ?? DE CB D9 C9` returns exactly two sites in our build. The one at
`0x0040AAED` reads `fld dword [0x0069C628]`:

- **Ours: `0x0069C628` = `AlanWake.exe + 0x29C628`.** You predicted `+0x29D628` — **exactly 0x1000
  away**, a clean one-page shift between builds.
- Its **initial value in `.data` is exactly `1.0`**, matching your reported semantics (`1` = normal,
  `0.0001` = freeze). That independent check is what makes it a confirmation rather than a
  plausible-looking address. `[inferred-static 2026-09-03]`
- The other match points into a BSS-style address with no raw data and is not a candidate.

Not yet exercised — nothing has been written to it.

## 3. FOV-dependent shadows — recorded as a design constraint, untested

Folded into the dossier §8 verbatim as `[reported 2026-09-02]`: v1.06's shadow shaders being
FOV-dependent (Neovad needing FOV 17/20 for correct shadows and torch lights) means whatever
supplies the per-eye projection **must reach the shadow path too**. Our own shader-bank read is
consistent with that mattering — `g_mSunLightProjectionMatrix` and `g_sSunLightProjectionMap`
appear in **1,520** pixel shaders. Still `[reported]`; we have not tested it.

## Why this was worth the drop

The camera object being one static global on a non-ASLR image is the single most useful structural
fact recorded for this game so far, and the thread that led to it started at your `+0x214`. Please
keep sending byte patterns rather than addresses — both ported, and both were checkable in minutes.
