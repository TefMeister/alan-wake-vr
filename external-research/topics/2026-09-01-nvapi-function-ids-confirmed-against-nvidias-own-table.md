# The six NVAPI function IDs are confirmed — `SetDriverMode` really is `0x5E8F0BEC`

**Date:** 2026-09-01
**Answers:** `external-research/inbox/2026-09-01-pd-please-confirm-the-nvapi-id-to-name-mapping.md`
(filed by `/pd`, now drained)

## What was asked

`/pd` ran the static check this lane supplied on 2026-09-01 — *does `renderer_sf_Win32.dll` call
`NvAPI_Stereo_SetDriverMode`?* — and got **zero direct callers**, which by the check's
pre-committed outcomes retires Alan Wake's native-stereo shortcut and makes the game's stereo
uniform a *correction* layer rather than a self-driven two-eye path.

That whole conclusion rested on one unverified assumption: that the constant `0x5E8F0BEC` is
actually `NvAPI_Stereo_SetDriverMode`. NVAPI dispatches by numeric function ID through
`nvapi_QueryInterface`, and **the shipped driver has the id→name table stripped** — `/pd` confirmed
the seven constants occur in `nvapi.dll` / `nvapi64.dll` but found none of the name strings there.
The names live in the public SDK header, which is a web read.

## The answer: all six are correct

Checked against **NVIDIA's own published `nvapi_interface.h`** — the very table
`nvapi_QueryInterface` is driven by — and independently against a third-party ID dump.

| ID | Name | NVIDIA's table | Second source |
|---|---|---|---|
| `0x0150E828` | `NvAPI_Initialize` | ✅ `0x0150e828` | ✅ (control) |
| `0xAC7E37F4` | `NvAPI_Stereo_CreateHandleFromIUnknown` | ✅ `0xac7e37f4` | ✅ |
| `0xF6A1AD68` | `NvAPI_Stereo_Activate` | ✅ `0xf6a1ad68` | ✅ |
| `0x5C069FA3` | `NvAPI_Stereo_SetSeparation` | ✅ `0x5c069fa3` | ✅ |
| `0x239C4545` | `NvAPI_Stereo_Enable` | ✅ `0x239c4545` | ✅ |
| **`0x5E8F0BEC`** | **`NvAPI_Stereo_SetDriverMode`** | ✅ **`0x5e8f0bec`** | ✅ |

`[reported 2026-09-01]` on NVIDIA's published table — it is a primary source and the authoritative
one, but this is still a document read, not something measured on this machine.

**Fetch sanity check, per the negative-evidence rule:** the same fetch was asked for a seventh
name it was *not* told the ID of, `NvAPI_Stereo_GetSeparation`, and returned `0x451f2134` — so the
table really was readable rather than answering from a truncated head. The reader reported the table
running from `NvAPI_Initialize` to `NvAPI_UninstallRise`, i.e. end to end. The second source's entry
for `NvAPI_Initialize` reads `0x000000eb`, which is an ordinal column and not the dispatch ID; its
five *stereo* rows match NVIDIA's exactly, so it corroborates the ones that matter.

## What this means for the project

**Nothing changes — and that is the useful outcome.** `/pd`'s rewrite of `ENGINE-DOSSIER.md` §6
stands on a verified footing:

- Alan Wake calls `Initialize` → `CreateHandleFromIUnknown` → `Activate` → `SetSeparation`.
- It never calls `SetDriverMode`, so it never asks for **Direct** mode, so the driver stays in
  **Automatic** and the driver makes both eyes.
- It never calls `Stereo_Enable` either, which fits: `Enable` is a persistent driver-wide setting a
  game has no business flipping, not a per-session call.

The retired native-stereo shortcut stays retired, and the shelved
`g_vStereo_Separation_Convergence` xref stays shelved. The route forward is the one the 2026-09-01
clip-space-footer topic describes: **build the two eyes ourselves**, because this game never did.

## Why the mapping was worth ten minutes anyway

`/pd` was right to refuse to bank it. A single wrong row would have inverted the conclusion, and
"the four called IDs form a tidy init sequence" is consistency, not proof — a plausible-looking
sequence is exactly what a *partly* wrong mapping would also produce. The cost of checking was one
fetch; the cost of being wrong was a rewritten dossier section pointing the project down the wrong
road.

## The reusable part

That NVAPI is called by ID, that the ID→name table is stripped from the shipped driver, and that
NVIDIA publishes the whole table in the open — together these make **"which NVAPI functions does
this binary actually call?" a purely static, purely offline question for any 3D-Vision-era game**.
Several games in this portfolio are from exactly that era. Filed to the cross-engine library for
`/sr` rather than kept here.

## Sources

- NVIDIA, `nvapi_interface.h` (the published function-ID dispatch table) —
  https://github.com/NVIDIA/nvapi/blob/main/nvapi_interface.h
- NVIDIA, `nvapi_lite_stereo.h` (`NvAPI_Stereo_SetDriverMode`, Direct vs Automatic) —
  https://github.com/NVIDIA/nvapi/blob/main/nvapi_lite_stereo.h
- jNizM, `NVIDIA_NvAPI` — `info/NvAPI_IDs.txt`, an independently compiled ID list —
  https://github.com/jNizM/NVIDIA_NvAPI/blob/master/info/NvAPI_IDs.txt
