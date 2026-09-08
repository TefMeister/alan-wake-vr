# 2026-09-08 — `IDirect3D9` slot 16 is ALWAYS already hooked on this machine, and the guard stands the mod down every time

`/lm`, dev PC, fully autonomous. Two launches, both closed cleanly through the game's own menu.

Evidence: `dev-archive/recon/2026-09-08-slot16-is-always-already-hooked/` (both launches' proxy log,
and a frame showing the game running normally while the mod is inert).

---

## 1. The `[FLAT]` row's first launch is answered — and the answer is the warning, not the instrument

The board's row said: *"**(1) Launch as-is** and read the instrument … ⚠️ Also watch for
`REFUSING to hook … slot 16` — if that line appears, the layered hook is real, the module holding it
is named, and the guard just prevented the launch-1 crash."*

**The line appeared on every load of both launches.** The layered hook is real, it is named, and
**the instrument produced nothing at all** — because the guard stands the whole mod down before a
device is ever created, and the constant-upload instrument lives on the device vtable.

```
REFUSING to hook IDirect3D9 slot 16: it already holds 73B54DD0, owned by
D:\Program Files (x86)\Steam\gameoverlayrenderer.dll, not the real d3d9.dll (73620000).
… Standing down - the game runs, this mod does not.
```

`[verified-live 2026-09-08, n=2 launches, 4 loads]`

**Zero perspective signatures were logged.** The only two matches for "perspective/signature" in the
log are the wording of the stereo-OFF banner itself.

---

## 2. ⭐ Two DIFFERENT foreign owners, and they change between loads 350 ms apart

This is the part that was not predicted and is worth more than the confirmation.

The proxy deliberately unloads and reloads itself once (the `FreeLibrary` dance that makes the
game's next `LoadLibraryA("d3d9.dll")` find us again). Slot 16 was inspected on each load:

| launch | load | slot 16 holds | owning module |
| --- | --- | --- | --- |
| via Steam | 1 | `73B54DD0` | `Steam\gameoverlayrenderer.dll` |
| via Steam | 2 | `73B54DD0` | `Steam\gameoverlayrenderer.dll` |
| **direct exe** | 1 | `73684B20`-adjacent `73B54DD0` | `Steam\gameoverlayrenderer.dll` |
| **direct exe** | 2 | `75882830` | **`C:\Windows\SYSTEM32\apphelp.dll`** |

Two things follow:

- **Launching `AlanWake.exe` directly does NOT avoid the Steam overlay.** With Steam running, the
  overlay is injected into the process anyway; going around the Steam launcher changes nothing.
  `[verified-live 2026-09-08, n=1]`
- **The owner CHANGED between two loads ~350 ms apart in the same process** — overlay on load 1,
  `apphelp.dll` on load 2, with different pointer values. A vtable is shared per class, so
  something rewrote slot 16 in between. **Why is not established.** Candidates, not collapsed:
  the compatibility shim engine installing late; the overlay re-hooking; or a pointer left dangling
  by our own unload that now resolves inside another module. Nothing here distinguishes them.

⚠️ **`apphelp.dll` is a Windows application-compatibility shim, not a third-party hook**, and there
is **no `AppCompatFlags\Layers` entry for AlanWake** in HKLM or HKCU `[measured 2026-09-08]` — so
any shim is coming from the system database rather than a user setting. If apphelp legitimately owns
a shimmed `d3d9` entry point, then **the guard's rule is too strict**: "the pointer must live inside
the real `d3d9.dll`" is false by design for a shimmed d3d9, and refusing it is refusing a benign OS
mechanism. That reading is `[hypothesis]` — it is consistent with the evidence and not demonstrated.

---

## 3. ⛔️ What this means for the project: the guard is correct and also fatal

The guard did exactly its job — **the game ran perfectly**, clean main menu, no crash, no recursion,
and both launches quit cleanly through the menu. Compare 2026-09-05, where chaining into the foreign
hook recursed `CreateDevice` 1,669× in 1 ms and killed the process.

**But "the game runs, this mod does not" is not a working state.** As written, the proxy can only
install when it wins the race for slot 16 outright, and on this machine it never does — the Steam
overlay is always there first, and something else is there by the second load.

**The stereo edit, the instrument, and the whole `[FLAT]` queue are unreachable until the hook
strategy changes.** That is a static problem, so the project re-gates to `[PD]`.

### The design that removes the race entirely

**Stop patching the `IDirect3D9` vtable at all.** We own the `Direct3DCreate9` export — the game
calls *ours*. Return **our own COM object** implementing `IDirect3D9`, whose `CreateDevice` we
implement directly and which forwards every other method to the real interface. Then:

- nothing is written into a shared vtable, so no one can be ahead of us and we are ahead of nobody;
- the Steam overlay's own hook keeps working on the real object, layered *below* us as it expects;
- the device we hand back can be wrapped the same way, which is where the constant-upload instrument
  belongs anyway.

That is more code than the current three-line patch, but it is the standard shape for a D3D9 proxy
and it is the only version that survives an environment we do not control.

**A smaller stopgap exists and is worse:** allow chaining into the foreign pointer plus a
re-entrancy guard. It would probably work, but it re-introduces exactly the failure the guard was
written to stop, and the 2026-09-05 crash showed that failure is timing-dependent — it appeared once
in four launches. A fix that is only usually safe against a bug that is only sometimes visible is
not worth shipping.

---

## 4. Automation, scored

| # | capability | verdict |
| --- | --- | --- |
| 1 | menu → gameplay | ✅ launch → intro video → `Esc`/`Space` → main menu, twice; `Continue Game` highlighted as the profile says |
| 2 | commands | n/a — no console on this title; the proxy's channel is the ini, which is read at load |
| 3 | character + camera | not exercised — pointless while the mod is inert |
| 4 | self-close | ✅ **twice, clean, no taskkill** — `Down`×5 to `Quit`, highlight verified by cropping the menu, `Enter`, `Enter` |

---

## 5. What is NOT established

- **Whether disabling the Steam overlay is sufficient.** It is the load-1 owner in every observation,
  but `apphelp.dll` owned load 2, so removing the overlay may simply expose the next hooker. Untested
  — it needs a Steam per-game setting change and a Steam restart, which this session did not make on
  the user's behalf.
- Why slot 16's owner changed between loads.
- Whether `apphelp` is a genuine shim of `d3d9` or a stale pointer.
- **Anything at all about the perspective signatures** — the instrument never ran. The 2026-09-07
  `(xs, ys)` re-keying is still completely untested live.
- Whether the home PC behaves the same. It has a different Steam install and may or may not shim.
