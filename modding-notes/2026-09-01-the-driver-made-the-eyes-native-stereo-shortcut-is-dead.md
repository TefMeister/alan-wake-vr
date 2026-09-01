# 2026-09-01 — Alan Wake never took the eyes off the driver. The native-stereo shortcut is dead.

**Date:** 2026-09-01, dev machine, `/pd` session. **The game was not launched, and nothing here has
been run.** Static analysis of shipped DLLs only.

---

## The question, and who framed it

This project's most attractive lead was that Alan Wake ships real NVIDIA 3D Vision support, with a
live in-game separation control — which was read as implying *"the per-eye offset mechanism is
already live and reachable."* If true, that is most of a VR camera for free.

`/gr` filed an inbox drop challenging exactly that reading, and — this is the useful part — it
supplied a **single static check with the outcomes written down in advance**:

> Does `renderer_sf_Win32.dll`'s stereo path call `NvAPI_Stereo_SetDriverMode`, and with which
> constant?
> **DIRECT** ⇒ a real self-driven two-eye path exists and the shortcut survives intact.
> **AUTOMATIC or absent** ⇒ the subsystem is a correction layer over a driver that no longer ships.

A pre-committed decision rule is worth a great deal: the result could not be argued either way after
the fact.

## How it was answered without a debugger

NVAPI does not expose ordinary imports. Entry points are resolved at runtime by **published function
ID** through `nvapi_QueryInterface`, so every wrapper contains a `push imm32` of its own ID — which
makes each one findable on disk as a five-byte pattern.

All seven stereo IDs are present in `renderer_sf_Win32.dll`. Presence proves nothing on its own,
because unused NVAPI dispatch stubs get linked in regardless. So the measurement that matters is
**how many direct callers each wrapper has**:

| NVAPI wrapper | ID | entry | direct callers |
|---|---|---|---|
| `NvAPI_Initialize` | `0x0150E828` | `0x100D04D0` | 4 |
| `NvAPI_Stereo_CreateHandleFromIUnknown` | `0xAC7E37F4` | `0x100D7600` | 2 |
| `NvAPI_Stereo_Activate` | `0xF6A1AD68` | `0x100D7820` | 1 |
| `NvAPI_Stereo_SetSeparation` | `0x5C069FA3` | `0x100D7C60` | 1 |
| **`NvAPI_Stereo_SetDriverMode`** | `0x5E8F0BEC` | `0x100D8B50` | **0** |
| `NvAPI_Stereo_Enable` | `0x239C4545` | `0x100D72F0` | 0 |

`[inferred-static 2026-09-01]` No wrapper is exported (1,231 exports checked), so no other module
calls in, and an absolute-immediate scan finds no stored pointer to `0x100D8B50` either.

**The zero is only meaningful because of the contrast.** Four of the six wrappers *are* called, so in
this binary a linked-but-unused stub is plainly distinguishable from a used one. That is what turns
"absent" into a result rather than an absence of evidence.

## The answer, and what it costs us

**`SetDriverMode` is never called.** It must be called before device creation to hand per-eye
rendering to the application, so the driver mode is never switched to DIRECT. Alan Wake used 3D
Vision **Automatic** — the *driver* duplicated each draw call and appended the clip-space offset
`x += Separation*(w − Convergence)`. The game's role was the consumer one: create a stereo handle,
activate it, set separation.

So `g_vStereo_Separation_Convergence` is a **consumer of driver-published values, not the producer of
an eye offset**. Driving it changes how the game corrects its post-processing and **moves no camera**.
The queued xref on that symbol is retired — it maps where an eye offset *would* go.

**§6 must now be answered the ordinary way:** find where the view-projection reaches the GPU and
override it. This project has no shortcut, and it is better to know that now than after building on it.

## ⚠️ The weak link, stated plainly

The structural result is solid and was verified here: seven **genuine** NVAPI dispatch IDs are
referenced by the game (all seven occur in both shipped drivers, `nvapi.dll` and `nvapi64.dll`, so
they are real function IDs), and one of them has zero callers while four have callers.

**What I could not verify on this machine is that `0x5E8F0BEC` is `NvAPI_Stereo_SetDriverMode`.**
That mapping comes from the published NVAPI ID list. I tried to confirm it against the shipped
driver and **the id→name table is stripped** — none of the function-name strings occur in either
`nvapi.dll` or `nvapi64.dll`. **If the mapping is wrong, this whole conclusion inverts**, so it is
recorded as `[reported]` rather than folded into the `[inferred-static]` result.

Supporting it short of proof: under this mapping the four *called* IDs form a coherent stereo
initialisation sequence (`Initialize` → `CreateHandleFromIUnknown` → `Activate` → `SetSeparation`),
and the two *uncalled* ones are exactly the pair a game in Automatic mode would not need. A scrambled
mapping would be unlikely to look that tidy. That is consistency, not confirmation.

**To close it:** check the IDs against NVIDIA's published `nvapi.h`. That is web research, so it
belongs in a `/gr` drop, not here.

## What is NOT established

The scan finds `E8` rel32 calls and absolute immediates. **A call through a runtime-computed pointer
would be missed.** That is unlikely — the other four wrappers are called directly, so the convention
is established — but it is the one way this conclusion could be wrong. The diagnostic that would show
the *derivation* is wrong rather than a detail needing tuning: set a breakpoint on `0x100D8B50` in a
live run and see whether it is ever hit. If it is, everything above is void.

## Two things gained along the way

- **`-forcestereo` is an audio switch** — *"forces stereo 2 channel speaker mode"*, beside
  `-forcesurround` in the public lists and in the binary's own option table.
  `[reported 2026-09-01, n=2 independent sources]` It was recorded here as a stereo-rendering lead.
  There is **no launch switch that enables stereo rendering**, which is consistent with the main
  finding.
- **`-rigidcamera` removes camera smoothing** (Remedy patch-added) and centres the camera behind Alan.
  `[reported]` Camera smoothing is the comfort hazard a VR conversion normally has to hunt down in the
  binary; here there is an official off-switch. Also a **diagnostic**: residual lag with it set means
  the smoothing lives somewhere else. Add it to the standard launch line beside `-freecamera
  -developermenu`, along with `-directaiming` (1:1 mouse) and `-nativekeys`.

## When this game is next up

Nothing here needs a launch to be believed. The one confirmation worth having, if a debugger is ever
attached for other reasons: **breakpoint `renderer_sf_Win32.dll+0xD7B50` (VA `0x100D8B50` at the
default base) and confirm it never fires.** If it fires, the shortcut is alive after all.
