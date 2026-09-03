# 3D Vision on a current driver is a discontinued feature — pointer to the Alice write-up

**Date:** 2026-09-03 · **Status:** 🆕 new · **Priority:** low · **Bears on:** dossier §6/§9 (the
game's native 3D Vision Automatic support and its live Ctrl+F3/Ctrl+F4 separation hotkeys).

The full topic lives in the sibling project, because it answered a question that project's modding
side asked directly:
`alice-madness-returns-vr/external-research/topics/2026-09-03b-3d-vision-automatic-on-a-current-driver-what-it-takes-and-why-it-is-not-a-vr-route.md`.
Alan Wake is in exactly the same position — a DX9 title in 3D Vision **Automatic** (confirmed
2026-09-01 by the zero-callers check on `SetDriverMode`), whose stereo is made in the driver.

**What transfers, in one paragraph.** NVIDIA ended 3D Vision with driver **425.31** (announced
2019-04-11) `[reported]`. DX11 stereo lingered to 452.06 via workarounds and was removed in October
2020; **DX9 games are *reported* to remain compatible on current drivers** (one source, unconfirmed).
The driver-made stereo also needs something to show it on — a 120 Hz 3D Vision display and emitter,
or anaglyph glasses in Discover mode. So on this machine the native stereo path, the Ctrl+F3/F4
hotkeys and the "Activate Stereo" menu item **will not produce a stereo picture** without a driver
downgrade or a driver-modding tool, unless the DX9 claim holds.

**Why it matters here, and why it is small.** The dossier already retired the native-stereo shortcut
(the driver owns both eyes; `renderer_sf_Win32.dll` only corrects effects using driver-published
values), so nothing on the critical path changes. Two practical consequences only: (1) any future
attempt to *observe* Remedy's own stereo as a reference picture needs the conditions above first —
do not spend a flat run discovering that; (2) if the DX9 claim is true, Discover-mode glasses are the
cheapest way to see it, and the 2026-08-25 topic's Ctrl+F3/F4 hotkeys would be live.

⚠️ Not a VR route. 3D Vision drives a display, not a headset.

## Sources

Listed in the Alice topic; the platform half was also filed to the cross-engine library's inbox.
