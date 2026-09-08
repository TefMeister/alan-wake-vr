# Two real, dev-exposed tools ship in the retail binary: `-freecamera` and `-developermenu`, plus a well-documented full command-line flag set

**Status:** 🆕 new · **Priority:** very high — the same category of find that unblocked Psychonauts'
investigation elsewhere in this portfolio (a dormant, official dev tool rather than something to
reverse-engineer from scratch). Directly seeds `ENGINE-DOSSIER.md` §6, §9, and §10.

## What was found

Alan Wake (the original 2010 PC release, not Remastered) ships with two genuine, Remedy-added
command-line flags, confirmed via multiple independent community sources (a dedicated Steam guide,
the Alan Wake Fandom wiki's "Console commands" page, and community discussion):

- **`-freecamera`** — added in patch v1.04. Enabled via Steam launch options
  (right-click → Properties → launch options → `-freecamera`). In-game, toggled by **pressing the
  right thumbstick** (requires a controller — no confirmed keyboard/mouse equivalent found). Once
  active: left stick moves, right stick rotates the camera, LT/RT scale movement speed, LB/RB move
  vertically, and X/B cycle through camera speed presets. This is a real, first-party free-camera
  tool — exactly the kind of thing this project's §6/§10 (camera & projection delivery, autonomous
  harness recipe) benefits enormously from having *before* any hooking work starts: it's a safe,
  zero-risk way to explore the world and observe camera behavior, and a plausible foundation for an
  autonomous frame-capture harness later.
- **`-developermenu`** — also a launch-option flag, adds a "Developer Menu" entry to the game's main
  menu. Per two independent Steam guides, its confirmed scope so far is **episode/difficulty
  selection and maximum ammo/consumables** — useful for save-recovery and fast iteration through
  content, but **not confirmed (by this research pass) to include camera, rendering, or other
  technical debug tools** — don't assume it goes further than documented without checking live. Still
  worth enabling by default during this project's investigation, since even a "just" progression/
  ammo debug menu is a genuine, low-effort way to reach any part of the game quickly for testing.
- **A well-documented general command-line flag set** (Fandom wiki + a dedicated fan reference site,
  "The Sudden Stop"'s Alan Wake PC Commands post): `-w <n>`/`-h <n>` (screen width/height), `-window`
  (windowed mode), `-novsync`, `-showfps`, `-sensscale <n>` (mouse sensitivity), `-locale=xx`,
  `-forcesurround`/`-forcestereo` (audio channel forcing) — a solid, citable starting point for
  `ENGINE-DOSSIER.md` §9's cvar/console cheat sheet, and `-window`/`-novsync`/`-showfps` in particular
  are useful for live investigation ergonomics regardless of camera work specifically.
  - ⚠️ **SUPERSEDED 2026-09-08 — this list is `[reported]` and is now known to be wrong in one place. The parser's own option table has since been read out of the shipped binary; see "The measured flag list" at the end of this file. In particular `-w <n>` / `-h <n>` are NOT real options.**

## Why this matters

Two genuine, official, already-present dev tools (free camera + a menu-based debug/progression tool)
significantly de-risk this project's early investigation phase — this is a stronger starting position
than several other fronts in this portfolio had, where any comparable tool had to be found via
third-party community reverse engineering (e.g. Mad Max's MMConsole) rather than being a flag Remedy
themselves shipped.

## Concrete next step

Enable both `-freecamera -developermenu` together as the default launch configuration for this
project's early live sessions (per one community comment, they can be combined in the same launch
options string). Use `-freecamera` for initial black-box camera/world exploration before any hooking
work, and check the Developer Menu live to confirm or expand its documented scope beyond
episode-select/ammo.

## Sources

- https://steamcommunity.com/sharedfiles/filedetails/?id=1135506903
- https://steamcommunity.com/sharedfiles/filedetails/?id=231208707
- https://steamcommunity.com/sharedfiles/filedetails/?id=231131068
- https://alanwake.fandom.com/wiki/Console_commands
- https://www.alanwake.info/2011/10/alan-wake-pc-commands.html


---

## The measured flag list (2026-09-08) — supersedes the `[reported]` list above

Folded in by `/gr` from `external-research/inbox/`; read by the modding lane straight out of
`AlanWake.exe`, from the parser's own option table sitting immediately beside the format string
`Unknown command line option "%s"` `[measured 2026-09-08]`.

```
shaders   SENSSCALE=/sensscale=   GPUCOUNT=/gpucount=   freecamera   directaiming
nativekeys   rigidcamera   showfps   verbose   developermenu   largeshadowmaps
noblur   forcesurround   forcestereo   cleanaccount   cleancloud   novsync
nosound   window   LOCALE=/locale=
```

**This moves the flag set from `[reported]` to `[measured]`** — it is no longer a community
list, it is the binary's own table — and it adds seven entries nobody had: **`rigidcamera`**,
**`noblur`**, `directaiming`, `nativekeys`, `largeshadowmaps`, `verbose`, `shaders`, plus
`gpucount=` and a bare `window`.

### ⚠️ One correction to the reported list

**`-w <n>` and `-h <n>` are not in the table.** Width and height come from `resolution.xml`.
Anyone repeating "use `-w`/`-h`" — including anyone reading the bullet higher up this page
— will get `Unknown command line option`. This is exactly the kind of error a community list
propagates and a binary read settles.

### ⛔️ Do not run these two

`cleanaccount` and `cleancloud` are in the same table. **The names say they wipe local account
state and Steam Cloud data. Nothing has been run to find out, and nothing should be.** Carry this
warning wherever the list is published — the list is more useful than it is safe to
experiment with blind.

### The two comfort flags were already researched — on 2026-09-01

`rigidcamera` and `directaiming` are **not new leads**: this lane wrote them up a week before the
binary read, in
[`2026-09-01-the-three-unrecorded-switches-and-a-forcestereo-correction.md`](2026-09-01-the-three-unrecorded-switches-and-a-forcestereo-correction.md),
which records that `-rigidcamera` removes the camera smoothing and `-directaiming` removes all
mouse acceleration and implies it — and which already recommends setting both as part of this
project's standard launch line. That recommendation is still unactioned.

### What did not change: the stereo entries

`Stereo Rendering:Override / Enable / Separation / Convergence / Eye Separation` are **confirmed
present in our binary** — in `renderer_sf_Win32.dll`, not `AlanWake.exe` — alongside
`Activate Stereo`, `NvidiaSpecificData` and `g_vStereo_Separation_Convergence`, and that DLL
imports `nvapi.dll`.

**This corroborates the reported material and does NOT reopen the route.** The 2026-09-01 topic
already records **zero direct callers** of `NvAPI_Stereo_SetDriverMode`, which makes the stereo
uniform a *correction* layer applied to a driver-made image rather than a switch we can throw; and
the 2026-09-03 topic records 3D Vision Automatic as discontinued. Recorded here as
**"confirmed in-binary, still retired"** so it is not re-chased as an open `[reported]` lead.
