# SteamVR now has a 32-bit OpenXR runtime, and `-noblur` is in Remedy's own patch notes

**Status:** 🆕 new · **Priority:** medium — both help the first headset look.

## 1. A 32-bit OpenXR runtime from SteamVR

- **SteamVR 2.17 left beta on 2026-09-10** with *"Added support for 32-bit OpenXR applications."*
  Accepting SteamVR's prompt to become the default OpenXR runtime registers it under the 32-bit
  `WOW6432Node` key as well `[reported 2026-10-07]`.
- This explains our own dev-PC measurement (dossier, `[measured 2026-10-06]`): `steamxr_win32.json` is
  on disk, but the 32-bit key is empty, because the prompt was never accepted (or SteamVR was set as
  default before 2.17).
- **For this project:** Alan Wake is 32-bit and the OpenXR path uses a 32-bit loader. On the home PC,
  with SteamVR 2.17+, point the ini's runtime at `steamxr_win32.json`, or accept the prompt. Virtual
  Desktop's VDXR is the fallback (XIII reached the headset through it). ⚠️ Untested on our machines.

## 2. `-noblur` is a real, supported switch

- Remedy's **v1.02** PC patch notes contain: *"Fix that blur occasionally got re-enabled even if -noblur
  command line option was specified"* `[reported]`. A 2012 user report adds it did not change frame rate.
- The 2026-09-08 pass recorded `-noblur` as *"untested and undocumented publicly"*. It is now documented.
- **For this project:** motion blur during head turns is a comfort problem in a headset. `-noblur`
  belongs on the standard launch line, next to `-directaiming` (2026-09-01 topic). Still not run by us.

## Sources

- vr.org, SteamVR 2.17 and 32-bit OpenXR (2026-09-12) — <https://vr.org/articles/steamvr-2-17-stable-32-bit-openxr-runtime-2026>
- GamingOnLinux, SteamVR 2.17 (2026-09) — <https://www.gamingonlinux.com/2026/09/steamvr-2-17-arrives-ready-to-go-for-the-steam-frame/>
- DSOGaming, Alan Wake PC patch 1.02 notes — <https://www.dsogaming.com/?p=18888>
