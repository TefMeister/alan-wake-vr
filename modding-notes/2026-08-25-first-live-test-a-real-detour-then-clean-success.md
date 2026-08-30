# 2026-08-25 — First live test: a genuine detour, then a clean, simple answer

## What happened, in plain terms

The simplest possible version of our proxy — just forwarding `Direct3DCreate9`, nothing
else — crashed the game outright on the very first try. Windows' own crash log confirmed it
was a real memory-access violation, not something vague. Removing our DLL entirely made the
game launch fine, so we knew for certain our file was the cause, even though the one thing it
actually did (call the real Direct3DCreate9 function) worked and returned a valid result.

To dig deeper, we added code to watch the *next* step — device creation — since that's
something our simple proxy wasn't looking at yet. That meant patching a low-level table of
function pointers inside the game's own Direct3D object, a standard and normally safe
technique.

**That new code turned out to be the actual problem, not the diagnostic tool we thought it
was.** With it in place, the game kept failing — first as the same crash, then, after we tried
a legitimate Windows compatibility fix meant for old games with heap bugs, as a different,
quieter failure (screen flashes black, then just stops, no error message at all).

The real test that cracked it: we tried the build with that new patching code disabled,
keeping everything else the same. It worked immediately, no issues. Then we removed the
Windows compatibility fix too, just to be thorough — still worked. So the compatibility fix
was never actually necessary; the genuine cause was specifically in our own new code, for a
reason we don't yet understand.

## Where things stand

The simple, working version — just forwarding the one function we actually need right now —
is what's deployed and confirmed working. The device-creation-watching code is still sitting
in our source file for later, but it's switched off and clearly marked not to be turned back
on without first understanding what actually went wrong.

## Why this is worth writing down properly

This is a good example of something worth remembering for every future project too: when a
"diagnostic" addition itself becomes the reason something breaks, the fix isn't to paper over
it with unrelated system-level workarounds — it's to isolate the actual new variable and test
it directly. The Windows compatibility flag felt like a plausible, low-risk fix at the time,
and it's good that we double-checked it was really needed rather than just assuming it was
and moving on.

Full technical detail: `alan-wake-vr-staging`, `proxy-d3d9/README.md`.
Distilled reference: `alan-wake-vr-engine-research`, `ENGINE-DOSSIER.md` §4/§11.
