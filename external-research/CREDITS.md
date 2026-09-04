# Credits & Attribution

This project is a reverse-engineering and modding effort built on the public
research, tools, and documentation of many people who came before us. None of
this would be possible without their work. We list every source we've drawn
on below — including work that helped only as inspiration — by name or
handle, as accurately as we could verify it.

## The game itself

This mod modifies, at runtime, the original **Alan Wake** (2010) by
**Remedy Entertainment**, published by Microsoft Game Studios / Remedy. The
game, its engine, and all of its assets are theirs, and the game is the
entire reason this project exists. **No game files, code, or assets are
distributed in any of this project's repositories** — only code, notes, and
tools we wrote ourselves, plus third-party components whose licenses permit
redistribution (noted below).

## Prior art, tools, and research this repo draws on

| Source / Work | Creator(s) | Link |
|---|---|---|
| Steam Community guide: free-camera & screenshots | Steam guide author | https://steamcommunity.com/sharedfiles/filedetails/?id=1135506903 |
| Steam Community guide: Developer Menu | Steam guide authors | https://steamcommunity.com/sharedfiles/filedetails/?id=231208707 |
| Alan Wake Wiki: Console commands | Fandom community | https://alanwake.fandom.com/wiki/Console_commands |
| The Sudden Stop: Alan Wake PC Commands | alanwake.info | https://www.alanwake.info/2011/10/alan-wake-pc-commands.html |
| NVIDIA GeForce forums: Alan Wake 3D Vision settings | NVIDIA forum community | https://www.nvidia.com/en-us/geforce/forums/discover/136359/alan-wake-what-are-the-3d-recommended-settings-/ |
| Helix Mod: Alan Wake | Helix Mod community | https://helixmod.blogspot.com/2017/05/alan-wake.html |
| Nvidia 3D Vision article (discontinuation facts) | Wikipedia contributors | https://en.wikipedia.org/wiki/Nvidia_3D_Vision |
| 3D Fix Manager (driver-support history, DX9 vs DX11, Discover mode) | Pauldusler | https://helixmod.blogspot.com/2017/05/3d-fix-manager.html |
| HelixVision driver-compatibility notes | Bo3b | https://steamcommunity.com/app/1127310/discussions/0/1635291505036080879/ |
| vorpX Alan Wake compatibility reports | vorpX forum community | https://www.vorpx.com/forums/search/Alan%20Wake/ |
| KitGuru (Space Oddity removal reporting) | KitGuru | https://www.kitguru.net/tech-news/mustafa-mahmoud/alan-wake-is-getting-an-update-to-remove-licensed-song/ |
| NVIDIA 3D Vision Automatic developer documentation (the clip-space footer, draw-call duplication, and the `StereoParmsTexture` / `nvstereo.h` correction pattern) | NVIDIA Corporation | https://archive.docs.nvidia.com/gameworks/content/technologies/desktop/nv3dva_background.htm · https://archive.docs.nvidia.com/gameworks/content/technologies/desktop/nv3dva_stereoscopic_issues.htm |
| NVAPI public headers and reference documentation (`NvAPI_Stereo_SetDriverMode`, Direct vs Automatic driver modes) | NVIDIA Corporation | https://github.com/NVIDIA/nvapi/blob/main/nvapi_lite_stereo.h · https://docs.nvidia.com/nvapi/nvapi__lite__stereo_8h.html |
| Scaleform / Autodesk documentation on 3D Vision automatic vs API-driven modes and the Ctrl+F3/F4 hotkeys | Autodesk (Scaleform documentation) | https://help.autodesk.com/cloudhelp/ENU/Scaleform-Help/scaleform_help/3di/stereoscopic/nvidia.html |
| GOG community command-line reference for Alan Wake (the `-forcestereo` = 2-channel speaker-mode correction) | GOG.com forum contributors | https://www.gog.com/forum/alan_wake/info_command_line_options_for_alan_wake_1 |
| *The Sudden Stop* Alan Wake PC commands reference (`-directaiming` 1:1 mouse control; sound-category placement of `-forcestereo`) | The Sudden Stop (alanwake.info) | https://www.alanwake.info/2011/10/alan-wake-pc-commands.html |
| Steam community discussion documenting `-rigidcamera` removing camera smoothing | Steam Community contributors | https://steamcommunity.com/app/108710/discussions/0/828939978253890023/ |
| NVAPI published function-ID dispatch table `nvapi_interface.h` (the id→name mapping that `nvapi_QueryInterface` is driven by; used to confirm `NvAPI_Stereo_SetDriverMode` = `0x5E8F0BEC`) | NVIDIA Corporation | https://github.com/NVIDIA/nvapi/blob/main/nvapi_interface.h |
| `NVIDIA_NvAPI` — `info/NvAPI_IDs.txt`, an independently compiled NVAPI function-ID list used as a second source | jNizM | https://github.com/jNizM/NVIDIA_NvAPI/blob/master/info/NvAPI_IDs.txt |
| Alan Wake Cheat Engine table (time-scale + FOV, the FOV read site) | Jim2point0, hosted by the FRAMED screenshot community | https://framedsc.com/CheatTables/AlanWake.CT |
| Alan Wake game guide (free camera, downgrade depot, table) | FRAMED screenshot community | https://framedsc.com/GameGuides/Alan_Wake.htm |
| Alan Wake 3D Vision fix (Helix Mod; FOV-dependent shadows, shader `2B37CDBA`) | Neovad, via the Helix Mod blog | https://helixmod.blogspot.com/2014/08/alan-wake.html |
| OpenAWE — open-source reimplementation of the Alan Wake / Northlight engine (GPL-3.0; studied for engine concepts and data formats, nothing copied) | the OpenAWE Project contributors | https://github.com/OpenAWE-Project/OpenAWE |
| AWTools — `unrmdp` / `unbin` readers for Alan Wake's archive formats | Nostritius | https://github.com/Nostritius/AWTools |
| neat — Northlight archive unpacker | TomEvin | https://github.com/TomEvin/neat |
| The "could not process hlsl shader" launch-failure thread (evidence of runtime shader compilation) | Steam Community discussion participants | https://steamcommunity.com/app/108710/discussions/0/864977025688898181/ |
| ReShade commit `74347b91d` "Fix hooking in Alan Wake" — freeing the system-DLL reference on unload, the primary source for the probe-then-reload bypass (read online, nothing copied) | crosire | https://github.com/crosire/reshade/commit/74347b91d |
| `LoadLibraryA` reference — the already-loaded-module base-name rule and the per-process reference count | Microsoft | https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibrarya |
| Alan Wake care package (Helix `d3d9.dll` + ReShade via ASI loader — practical proof a game-folder `d3d9.dll` hosts the real device) | the package author, via Nexus Mods | https://www.nexusmods.com/alanwake/mods/9 |

Development on this project is AI-assisted: much of the research, code, and
documentation was produced with **Claude (Anthropic)** (https://claude.com)
working alongside the project owner.

## Missing from this list?

If you — or someone whose work you know — contributed to, influenced, or
even just inspired anything used in this project and you aren't credited
here, please **open a GitHub issue on this repo** and we'll correct it as
soon as possible. We would much rather over-credit than leave anyone out.

## Respecting creators

This project exists because other people generously shared their
reverse-engineering research, tools, and modding know-how in public — we've
tried to credit every one of them by name or handle above, as accurately as
we could verify. If you are the creator or rightful owner of anything
credited or used here and you'd rather your work not be referenced in this
repo, or you want specific content removed or no longer used by the mod,
please tell us: **open a GitHub issue on this repo**. We'll act on that
request promptly — no argument, no delay — and we'll find another way to get
the job done that doesn't rely on your material. This is your work; we're
just grateful to have learned from it.
