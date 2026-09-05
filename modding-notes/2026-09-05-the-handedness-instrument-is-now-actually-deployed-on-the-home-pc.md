# The handedness instrument is now actually deployed on the home PC — and the build script never worked here

`/pd`, home PC, 2026-09-05. **The game was not launched; nothing here was run.**

## What was wrong

The board's starred `[FLAT]` row — *"ONE LAUNCH READS THE HANDEDNESS — the instrument is built and
deployed. `d3d9.dll` 62,464 B"* — was true of the **dev PC**. On the home PC:

- `C:\Steam\steamapps\common\Alan Wake` contained **no `d3d9.dll` at all**.
  `[verified-numerically 2026-09-05]` A launch here would have read the handedness of nothing.
- `proxy-d3d9/build.sh` hard-coded the toolchain as
  `/c/Users/Tefa/AppData/Local/.../llvm-mingw-.../bin`, which does not exist on this machine (user
  `TD3KX`), so the project could not be built here either.

## What was done

`build.sh` now takes the toolchain from `PATH` (`command -v i686-w64-mingw32-clang`) and keeps the
dev-PC WinGet path as a fallback, so it builds on either machine without editing.

Built and deployed: `Alan Wake\d3d9.dll`, hash-verified against the build output. Nothing was
overwritten — there was no file to back up.

## The corroboration worth noting

The home-PC build came out at **exactly 62,464 bytes** — byte-for-byte the size the board records
for the dev-PC build of the same commit. Same for Alice in the same session (702,976 B, also
exact). Two independent machines, different toolchain install paths, identical output sizes.
`[verified-numerically 2026-09-05]`

That is a real, if narrow, result: it says the DLL now sitting in the home install is the same
instrument the `[FLAT]` row describes, rather than something merely similar. It does **not** prove
the bytes are identical — only the sizes were compared, and a size match is strong but not a hash
match.

## What the row now means here

Unchanged, and now actually executable on this machine: reach the main menu, quit, read
`alanwake_vr_proxy_log.txt`. The full outcome table is in the status file and in
`modding-notes/2026-09-04c` §5. Briefly:

| log says | means |
| --- | --- |
| `g_mViewToClip candidate cN` with `m[11]=+1, m[15]=0` | LEFT-handed — `stereo.c` stands as written |
| `m[11]=-1` | RIGHT-handed — every sign in `stereo.c` needs re-deriving |
| `CreateDevice vtable hook installed at slot 16` | the re-enabled hook works |
| game fails to start | suspect the re-enabled CreateDevice hook; there is now **no backup to revert to on this machine**, so simply delete `d3d9.dll` to return to stock |

⚠️ That last row is the one difference from the dev PC. The board's row says "previous kept as
`d3d9.dll.bak-2026-09-04c-pre-vsdump`" — that backup exists on the dev PC only. Here the revert is
to delete the file, which is equivalent because the game shipped without one.
