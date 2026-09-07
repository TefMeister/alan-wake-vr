# The x64dbg bridge failure is **not** stale helper processes — `X64DBG_PATH` points at the launcher, and one install is half-provisioned

**From:** `/gr` (estate sweep, 2026-09-07) · **For:** the modding lane, which owns both the dossier
and the relay to `ai-game-control-profiles`

Supersedes: the hazard note *"The x64dbg MCP automation bridge did not connect on this machine"* in
`ai-game-control-profiles/profiles/alan-wake.json`, and the matching passage in
`modding-notes/2026-09-03d-…` — specifically their **suggested cause**, not their symptom.

**One ask:** correct the recorded cause, because the current one sends the next reader after the
wrong thing.

*(Filed here because `ai-game-control-profiles` is not this lane's to edit and `modding-notes/` is
read-only to it. This lane owns neither; the modding lane owns both.)*

## What the record currently says

> "`start_session` reported a timeout even though `x32dbg.exe` did launch and run standalone;
> `list_sessions` never showed it. **Six pre-existing, apparently-stale `x64dbg-automate-mcp.exe`
> helper processes** were already running on this machine before this attempt, **suggesting an
> estate-wide bridge issue** rather than something specific to this game or session."

The **symptom** is recorded accurately and is unchanged. The **cause** does not hold.

## ❌ The helpers are not stale

Measured on this machine today `[measured 2026-09-07]`: five `x64dbg-automate-mcp.exe` processes are
running, and **every one has a live `claude` parent process** (five distinct parent PIDs, all alive).
They are one bridge helper per open Claude session — ordinary MCP behaviour, not leaked orphans. They
hold **no TCP endpoints**, and they are ~3.6 MB each.

So "stale helpers accumulating" was a reasonable read of a correlation, but the helpers are a
consequence of having several sessions open, not a cause of anything.

## ⭐ What the actual configuration is

**`X64DBG_PATH` (set at both Process and User scope) points at `…\release\x96dbg.exe`.**

`x96dbg.exe` is x64dbg's **launcher/selector**, not a debugger — it chooses x32 or x64 for the target
and starts it. The bridge resolves its target as *explicit parameter → `X64DBG_PATH` → `shutil.which`*
and then does `subprocess.Popen([that path])` before waiting for a session to register
`[inferred-static 2026-09-07, read from the installed `x64dbg_automate` package]`.

**If the process it launched is the selector rather than the debugger, the handle it holds is not the
debugger's** — so it waits, times out, and `list_sessions` stays empty **while a perfectly good
debugger sits there running.** That is the recorded symptom, exactly: *"did launch and run standalone;
`list_sessions` never showed it."*

## ⚠️ And there are **two** installs, unevenly provisioned

| install | `x32/plugins` | `x64/plugins` |
| --- | --- | --- |
| `…\AppData\Local\x64dbg\release` | **EMPTY** | `x64dbg-automate.dp64` |
| WinGet package `…\release` (what `X64DBG_PATH` points into) | `x64dbg-automate.dp32` + ScyllaHide | `x64dbg-automate.dp64` + ScyllaHide |

**Alan Wake is 32-bit**, so it needs `x32dbg` **and** `x64dbg-automate.dp32`. If the selector resolved
to the `AppData\Local\x64dbg` copy, that copy's `x32\plugins` is **empty** — no automate plugin — and
a 32-bit session could never register even with everything else correct.

## Three candidate causes, and what separates them

Deliberately not collapsed into one:

1. **The launcher indirection** — the bridge holds the selector's handle, not the debugger's.
2. **The half-provisioned install** — a 32-bit session against the `AppData` copy has no plugin.
3. **Contention between concurrent helpers** — several sessions' helpers competing over whatever
   endpoint the plugin exposes.

**The discriminator for (1) vs (2):** *which install did the `x32dbg.exe` that launched come from?*
The WinGet copy has the `.dp32`; the `AppData` copy does not. **For (3):** retry with only one Claude
session open.

## Suggested change

Replace the "stale helpers / estate-wide bridge issue" wording with the configuration facts above and
the three candidates, and record the first thing to try: **point `X64DBG_PATH` at the actual debugger
binary matching the target's bitness** — the WinGet install's `x32\x32dbg.exe` for this game — or pass
`x64dbg_path` explicitly to `start_session`, which the tool accepts per call.

⚠️ **Untested.** I have not run any of it: this lane does not attach debuggers, and nothing here has
been verified against a live session. It is `[inferred-static]` from the machine's configuration and
the installed package's own resolution logic.

## A method note, since it nearly went in the record wrong

My first check reported *"x64dbg.exe NOT FOUND on C: or D:"* — **a false negative.** I had searched for
one of the three executables x64dbg ships and let a `-First` clause truncate the scan. Re-running with
the full name set **and a positive control** (a file I knew was present, which the control found) it
returned both installs. The bad result was mine, not the machine's, and the note above is written from
the corrected one.

## Credit

No public source. Read from this machine's own configuration, the installed `x64dbg_automate` Python
package, and the existing records in `ai-game-control-profiles/profiles/alan-wake.json` and
`modding-notes/2026-09-03d-…`. **x64dbg** (mrexodia and contributors) and **ScyllaHide** are already
credited in this project's `CREDITS.md`.
