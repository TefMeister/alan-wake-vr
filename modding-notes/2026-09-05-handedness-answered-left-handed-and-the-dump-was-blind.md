# The handedness is answered — LEFT-handed, `clip.w = +view.z` — after two blind instruments and one crash (2026-09-05, home PC, `/lm`)

Four launches, all driven from outside the game (`dev-archive/tools/awdrive.py`; Tefa authorised
launching for the session and was away). The board's starred `[FLAT]` row said one launch would read
the handedness. It took four, because the instrument built on 2026-09-04c could not see the
projection at all, and the fix had to be found live. Evidence:
`dev-archive/recon/2026-09-05-handedness-home-pc/` (three logs; the 10 MB one gzipped).

## The verdict

`g_mViewToClip` is **LEFT-handed: the w-from-z entry is +1, so `clip.w = +view.z`**, and it is
stored exactly as dossier §6 settled statically — registers are the ROWS of a column-vector matrix
(`clip = P·view`), so the +1 sits at storage index 14 (register 3, component z) and the depth offset
`-zn·zf/(zf−zn)` at index 11 (register 2, component w). `stereo.c` stands as written.
`[verified-live 2026-09-05, n=1 launch, 10 five-second windows per register, in-engine intro scene]`

Three true projections were seen, every one of them left-handed:

| register | xs | ys | ys/xs | P[2][2] | P[2][3] | near, far | what it is |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **c192** | 1.2088 | 2.1490 | **1.778 (16:9)** | 1.0002 | −0.200 | 0.2 … 1000 | **the main camera**, in the skinned shaders (the census said c192 for exactly those) |
| c7 | 1.2088 | 2.1490 | 1.778 | 1.1196 | −1196.3 | 1068 … 10000 | the same lens with a far depth slice — distant scenery / sky pass |
| c0 | 1.0000 | 1.0000 | 1.000 | 1.0256 | −0.051 | 0.05 … 2 | a square 90° projection with a 2-unit range — a point-light shadow or cubemap face |

`xs = 1.2088` gives a horizontal FOV of 79.2°, `ys = 2.149` a vertical one of 50.0°; the ratio is
the 1920×1080 aspect to three decimals, which is what makes the c192/c7 pair unmistakable. Everything
else the scan flagged (c1, c2, c5, c8, … in steps of 3 through the palette, c40, c81, c87) is a
3×4 bone or world matrix whose storage happens to carry a 1 at index 14 — look-alikes, listed in the
log and discarded by shape.

**Caveat on c0:** the census puts the main camera at c0 in 2,238 (non-skinned) shaders, and the
scan only saw the shadow projection there. The scan logs one sighting per register per five
seconds, and the shadow pass is drawn first in the frame, so the camera's c0 upload is masked by
the rate limit, not absent. c192's numbers make the same statement for the same lens; a follow-up
could log the first sighting *per distinct xs/ys* rather than per register.

## Why it took four launches

**Launch 1 crashed at 7 s — the layered-hook hazard the source itself predicted.** At the first
unload, slot 16 of the `IDirect3D9` vtable held someone else's pointer (`747C0710`, most likely
the Steam overlay's `GameOverlayRenderer` hook, layered on top of ours during the 700 ms the first
block lived); our unhook correctly stood down; on the second load we hooked again *with the
overlay's hook as "real"*, and the two chained into each other — `IDirect3D9::CreateDevice called`
1,669 times in one millisecond, then the process died (an empty crash dump, Steam's log shows
`App Running` for 7 s). Launches 2–4 had no layered hook (the first block lived only 16 ms) and
the chain ran cleanly. **So the race is real and timing-dependent** `[verified-live 2026-09-05,
n=1 crash, n=3 clean]`. Mitigation candidates: refuse to install the hook when slot 16 is already
foreign; or never chain into a foreign pointer that is not the runtime's own. Recorded on the
board as a `[PD]` row.

**Launch 2 ran the 2026-09-04c instrument to the in-engine intro, and it saw nothing.** `c0`
climbed at ~500,000 uploads/s showing one flat 2D matrix, `c192` showed palette data, `c4` and
`c7` were never counted. Two defects, found by reading the code against the numbers:

1. The candidate loop `break`s on the first register an upload spans, and this engine uploads
   **whole 128-register blocks** (`c0+128` and `c128+128`, ~6,000 of each per second in a 3D
   scene, plus `c0+4`/`c0+5` for the video quad and UI) — so every block starting at 0 was
   counted against c0 alone, and the matrix printed was whatever happened to sit at c0..c3.
2. The old reading table tested `m[11] = ±1` — that is the row-vector D3D convention, which
   §6 of the dossier had *already* ruled out statically on 2026-09-03 ("registers are rows,
   translation in `.w`"). In the dossier's own convention the ±1 lives at index 14. The
   instrument contradicted the dossier it was built to test, and would have said "neither
   convention" forever.

**Launch 3 (register-agnostic instrument, index-11 signature only)** proved the histogram and
found no perspective anywhere in 33,000 full-block flushes — which was itself the evidence for
the index-14 layout. **Launch 4 (both signatures)**: 142 sightings in the first two minutes of the
in-engine intro, verdict above.

The instrument now in `staging/alan-wake-vr/proxy-d3d9/src/proxy.c` (`28a45fe`): a per-5-second
`(start+count : n)` histogram of every upload range, and a scan of every 4-register window of every
upload against both perspective signatures, logging the first sighting per register and then at
most one per 5 s. The four census candidates are still counted, all of them, without the `break`.
`VS_DUMP_EVERY` raised 4000 → 400,000. Deployed here as `d3d9.dll` (66,048 B); the 2026-09-04c
build kept as `d3d9.dll.bak-2026-09-05-pre-agnostic-dump`.

## Also learned, for the profile

- **Keyboard: scancode `SendInput` does NOT reach this game on this machine; virtual-key events
  do.** Space by scancode (twice, once held 0.25 s) left the title screen untouched; `wVk=VK_SPACE`
  passed it at once. The dev PC record says scancodes worked on 2026-09-04 — `n=1` each way, so
  the profile now says "try VK first". `[verified-live 2026-09-05]`
- **Menus:** title (Space) → main menu `Continue Game / New Game / Episodes / Options / Extras /
  Quit`; `Continue Game` opens a `Load Game` slot list (`1: Steam Cloud Alan Wake` after one
  autosave) — one more Enter than the profile assumed; `New Game` → `Difficulty Easy / Normal /
  Nightmare`. **Pause menu (Esc in gameplay):** `Resume Game / Restart Checkpoint / Manuscript /
  Options / Statistics / Quit To Menu` (Down ×5) → `Are you sure you want to Quit?` → Enter → main
  menu; then Down ×5 → Quit → Enter → confirm Enter → process exits within 2 s, hooks unhooked in
  order. **A full in-game → desktop quit route is now proven** (twice). Esc during a video opens the
  pause menu (does not skip); Esc again resumes.
- **An Enter sent within ~5 s of the title→menu transition is eaten** (twice). Capture-verify the
  menu before pressing.
- **Where the 3D actually is:** the title's foggy forest and the lighthouse main menu are VIDEO
  (only `c0+4`/`c0+5` uploads); the studio logos before the title and the in-engine intro after the
  fly-over video are 3D (full-block flushes). A handedness read needs the intro, not the menu.
- First launch on a fresh install: Steam runs a 7-second first-run setup that shows in the content
  log as `App Running` and exits; the game itself starts on the second launch attempt. (Launch 1's
  crash was separate — the log proves the recursion.)
- The small (~15.7 KB) crash dump at every clean exit is now n=3 (15,718 / 15,666 B) — a benign
  shutdown-path exception, not ours: it appears with the hooks already removed.
- Windowed mode from a pre-created `Documents\Remedy\AlanWake\resolution.xml` (`fullscreen=0`)
  works on a never-run install; no minimise hazard seen in four launches.

## Not established

- Whether the c0 camera projection (non-skinned shaders) is identical to c192's — masked by the
  rate limit, see above.
- The engine unit (near 0.2 reads as metres; the c7 pass's 1068 near plane is odd in metres).
- What the layered hook at slot 16 in launch 1 actually was (Steam overlay is the likely owner;
  not proven).

## Automation on Alan Wake, scored (§5a)

menu → gameplay **PROVEN** (title → main menu → New Game → difficulty → intro; Continue → slot →
load; n=4 launches) · commands **N/A** (no console) · character movement **NOT exercised** (in-engine
intro only; WASD by VK untested) · camera **NOT proven** · self-close **PROVEN through the menus**
(pause → Quit To Menu → confirm → Quit → confirm; twice; hooks unwound; no `WM_CLOSE`).
