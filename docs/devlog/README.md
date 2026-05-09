# Devlog

The rendered devlog lives at **<https://jmcpheron.github.io/pycon2026/devlog/>** — that's the canonical place to read it.

Posts are HTML, not Markdown. To browse the source: open [`index.html`](index.html) or any `YYYY-MM-DD-*.html` file directly.

The shared stylesheet is [`devlog.css`](devlog.css). The canonical scaffold for new posts is [`_post.template.html`](_post.template.html), maintained by the project-local `/devlog` Claude Code skill.

## Posting from the Claude Code mobile app

This repo ships a project-local `/devlog` skill. From the Claude Code mobile app: open a session in this repo, attach photos, type `/devlog <one-line title or note>`. The skill creates or appends to today's HTML post, drops assets in `assets/<post-slug>/`, prepends a card to `index.html`, and stages everything for review. Nothing auto-pushes.
