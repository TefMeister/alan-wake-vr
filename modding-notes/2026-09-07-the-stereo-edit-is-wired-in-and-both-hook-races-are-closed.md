# 2026-09-07 — The stereo edit is wired in, and the race that killed launch 1 is closed

*Session: `/pd alan wake`, dev PC, **static only, NO LAUNCH**. The game was not launched and nothing
here has been run. Lane claim taken 18:40 and released after the write-up.*

**Both `[PD]` rows are done.** `stereo.c` — numerically verified since 2026-09-03 and connected to
nothing — now runs in the live constant path, and the two defects standing in front of it are fixed.

---

## 1. ⭐ The instrument was keyed by REGISTER, which hid the thing it existed to find

`g_persp[register]`: the first perspective-shaped matrix seen at a register set `seen`, and every
later one at that register was rate-limited behind the same entry.

**So a shadow pass uploading a projection at c0 masked the camera projection at c0 for the rest of
the run** — and c0 is exactly where the non-skinned camera projection lives. The one matrix the
session most needed to see was the one most likely to be hidden.

It is now keyed by **(xs, ys)** = `m[0][0]`, `m[1][1]`. That key is right three ways over:

- they **differ** between a shadow frustum and the camera (different FOV and aspect);
- they are **unchanged by transpose**, so the key does not depend on settling the storage layout —
  which is still the one thing the 2026-09-05 run left ambiguous;
- they are **what the shear scales from**, so the signature the log prints is literally the string to
  paste into the ini.

Every distinct projection now announces itself once, in full, with the list of registers it has been
seen at, and prints the exact ini lines that would select it.

---

## 2. The shear: `aw_stereo_apply_block()` `[verified-numerically 2026-09-07]`

The match/copy/edit is a **pure function in `stereo.c`**, deliberately, so the code that runs in the
game is the code the host self-test exercises — not a transcription of it. §6 of the `/pd` command
exists because a Far Cry 2 check once verified a Python transcription and passed while the shipped
code was wrong.

Three properties matter, and all three are tested:

1. **Found by offset INSIDE the block, never by `start == reg`.** The engine flushes whole
   128-register blocks (`c0+128`, `c128+128`) per draw, so `start` is the block base; a
   `start == reg` test would fire on nothing at all.
2. **The engine's buffer is never written.** The pointer handed to the hook may be the live constant
   store, so the edit lands in a copy; when nothing matches, the original is forwarded untouched and
   the copy is not even written.
3. **A zero signature is refused.** Most of a 128-register flush is zero padding — a zero key would
   shear dozens of windows.

**Nine test groups added** to `stereo_test.c`: the matrix at offset 53 of a 128-register block is
found and its offset reported; the source is unmodified; nothing outside the matched window changes;
the edited window equals `aw_stereo_apply_fused_clip` exactly; a non-match leaves `dst` alone; zero
signature, `C <= 0`, a short block and `NULL` are all refused; two windows in one block are both
edited; and `eye_dx = 0` is bit-identical.

**The suite was mutation-checked.** Injecting "edit window 0 instead of the matched offset" into the
shipped function made it report `*** FAILURES ABOVE ***`; restoring gave `ALL CHECKS PASSED`. A pass
is therefore evidence, not a test that cannot fire.

### ⚠️ It ships switched OFF, and that is not caution for its own sake

**Attribution is a runtime question.** The same shader serves the camera and a shadow view; nothing
static separates them, and `stereo.h` says so outright. So the operator reads a signature off the
instrument and names it in `d3d9_proxy.ini`.

**NOT ESTABLISHED: that any particular signature is the camera's.** And the failure is not the one
you would watch for — if the shear lands on the wrong projection, **the camera looks fine and the
shadow map corrupts**: shadows swimming, detaching from casters, or striping as you move. Anyone
judging by "does the camera look right" will miss it.

---

## 3. ⭐ The layered-hook race that killed launch 1 `[compile-verified 2026-09-07]`

Launch 1 on 2026-09-05 recursed `CreateDevice` **1,669 times in one millisecond** and died.

The cause is a **layered hook**: something else — the Steam overlay is the likeliest — had already
replaced the slot, so the pointer cached as "the real one" was itself another hook that chains
onward. Chaining into it is harmless exactly once; it stops being harmless the moment that hook
re-enters, and then the two call each other until the stack is gone.

The **unload** path already refused to restore a slot that was not ours. **The install path checked
nothing** — that is the half that crashed.

Both installs now verify, *before caching*, that the pointer belongs to the real `d3d9.dll`
(`GetModuleHandleExA(FROM_ADDRESS | UNCHANGED_REFCOUNT)`), and otherwise **stand down and log the
owning module by name**:

- `IDirect3D9` slot 16 — the one that crashed;
- `IDirect3DDevice9` slot 94 — the same test, because the device vtable also comes from the real
  d3d9 and a foreign pointer there would recurse identically, just on a function called thousands of
  times per frame.

A pointer with **no owning module** is refused too: an unbacked address is a trampoline, which is
precisely the case to avoid.

⚠️ **Launches 2–4 were clean only because the first block happened to live 16 ms instead of 700.**
They were timed lucky, not protected. Standing down costs the mod for that run; chaining costs the
process — which is the right trade and now the coded one.

---

## 4. Build and deployment

- `build.sh` links `stereo.c`.
- **Deployed on the DEV PC: `d3d9.dll` 73,216 B**, SHA-256 verified identical to the build output.
  Previous kept as `d3d9.dll.bak-2026-09-07-pre-stereo`.
- ⚠️ **The dev PC was still on the 2026-09-04c build (62,464 B)** — the 2026-09-05 instrument only
  ever reached the home PC, so the dev PC had skipped a generation. **The home PC now needs a
  rebuild** to get any of this.
- `d3d9_proxy.ini.template` ships beside the source, with the reading order and the failure tell
  written into it.
- Strict build (`-Wall -Wextra -Wpedantic -Wshadow -Wconversion`) is **clean for every line added
  this session**. Three `missing-field-initializer` warnings remain on the pre-existing `g_vs`
  candidate array; they were not introduced here and were left alone rather than widening the diff.
- Two build-script defects fixed while in there: `build-selftest.sh` hard-coded the dev PC's WinGet
  toolchain path *and* the `-pd` clone root for the toolkit. Both now resolve per machine and per
  lane, the way `build.sh` already did. Self-tests re-run after the edit — still `ALL CHECKS PASSED`.

---

## 5. Also folded this session

**`/gs`:** one bare `[verified-live]` with no date in `status/alan-wake-vr.md` — the register-flush
observation. Dated to `[verified-live 2026-09-04, n=1 launch]` from the surrounding text. The
dossier had zero bare tags, so it was a stray copy, not a habit.

**`/gr`: the x64dbg bridge failure has a different cause than recorded.** The old note blamed stale
helper processes and an estate-wide issue. The helpers are not stale — five were running and **every
one had a live `claude` parent**, holding no TCP endpoints `[measured 2026-09-07]`. What is actually
true `[inferred-static 2026-09-07]`:

- **`X64DBG_PATH` points at `x96dbg.exe`, the launcher/selector — not a debugger.** The bridge
  `Popen`s that path and waits for a session to register, so it holds the selector's handle, times
  out, and `list_sessions` stays empty *while a working debugger sits there running*. That is the
  recorded symptom exactly.
- **Two installs, unevenly provisioned.** The `AppData\Local\x64dbg` copy has an **empty
  `x32\plugins`**, and this game is 32-bit — against that copy a session could never register.

First thing to try: point `X64DBG_PATH` at the WinGet install's `x32\x32dbg.exe`, or pass
`x64dbg_path` per call. **Untested — nothing here has been run against a live session.** The symptom
in the old record was accurate and is unchanged; only the cause is replaced.

---

## 6. What the next launch actually does

Two launches, and the first needs no configuration at all:

1. **Launch as-is.** The instrument logs every distinct perspective signature with the registers it
   appears at. Read off which is the camera — its xs/ys should track the game's aspect ratio.
   Also watch for `REFUSING to hook ... slot 16`: if that appears, the layered hook is real and
   named, and the guard just prevented the launch-1 crash.
2. **Set `[stereo] Enabled=1` with that signature, `EyeDx` and `Convergence`, and relaunch.** The log
   prints `stereo: FIRST edit applied - block c<start>+<count>, matrix at offset +<k>` on the first
   edit. No such line with `Enabled=1` means the signature never matched.

**The failure to watch for is a corrupted shadow map, not a wrong-looking camera.**
