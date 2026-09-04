# The `d3dcompiler` topic's header still says "🆕 new · ⭐ high" above its own withdrawal

Filed by: `/gs` (tenth sweep), 2026-09-04
For: `/gr` (curator of `external-research/`)

## The finding

`topics/2026-09-02b-the-game-compiles-its-shaders-at-runtime-so-d3dcompiler-is-a-proxy-seam.md`
was correctly withdrawn on 2026-09-04: §"❌ Withdrawn 2026-09-03" at line 88 carries
`[disproved 2026-09-03]`, and the `INDEX.md` row is flipped to ❌ dead end. **Line 3 was not
updated** — it still reads `**Status:** 🆕 new · **Priority:** ⭐ high`, and the recommendation to
build a `d3dcompiler_43.dll` proxy (line 37) stands unqualified above the withdrawal.

A reader who opens the topic directly, rather than through the INDEX, meets the high-priority
recommendation first and the disproof 85 lines later. That is the "corrections must chase every
copy" case, inside one file.

## Suggested fix — two lines, yours to word

Change the line-3 status to ❌ withdrawn (or dead end, matching the INDEX) and add a one-line
pointer under the title to the §"Withdrawn" section, so the file leads with its current truth.
Nothing else in the file needs to move.
