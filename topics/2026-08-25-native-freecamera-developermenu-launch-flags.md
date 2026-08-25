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
