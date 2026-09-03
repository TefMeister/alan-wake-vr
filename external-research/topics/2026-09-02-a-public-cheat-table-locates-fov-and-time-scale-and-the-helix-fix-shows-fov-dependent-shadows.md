# A public cheat table locates the FOV field and a global time-scale; the Helix fix shows v1.06's shadows are FOV-dependent

**Status:** 🆕 new · **Priority:** high — the board's main line is now "answer §6 the ordinary way: locate
the camera and projection delivery", and this gives it a starting address in the exe instead of a cold
scan of a 1,231-export renderer DLL.

## 1. Jim2point0's Cheat Engine table — two addresses in `AlanWake.exe`

The screenshot community FRAMED hosts a table for the original game (author Jim2point0), read online as
plain XML. `[reported 2026-09-02]` — the addresses are for whichever build the author used; FRAMED's
guide says the game must be **downgraded through Steam's `download_depot`** for it to work, so treat
the module offsets as **build-specific** and the byte patterns as the portable part.

| what | where | how |
| --- | --- | --- |
| **Game speed** (float; `0.0001` = frozen, `1` = normal) | **`AlanWake.exe + 0x29D628`** (VA `0x69D628` at the default base) | a plain global; read at `AlanWake.exe + 0xAB6D` by `fld dword ptr [0x69D628]` — bytes `D9 05 28 D6 69 00`, surrounded by `D6 69 00 DE CA` … `DE CB D9 C9 DE` |
| **FOV** (float) | **`+0x214` on an object returned by a call** | at `AlanWake.exe + 0x3F5C3` (VA `0x43F5C3`): `fld dword ptr [eax+0x214]` — bytes `D9 80 14 02 00 00`, preceded by a `call` (`E8 9D 62 17 00`) and followed by `fstp dword ptr [esp+0x10]` then another `call` (`D9 5C 24 10 E8`) |

The table's FOV hook is a code-cave at that instruction that saves `eax` — **the object pointer** — and
lets the user edit `[obj+0x214]` live with numpad `+`/`−` in `0.1` steps. So the shape is:

```
call  <accessor>            ; returns the camera/view object in eax
fld   dword [eax+0x214]     ; its FOV
fstp  dword [esp+0x10]      ; passed as an argument…
call  <consumer>            ; …to whatever builds the projection from it
```

That is the same "get the camera object, read a field" shape Psychonauts' camera turned out to have,
and it is in the **exe**, not in `renderer_sf_Win32.dll` — the projection is decided game-side and handed
to the renderer. `[inferred-static 2026-09-02, from the table's bytes, n=1]`

**Why this matters for §6.** The dossier's "Where projection `P` / FOV comes from" line is empty. This
gives: a field offset for FOV, an instruction that has the camera object in `eax` every time it runs,
and the call immediately after it as the first place to look for the projection build. Pattern-scan
for `D9 80 14 02 00 00 D9 5C 24 10 E8` in the installed build; if it hits once, the accessor and the
consumer are the two `E8` targets either side of it.

**The time-scale global is a harness tool.** A frozen world (`0.0001`) with the render loop still
running is exactly what a static camera/projection probe wants — the same frame, repeatedly, while
values are read back. Read it at `+0x29D628` on the table's build; find it in ours by the
`D9 05 ?? ?? ?? ?? DE CB D9 C9` neighbourhood or a float scan from `1.0`.

## 2. The Helix Mod fix — what a 3D Vision fixer learned about this renderer

Neovad's DX9 Helix Mod fix (2014) for v1.00.16.3209, later updated for v1.06, fixes "Skybox, Stars,
Flares, Main Shadows, Lights" and eventually the moon. `[reported 2026-09-02]` The parts that matter here:

- **"In version 1.06 shadows rebuilded and FOV dependent."** The v1.06 shadow shaders derive something
  from the projection — Neovad's workaround was to set the in-game FOV slider to **17 of 20** for
  correct shadows and torch lights. For us: **any projection override must be applied where the shadow
  path reads it too**, or shadows will disagree with the eye. That is a per-pass consistency
  requirement to design for, not a surprise to meet later.
- **The main shadow vertex shader is hash `2B37CDBA`**; Neovad found `dp3 r1.x, c0.xyww, r0` in it —
  **register `c0` carries a projection-shaped term** in that shader. One register named in one shader
  is not a convention, but it is the first named vertex-shader constant on this renderer, and Helix
  Mod's `ShaderOverride` dump mode produces the whole disassembled corpus the way Psychonauts' offline
  `D3DXDisassembleShader` pass did — the technique that proved register 6 there transfers unchanged.
- It is the **older-build** fix; later official patches made the game "almost 3D Vision ready" (the
  2026-08-25 topic) — consistent with the driver owning the eyes (2026-09-01 topic).

## 3. Free camera — controller only, and a downgrade note

FRAMED confirms what the 2026-08-25 topic recorded: `-freecamera` in the launch options, **right stick
click** to toggle, **controller required**, no photo mode, DSR and custom aspect ratios work, ReShade
works. Nothing new on a keyboard equivalent. The Steam guide on the same subject rate-limited this
pass (HTTP 429) and was not read.

## Concrete next steps

1. **Static, no launch:** scan the installed `AlanWake.exe` for the two byte patterns above; record
   the VA of the FOV read and the two calls around it, and the time-scale global.
2. **Static:** disassemble forward from the consumer call to find the projection build — expect a
   `D3DXMatrixPerspectiveFov*`-style routine or an in-house equivalent taking FOV, aspect, near, far.
3. **Flat run, later:** with `-rigidcamera -freecamera`, hook the FOV read to capture the camera object,
   dump its first `0x300` bytes across a few frames of movement, and look for the view basis and
   position the way Psychonauts' `camera+0x150` was found.
4. When the projection override is built, **check shadows** first — v1.06's are FOV-dependent.

## Sources

- https://framedsc.com/GameGuides/Alan_Wake.htm — FRAMED game guide (free camera, table, downgrade depot)
- https://framedsc.com/CheatTables/AlanWake.CT — Jim2point0's table, read online as XML
- https://helixmod.blogspot.com/2014/08/alan-wake.html — Neovad's Helix Mod fix and its comment thread

## ✅ Verdict 2026-09-03 — both addresses verified statically in our build; byte patterns ported exactly (folded from `inbox/`)

- **FOV read at `[camera+0x214]`** — the pattern `D9 80 14 02 00 00 D9 5C 24 10 E8` matched **exactly
  once**; our build has it at **`0x0043F533`** (`AlanWake.exe+0x3F533`), `0x90` from the table's
  `+0x3F5C3` — the "offsets are for the older build, patterns are portable" caveat did its job.
  The accessor before it is `0x005B5800`: `mov eax, [0x0076C5D8]` / `ret`. **So the camera object
  sits behind ONE static global, `[0x0076C5D8]`**, corroborated by 151 direct callers of that getter
  and by the global's own writer cluster and teardown `[inferred-static 2026-09-03]`. The modding
  side calls this the single most useful structural fact recorded for this game so far.
- **`AlanWake.exe` has no ASLR** — `DllCharacteristics = 0x8000`, `DYNAMIC_BASE` unset, no `.reloc`.
  Fixed at `0x400000`; every static address in this project is permanent.
- **Global time-scale** — `D9 05 ?? ?? ?? ?? DE CB D9 C9` returns two sites; the live one reads
  `[0x0069C628]` (`+0x29C628`, exactly one page from the table's `+0x29D628`), and its initial `.data`
  value is exactly `1.0`, the independent check that makes it a confirmation
  `[inferred-static 2026-09-03]`. Not yet written to.
- ⚠️ **The consumer after the FOV read is still only a candidate for the projection build.** The code
  does `fmul [0.4]` then `fadd [0.8]` — a linear remap, not degrees-to-radians (`0.0174533`). Recorded
  as unestablished.
- **FOV-dependent shadows** folded into dossier §8 as `[reported 2026-09-02]`; the shader-bank read
  is consistent with it mattering (`g_mSunLightProjectionMatrix` in 1,520 pixel shaders). Untested.

Request from the modding side, adopted as this lane's practice for this game: **send byte patterns,
not addresses.** Both ported and both were checkable in minutes.
