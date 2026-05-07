---
name: devlog
description: Append to the public R&D devlog at docs/devlog/. Use when the user wants to log progress, attach photos or videos, or capture an idea for the PyCon 2026 build journal. Triggers on `/devlog ...` or natural-language requests like "log this", "post to the devlog", or "add a journal entry".
---

# /devlog — append to the public R&D journal

This repo keeps a public, markdown-based working journal at `docs/devlog/`. Every post is one `YYYY-MM-DD-slug.md` file. Photos and clips referenced in a post live in `docs/devlog/assets/<same-slug>/`.

The user may invoke this skill from the Claude Code mobile app, often with attached image or video files. Treat any attached media as belonging to the post you're about to write.

## What this skill should do

1. **Resolve the slug for today's post.**
   <!-- TODO(jmcpheron): define your slug rule. Suggested behaviors to choose
        between — pick one, then delete the others:

        a) One post per day, fixed slug `daily-notes`. Title arg becomes the
           heading of a new `## <timestamp>` section appended to the file.
           (Pro: predictable. Con: mixes unrelated topics into one file.)

        b) One post per topic, slug derived from the user's title arg
           (kebab-cased, ≤ 6 words). New post if no existing file for today
           with that slug; otherwise append.
           (Pro: clean per-topic posts. Con: needs slug-collision handling.)

        c) Hybrid: if the user passes `--title "..."`, behavior (b);
           otherwise behavior (a). -->

2. **Compute the file path.** `docs/devlog/<YYYY-MM-DD>-<slug>.md`. Use the local date — confirm with `date +%Y-%m-%d` if unsure.

3. **Save attached media.**
   - Move/copy any attached image or video files into `docs/devlog/assets/<YYYY-MM-DD>-<slug>/`.
   - Preserve original extensions. If two attachments collide on filename, append `-2`, `-3`, etc.
   - Acceptable extensions: `.jpg .jpeg .png .gif .webp .heic .mp4 .mov .webm`.

4. **Write the post body.** If the file is new:
   ```markdown
   # <Title from user, or first sentence of message>

   *<YYYY-MM-DD> · jmcpheron*

   ## <HH:MM>

   <user's message text>

   ![<alt>](assets/<slug>/<file>)
   ```
   If the file exists, append a new `## <HH:MM>` section at the bottom with the same body shape.

5. **Update `docs/devlog/README.md`** so the post (or new section) is reachable from the index.
   <!-- TODO(jmcpheron): pick an index format. Options:
        - Always-prepend: insert this entry as the first bullet under "## Posts"
          and leave older entries in place.
        - Group by date: ensure a `### YYYY-MM-DD` heading exists, then
          add this post as a bullet under it.
        - No-op when appending to an existing post (only add to the index
          when a *new* file is created). -->

6. **Stage but do not commit.** Run `git add docs/devlog/...` for the new/changed files. Show the user the staged diff (`git diff --cached --stat`). Do **not** run `git commit` or `git push` — the user reviews before publishing.

## Things this skill must not do

- Auto-commit or auto-push.
- Edit posts older than today (the journal is append-only by convention).
- Rewrite the user's words. Only rephrase a title if explicitly asked.
- Touch any path outside `docs/devlog/` and (for staging) the git index.

## Things to clarify before writing if not obvious

- If no attachment is present and the message has no clear topic, ask whether this is a quick note (append to today's `daily-notes`) or a new dedicated post.
- If the user passed `--title` but a file with that slug already exists for today, ask whether to append or to use a new slug.

## Example invocation

> User (mobile): `/devlog gear came off the bed clean — first try` *(with a photo attached)*

Skill should:
- Resolve slug (per the rule chosen above).
- Save the photo to `docs/devlog/assets/<date>-<slug>/IMG_xxxx.jpg`.
- Create or append to `docs/devlog/<date>-<slug>.md` with the message and an image reference.
- Update the index.
- Stage the changes.
- Reply with the file path and a one-line "staged, ready to push when you are".
