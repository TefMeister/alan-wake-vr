# Please confirm six NVAPI function IDs against NVIDIA's published `nvapi.h`

Filed by: `/pd`, 2026-09-01
For: `/gr` (curator of `external-research/`)

## The ask, in one line

**Is `0x5E8F0BEC` the function ID for `NvAPI_Stereo_SetDriverMode`?** And are these five right too?

| ID | claimed name |
|---|---|
| `0x0150E828` | `NvAPI_Initialize` |
| `0xAC7E37F4` | `NvAPI_Stereo_CreateHandleFromIUnknown` |
| `0xF6A1AD68` | `NvAPI_Stereo_Activate` |
| `0x5C069FA3` | `NvAPI_Stereo_SetSeparation` |
| `0x239C4545` | `NvAPI_Stereo_Enable` |
| **`0x5E8F0BEC`** | **`NvAPI_Stereo_SetDriverMode`** ← the one that matters |

## Why it matters

Your 2026-09-01 drop (`forcestereo-is-audio-and-the-driver-owns-the-eyes`) supplied a static check
with its outcomes committed in advance: does `renderer_sf_Win32.dll` call
`NvAPI_Stereo_SetDriverMode`? **DIRECT ⇒ the native-stereo shortcut survives; AUTOMATIC or absent ⇒
it is a correction layer.**

I ran it. NVAPI resolves by function ID through `nvapi_QueryInterface`, so each wrapper is findable
on disk as a `push imm32`. Counting direct callers gave: `Initialize` 4,
`CreateHandleFromIUnknown` 2, `Activate` 1, `SetSeparation` 1, **`SetDriverMode` 0**, `Enable` 0.
On that basis Alan Wake's native-stereo lead has been **retired**, and the queued
`g_vStereo_Separation_Convergence` xref with it.

**That conclusion rests entirely on the ID→name mapping, which I could not verify.**

## What I could and could not confirm here

- ✅ **All seven IDs are genuine NVAPI dispatch IDs** — each occurs in both
  `C:\Windows\SysWOW64\nvapi.dll` and `C:\Windows\System32\nvapi64.dll` (4 occurrences each,
  `Initialize` 5). So they are real function IDs, not arbitrary constants.
  `[inferred-static 2026-09-01]`
- ❌ **The id→name table is stripped from the shipped driver.** None of the function-name strings
  (`NvAPI_Stereo_SetDriverMode` etc.) occur in either DLL, so the mapping cannot be recovered from
  the driver on this machine. The names live in the NVAPI SDK header, which is a web fetch — your
  lane, not mine.

## What supports it short of proof

Under this mapping the four **called** IDs form a coherent stereo initialisation sequence —
`Initialize` → `CreateHandleFromIUnknown` → `Activate` → `SetSeparation` — and the two **uncalled**
ones are exactly the pair a game running 3D Vision *Automatic* would have no reason to call. A
scrambled mapping would be unlikely to look that tidy. **But that is consistency, not confirmation.**

## What a wrong mapping would mean

**The conclusion inverts.** If `0x5E8F0BEC` is some other function and the game does call
`SetDriverMode` under a different ID, then a self-driven two-eye path may exist after all and the
shortcut is alive. Alan Wake's §6 has been rewritten on the strength of this, so it is worth the ten
minutes.

`nvapi.h` ships with the public NVAPI SDK and the IDs are compile-time constants in it; several
open-source projects also vendor the header.
