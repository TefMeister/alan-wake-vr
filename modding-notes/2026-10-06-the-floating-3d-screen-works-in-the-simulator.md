# 2026-10-06 (late): the floating 3D screen works in the simulator

Dev PC, `/lm`, three launches, using the OpenXR simulator (a stand-in for a headset that shows what each eye
would see in a window).

## What happened

- **First try: no headset found.** Starting the game's exe directly makes it restart itself through Steam, which
  throws away any setting given to the first start. Fix: our file now reads the runtime to use from its own settings
  (`[vr] RuntimeJson`), so this game can use the simulator while the PC's real VR setup is left alone.
- **Second try: it works.** The headset side started, made one image per eye, and kept sending frames. The simulator
  reported a healthy session at its full 90 frames a second, and its view showed the game screen in both eyes.
  `[verified-live 2026-10-06, n=2 launches]`
- **The screen was at floor height** at first; it is now placed wherever the head is when the session starts
  (1.70 m in the simulator), and stays there.

## Where this leaves Alan Wake

Everything needed for a first headset look is built and checked on the monitor and in the simulator: two eyes,
lighting per eye, and the floating 3D screen. The next step is Tefa trying it in the real headset on the home PC
(a reminder with the exact steps is waiting there). After that: head tracking into the game camera.

## Not established

- How it looks and feels in a real headset.
- Frame rate on the home PC.

Evidence: `dev-archive/recon/2026-10-06-headset-output-in-the-simulator/`.
