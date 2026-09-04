# 2026-09-04c (`/pd`, dev PC, static only) — the CreateDevice hook is back on, and the `g_mViewToClip` dump is built

**The game was not launched, and nothing here has been run.** Both `[PD]` rows are closed by one
build, because they are the same build: re-enabling the device hook is what yields the device
pointer the matrix dump needs. The next launch answers the question the board calls the one thing
that could falsify the whole static line.

---

## 1. Why both rows became doable at once

This morning's `/pd` established that the proxy was being bypassed on the game's second
`d3d9.dll` load and fixed it, and separately explained the 2026-08-25 "CONFIRMED BROKEN" verdict on
`install_createdevice_hook()` as a lifetime bug rather than a problem with vtable hooking.

The 19:03 launch confirmed both `[verified-live 2026-09-04, n=1]`: one process shows the probe load,
the explicit unload with our new "releasing the system d3d9.dll reference" line, **a second
`proxy loaded` block in the same process that never unloads**, and the title and main menu rendering
through it. The proxy owns the real device.

That is what makes these two rows one job. `install_createdevice_hook()` is the **only** place the
game's real `IDirect3DDevice9` is handed to us, and the device vtable is what carries
`SetVertexShaderConstantF`. No device, no constant reads.

## 2. The CreateDevice hook, re-enabled

One call, restored, with the reasoning recorded next to it rather than in a commit message. The
unhook path built this morning stays exactly as it was — it is what makes re-enabling safe, since
the crash it caused was a pointer into our DLL left in a shared vtable across an unload.

⚠️ **If the game fails to start on this build, this is the first suspect**, and
`d3d9.dll.bak-2026-09-04c-pre-vsdump` beside it is the last known-good build.

## 3. The `g_mViewToClip` dump

**What it answers.** Everything in `stereo.c` assumes the projection is left-handed with
`clip.w = view.z` and mathematical row 3 = `[0,0,1,0]`, taken from the `dp4 r0.w, c3, r1` pattern
plus the D3D convention. That is an assumption, not a measurement. One look at a live matrix settles
it and also gives the engine unit the IPD must be expressed in.

**Where it looks, and why not one register.** The 2026-09-03 shader-bank census found
`g_mViewToClip` is a standalone 4×4 projection in 4,467 vertex shaders — not fused with the view —
and that **its register is not fixed**: `c0` in 2,238 shaders, `c192` in 2,084, `c4` in 128, `c7` in
17. The split is the skinning palette, which occupies `c0..c191` and pushes the camera block to
`c192` in skinned shaders. So the dump watches all four rather than assuming one, and reports which
actually received an upload.

**Two design points that matter more than they look:**

- **The capture is SPANNING, not equality.** An upload may start below a candidate and contain it —
  `c192` sits immediately past the 192-register palette, so a single upload of the whole range would
  start at 0 and cover it. Testing `start == reg` would then report "never seen" for a register
  written every frame, which is the most misleading possible negative. The capture takes any upload
  where `start <= reg` and `reg + 4 <= start + count`, offsetting into the data.
- **The hot path does no I/O.** `SetVertexShaderConstantF` runs thousands of times a frame, so the
  hook copies 16 floats into a fixed slot and tests a counter. The first sighting at each candidate
  logs immediately; after that, once every 4,000 uploads. Every candidate is also dumped once more
  at detach, so a session that never reaches the periodic cadence still leaves its numbers behind.

**It is read-only.** Nothing is modified. The point is to find out whether the assumption behind the
future write is true.

**The log states the verdict, not just the numbers**, so nobody has to re-derive the convention at
the moment of reading:

| what the log says | meaning |
| --- | --- |
| `m[11]=+1, m[15]=0 -> clip.w = +view.z, LEFT-handed` | **the assumption holds** and `stereo.c`'s derivation stands as written |
| `m[11]=-1 -> RIGHT-handed` | the derivation assumes the opposite; **every sign in it needs re-deriving** |
| `neither convention` | that register is not `g_mViewToClip` in the shaders that ran, or the projection is not a plain perspective — compare the other candidates before concluding |

## 4. The lifetime rule, applied to the new hook too

The device vtable is shared per interface class exactly like the `IDirect3D9` one, so the same
hazard applies: a pointer into this DLL must come out before the DLL can unload.
`remove_vsconst_hook()` restores the runtime's own pointer, refuses to touch the slot if some later
hook owns it, and **runs first at detach** — device vtable, then the `IDirect3D9` vtable, then the
module reference. That ordering is deliberate: each holds a pointer into this DLL and the
2026-08-25 crash was exactly one of them left behind.

`[compile-verified 2026-09-04]`, builds clean, the single export intact. Slot 94 for
`SetVertexShaderConstantF` was **read from the SDK header's own `IDirect3DDevice9Vtbl`**, not
assumed — the same check already run for `Reset` (16) and `Present` (17).

**Deployed** to `Alan Wake\d3d9.dll` (62,464 B); the previous build is kept as
`d3d9.dll.bak-2026-09-04c-pre-vsdump` and one copy reverts.

**NOT established:** that either hook survives a real frame. The device hook has never run against
the real device — only against the throwaway probe, in 2026-08-25's failed attempt — and the
constant hook has never run at all.

## 5. What the next launch answers

One launch, reach the main menu (a level is better but not required — the menu renders through us),
quit, read `alanwake_vr_proxy_log.txt`:

| line | meaning |
| --- | --- |
| `CreateDevice vtable hook installed at slot 16` then `IDirect3D9::CreateDevice called` | the re-enabled hook works and the lifetime explanation was right |
| `SetVertexShaderConstantF hook installed at device vtable slot 94` | we are on the device's constant path |
| `g_mViewToClip candidate cN` with a 4×4 and a `reading:` line | **the handedness question is answered** — take the verdict from the reading line |
| a candidate that never appears | that register carries nothing in the shaders that ran; the menu may not exercise skinned shaders, so `c192` silently absent is expected until a level loads |
| the game fails to start | the re-enabled CreateDevice hook is the first suspect; revert to the backup |
| a hang at exit | the unhook ordering; revert and say which line was last |
