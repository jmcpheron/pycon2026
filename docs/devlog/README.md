# Devlog

Public R&D journal for the PyCon 2026 scadia artifact. Working out loud — design choices, prints that worked, prints that didn't, ideas that got rejected.

Posts are plain Markdown so they render natively in the GitHub web UI. Photos and clips live next to each post in `assets/<post-slug>/`.

## Posts

<!-- newest at the top -->

- **2026-05-07** — [Building the SCADvil — first attempt](2026-05-07-scadvil-anvil.md) — Phase 3 stage 1: scadia produced an anvil that scored 8/10 from the vision critic but the SCAD source has three CSG bugs the loop couldn't see.
- **2026-05-06** — [Card-text layout mockups](2026-05-06-card-text-mockups.md) — six variants of the embossed face, comparing single-line vs. two-line vs. full-path layouts.
- **2026-05-06** — [Pivot from challenge coin to business card](2026-05-06-pivot-to-business-card.md) — why the conference giveaway changed shape and what that buys us.

## Posting from the Claude Code mobile app

This repo ships a project-local `/devlog` skill. From the Claude Code mobile app:

1. Open a session in this repo.
2. Attach photo(s) or short video(s) of whatever you want to log.
3. Type `/devlog <one-line title or note>`.
4. The skill creates or appends to today's post, drops the assets in `assets/<post-slug>/`, and stages the changes for review.

You commit and push when you're ready — the skill never auto-pushes.
