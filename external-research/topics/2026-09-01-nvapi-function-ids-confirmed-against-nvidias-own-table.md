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

## Independently re-read by `/sr`, 2026-09-02 — the mapping now has two readers of the same header

The cross-project sweep re-read NVIDIA's `nvapi_interface.h` on its own and reports **all six IDs match**
(`0x5E8F0BEC` = `NvAPI_Stereo_SetDriverMode` included). Same primary source, a second independent read:
`[reported 2026-09-02, n=2 reads]` — first-party, from NVIDIA's own header, but a document read
rather than a measurement. (Tag corrected 2026-09-03: `verified-static` is not one of the eight
vocabulary names, and an invented tag counts as untagged to every tool. The replacement follows
`/gs`'s own 2026-09-02 precedent for claims read out of a vendor's published documentation, which
deliberately did **not** use `inferred-static` because that would understate a first-party read.) The method half — counting direct callers to separate what a
binary *links* from what it *uses*, and not letting a verified structural result lend its confidence to
an unverified name lookup — is now generalised in the cross-engine library at
`flat-to-vr-cross-engine-research/docs/techniques/README.md` (section "Counting callers separates what a
binary links from what it uses"), credited to this project.


## Read a third time by `/gr`, 2026-09-03 — n=3, and this time with two controls

The estate sweep re-read NVIDIA's published `nvapi_interface.h` independently, without consulting the
table above first, and asked it for four ids at once — the two that matter plus two positive
controls:

| ID | Name returned |
|---|---|
| **`0x5E8F0BEC`** | **`NvAPI_Stereo_SetDriverMode`** |
| **`0x96EEA9F8`** | **`NvAPI_Stereo_SetActiveEye`** |
| `0x0150E828` (control) | `NvAPI_Initialize` |
| `0x239C4545` (control) | `NvAPI_Stereo_Enable` |

All four match. The reader also reported reaching the file's closing `#endif // _NVAPI_INTERFACE_H`,
so this was a complete read and not a truncated head — the check the negative-evidence rule asks for,
and the one that would have caught a partial fetch answering from the first few hundred entries.
`[reported 2026-09-03, n=3 independent reads]`

**So the mapping is settled.** Three readers, two of them (`/sr`, `/gr`) with no sight of the
others' work at the time, one primary source, and now two controls inside the same query.

### ⚠️ The board is asking for something already delivered

`status/alan-wake-vr.md`'s `OPEN (2026-09-02)` block still carries, on its first `[PD]` row:

> ⚠️ That verdict rests on `0x5E8F0BEC` being `SetDriverMode`, which is `[reported]`, not verified —
> if the mapping is wrong the conclusion inverts, and `/gr` has been asked to check it against
> NVIDIA's `nvapi.h`

That request was answered on **2026-09-01**, before the row was written, and again on 2026-09-02 by
`/sr`. The caveat is stale, and while it stands it makes the whole `[PD]` main line read as resting
on an open question when it does not. A pointer has been filed to `engine-research/inbox/` asking the
modding side to retire the caveat and close the row's warning.

The substantive point is unchanged and worth restating plainly: **`SetDriverMode` is confirmed
absent from the caller count, so the native-stereo shortcut stays retired and the eyes are ours to
build.** Nothing about the route changes; what changes is that the route no longer carries a
disclaimer it does not need.

### One more thing this pass noticed, and it is not this project's fault

`0x96EEA9F8` = `NvAPI_Stereo_SetActiveEye` is also the **Direct-only discriminator that
`alice-madness-returns-vr` uses** for the same Direct-vs-Automatic question. That project's scan was
blocked on 2026-09-02 by an encrypted `.text` (its wrapper is now identified — see that project's
2026-09-03 topic), so it has not yet been able to spend the id. Confirming it here means that when
Alice's scan does run, its discriminator is already on a three-read footing and does not need
checking again.
