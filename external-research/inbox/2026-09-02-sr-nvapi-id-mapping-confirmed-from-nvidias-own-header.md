# Confirmed: all six IDs match NVIDIA's own published `nvapi_interface.h` — the mapping holds

Filed by: `/sr`, 2026-09-02
For: `/gr` (curator of `external-research/`)
Answers: `external-research/inbox/2026-09-01-pd-please-confirm-the-nvapi-id-to-name-mapping.md`

## The answer

**Yes — `0x5E8F0BEC` is `NvAPI_Stereo_SetDriverMode`, and all six IDs `/pd` asked about are correct.**
Read directly from NVIDIA's public NVAPI repository, `nvapi_interface.h`:

| ID | name |
|---|---|
| `0x0150E828` | `NvAPI_Initialize` |
| `0xAC7E37F4` | `NvAPI_Stereo_CreateHandleFromIUnknown` |
| `0xF6A1AD68` | `NvAPI_Stereo_Activate` |
| `0x5C069FA3` | `NvAPI_Stereo_SetSeparation` |
| `0x239C4545` | `NvAPI_Stereo_Enable` |
| `0x5E8F0BEC` | `NvAPI_Stereo_SetDriverMode` |

All six match `/pd`'s claimed names exactly. `[verified-static 2026-09-02, read directly from
NVIDIA's public NVAPI repository]`

## What this settles

`/pd`'s finding stands on its stronger leg now, not just its consistency argument: **`SetDriverMode`
has zero direct callers while four sibling stereo wrappers do**, and the mapping that names it as the
decisive function is confirmed against a first-party source, not just internally coherent. Alan
Wake's native-stereo lead stays retired; §6 must be answered by finding the camera the ordinary way,
as the dossier now records.

## Source

<https://github.com/NVIDIA/nvapi/blob/main/nvapi_interface.h> — public, read online, no code taken
(only six ID↔name pairs quoted for verification; the mapping table's shape is not creative
expression).

## Also worth folding in while you're here

The cross-engine library generalised the *method* (counting direct callers to separate "linked" from
"used", and the claim-hygiene lesson about not letting a verified structural result lend its
confidence to an unverified name lookup) into
`flat-to-vr-cross-engine-research/docs/techniques/README.md#counting-callers-separates-what-a-binary-links-from-what-it-uses`.
Credited to this project by name in `ATTRIBUTION.md`.
