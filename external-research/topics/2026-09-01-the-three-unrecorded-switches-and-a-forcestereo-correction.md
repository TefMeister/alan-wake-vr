# The three unrecorded switches — and `-forcestereo` is an AUDIO option, not a stereo-3D one

**Status:** 🆕 new · **Priority:** high for the correction, medium-high for the rest — one of the
three previously-unrecorded switches turns out to be a genuine VR-comfort lever Remedy shipped, and
one switch the dossier and status board are counting on means something else entirely.

## Where this came from

`/pd`'s binary read on 2026-09-01 recovered the game's full command-line option table and found three
entries no public list we had carried: **`shaders`**, **`directaiming`** and **`nativekeys`**. It
asked for a research pass on them. Researching them also settled a fourth, which was already being
relied on.

## ⚠️ The correction: `-forcestereo` is a speaker-mode switch

Two independent public sources describe it identically `[reported 2026-09-01, n=2 sources]`:

| Source | Wording |
| --- | --- |
| GOG community command-line list | *"Forces stereo 2 channel speaker mode"* |
| *The Sudden Stop* (fan reference) | listed under **Sound**: *"Allows stereo speaker mode"* |

Both list it immediately beside **`-forcesurround`** (*"Forces 5.1 speaker mode"*), and that is
exactly how the two sit in the binary's own option table — `forcesurround · forcestereo` adjacent.
The audio reading is the only one consistent with both the documentation and the binary layout.

**This matters because it is currently being counted the other way.** `status/alan-wake-vr.md`
(2026-09-01) lists `forcestereo` as one of *"four that matter here"* alongside `developermenu`,
`rigidcamera` and `window`, in a note about the native stereo subsystem, and
`ENGINE-DOSSIER.md` §9 files it in a row of *"resolution/windowed/vsync/…/audio-channel flags"*
whose grouping is right but whose prominence elsewhere is not. **There is no evidence of a
command-line switch that turns on 3D stereo rendering** — which is consistent with the finding in
`2026-09-01-3d-vision-automatic-the-driver-makes-the-eyes-not-the-game.md`, where the on-switch for
this era's stereo was a driver-side and NVAPI-side thing, never a game launch flag.

A pointer with a `Supersedes:` header has been filed to `engine-research/inbox/`.

## ⭐ `-directaiming` and `-rigidcamera` — Remedy shipped a camera-smoothing kill switch

This is the genuinely valuable half.

- **`-directaiming`** — *"Enables 1:1 mouse control mode"* (The Sudden Stop). Community sources add
  that it **removes all mouse acceleration** and **implies `-rigidcamera`**
  `[reported 2026-09-01]`.
- **`-rigidcamera`** — added by Remedy in a patch *"for those who are sensitive to the default
  mouse/camera controls"*; it **removes the camera smoothing**, so the camera responds directly to
  input instead of interpolating toward it, and centres the camera behind Alan
  `[reported 2026-09-01]`.

**Why this is a VR finding and not a control-preferences footnote.** Camera smoothing, mouse
acceleration and any non-1:1 mapping between head/hand input and view movement are among the most
reliable causes of discomfort in a flat→VR conversion: the view lags the head, then catches up, and
the mismatch between the vestibular signal and the image is precisely the nausea mechanism. Every
project in this estate that reaches a head-tracked camera eventually has to find and defeat that
smoothing, usually by locating the interpolation in the binary.

Here **Remedy shipped the off-switch**, official and zero-risk, reachable before any hooking exists.

That also makes `-rigidcamera` a useful *diagnostic*: if the camera still lags with it set, the
residual smoothing is somewhere else, and that is worth knowing early rather than after a hook is
built on the assumption it was the only one.

## `-nativekeys` and `-shaders`

- **`-nativekeys`** — reported to stop the **keyboard layout from being changed/lost on exiting the
  game** `[reported 2026-09-01]`. So this is an OS input-layout courtesy switch, not an input-path
  lever. Worth setting for any automation run purely so an unattended session cannot leave the
  machine's keyboard layout altered. (Unrelated in mechanism to the DOOM keyboard-layout trap
  recorded elsewhere in this estate, which was about virtual-key codes on the *input* side — noted
  only so the two are not conflated.)
- **`-shaders`** — **no public documentation found.** It appears in no community list. It is first in
  the binary's option table and takes no obvious value. Left explicitly unknown; a plausible reading
  is a shader-recompilation or shader-debug switch, but that is `[hypothesis]` with nothing behind
  it. If §6 ever needs the game to rebuild its shaders — which the clip-space-footer technique in the
  sibling topic *would* need — this switch is worth trying live and observing, since it is the only
  shader-named affordance the game exposes.

## Concrete next steps

1. **Set `-directaiming -rigidcamera` as part of this project's standard launch line**, alongside the
   already-recommended `-freecamera -developermenu`. It costs nothing and removes a smoothing layer
   that would otherwise have to be found in the binary.
2. **Stop treating `-forcestereo` as a stereo-rendering switch.** The stereo question is decided by
   the NVAPI driver-mode xref in the sibling topic, not by a launch flag.
3. **Try `-shaders` live once, and observe** — it is cheap, and it is the only unknown left in the
   table.

## Sources

- https://www.gog.com/forum/alan_wake/info_command_line_options_for_alan_wake_1
- https://www.alanwake.info/2011/10/alan-wake-pc-commands.html
- https://alanwake.fandom.com/wiki/Console_commands
- https://alanwake.fandom.com/wiki/Changelogs
- https://steamcommunity.com/app/108710/discussions/0/828939978253890023/
