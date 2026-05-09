# Pivot: scadia AI loop → PyCon 2026 badge (`badgeforge`)

*2026-05-08 · jmcpheron*

## What changed

The headline of the repo flipped from the **scadia AI design loop** (the Phase 3 Raspberry Pi case progression) back to **shipping a physical 3D-printed PyCon badge** at the conference. The AI-loop code stays in the repo and still works — it's just no longer the framing the README leads with.

A new tiny Python package, `badgeforge`, wraps `models/card.scad` and OpenSCAD into a single CLI:

```bash
uv run badgeforge build --name "Your Name" --github "yourhandle"
```

That same command runs in CI on every push, so `models/card.stl` in the repo always matches the source.

## Why

<!-- TODO(jmcpheron): write your own reasoning here in your own voice.
     Suggested beats — pick whichever resonate, ignore the rest:

     - the deadline math (today 2026-05-08, conference May 14–17, demo
       deadline May 13) and what it forced
     - what felt over-ambitious about finishing the Raspberry Pi arc
       in the last week
     - why the badge felt right: it was already half-built (Phase 2),
       it's the kind of thing people remember from a conference,
       "fork and print your own" is a real invitation
     - the Python angle — what `badgeforge` earns in a talk that the
       previous bash-only build-stl.yml didn't
     - anything about the print-in-place gear that excites you to ship -->

## What's now in place

- `src/badgeforge/` — Click CLI + OpenSCAD subprocess wrapper. Two short files (`cli.py`, `build.py`).
- `models/card.scad` — parameterized on `name` and `github` via OpenSCAD's `-D` flag, variant 2 layout from the [mockups post](2026-05-06-card-text-mockups.md) baked in (`[gh] <name>` over `<github>`).
- `.github/workflows/build-stl.yml` — installs `uv`, runs `badgeforge build` for the badge, falls back to a bash loop for the legacy scadia models so nothing else broke.
- README rewritten with the badge as the headline; scadia content folded into a collapsible "Earlier" section.

## Print timeline (5-day window)

| Day | Date | Goal |
|-----|------|------|
| 1 | 2026-05-08 (today) | Land code, first test print of the badge body to confirm dimensions on the actual printer. |
| 2 | 2026-05-09 | Full badge with print-in-place gear. Iterate clearances if it fuses. |
| 3 | 2026-05-10 | Buffer day for one more iteration. Polish README. |
| 4 | 2026-05-11 | Final personal-badge print. |
| 5 | 2026-05-12 | Slack day. |
| Demo | 2026-05-13 | Repo + physical badge ready. |

## Known limits

- Default text is `jmcpheron` / `pycon2026` (9 chars each). Strings noticeably longer overflow the gear pocket — the smoke test with `"github.com/jmcpheron"` produced a fused model. Auto-sizing is out of scope this week; document the envelope and move on.
- OpenSCAD 2021.01 is what's on the local machine; CI uses Ubuntu's `openscad` package. Renders match for the shapes in `card.scad`.
- Print-in-place clearance (`gear_z_lift = 0.2 mm`) is right at the edge for a 0.4 mm nozzle. Plan calls for at least one re-print if the gear binds.

## What's next

<!-- TODO(jmcpheron): fill in after the first physical print —
     photos go in assets/2026-05-08-pivot-to-badge/ and reference them
     with `![alt](assets/2026-05-08-pivot-to-badge/<file>)`. Or start
     a fresh post for the print log if you'd rather keep this one
     focused on the pivot. -->
