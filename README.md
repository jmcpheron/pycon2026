# scadia

> Drive OpenSCAD with Claude. Natural language in, 3D models out — built as a **bounded design loop** with vision feedback.

[![CI](https://github.com/jmcpheron/pycon2026/actions/workflows/ci.yml/badge.svg)](https://github.com/jmcpheron/pycon2026/actions/workflows/ci.yml)
[![Build STL](https://github.com/jmcpheron/pycon2026/actions/workflows/build-stl.yml/badge.svg)](https://github.com/jmcpheron/pycon2026/actions/workflows/build-stl.yml)
[![Pages](https://github.com/jmcpheron/pycon2026/actions/workflows/pages.yml/badge.svg)](https://jmcpheron.github.io/pycon2026/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)

<p align="center">
  <img src="docs/assets/m10-nut.png" alt="An M10 hex nut rendered by scadia" width="400" />
  <br/>
  <em>An M10 hex nut. Generated end-to-end from the prompt <code>"a hexagonal nut, M10"</code>.</em>
</p>

---

> **PyCon 2026 demo** — Built to share at PyCon US 2026 in Long Beach (May 14–17). [Live demo page →](https://jmcpheron.github.io/pycon2026/)

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/jmcpheron/pycon2026)

## Quickstart

```bash
git clone https://github.com/jmcpheron/pycon2026
cd pycon2026
uv sync
cp .env.example .env  # then add your ANTHROPIC_API_KEY
uv run scadia "a hexagonal nut, M10" --iterations 3
```

Every iteration's `.scad`, `.png`, validation report, and the critique land in `output/run-<timestamp>/` along with a `manifest.json` that records the loop's stop reason.

## How it works

```
                    ┌─────────────────┐
   user prompt ────►│  generate SCAD  │  Anthropic, text-in/text-out
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     OpenSCAD    │
                    │  (subprocess)   │
                    └────────┬────────┘
                       PNG    │   stderr
                  ┌───────────┴────────────┐
                  ▼                        ▼
          ┌──────────────┐         ┌────────────────┐
          │ vision critic │         │  validator     │
          │ (sensor)     │         │  (sensor)      │
          │ blocking /   │         │  manifold,     │
          │ nonblocking, │         │  geometry,     │
          │ next action  │         │  warnings      │
          └──────┬───────┘         └────────┬───────┘
                 │                          │
                 └──────────┬───────────────┘
                            ▼
                    ┌──────────────┐
                    │  controller  │   should_continue:
                    │   (agent.py) │   is another iteration
                    └──────┬───────┘   likely to improve the model?
                           │
                  ┌────────┴────────┐
                  │                 │
              refine SCAD       final STL
              (loop back)        (done)
```

The critic does not decide when we are done. The controller decides whether another iteration is worth spending. The critic is one input.

## Showcase models

The [`models/`](models/) directory holds checked-in OpenSCAD source files. On every push, the [`build-stl`](.github/workflows/build-stl.yml) workflow compiles them to STL files and commits them back — so you can grab a printable `.stl` straight from the repo without running anything locally.

## Running in Codespaces

Click the **Open in GitHub Codespaces** button above. The container comes with Python 3.12, OpenSCAD, and `xvfb` pre-installed. Inside the Codespace:

```bash
# Add your key as a Codespaces secret named ANTHROPIC_API_KEY
# (Settings → Codespaces → secrets), then:
xvfb-run uv run scadia "a small mug" --iterations 3
```

The `xvfb-run` prefix gives OpenSCAD an OpenGL context for PNG rendering. STL-only commands don't need it.

## Requirements (local)

- Python 3.11+
- [OpenSCAD](https://openscad.org/) on your `$PATH`
- An Anthropic API key
- [`uv`](https://docs.astral.sh/uv/) (recommended)

## Status

**Phase 3 (current): Raspberry Pi demo arc.**

<!-- TODO(jason): one-line pitch — the headline a PyCon attendee should walk away repeating. -->

The PyCon talk demo is a four-stage progression, each stage same loop, increasing real-world constraint:

1. **Bolt** — mechanical primitive. *Shows:* cylinders, hex, chamfers. *Status:* covered by [`models/m10-nut.scad`](models/m10-nut.scad).
2. **SCADvil** — a small project-mascot calibration anvil. *Shows:* shape composition, overhangs, embossed text, holes, recognizable silhouette. *Status:* coming in a follow-up commit on this branch.
3. **Raspberry Pi 5 wall mount** — practical mounting plate at real Pi 5 dimensions (85 × 56 mm board, 58 × 49 mm mounting-hole pattern, M2.5 clearance). *Shows:* dimensional fidelity, screw clearances, standoffs. *Status:* coming in a follow-up commit.
4. **Retro Pi 5 case** — same Pi 5 constraints, layered 1980s-microcomputer design intent (vents, ribs, embossed `PYCON 2026`). *Shows:* preserving constraints while adding aesthetic intent. *Status:* coming in a follow-up commit.

<!-- TODO(jason): "Why Raspberry Pi" framing — the hook explaining why this isn't just generating cute models. Draft you wrote earlier: "The goal is not just 'make a cute model.' The goal is to see whether an AI agent can respect real-world hardware constraints while using OpenSCAD as a deterministic geometry backend." Edit in your voice. -->

> **Earlier phases:** v1 — the bounded design loop with two sensors (still the engine). Phase 2 — a 3D-printable business card with a print-in-place spinning gear; the artifact pivoted, the loop didn't. Working out loud in [`docs/devlog/`](docs/devlog/).

## License

MIT
