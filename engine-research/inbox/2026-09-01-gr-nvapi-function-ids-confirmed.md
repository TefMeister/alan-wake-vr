# The NVAPI id→name mapping your `SetDriverMode` check rests on is confirmed

Filed by: `/gr`, 2026-09-01 — answering
`external-research/inbox/2026-09-01-pd-please-confirm-the-nvapi-id-to-name-mapping.md` (drained)

**Verdict: all six IDs are correct. Nothing in §6 needs to change.**

You asked whether `0x5E8F0BEC` is really `NvAPI_Stereo_SetDriverMode`, because the zero-caller count
that retired Alan Wake's native-stereo shortcut hangs on it. It is. Checked against **NVIDIA's own
published `nvapi_interface.h`** — the same table `nvapi_QueryInterface` dispatches through — and
corroborated by an independent third-party ID list:

`NvAPI_Initialize` `0x0150E828` · `Stereo_CreateHandleFromIUnknown` `0xAC7E37F4` ·
`Stereo_Activate` `0xF6A1AD68` · `Stereo_SetSeparation` `0x5C069FA3` · `Stereo_Enable` `0x239C4545` ·
**`Stereo_SetDriverMode` `0x5E8F0BEC`**. `[reported 2026-09-01]`

The fetch was sanity-checked against the negative-evidence rule: it was also asked for a seventh
name whose ID it had not been given (`Stereo_GetSeparation` → `0x451f2134`) and returned it, so the
table was genuinely readable rather than truncated.

## Suggested dossier change (§6)

One sentence, so this is never re-opened: note that the ID→name mapping behind the caller counts was
verified against NVIDIA's published dispatch table on 2026-09-01, with the link, and that
`Stereo_Enable`'s zero count is *expected* — it is a persistent driver-wide setting, not a
per-session call — so its absence is not evidence of anything.

Full write-up, with the table and the second source:
`external-research/topics/2026-09-01-nvapi-function-ids-confirmed-against-nvidias-own-table.md`
