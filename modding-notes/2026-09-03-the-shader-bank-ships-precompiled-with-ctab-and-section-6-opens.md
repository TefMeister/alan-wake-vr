# The shader bank ships pre-compiled with CTAB intact — §6 is answered off disk, with no launch

**Session:** `/pd`, dev PC, 2026-09-03. **The game was not launched, and nothing here has been
run.** Everything below is read off files already on this disk.

## Headline

`shaders\build\pc\*.obj` — 62 files, ~16 MB — are **`RFX ` containers holding pre-compiled D3D9
shader bytecode with the `CTAB` constant table intact**. That is **9,971 constant tables in 691
distinct layouts**, every one naming its constants and giving the register they land on.
`[inferred-static 2026-09-03, n=9971 tables]`

The engine's transform chain is **view-centric**, which is the best possible shape for a VR
conversion:

| constant | stage | register | shaders | what it is |
| --- | --- | --- | --- | --- |
| `g_mViewToClip` | `vs_3_0` | `c0 x4` / `c192 x4` / `c4` / `c7` | 4,467 | **the projection matrix, standalone** |
| `g_mLocalToView` | `vs_3_0` | `c4 x3` / `c196 x3` / `c7` / `c199` | 4,553 | object → view (4x3) |
| `g_mViewToWorld` | both | `ps c7`, `vs c4`/`c196` | 2,788 | view → world |

**Why this matters more than the raw numbers.** Every other project in this portfolio has had to
fight a *fused* matrix — Mad Max's `WorldViewProjMatrix`, Enslaved's `c0` ViewProjection. Alan Wake
hands over **projection separately from view**. So the two halves of a stereo camera are two
independent, single-constant writes:

- **eye separation** → a translation in view space, i.e. `g_mLocalToView`
- **asymmetric per-eye frustum** → `g_mViewToClip` alone, with no world transform to decompose

Nothing needs to be un-fused, and no matrix has to be inverted to get at the projection.

## The register is NOT fixed — and the reason is provable

`g_mViewToClip` lands on four different registers across the corpus:

```
c0    x4 : 2238 shaders
c192  x4 : 2084 shaders
c4    x4 :  128 shaders
c7    x4 :   17 shaders
```

The `c0` / `c192` split is **the skinning palette**. `GPU_skinning_matrices` is `vs_3_0 c0 x192`
in all 1,958 shaders that carry it — it occupies `c0..c191` — so a skinned shader has to push the
camera block to `c192`. Tested per-shader rather than by matching totals:

```
skinning=False   g_mViewToClip c0    : 2238
skinning=True    g_mViewToClip c192  : 1954     <- no exceptions
skinning=False   g_mViewToClip c192  :  130
skinning=False   g_mViewToClip c4    :  128
skinning=False   g_mViewToClip c7    :   17
```

**Skinning implies `c192` with zero counter-examples (n=1,954).** The converse does *not* hold:
130 unskinned shaders also use `c192`. So "skinned" predicts the register, but the register does
not predict "skinned" — stated separately because only the first direction is load-bearing.

**Consequence for the proxy design:** a proxy must **not** blindly write `c0`. The CTAB travels
*inside the bytecode*, so the clean answer is to parse it at `CreateVertexShader` time and build a
shader-to-register map at runtime, then write the right register per draw. This needs no launch to
design and no guesswork at runtime.

## Coverage — what would and would not receive an eye offset

- **5,103 vertex shaders**; 4,982 (**97.6%**) carry some `*ToClip` matrix.
- The **121** that carry none are spread over **22 files, every one of them a screen-space,
  fullscreen or effect pass** — Godray (17), SSAO (16), BloomX86 (12), DeferredLight (11),
  VolumetricLight (11), ShadowBuffer (10), Velocity (8), Blur (6), BilateralFilter (5),
  ConvertToLinearDepth (4), VectorBlur (4), ShadeEffect (3), and ten more with one or two each
  (BioTypeSampler, DarkPresence, GenerateMipmaps, LightBoost, AfterImage, AutoExposure, Backdrop,
  DarkLight, Displace, Flare). Complete list in the recon folder. Those operate in screen space and
  **should not** be offset — correct behaviour, not a coverage gap.

Three things *would* be missed by a naive "offset `g_mViewToClip` only" implementation, and each is
a known stereo failure mode elsewhere in this portfolio:

1. **Alternate fused paths exist.** `g_mWorldToClip` (264), `g_mLocalToClip` (251) and
   `g_mObjectToWorld` + `g_mWorldToClip` pairs bypass view space entirely. These need a full
   per-eye VP, not a projection tweak.
2. **Deferred reconstruction.** `g_mClipToView` (90) and `g_mViewToWorld` in **pixel** shaders
   (`ps c7`, 768 + 472) rebuild view/world position from depth. If those stay mono while geometry
   goes stereo, deferred lighting is wrong in one eye — the classic deferred stereo trap.
3. **Motion blur.** `g_mCurrentLocalToClip` / `g_mPreviousLocalToClip` (8 each, `Velocity.obj`).
   **This is exactly the trap enslaved-vr hit on 2026-09-02** — motion blur reprojecting through an
   un-offset matrix. Alan Wake ships `-noblur`; use it while judging any stereo run.

The complete transform vocabulary is 33 distinct constant names; the full list is in the recon
folder rather than repeated here.

## §6 game side: the camera object is a static global, and this exe has no ASLR

`/gr`'s 2026-09-02 drop gave a byte pattern for the FOV read, taken from an older build. **It ports
to our build and matches exactly once** in the whole exe:

```
0x0043F521  fstp [esp+0x1c]
0x0043F525  call 0x004434D0
0x0043F52A  fstp [esp+0x18]
0x0043F52E  call 0x005B5800        <- the accessor
0x0043F533  fld  dword [eax+0x214] <- FOV
0x0043F539  fstp [esp+0x10]
...
0x0043F551  fmul qword [0x633140]  ; * 0.4
0x0043F557  fadd qword [0x633930]  ; + 0.8
```

The accessor at `0x005B5800` is two instructions:

```
mov eax, dword ptr [0x0076C5D8]
ret
```

So **the camera object lives behind one static global pointer, `[0x0076C5D8]`, and FOV is
`[[0x0076C5D8] + 0x214]`.** `[inferred-static 2026-09-03]`

Corroboration, because `n=1` is not verification:

- **151 direct callers** of that getter across `.text` — this is *the* camera, not a camera.
- Seven references to the global itself: the getter, a cluster of writers at `0x005B7AA6` to
  `0x005B7EB4`, and a `mov dword [0x0076C5D8], 0` teardown — the shape of a managed object pointer.

**`AlanWake.exe` has `DllCharacteristics = 0x8000`: no `DYNAMIC_BASE`, and no `.reloc` section at
all.** The image is fixed at `0x400000`, so **every static address in this project is permanent** —
there is no ASLR rebase check to do, unlike doom-2016-vr's ringcam. `[inferred-static 2026-09-03]`

The `fmul 0.4` / `fadd 0.8` pair immediately after the FOV read is a linear remap, not a
degrees-to-radians conversion (that constant would be 0.0174533). **I have not established that
this call site builds the projection matrix** — `/gr` offered the consumer as a candidate and it
remains one. What is established is where FOV lives and how to reach it.

### Camera struct, partially mapped — weaker, tagged accordingly

Reads taken directly off `eax` at the getter's call sites fall into two bands: `+0x138` to `+0x164`
and `+0x200` to `+0x214`. Every observed offset in the first band (`0x138, 0x140, 0x148, 0x14C,
0x150, 0x154, 0x15C, 0x164`) sits on a 4-byte grid inside a 48-byte span, **which is consistent
with a 4x3 / 3x4 transform at `+0x138`** — but consistency is all it is. `[hypothesis 2026-09-03]`
`+0x210` is written with an immediate at four sites, adjacent to FOV.

**The diagnostic that would show this is wrong** rather than merely unconfirmed: read the 12 floats
at `+0x138` live and check row orthonormality. If they are not three orthonormal 3-vectors plus a
translation, it is not a camera basis and the band is something else.

## ⚠️ The deployed proxy's "live-verified" status is not supported by the evidence on disk

`d3d9.dll` (56.5 KB, 2026-08-25) is deployed in the game folder. Read of its strings: it contains
**no** hook code — it is the plain forwarding build, the one recorded as working.
`[inferred-static 2026-09-03]`

But `alanwake_vr_proxy_log.txt` — the only run evidence on this disk — records **two launches that
both ended immediately** `[measured 2026-09-03, from the log file]`:

```
16:16:15.645 loaded, PID=10660 ... Direct3DCreate9 -> 03807940 ... 16:16:15.776 unloading
16:20:25.685 loaded, PID=28072 ... Direct3DCreate9 -> 03842BB8 ... 16:20:25.816 unloading
```

131 ms of `d3d9.dll` lifetime per launch, one load/unload cycle each, nothing after. That is not a
game that reached gameplay. The log appends across runs, so a later successful run would still be
here — and is not.

**I am not claiming the proxy is broken.** I am claiming the *recorded* status ("live-verified
working, the game runs cleanly with it") is **not** what the only surviving evidence shows, and the
two are not reconcilable from static data. `[hypothesis 2026-09-03]`

**Why this matters right now:** the board has four `[FLAT]` items for this game. If the deployed
proxy does prevent startup, that flat session fails for a reason unrelated to what is being tested,
and the time is wasted. **Cheapest possible resolution, before anything else that run:** launch
once with the proxy in place.

- Game reaches the menu ⇒ the recorded status is right and this note is the thing that was wrong;
  the log lines were two aborted launches that nobody wrote down.
- Game exits immediately ⇒ rename `d3d9.dll` aside and relaunch to confirm the proxy is the cause.
  That also puts the 2026-08-25 "the vtable hook was the problem" conclusion back in question,
  because that conclusion was drawn while the plain proxy was believed to work.

## What this changes about the plan

- **The `nvapi.dll` proxy drops down the queue.** Its justification was that the stereo path was
  only reachable through the driver. With `g_mViewToClip` directly writable through a D3D9 proxy,
  it buys nothing on the critical path. Not disproved — the renderer *does* call `Stereo_Activate`
  once — just no longer the short road. Kept, re-ranked.
- **§6 is no longer the open question it was.** The lever is identified on both sides: the shader
  constant, and the game-side camera object.
- **The real blocker is now injection depth, not knowledge.** Everything above needs a proxy that
  can intercept `SetVertexShaderConstantF` — i.e. device-level interception, which is exactly what
  the unexplained 2026-08-25 vtable-hook failure blocks. That failure has moved from a footnote to
  the critical path.

## Method note worth reusing

The `/gr` drop that prompted this concluded the opposite of what the disk shows — reasonably, from
public evidence. The check that separated them cost one `ls`: **look at what the game ships before
accepting a claim about what it does at runtime.** `shaders\build\pc\` answers it in one listing.
