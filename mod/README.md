# Alan Wake VR

A VR conversion mod for **Alan Wake (2010)** by Remedy Entertainment — the
goal is stereo rendering and 6DOF head tracking, and ultimately motion-
controlled play, in the flashlight-and-shotgun psychological thriller.

> **Status: work in progress — nothing playable released yet, no code
> written yet.** This folder holds releases only; watch it if you
> want to know the moment there is something to try.

## What this will be

Alan Wake runs on Remedy's own proprietary in-house engine for this title —
a predecessor to the studio's later, publicly-named **Northlight** engine
(which debuted with *Quantum Break* in 2016). This earlier engine has no
widely-used public name. Nothing about its internals is assumed yet; the
[engine dossier](../engine-research/)
will be filled in from first principles, following the same reusable
[flat-to-VR playbook](../engine-research//blob/main/PLAYBOOK.md)
used across all of our conversions. As with our other projects, the playable
mod is almost the by-product — the real goal is the knowledge gained on the
way there, written down and shared so anyone can do the same for any game.

## What you will need

- Your own legitimate copy of **Alan Wake** (this mod contains **no** game
  files).
- A PC VR headset and runtime (SteamVR and/or OpenXR — to be decided as
  engine research progresses).

## The folders for Alan Wake VR

Everything for this game lives in one repository, one folder per job — so you
always know where to look. You are in **`mod/`**.

| Folder | What lives here |
| --- | --- |
| **`mod/`** ← you are here | The mod itself — releases only, once there is something to release. |
| [`dev-archive/`](../dev-archive/) | Full development history — snapshots, probes, dead ends, raw recon. |
| [`modding-notes/`](../modding-notes/) | Readable field notes / progress ledger. |
| [staging/alan-wake-vr](https://github.com/TefMeister/staging/tree/main/alan-wake-vr) 🔒 | **Private** — unverified WIP builds, cross-machine handoff. |
| [`engine-research/`](../engine-research/) | Distilled engine reference (dossier) + reusable VR RE playbook. |
| [`external-research/`](../external-research/) | Ongoing public-research leads, gathered separately from hands-on modding work. |

## Credits, scope, and legality

Non-commercial fan project; requires an owned copy; redistributes no original
assets. We credit everyone whose work this builds on — see
[`CREDITS.md`](CREDITS.md) — and we honour correction/removal requests from
rights holders promptly.

## Contributing & policy

See [CONTRIBUTING.md](CONTRIBUTING.md) — how we credit and link sources, our
**study-everything-public but write-our-own-code** rule (we copy no one else's
source code or files, any license or price), the terms for reusing our work
(free, with credit), and how to request a correction or removal.
