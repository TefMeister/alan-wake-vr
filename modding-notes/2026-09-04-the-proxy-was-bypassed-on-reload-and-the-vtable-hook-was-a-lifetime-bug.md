# 2026-09-04 (`/pd`, dev PC, static only) — the proxy was being bypassed on reload, and the "confirmed broken" vtable hook was a lifetime bug

**The game was not launched, and nothing here has been run.** The board's `[PD]` row is answered,
a one-line fix is built and deployed, and a 2026-08-25 verdict is corrected with a mechanism rather
than a guess.

---

## 1. Where the real device came from: nowhere we could see, because we were bypassed

The row asked why our hook only ever sees one short-lived `Direct3DCreate9` and never a second call
for the device the game actually renders with. A `/gr` drop
(`2026-09-04-gr-free-the-real-d3d9-on-detach-or-the-reload-bypasses-the-proxy.md`) supplied the
mechanism, and it checks out against our own source:

- The game loads `d3d9.dll`, calls `Direct3DCreate9` once, and **unloads it again about 6 ms later**
  `[measured, n=3 launches]`, then loads `"d3d9.dll"` a second time for the real device.
- `load_real_dll()` takes a reference on `C:\Windows\system32\d3d9.dll` **by full path** and, until
  today, **never released it** — `DLL_PROCESS_DETACH` only closed the log file
  `[inferred-static 2026-09-04, read in our own proxy.c]`.
- `LoadLibrary` matches an unqualified name against the **base names of already-loaded modules**
  before searching any directory (Microsoft's own remarks on `LoadLibrary`). So after our proxy
  unloaded, the still-resident system `d3d9.dll` satisfied the game's second
  `LoadLibraryA("d3d9.dll")`, the game folder was never searched again, and the real device was
  created on the real runtime with us nowhere in the chain.

**ReShade needed the identical fix for this identical game** — commit `74347b91d`, 4.5.2,
*"Fixed hooking in Alan Wake"*: free the reference to the module loaded for export hooks.
`[reported, primary source]`

**The fix, built and deployed:** `FreeLibrary(real_d3d9)` at `DLL_PROCESS_DETACH`.

Two details the drop did not specify and that matter:

- **Only when `lpReserved == NULL`.** A non-NULL value means the process is terminating, and a DLL
  must not free libraries then; the loader is tearing everything down anyway. The Alan Wake case is
  the other one — an explicit `FreeLibrary` by the game — where releasing the reference is both safe
  and the entire point. The log line now says which case it was.
- **Calling `FreeLibrary` inside `DllMain` is against the general guidance** (loader-lock re-entry).
  It is done here because the unload is the only moment the reference can be released, because
  `d3d9.dll`'s own `DllMain` does no work that can re-enter us, and because ReShade ships the same
  call for the same reason. **If a future launch hangs at exactly this point, this is the suspect**
  — reverting to the previous build merely returns the game to bypassing the proxy rather than
  hanging.

**NOT established:** that the second load now finds us. That is what the next launch shows.

## 2. The `install_createdevice_hook` verdict was wrong, and the real cause is mechanical

The proxy carried a hook, disabled, under a comment beginning **"CONFIRMED BROKEN, 2026-08-25"**,
recording that with it installed the game reliably failed to start (an access violation in `ntdll`,
then a silent early exit after a Fault-Tolerant Heap flag was tried) and that *"the real cause is
something about how this specific patch is applied to this specific game's vtable; not yet
understood"*.

Two facts, neither new but never put side by side, fully explain it `[inferred-static 2026-09-04]`:

1. `install_createdevice_hook()` writes `Hooked_CreateDevice` — **an address inside our DLL** — into
   slot 16 of the `IDirect3D9` vtable, and **nothing ever put the original back**. There was no
   unhook path at all.
2. This game **unloads our DLL about 6 ms later** (§1).

A D3D9 vtable is shared per interface class, not per instance, so the patch outlives the object it
was installed through. The sequence is therefore: patch slot 16 → our DLL is unloaded → the game
calls `IDirect3D9::CreateDevice` on the real runtime → **the call jumps into unmapped memory**. That
is an access violation raised in the loader's address space, which is exactly the reported symptom,
and it would happen every single time.

So **"the technique is broken for this game" is `[disproved 2026-09-04]`** as a statement about
vtable hooking. What was broken is that a patch pointing into a DLL must be removed before that DLL
can be unloaded. `remove_createdevice_hook()` now does that, restoring the runtime's own pointer, and
`DllMain` calls it **first** — before the `FreeLibrary` above, because the vtable lives in the system
`d3d9.dll`'s own read-only data and must not be written after that module is released. It restores
only if slot 16 is still ours; a pointer belonging to some later hook is logged and left alone,
because clobbering it is its own crash.

⚠️ **The hook is still disabled, deliberately.** This explanation is static. It fits every recorded
symptom and needs no other cause, but it has not been live-tested, and the last time the hook was
switched on the game did not start. Re-enable it in a launch of its own, with nothing else changed,
so a failure has exactly one candidate cause.

⚠️ **A verification detail worth knowing:** with the hook disabled the optimiser strips
`remove_createdevice_hook()` entirely as dead code, so **the deployed binary contains none of it** —
and does not need to. It was proved to compile in correctly by building a scratch copy with the hook
call enabled and confirming all three of its log strings appear in that binary; the scratch build was
then discarded and the source restored. `[compile-verified 2026-09-04]`

## 3. What the next launch answers

The deployed proxy is `d3d9.dll`, 58,368 B; the previous build is kept as
`d3d9.dll.bak-2026-09-04-pre-freelibrary` (57,856 B) and one copy reverts. Launch, reach gameplay,
quit, then read `alanwake_vr_proxy_log.txt`:

| what the log shows | meaning |
| --- | --- |
| **a SECOND "proxy loaded" block in the same PID**, followed by `Direct3DCreate9` | **the bypass is fixed** — we are in the chain for the real device, and the whole M1/M2 device-interception plan is unblocked |
| one block only, ending in "unloading (explicit FreeLibrary)" | the reference was released but something else still pins the system DLL; enumerate loaded modules at detach next |
| the game hangs at exit or on the second load | the `FreeLibrary`-inside-`DllMain` risk in §1 has bitten; revert to the backup, which merely restores the old bypass |
| the game fails to start at all | unexpected — the hook is still disabled, so the only behaviour change is the detach path; revert and say so |

Once a second block appears, the follow-on is a launch of its own: re-enable
`install_createdevice_hook()` and nothing else, and see whether §2's explanation holds.
