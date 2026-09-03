# The proxy-startup question, and the log as it stood BEFORE the 2026-09-03 run

`alanwake_vr_proxy_log-BEFORE-2026-09-03-run.txt` is the **complete** proxy log as it existed
before this project's first `/lm` session, preserved because it is the only run evidence on disk
and the game folder is outside every repository. **The live log appends**, so anything after these
**10 lines** belongs to a later run.

## What it contains, in full

Two launches, 2026-08-25, and nothing else:

```
16:16:15.645 loaded, PID=10660 | Direct3DCreate9 -> 03807940 | 16:16:15.776 unloading
16:20:25.685 loaded, PID=28072 | Direct3DCreate9 -> 03842BB8 | 16:20:25.816 unloading
```

## Reading it precisely

- **`Direct3DCreate9` SUCCEEDED both times** — it returned a valid non-null `IDirect3D9`. The proxy
  forwards correctly; this is not a fatal load failure.
- The unload comes **6 ms after that return**, and 131 ms after load. (The board previously said
  "131 ms after `Direct3DCreate9` returned"; the 131 ms is measured from load.)
- **One `Direct3DCreate9` and no `CreateDevice`.** A game that reached gameplay would go on to
  create a device. This did not.
- **The deployed `d3d9.dll` is dated 16:06 the same day**, and the log's first entry is 16:16. Since
  the log appends, **these two aborted launches are every run this build has ever performed.** There
  is no evidence on disk that this build ever reached gameplay.

That last point sharpens `/pd`'s 2026-09-03 note, which said the recorded "live-verified working"
status and the log "are not reconcilable from static data". They still are not — but the reason is
narrower than it looked: it is not that a successful run might be missing from the log, it is that
the log covers this build's entire life.

⚠️ **This is not a claim that the proxy is broken.** `Direct3DCreate9` returning a valid pointer
argues the opposite. The likeliest readings remain (a) two launches aborted by hand and never
written down, or (b) the game exiting for a reason of its own — it was possibly started outside
Steam, and this title checks for its launcher.

The proxy is the **plain forwarding build**: exports are exactly `Direct3DCreate9`, one symbol, no
hook code `[inferred-static 2026-09-03]`. Revert is a one-step **delete** — the game ships no
`d3d9.dll` of its own and uses the system copy.

---

## ✅ RESOLVED 2026-09-03 — the build DOES reach gameplay; `alanwake_vr_proxy_log-AFTER-2026-09-03-run.txt`

The first `/lm` session on this game launched with this exact proxy still deployed. The log gained
one more identical fast load/unload cycle (`AFTER` file, last 5 lines) — but a screenshot taken
seconds later showed the game in live, moving gameplay with a working HUD. `[verified-live
2026-09-03]`

**So the line above — "there is no evidence on disk that this build ever reached gameplay" — is
superseded, not by new reasoning but by an actual launch.** The fast cycle was never the failure
mode it looked like; it's something else entirely (see the write-up in `modding-notes/` for the
current best guess: a throwaway capability-probe device, separate from the real one). Full
analysis: [`modding-notes/2026-09-03d-windowed-mode-staged-and-the-proxy-is-confirmed-live.md`](../../../modding-notes/2026-09-03d-windowed-mode-staged-and-the-proxy-is-confirmed-live.md).

**Not investigated further:** where the real device's `IDirect3D9` actually comes from, since our
hook only ever sees the one short-lived call. That's the new open question, not "does the proxy
work" — it demonstrably does.
