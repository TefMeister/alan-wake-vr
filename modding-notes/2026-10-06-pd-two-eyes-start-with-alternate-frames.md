# 2026-10-06 (/pd, no launch): two eyes — start with alternate frames

**The game was not launched; nothing here has been run.**

## The choice

There are three ways to give each eye its own picture:

1. **Alternate frames.** Draw one frame for the left eye, the next for the right. The headset shows each eye its
   own frames, at half the frame rate. Needs nothing new from the game: our edit already moves the camera for one
   eye (proven live today), so it only has to flip sides every frame.
2. **Draw every pass twice in one frame.** The proper result, but this game draws in many passes (lighting,
   shadows, fog, glows), and each would have to be doubled.
3. **Ask the game to draw the whole frame twice.** Clean, but needs the game's own "draw a frame" routine found first.

Number 1 is built now; 2 or 3 is the upgrade later. Nothing in 1 is thrown away by doing 2 or 3.

## What was built

- A new small file hooks the moment each frame is finished and flips the eye for the next frame.
- It only switches on when the settings file says `Mode=afr`, so the installed game behaves exactly as before
  until then.
- It is taken back out cleanly if our file is unloaded, like every other hook in this project.
- Builds cleanly; the existing self-tests pass. `[compile-verified 2026-10-06]`

## Known costs

- Each eye updates at half the frame rate.
- Motion blur looks at the last frame, which is now the other eye; test with the game's `-noblur` option.
- Flat screen effects that do not use the camera values (the lamp glow) stay the same in both eyes.
- Lighting is worked out from depth using the camera's inverse; at a real eye distance the error is a few
  centimetres at 10 m. Fixing it needs one more hook, queued.

## Next

One launch: set `Mode=afr`, switch the edit on, take about ten quick screenshots. They should fall into two groups,
Alan nudged left in one and right in the other. If the log shows no `afr:` lines, the game finishes its frames
another way and that one needs hooking instead.

## Not established

- That the game finishes its frames through the hook used here.
- How it looks or feels in a headset (no headset output yet).
