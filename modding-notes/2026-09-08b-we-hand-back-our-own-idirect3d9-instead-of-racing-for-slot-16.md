# 2026-09-08b — we hand back our own `IDirect3D9` instead of racing for slot 16

`/pd`, dev PC. **The game was not launched and nothing here has been run.** The one `[PD]` row is
closed. Compile-verified, with the vtable layout checked against `d3d9.h` at compile time — and that
check verified to be capable of failing.

Deployed `a788b9dfb94d`, 216,576 B, stamped. Previous build backed up as
`d3d9.dll.bak-2026-09-08-pre-wrapper`.

---

## 1. The problem, and why patching could never have worked

`REFUSING to hook IDirect3D9 slot 16` fired on **every load of both launches**
`[verified-live 2026-09-08, n=2 launches, 4 loads]`. The Steam overlay owned load 1; `apphelp.dll`
owned load 2. The guard is correct — the game ran perfectly, no recursion, clean quits, against
2026-09-05 where chaining into a foreign pointer recursed `CreateDevice` **1,669 times in one
millisecond** and killed the process.

But standing down happens **before a device is created**, so the constant-upload instrument never
ran and **zero perspective signatures were logged**. "The game runs, this mod does not" blocked the
entire flat queue.

**Patching a shared vtable is a race with no winning move.** Whoever writes last wins, and we do not
control when we are loaded. Being cleverer about the patch cannot fix that; the 2026-09-05
1,669-deep recursion is what "cleverer" already cost once.

## 2. The fix: stop racing

We own the `Direct3DCreate9` export, so `Direct3DCreate9` now returns **an object of our own** —
17 methods, all forwarding, whose vtable lives in this DLL and which nobody else has ever seen.

- nothing is written into a vtable shared with anyone, so there is nothing to restore and nothing to
  race for;
- nobody can be "ahead of us", because the object did not exist before us;
- **the Steam overlay's hook keeps working, layered below us** — its patch is on the *real* object's
  vtable, and every one of our forwarders calls straight into it.

### The vtable is typed as `d3d9.h`'s own `IDirect3D9Vtbl`

Not a hand-rolled array of `void *`. That means the compiler checks all seventeen signatures **and
their order** against the header. A hand-rolled vtable lets one wrong slot compile cleanly and then
corrupt a call at runtime with the wrong arguments, which is the worst failure available here.

On top of that, two compile-time assertions:

```c
sizeof(struct IDirect3D9Vtbl) == 17 * sizeof(void *)
offsetof(struct IDirect3D9Vtbl, CreateDevice) == 16 * sizeof(void *)
```

**Verified that they can actually fail:** changing the second to `15 *` makes the build stop with
*"declared as an array with a negative size"* `[verified-numerically 2026-09-08]`. A check that
cannot fail is not evidence, and this one can — so its passing does establish that `CreateDevice`
really is slot 16, which is what the whole stand-down was about.

### The old path was deleted, not disabled

`install_createdevice_hook` / `remove_createdevice_hook` / `Hooked_CreateDevice` are gone. A
disabled hook invites re-enabling, and this one cannot be made to work. Their history is preserved
as a comment where they used to live, because it is worth keeping: the 2026-08-25 "CONFIRMED BROKEN"
verdict (`[disproved 2026-09-04]` — it was a lifetime bug, not a vtable-hooking problem), the
2026-09-05 recursion, and the 2026-09-07 guard that was correct and still left the mod inert.

`slot_is_foreign()` is **kept** — the device-side instrument still patches a vtable and still needs
it.

---

## 3. Lifetime — the one thing that can still crash, and what stops it

Our wrapper's vtable points into this DLL, so the DLL must not unload while the game holds a
wrapper. That is the *same class of bug* as the 2026-08-25 crash, in a new shape.

So the wrapper takes a reference on our own module while any wrapper is alive, and releases it when
the last one dies.

**The ordering is what makes this safe, and it is deliberate.** The game releases the throwaway
`IDirect3D9` *before* it unloads `d3d9.dll` — releasing a COM object after freeing the library it
came from is not legal — so our extra reference is gone by the time the game's `FreeLibrary` runs.
That keeps the 2026-09-04 mechanism working **unchanged**: our proxy really does unload, the system
`d3d9.dll` reference really is released, and the game's *second* `LoadLibraryA("d3d9.dll")` really
does search the game folder and find us again `[verified-live 2026-09-04, n=1]`.

⚠️ **The one ordering still unsafe** is a game that unloads `d3d9.dll` while holding our wrapper.
That was already fatal before this change and no wrapper design survives it.

**A good interaction, checked rather than assumed:** while a wrapper is alive our module reference
also prevents `DLL_PROCESS_DETACH` from running — which means the existing `FreeLibrary(real_d3d9)`
in `DllMain` cannot fire while a wrapper still points at an `IDirect3D9` that came from that module.
The two mechanisms reinforce each other rather than fighting.

---

## 4. Scope: the DEVICE is still reached by a vtable patch, deliberately

`IDirect3DDevice9` has **119 methods**. A hand-written wrapper for it is a large amount of purely
mechanical code in which one wrong slot silently corrupts a call — and **there is currently no
evidence the device slot is contested at all.** The stand-down that blocked everything happened on
`IDirect3D9` slot 16, *before a device ever existed*, so the device slot has never been reached to
find out.

`install_vsconst_hook()` carries the same foreign-slot guard, so if it *is* contested the result is a
clean stand-down of the instrument alone, with the game still running and a log line saying so. **That
is when the device deserves the same treatment — and not before**, because building it now would be
building against a guess. Per the board's own scope rule, that makes it not a `[PD]` row yet: its
shape depends on a test that has not run.

---

## 5. What the size change actually is

The DLL went 73,216 → 216,576 bytes, which looks alarming for ~250 lines of thin forwarders. It is
not code:

| section | before | after | delta |
| --- | --- | --- | --- |
| `.text` | 0x2e30 | 0x3092 | **+610 bytes** |
| `.rdata` | 0x1c4f | 0x7225 | +22 KB (log strings + the vtable) |
| `.debug_*` | 40,948 | 101,516 | +59 KB |

`[verified-numerically 2026-09-08]`. **The code grew by 610 bytes** — exactly what seventeen thin
forwarders should cost. The rest is DWARF type information for the D3D9 structs the signatures
reference (`D3DCAPS9`, `D3DADAPTER_IDENTIFIER9`, and friends) plus the explanatory log strings, and
the remainder is PE section padding. Nothing was accidentally inlined or pulled in; `-ldxguid`
and `-luuid` add **zero** bytes (measured by linking the old source with and without them).

Not stripped: the loader history on this project means a symbolic crash address is worth more than
143 KB of disk.

---

## 6. Also fixed: the build was not reproducible

Two builds of identical source differed by 2 bytes (the PE `TimeDateStamp`), so `CONVENTIONS.md`'s
*rebuild and compare the hash* check silently could not work here. `-Wl,--no-insert-timestamp` →
**0 differing bytes** `[verified-numerically 2026-09-08]`.

⚠️ **That is the FOURTH project today** — `doom-2016-vr`, `unreal-gold-vr`, `mad-max-vr` and now
this one, across two toolchains. Four for four. The rule is in `CONVENTIONS.md`; the short version is
**build twice and diff before trusting a hash comparison anywhere.**

`-Wextra` was *not* added here, unlike mad-max: it produces three pre-existing
missing-field-initializer warnings on `g_vs[]` that are benign, and a build that always warns is a
build whose warnings get ignored.

---

## 7. What this session did NOT establish

- **That the wrapper works.** It is compile-verified and the slot layout is proven against `d3d9.h`;
  the game has not been launched. A COM wrapper that returns the wrong thing from one forwarder
  would look like a game that starts and then misbehaves in one specific way.
- Whether the *device* slot is also contested. Unknown, and unknowable until a device is created.
- Whether disabling the Steam overlay frees slot 16 — moot now for the mod, but still the cleanest
  proof of what owns it.
- Anything about the perspective signatures. **Zero have been logged**, which is precisely what this
  change exists to change.

---

## 8. What to run next time the game is up

**Just launch it.** Everything below is read from the log.

| what the log says | meaning |
| --- | --- |
| `returning OUR IDirect3D9 … wrapping the real …` | ⭐⭐ the wrapper is in the chain. This is the line that was impossible before |
| `IDirect3D9::CreateDevice (through OUR wrapper)` | **the blocker is gone** — we now see the device, which is what the whole flat queue waited on |
| `SetVertexShaderConstantF hook installed …` | the instrument is live; go straight to the perspective-signature rows |
| `REFUSING to hook IDirect3DDevice9 slot …` | the device slot is contested too. The game still runs; only the instrument is lost. **That** is when the device gets the same wrapper treatment |
| game does not start at all | this build is the first suspect — restore `d3d9.dll.bak-2026-09-08-pre-wrapper` |
| no proxy log lines at all | we were not loaded; a different problem from any of the above |

Then the original row is unchanged and still first: read every distinct perspective signature,
keyed by `(xs, ys)`, decide which is the camera (its xs/ys should track the aspect ratio), and set
`[stereo] Enabled=1` with that signature plus `EyeDx`/`Convergence`.

⚠️ **The failure to watch for is a corrupted shadow map, not a wrong-looking camera** — the same
shader serves both, so a wrong signature leaves the camera fine while shadows swim.
