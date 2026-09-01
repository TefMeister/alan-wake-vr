# Research index

**Last `/gr` pass: 2026-09-01 — FULL.** Inbox drained (the `-freecamera` verdict → ✅). Two new
topics, both answering questions the modding side asked directly: NVIDIA 3D Vision Automatic makes
its two eyes **in the driver**, so the game's stereo uniform corrects effects rather than moving a
camera — and `-forcestereo` is an **audio** switch, corrected into `engine-research/inbox/`. The
clip-space stereo footer this uncovered was filed to the cross-engine library for `/sr`.

Every research topic gathered for this project, newest first. Each row links to a self-contained
write-up in `topics/`. Status tags:

- 🆕 **new** — found, not yet acted on by the modding side.
- 👀 **reviewed** — a modding session has read it and factored it into a decision, but nothing shipped from it yet.
- ✅ **incorporated** — directly led to a real change (code, a test, a note) in one of the other five repos; linked below.
- ❌ **dead end** — checked out, didn't pan out; kept for the record so it isn't re-investigated from scratch.

| Date | Topic | Status | Summary |
| --- | --- | --- | --- |
| 2026-09-01 | [Three unrecorded switches, and a `-forcestereo` correction](topics/2026-09-01-the-three-unrecorded-switches-and-a-forcestereo-correction.md) | 🆕 new | `-forcestereo` is a **2-channel speaker-mode** flag, not stereo 3D — it sits beside `-forcesurround` in the binary and in every public list; a `Supersedes:` pointer went to `engine-research/inbox/`. The real find is **`-directaiming` / `-rigidcamera`**: Remedy's own shipped switches for 1:1 mouse control and **removing camera smoothing** — the comfort layer a VR conversion normally has to hunt down in the binary. `-nativekeys` preserves the keyboard layout on exit; `-shaders` has no public documentation at all. |
| 2026-09-01 | [3D Vision Automatic: the driver makes the eyes, not the game](topics/2026-09-01-3d-vision-automatic-the-driver-makes-the-eyes-not-the-game.md) | 🆕 new | Answers the modding lane's question. Neither branch it offered is right: the driver did **not** reproject, and the game's shaders did **not** apply the offset. NVIDIA's own docs — the driver appends a clip-space footer `x += Separation*(w − Convergence)` to every vertex shader and splits each draw in two. `g_vStereo_Separation_Convergence` / `Stereo Texture` is the `nvstereo.h` **correction** pattern, a consumer of driver-published values. One live thread remains: whether `Activate Stereo` calls `NvAPI_Stereo_SetDriverMode(DIRECT)`. Downgrades §6's shortcut; hands us a technique we can build ourselves. |
| 2026-08-25 | [Native -freecamera + -developermenu launch flags](topics/2026-08-25-native-freecamera-developermenu-launch-flags.md) | ✅ incorporated | The retail game ships two real Remedy-added dev tools reachable via launch options — a free camera (controller-driven) and a Developer Menu — plus a well-documented full command-line flag set. Same category as the Psychonauts precedent: a dormant official tool, not something to reverse-engineer. Factored into ENGINE-DOSSIER.md §6/§9/§10. **✅ 2026-09-01: binary-confirmed by the modding side** — both flags sit in `AlanWake.exe`'s option table immediately after the parser's own `Unknown command line option "%s"`, so they are parsed options with a rejection path, not suggestive strings. The same check recovered three switches this topic did not have; see the 2026-09-01 row above. |
| 2026-08-25 | [Native 3D Vision support + HelixMod](topics/2026-08-25-native-3d-vision-support-and-helixmod.md) | 👀 reviewed | The game shipped with real NVIDIA 3D Vision support, with later patches reportedly needing little to no third-party fixing; live Ctrl+F3/Ctrl+F4 separation hotkeys are a strong hint the per-eye offset mechanism is already reachable. Factored into ENGINE-DOSSIER.md §6/§9. |
| 2026-08-25 | [DRM history + vorpX status](topics/2026-08-25-drm-history-and-vorpx-status.md) | ✅ incorporated | Originally shipped on Games for Windows Live (undated removal, unlike Alice/PoP2008's clean dated patches); vorpX works but only confirmed in the weaker Cinema mode for the original game — a real gap vs. this portfolio's stronger fronts, recorded honestly. **Follow-up: the modding session specifically checked the installed build for GFWL/xlive artifacts and found none** — see ENGINE-DOSSIER.md §4. |

## How to add a topic

1. New file in `topics/`, named `YYYY-MM-DD-short-slug.md`.
2. One row added to the table above, newest at the top.
3. Update the status tag here as it moves through review → incorporated/dead-end (the modding side should update this when it acts on a lead, so the index reflects reality without the research side needing to poll).
