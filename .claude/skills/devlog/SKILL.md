---
name: devlog
description: Append to the public R&D devlog at docs/devlog/. Use when the user wants to log progress, attach photos or videos, or capture an idea for the PyCon 2026 build journal. Triggers on `/devlog ...` or natural-language requests like "log this", "post to the devlog", or "add a journal entry".
---

# /devlog — append to the public R&D journal (HTML edition)

This repo keeps a public, **HTML-based** working journal at `docs/devlog/`. Every post is one self-contained HTML file: `YYYY-MM-DD-<slug>.html`. Photos and clips referenced in a post live in `docs/devlog/assets/<same-slug>/`.

The user may invoke this skill from the Claude Code mobile app, often with attached image or video files. Treat any attached media as belonging to the post you're about to write.

## What this skill should do

1. **Resolve the slug for today's post.** **One post per topic** — slug derived from the user's title arg (kebab-cased, ≤ 6 words). New post if no existing file for today with that slug; otherwise append. If the user passes no title, prompt them for one short phrase rather than defaulting to a daily-notes file.

2. **Compute the file path.** `docs/devlog/<YYYY-MM-DD>-<slug>.html`. Use the local date — confirm with `date +%Y-%m-%d` if unsure.

3. **Save attached media.**
   - Move/copy any attached image or video files into `docs/devlog/assets/<YYYY-MM-DD>-<slug>/`.
   - Preserve original extensions. If two attachments collide on filename, append `-2`, `-3`, etc.
   - Acceptable extensions: `.jpg .jpeg .png .gif .webp .heic .mp4 .mov .webm`.

4. **Write the post body.**
   - **New file:** copy `docs/devlog/_post.template.html` to the new path, then replace the placeholders:
     - `{{TITLE}}` — the user's title or first-sentence summary
     - `{{DATE_ISO}}` — `YYYY-MM-DD`
     - `{{DATE_HUMAN}}` — same value (the template uses one format)
     - `{{LEDE}}` — a one-sentence summary of the post (≤ 220 chars)
     - `{{SLUG}}` — the resolved slug
     - `{{PREV_HREF}}` / `{{PREV_TITLE}}` — chronologically previous post (or remove the `<a class="prev">` if this is the first post)
     - `{{NEXT_HREF}}` / `{{NEXT_TITLE}}` — leave empty placeholder `<span></span>` initially; the next post's creation updates this one
   - Replace the example `<section class="entry">` content with the user's message text wrapped in proper HTML (`<p>…</p>`, `<ul><li>…</li></ul>`, `<pre class="code"><code>…</code></pre>` for any code blocks the user pastes).
   - Drop image references as `<figure><img src="assets/<slug>/<file>" alt="<alt>" loading="lazy"><figcaption><span class="num">FIG 01</span><span class="desc">…</span></figcaption></figure>`.
   - **Existing file:** append a new `<section class="entry">` BEFORE the `</article>` close tag with this shape:
     ```html
     <section class="entry">
       <h2>HH:MM</h2>
       <p>…user's message…</p>
       …figures, code blocks, etc.…
     </section>
     ```
     Use the time the post is being added (24-hour format) as the `<h2>`.

5. **Update the devlog index** (`docs/devlog/index.html`).
   - **New file:** prepend a new `<article class="post-card">` immediately after the `<!-- newest -->` marker comment:
     ```html
     <article class="post-card">
       <p class="date">YYYY · MM · DD</p>
       <h2><a href="<filename>.html">Post Title</a></h2>
       <p class="lede">…one-line summary…</p>
       <div class="tag-row">
         <span class="tag tag-<kind>"><kind></span>
       </div>
     </article>
     ```
     Pick the most appropriate `<kind>` tag class: `tag-pivot`, `tag-decision`, `tag-experiment`, or `tag-print-log`. Multiple tags are allowed.
   - **Append to existing file:** no index change needed — the existing card is still accurate.

6. **Stage but do not commit.** Run `git add` for the new/changed files. Show the user the staged diff (`git diff --cached --stat`). Do **not** run `git commit` or `git push` — the user reviews before publishing.

## Things this skill must not do

- Auto-commit or auto-push.
- Edit posts older than today (the journal is append-only by convention).
- Rewrite the user's words. Only rephrase a title if explicitly asked.
- Touch any path outside `docs/devlog/` and (for staging) the git index.
- Write Markdown. **Posts are HTML.** The shared stylesheet `devlog.css` and the template `_post.template.html` are the canonical sources of truth for structure.

## Things to clarify before writing if not obvious

- If no attachment is present and the message has no clear topic, ask whether this is a quick note (append to today's most recent post) or a new dedicated post.
- If the user passed a title but a file with that slug already exists for today, ask whether to append or to use a new slug.

## Manual smoke test (run after first invocation)

```bash
python3 -m http.server 8765 -d docs &
sleep 1
curl -s http://localhost:8765/devlog/ | grep -c '<article class="post-card">'   # should equal current post count
curl -sI http://localhost:8765/devlog/<YYYY-MM-DD>-<slug>.html | head -3        # should return 200
kill %1 2>/dev/null
```

## Example invocation

> User (mobile): `/devlog gear came off the bed clean — first try` *(with a photo attached)*

Skill should:
- Resolve slug (e.g. `gear-came-off-clean`).
- Save the photo to `docs/devlog/assets/<date>-<slug>/IMG_xxxx.jpg`.
- Copy `_post.template.html` → `docs/devlog/<date>-<slug>.html`, fill placeholders, replace the example section with the user's note + the figure.
- Prepend a `<article class="post-card">` to `index.html` (newest first) with the `tag-print-log` chip.
- Stage the changes.
- Reply with the file path and a one-line "staged, ready to push when you are".
