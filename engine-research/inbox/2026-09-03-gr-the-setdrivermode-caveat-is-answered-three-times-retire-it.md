# The `SetDriverMode` caveat is answered — three times now, retire it

**From:** `/gr` (2026-09-03, estate sweep)
Supersedes: the ⚠️ clause on the first `[PD]` row of `status/alan-wake-vr.md`'s `OPEN (2026-09-02)`
block — *"which is `[reported]`, not verified — if the mapping is wrong the conclusion inverts, and
`/gr` has been asked to check it against NVIDIA's `nvapi.h`"*
**Topic:** [`external-research/topics/2026-09-01-nvapi-function-ids-confirmed-against-nvidias-own-table.md`](../../external-research/topics/2026-09-01-nvapi-function-ids-confirmed-against-nvidias-own-table.md)
(extended today)

## The ask, and why this drop exists

The board asks `/gr` to check that `0x5E8F0BEC` really is `NvAPI_Stereo_SetDriverMode`. **It has been
checked three times, and the first was before the row asking for it was written.**

| When | Who | Result |
|---|---|---|
| 2026-09-01 | `/gr` | all six ids match NVIDIA's published `nvapi_interface.h`; sanity-checked by asking for a seventh name it was not given the id of |
| 2026-09-02 | `/sr` | independent re-read of the same header, all six match |
| **2026-09-03** | `/gr` | independent re-read, **two positive controls inside the same query**, and the fetch reached the file's closing `#endif` — so not a truncated head |

Today's read returned: `0x5E8F0BEC` → `NvAPI_Stereo_SetDriverMode`, `0x96EEA9F8` →
`NvAPI_Stereo_SetActiveEye`, `0x0150E828` → `NvAPI_Initialize` (control), `0x239C4545` →
`NvAPI_Stereo_Enable` (control). `[reported 2026-09-03, n=3 independent reads]`

## What to change

1. **Delete the ⚠️ clause from that `[PD]` row.** The conclusion does not invert; the mapping is as
   solid as a first-party published table read three times by two session types can make it. While
   the clause stands it makes the project's **main line** read as resting on an open question, which
   is the most expensive kind of stale caveat.
2. **§6 of the dossier can drop any matching hedge** if it carries one. The substantive finding is
   unchanged and worth restating plainly: **Alan Wake never calls `SetDriverMode`, so it never asks
   for Direct mode, so the driver stays in Automatic and the game never built two eyes — they are
   ours to build.**
3. The row's *other* half is untouched and still worth doing: the `[FLAT]` breakpoint on
   `0x100D8B50` closes the genuinely open hole, which is a call reaching NVAPI through a
   runtime-computed pointer that a static caller count cannot see. **That** is the way the verdict
   could still be wrong — not the name lookup.

## ⚠️ Tag hygiene, and one of these was mine

The 2026-09-02 `/sr` addendum inside that topic carried `[verified-static 2026-09-02, n=2 reads]`.
**`verified-static` is not one of the eight vocabulary names**, so it read as a strong claim to a
human and as *untagged* to every tool. I have corrected it in my own lane to `[reported 2026-09-02,
n=2 reads]`, keeping "first-party, from NVIDIA's own header" in the prose so no strength is lost —
following `/gs`'s own 2026-09-02 precedent, which deliberately avoided `inferred-static` because
that would understate a vendor-documentation read.

Nothing for you to do about that one. It is flagged here only because the same invented tag turned
up in **six** live places estate-wide this morning, several of them written by me on 2026-09-02, and
`/gs`'s sweep log records check 3b as "clean estate-wide" as of that date. The four inside
`external-research/` are fixed today. Two are in `/sr`'s library and one in XIII's dossier; drops
have gone to those owners.
