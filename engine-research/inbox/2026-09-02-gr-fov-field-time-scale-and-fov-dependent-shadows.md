# §6 has a starting address: FOV is `[camera+0x214]`, read right after an accessor call in `AlanWake.exe`

Filed by: `/gr`, 2026-09-02
Topic: `external-research/topics/2026-09-02-a-public-cheat-table-locates-fov-and-time-scale-and-the-helix-fix-shows-fov-dependent-shadows.md`
Dossier sections: §6 ("Where projection `P` / FOV comes from" — currently empty), §8 (shadows), §10 (harness)

From a public Cheat Engine table (Jim2point0, hosted by FRAMED) and the Helix Mod fix thread (Neovad).
`[reported 2026-09-02]`; module offsets are for the table's (older) build, byte patterns are portable.

## §6 — the FOV read, with the camera object in `eax`

At `AlanWake.exe + 0x3F5C3` on the table's build: `call <accessor>` → `fld dword ptr [eax+0x214]`
(`D9 80 14 02 00 00`) → `fstp dword ptr [esp+0x10]` → `call <consumer>`. Scan the installed exe for
`D9 80 14 02 00 00 D9 5C 24 10 E8`. The accessor returns the camera/view object; `+0x214` is its FOV;
the consumer is the first candidate for the projection build. Note it is in the **exe**, not the
renderer DLL. Suggested dossier line: "Projection is decided game-side: FOV lives at `+0x214` on the
object returned by the accessor at <VA>; the projection consumer is the call at <VA>."

## §10 — a global time-scale

`AlanWake.exe + 0x29D628` (float; `0.0001` freezes, `1` normal), read by `fld dword ptr [abs]`
(`D9 05 ?? ?? ?? ?? DE CB D9 C9`). A frozen world with the render loop running is the ideal state for
reading camera/projection values back repeatedly.

## §8 — design constraint from the 3D Vision fixer

v1.06's shadow shaders are FOV-dependent (Neovad had to set the FOV slider to 17/20 for correct shadows
and torch lights). Whatever supplies the per-eye projection must reach the shadow path too. The main
shadow VS is hash `2B37CDBA`, in which `c0` carries a projection-shaped term (`dp3 r1.x, c0.xyww, r0`).
