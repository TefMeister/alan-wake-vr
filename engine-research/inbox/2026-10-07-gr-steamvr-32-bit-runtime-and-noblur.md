# Two small answers: SteamVR's 32-bit runtime, and `-noblur` is real

From `/gr`, 2026-10-07. Topic: `external-research/topics/2026-10-07-steamvr-32-bit-runtime-and-noblur-is-documented.md`.

1. **Dossier "Runtime on the dev PC"** says the 32-bit key is empty although SteamVR ships
   `steamxr_win32.json`. Public reason: **SteamVR 2.17 (stable 2026-09-10) added 32-bit OpenXR**, and
   only fills the 32-bit key when you accept its "set as default OpenXR runtime" prompt `[reported]`.
   For the home-PC first look, `runtime_json=` can point at `steamxr_win32.json` directly. Untested here.
2. **The `[FLAT]` row's `-noblur` "completely untested"** — still untested by us, but no longer
   undocumented: Remedy's v1.02 patch notes say *"Fix that blur occasionally got re-enabled even if
   -noblur command line option was specified"* `[reported]`. So it is a shipped, supported switch that
   turns motion blur off. Worth adding to the standard launch line beside `-directaiming`.
