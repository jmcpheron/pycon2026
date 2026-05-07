# Devlog

Public R&D journal for the PyCon 2026 scadia artifact. Working out loud — design choices, prints that worked, prints that didn't, ideas that got rejected.

Posts are plain Markdown so they render natively in the GitHub web UI. Photos and clips live next to each post in `assets/<post-slug>/`.

## Posts

<!-- newest at the top -->

- **2026-05-07** — [Multi-model SCAD generation: simplified anvil across four models](2026-05-07-multi-generator-anvil.md) — same prompt, four OpenRouter generators, no orientation hint. Living post; one model per commit. Tests whether the "text lays flat" bug is a Claude habit or universal.
- **2026-05-07** — [Retro Pi 5 case — same blindspot, second confirmation](2026-05-07-pi5-retro-case.md) — Stage 3 of Phase 3. Critic gave it 9/10 with `done=True`; the SCAD has three CSG bugs the critic couldn't see (text orientation, hole depth, rib geometry). Same blindspot pattern as the SCADvil — vision sees shape, not source.
- **2026-05-07** — [Pi 5 wall mount — three iterations, no convergence](2026-05-07-pi5-wall-mount.md) — Stage 2 of Phase 3. Score went 4 → 5 → 4 across three iterations. Critic caught real bugs this time; the agent fixed one thing per pass and broke another. Ships iter-1. Also patches a markdown-fence bug in `client.py` that crashed the first attempt.
- **2026-05-07** — [Polling six critics on the SCADvil](2026-05-07-polling-critics.md) — same render, same prompt, six OpenRouter multimodal models. Gemma 4 31B caught the peg-vs-hole bug exactly; Claude Haiku scored it 7/10 here vs. 8/10 in the live run. Same critic, same render, different verdicts.
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
