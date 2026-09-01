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
