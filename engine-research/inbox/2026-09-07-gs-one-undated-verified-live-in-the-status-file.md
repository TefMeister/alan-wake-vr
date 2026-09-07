# One bare `[verified-live]` with no date, in `status/alan-wake-vr.md` — the dossier is clean

**Filed by `/gs`, 2026-09-07 (fourteenth sweep). For the modding lane.** Read-only session; nothing
was edited. One-line fix.

## The hit

`claude-memory/status/alan-wake-vr.md:20`, in the "Launch 2 (09-04c dump, into the intro): blind"
bullet — the clause about the engine flushing whole 128-register blocks (`c0+128`, `c128+128`,
~6k/s each in 3D) carries a bare **`[verified-live]`** with no date.

The name is valid; the date is missing, and `CONVENTIONS.md` → "Claim hygiene" specifies
`[verified-live YYYY-MM-DD, n=K]`. Undated, a reader cannot tell whether it was observed before or
after the 09-04 `FreeLibrary` fix — which matters here more than usual, because that fix changed
which device the proxy owns, and therefore what a register-flush observation even refers to.

From the surrounding text the observation belongs to the **09-04c launch**, so
`[verified-live 2026-09-04, n=1 launch]` is the likely form — but that is the author's call, not
mine, and the `n=` should say what was actually run.

## Scope — deliberately narrow

`claude-memory` has no `inbox/`, so this drop is filed here to reach the lane that owns both files.

**`engine-research/ENGINE-DOSSIER.md` has zero bare `[verified-live]` tags** — checked directly
this sweep. The dossier's own `n=1` entries (§ lines 56, 78, 110, 125) are all dated and all carry
an explicit `n=`, including the good `[verified-live, n=1 crash, n=3 clean]` form, which is exactly
the shape the vocabulary is for. So this is a single stray copy in `status/`, not a lane habit —
no wider grep is being asked for.
