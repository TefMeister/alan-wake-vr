# DRM history: originally Games for Windows Live; vorpX works but only confirmed in the weaker Cinema mode

**Status:** 🆕 new · **Priority:** high — seeds `ENGINE-DOSSIER.md` §4 and §12 honestly, including a
real gap compared to this portfolio's stronger fronts.

## DRM history

The original 2012 PC release of Alan Wake was distributed through **Games for Windows Live (GFWL)**
— Microsoft's now-defunct online-activation/achievement platform, which required product-key
activation. GFWL was shut down by Microsoft years ago industry-wide, and the game continues to be
sold and run on Steam today, so the Steam build must have been migrated off GFWL at some point — but
this research pass **could not find a specific, dated confirmation** of exactly when/how that
migration happened (unlike the clean, dated "Jan 2022 patch" stories found for Prince of Persia 2008
and Alice: Madness Returns elsewhere in this portfolio). What is confirmed: the game had a **separate,
unrelated delisting** from May 2017–October 2018 over expired music licensing (not DRM/anti-piracy),
and a **September 2024 patch removed a licensed song** ("Space Oddity," replaced with an original
track by Petri Alanko) — again a licensing matter, not DRM. **Static recon should specifically check for GFWL-era
artifacts** (config keys, `xliveinit`/`xlive.dll`-style references, activation dialogs) as a first
pass, rather than assuming a clean result the way the dated Alice/PoP2008 precedent would suggest —
this game's DRM history is real but less precisely documented than those two.

## vorpX status: works, but the confirmed mode is weaker than this portfolio's best fronts

vorpX has active forum discussion for the original Alan Wake, describing it as running via
**Cinema mode** — vorpX's lowest-fidelity mode (a flat virtual screen in a virtual room, no
stereoscopic depth reconstruction and no head-tracked world-relative camera). This research pass did
not find confirmation of Geometry 3D or full head-tracked/FullVR mode working for the *original*
2010/2012 release specifically (separate vorpX threads exist for Alan Wake Remastered and Alan Wake
2, which are different games/builds and shouldn't be conflated with this project's target). **This is
a meaningfully weaker third-party feasibility signal than Mad Max (Geometry 3D + head tracking) or
Alice: Madness Returns (Geometry 3D + motion-controller emulation)** — worth recording honestly rather
than overstating. The companion native-3D-Vision topic (this same sweep) is currently this project's
strongest actual evidence that per-eye camera/projection work is tractable here, not the vorpX result.

## Concrete next step

During static recon, check specifically for GFWL/xlive artifacts rather than assuming DRM-free by
default. Treat vorpX's Cinema-mode-only precedent as a modest, not strong, feasibility signal, and
lean on the native 3D Vision findings (companion topic) as the more meaningful evidence for §6/§12.

## Sources

- https://steamcommunity.com/app/108710/discussions/0/2741975115066499810/
- https://www.kitguru.net/tech-news/mustafa-mahmoud/alan-wake-is-getting-an-update-to-remove-licensed-song/
- https://www.vorpx.com/forums/search/Alan%20Wake/
