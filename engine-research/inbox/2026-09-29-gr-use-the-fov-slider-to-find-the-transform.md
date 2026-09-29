# /gr 2026-09-29: use the in-game FOV slider to find where the transform lives

For the `[PD]` "new hypothesis" row and §6f "What is NOT established". The game's own FOV slider (Options →
Controls, 20 notches, default 10) is a controlled knob on the projection `[reported]`. Diff every constant upload
path (VS/PS F/I/B, SetTransform, effect setters) and camera-ish memory between slider 10 and 20: whatever scales by
tan(fov20/2)/tan(fov10/2) is the real route; if nothing on the wrapped device changes, the scene is not drawn through
it. Topic: `external-research/topics/2026-09-29-the-fov-slider-is-a-free-probe-for-where-the-transform-lives.md`.
