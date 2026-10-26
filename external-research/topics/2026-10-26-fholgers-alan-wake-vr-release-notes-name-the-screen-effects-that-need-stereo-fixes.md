# fholger's Alan Wake VR release notes name the screen effects that needed stereo fixes

*Watch check for the paused project (paused 2026-10-25 because fholger is making an Alan Wake VR mod). Our board's
frozen rows include the street-lamp glow sprites that stay put through the eye shift (dossier §6l) and the camera
jitter recorded on 2026-10-11. fholger's public notes touch both areas.*

## State of fholger's mod on 2026-10-26 `[reported 2026-10-26]`

- GitHub `fholger/alanwake_vr`: two releases, v1.0.0 (2026-10-17) and v1.1.0 (2026-10-20); nothing newer. The
  repository holds a README, a third-party notice and funding links, not the source.
- The mod's site (alanwake.vrmods.eu) offers v1.1.0 as a free download (Patreon for donations): 6DoF head tracking
  and "synced stereo rendering", gameplay unchanged (seated, third person, gamepad or keyboard and mouse). A
  first-person mode with motion controls "might" come later; American Nightmare "might" be supported later. Original
  Alan Wake only (Steam, GOG, Epic), not the Remastered edition.
- Known issue on the site: Meta Horizon Link does not work, and the Meta Link **32-bit** OpenXR runtime appears broken,
  so Quest owners are told to use Steam Link or Virtual Desktop. This matches our 2026-10-07 topic on 32-bit OpenXR
  runtimes for this 32-bit game.

## What the v1.1.0 notes say was fixed `[reported 2026-10-26]`

- the pickup-item highlight effect made stereo-correct;
- "bright spots on light sources" restored;
- some fog billboards improved in VR;
- interaction markers moved into the 3D scene instead of the HUD layer; prompts and subtitles raised on the HUD;
- the post-processing vignette disabled, because it is not stereo-correct.

## Why it matters for this project `[hypothesis]`

- Our frozen `[PD]` row about lamp halos that stay put is very likely the same family as fholger's "bright spots on
  light sources" and "fog billboards": screen-space or billboard passes that need their own per-eye handling. If the
  project resumes on top of his mod, that work is already done.
- "Synced stereo" (both eyes for the same game frame) is the opposite choice to our alternate-frame design, where each
  eye is a separate game frame. Our 2026-10-11 jitter recording found the camera value unchanged on some pictures
  despite a fresh pose; alternate-frame rendering is one of the named suspects. fholger's choice suggests the synced
  route is workable in this engine, which is useful if the project ever resumes on its own code.

## Next step

None while paused. If Tefa resumes the project, start from fholger's release (as the pause note says), and check his
README for any public description of how the synced stereo is done before re-opening our own jitter row.

## Sources

- fholger, Alan Wake VR, https://github.com/fholger/alanwake_vr (releases page, read 2026-10-26)
- fholger, Alan Wake VR site, https://alanwake.vrmods.eu/ (read 2026-10-26)
