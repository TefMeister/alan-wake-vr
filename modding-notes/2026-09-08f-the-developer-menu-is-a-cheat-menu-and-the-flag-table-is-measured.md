# 2026-09-08f — the developer menu is a cheat menu, and the flag list is now measured from the binary

*Session: `/lm alan-wake-vr`, dev PC, one launch, fully autonomous. The static half needed no game
at all and is what produced the durable finding.*

**The `-developermenu` row is CLOSED, and it closed at a third outcome the row did not list: the
menu appears, works, and contains nothing this project can use.**

---

## 1. Static first — and it corrected the row before the game was even launched

`AlanWake.exe` carries the parser's own option table immediately beside the format string
`Unknown command line option "%s"` `[measured 2026-09-08]`:

```
shaders   SENSSCALE=/sensscale=   GPUCOUNT=/gpucount=   freecamera   directaiming
nativekeys   rigidcamera   showfps   verbose   developermenu   largeshadowmaps
noblur   forcesurround   forcestereo   cleanaccount   cleancloud   novsync
nosound   window   LOCALE=/locale=
```

That is the whole list, from the shipped binary rather than a wiki, and it **supersedes the
`[reported]` list** in `external-research`. Seven entries were unrecorded: **`rigidcamera`**,
**`noblur`**, `directaiming`, `nativekeys`, `largeshadowmaps`, `verbose`, `shaders`.
⚠️ `-w <n>` / `-h <n>` are **not** in the table — that reported advice is wrong; width and height come
from `resolution.xml`.

⛔️ **`cleanaccount` and `cleancloud` are in the same table.** Nothing has been run to find out what
they do and nothing should be: the names say they wipe local account state and Steam Cloud, and this
project's save is the test fixture.

### The stereo entries are real, are in the renderer DLL, and are still retired

`Stereo Rendering:Override / Enable / Separation / Convergence / Eye Separation` are **absent from
`AlanWake.exe`** and present in **`renderer_sf_Win32.dll`** (`Stereo Rendering` ×5, `Convergence`
×2, `Eye Separation` ×1) `[measured 2026-09-08]`, in one cluster with `Get SLI State`,
`Set Stereo Mode`, `Activate Stereo`, `Deactivate Stereo`, `g_sStereoBuffer`, `Stereo Texture`,
`NvidiaSpecificData` and **`g_vStereo_Separation_Convergence`**. That DLL imports `nvapi.dll` and
`nvpowerapi.dll`.

⚠️ **This corroborates `/gr`'s report in our own binary and does NOT reopen the route.** Our own
`external-research` already records (2026-09-01) **zero direct callers of
`NvAPI_Stereo_SetDriverMode`**, making the stereo uniform *"a correction layer rather than a
self-driven two-eye path"*, and (2026-09-03) that 3D Vision Automatic is discontinued. So
`g_vStereo_Separation_Convergence` corrects a **driver-made** stereo image; it is not a two-eye
renderer we can drive.

**I had written the board row myself an hour earlier saying the opposite** — *"they exist and respond
⇒ the game ships its own stereo path and this project changes shape entirely"*. That was wrong, and
reading our own record before launching is what caught it. Corrected in dossier §6g.

## 2. The launch: the menu exists and is a cheat menu

Launched `AlanWake.exe -developermenu -rigidcamera -noblur` directly. No
`Unknown command line option`, game started normally.

**`[Developer Menu]` appears in the main menu**, between `Extras` and `Quit`
`[verified-live 2026-09-08, n=1 launch]`. Its entire contents:

| entry | state |
| --- | --- |
| `Get Lots of Guns` | greyed out at the main menu (in-game only) |
| `Get Flashlight and Batteries` | greyed out at the main menu (in-game only) |
| `Unlock all Episodes (Easy and Normal)` | selectable |
| `Unlock Nightmare difficulty` | selectable |

**No stereo entries. No camera, FOV, freeze-render, wireframe or debug-draw toggles. No cvar
console.** It is a QA unlock menu.

**Nothing was selected.** All four alter save/profile state, and the save is the test fixture; the
menu was opened, photographed and backed out of with `Esc`.

## 3. ⚠️ A hazard the flag introduces: it shifts every menu index by one

`[Developer Menu]` is inserted into **both** the main menu (between `Extras` and `Quit`) **and the
pause menu** (between `Statistics` and `Quit To Menu`). So with the flag on:

| route | without the flag | with `-developermenu` |
| --- | --- | --- |
| main menu → `Quit` | Down ×5 | **Down ×6** |
| pause menu → `Quit To Menu` | Down ×5 | **Down ×6** |

A session that blind-counted the recorded ×5 would land on `[Developer Menu]` instead — harmless
here, but the same off-by-one on a differently-ordered menu is how a save gets overwritten. The
capture-and-verify rule caught it on the first step, as intended.

## 4. `rigidcamera` — half an experiment, honestly

With `-rigidcamera` armed, held `W` and captured 14 frames while walking. Per-frame **vertical**
camera shift, measured by cross-correlation on the far field (upper band, dominated by camera motion
rather than the road rushing past):

```
0 0 0 0 0 0 0 0 0 0 0 0 0   -> mean |dy| = 0.00 px, max 0 px
```

Two checks so this null means something:

- **The frames really were changing** — consecutive frame-to-frame mean |luma delta| ran 1.97–4.47,
  so the game was rendering and Alan was walking, not a frozen capture.
- **The estimator can detect a shift** — injecting known offsets of ±1, ±3, ±8 px into a real frame
  recovered each magnitude exactly. A null from a blind estimator would be worthless; this one is
  not blind.

⚠️ **NOT established: that `-rigidcamera` did anything.** Alan Wake's third-person camera may have no
vertical bob to begin with. This is the treatment half of an A/B with no control. **The control is
one launch with no flags at the same save point, captured the same way** — and the numbers above are
directly comparable to it.

`-noblur` was armed in the same run and **not tested at all**, for the same reason: motion blur needs
a no-flag control to attribute.

## 5. Automation

| capability | status |
| --- | --- |
| 1. menu → gameplay | ✅ proven again, including the new 7-row menu |
| 2. console / exec commands | **N/A** — the dev menu is not a console; the ini is still read at load only |
| 3. character + camera | ✅ character movement driven for the walk capture |
| 4. self-close | ✅ graceful through the game's own menu, no `taskkill` |

## 6. What to run next time

**One launch with NO flags**, same save point, same walk capture — that is the control that turns
§4 into a result about `rigidcamera`, and it can carry a `noblur` observation at the same time.
Cheap, and it is the only outstanding thing either flag needs.

Evidence: `dev-archive/recon/2026-09-08f-the-developer-menu-is-a-cheat-menu-and-the-flag-table-is-measured/`.
