# The layered-hook race is a known Steam-overlay conflict — and it can be switched off for the test

**Status:** 🆕 new · **Priority:** medium — it does not change the `[PD]` fix, which is right as
designed; it corroborates the diagnosis and adds a free way to separate our bug from the overlay's
during the `[FLAT]` relaunch that follows.

## The row this is about

> **`[PD]` close the layered-hook race that crashed launch 1 (2026-09-05):** when slot 16 already
> holds a foreign pointer at install or unload time (**Steam overlay, most likely**), do NOT chain
> into it — refuse the install, or stand down and log. Launch 1 recursed `CreateDevice` **1,669× in
> one ms** and died; launches 2–4 were clean because the first block lived 16 ms instead of 700.

Two things were worth checking publicly: is "Steam overlay, most likely" a good guess, and has anyone
published a better mitigation than refusing the install?

## What the public record says `[reported 2026-09-05]`

**The guess is well-supported, and the conflict is documented as a general one rather than an
Alan Wake quirk.** Steam's own community discussions record that the older external overlay
coexisted with proxy DLLs (`d3d9.dll`, `dxgi.dll`, `ddraw.dll`, `opengl32.dll`) but that **the newer
overlay hooking code conflicts with other hooks and proxies**, up to and including crashes when it
tries to hook a game that already has one. The same threads name `CreateDevice` explicitly as part of
the overlay's initialisation path, and the general rule surfaces repeatedly: **two overlays using the
same hooking method on the same object will conflict.**

That matches the observed failure closely — a foreign pointer already in the device-creation slot,
and a recursion when our chain and theirs each call through to what they believe is the original.

**Two honest limits.** This is forum and community material, not a Valve technical statement, and
none of it names Alan Wake or this recursion specifically — so it corroborates the *class* of
failure, not this instance. And the timing detail the board records (clean when the first block lived
16 ms, fatal at 700 ms) is a race whose shape is ours; nothing public speaks to it. **Nothing here
justifies changing the fix**, which stands on our own measurement.

## ⭐ The practical addition: turn the overlay off and the race cannot occur

The `[PD]` row's fix is the right permanent answer — refuse to chain into a foreign pointer. But for
the `[FLAT]` relaunch that follows it, there is a free control the row does not mention: **disable
the Steam overlay for this game** (per-game: Properties → General → uncheck the in-game overlay), and
the foreign pointer should not appear at all.

That gives a clean two-way test at zero extra cost:

| overlay | expected |
| --- | --- |
| **off** | slot 16 is ours; no foreign pointer logged; no recursion. If a foreign pointer *still* appears, **it is not the Steam overlay** — and the module name in the log is then a genuinely new finding worth chasing. |
| **on** | the new refusal path is exercised. It should log the foreign module and stand down, not recurse. |

So one setting turns "did we fix the race?" and "was it really the overlay?" into two separate,
individually readable launches, and it makes the first stereo-proxy run — the one that actually
matters — repeatable without a third-party hook in the frame at all. Given launch 1 died in one
millisecond, having a configuration where the race provably cannot arise is worth more than the
usual "try it and see".

⚠️ Two cautions. The Steam overlay is how some setups reach screenshots and the in-game browser, so
turn it back on afterwards. And **record which state each log came from** — a `slot94`-style
ambiguity between runs is exactly the kind of thing that costs a session later.

## Concrete next steps

1. Build the refusal path as the `[PD]` row specifies. Nothing here changes it.
2. On the first `[FLAT]` relaunch, run **overlay off** — the cleanest possible read of the stereo
   proxy, and it confirms the overlay was the foreign pointer by its absence.
3. Then one run with the **overlay on**, to exercise the refusal path deliberately and confirm it
   logs the module and stands down rather than recursing.
4. Record the overlay state beside every log.

## Sources

- Steam Community discussions on overlay/proxy-DLL incompatibility and the newer overlay's hooking
  behaviour (Big Picture and Steam Client Beta group threads), read 2026-09-05 — community reports,
  not a Valve statement. Credit: the Steam community posters who documented it.
- This project's board `[PD]` row and the 2026-09-05 `/lm` launch-1 measurements, which are the
  actual evidence for the diagnosis.
