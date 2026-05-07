"""Run one or more OpenRouter generation models against the same SCAD prompt.

Single-shot: SYSTEM_GENERATE + user prompt → SCAD → render. No iteration loop,
no critic. Captures what each model produces on first try; saves per-model
.scad, .png (or error), and raw API response, plus a comparison.md.

Reuses scadia's SYSTEM_GENERATE prompt and the OpenSCAD render subprocess, so
results are directly comparable to the live agent's iter-0 output.

Usage:
    # one model
    uv run python scripts/multi_generator.py \\
        --model anthropic/claude-haiku-4.5 \\
        --prompt "$(cat /path/to/prompt.txt)" \\
        --out output/experiments/multi-gen-2026-05-07/

    # several models, same out dir (artifacts coexist by slug)
    uv run python scripts/multi_generator.py \\
        --models anthropic/claude-haiku-4.5,google/gemini-2.5-flash \\
        --prompt "..." \\
        --out output/experiments/multi-gen-2026-05-07/
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
from dotenv import load_dotenv

from scadia.client import _strip_fence
from scadia.prompts import SYSTEM_GENERATE
from scadia.render import RenderError, scad_to_png

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def slugify(model: str) -> str:
    return model.replace("/", "_")


def call_openrouter(client: httpx.Client, model: str, prompt: str, max_tokens: int) -> tuple[str | None, dict, str | None]:
    """Returns (scad_text_or_None, raw_response, error_message_or_None)."""
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_GENERATE},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
    }
    try:
        r = client.post(OPENROUTER_URL, json=body, timeout=120.0)
        r.raise_for_status()
        data = r.json()
    except httpx.HTTPStatusError as e:
        return None, {"http_error": e.response.status_code, "body": e.response.text[:500]}, f"HTTP {e.response.status_code}"
    except Exception as e:
        return None, {"error": f"{type(e).__name__}: {e}"}, f"{type(e).__name__}: {e}"

    try:
        msg = data["choices"][0]["message"]
        content = msg.get("content") or ""
        if isinstance(content, list):
            content = " ".join(p.get("text", "") for p in content if isinstance(p, dict))
        scad = _strip_fence(str(content))
        if not scad.strip():
            return None, data, "empty content"
        return scad, data, None
    except (KeyError, IndexError, TypeError) as e:
        return None, data, f"unexpected response shape: {e}"


def run_one(client: httpx.Client, model: str, prompt: str, out_dir: Path, max_tokens: int) -> dict:
    slug = slugify(model)
    print(f"[multi_gen] {model:<40} ", end="", flush=True)
    t0 = time.monotonic()

    scad, raw, gen_err = call_openrouter(client, model, prompt, max_tokens)
    elapsed_gen = round(time.monotonic() - t0, 2)
    (out_dir / f"{slug}.raw.json").write_text(json.dumps(raw, indent=2))

    if scad is None:
        result = {"model": model, "elapsed_gen_s": elapsed_gen, "error": gen_err, "stage": "generate"}
        (out_dir / f"{slug}.error.json").write_text(json.dumps(result, indent=2))
        print(f"GEN FAIL  ({gen_err})")
        return result

    (out_dir / f"{slug}.scad").write_text(scad)

    t1 = time.monotonic()
    try:
        scad_to_png(scad, out_dir / f"{slug}.png", workdir=out_dir / f"{slug}.work")
        elapsed_render = round(time.monotonic() - t1, 2)
        result = {"model": model, "elapsed_gen_s": elapsed_gen, "elapsed_render_s": elapsed_render, "ok": True}
        print(f"OK   gen={elapsed_gen}s  render={elapsed_render}s")
    except RenderError as e:
        elapsed_render = round(time.monotonic() - t1, 2)
        result = {
            "model": model,
            "elapsed_gen_s": elapsed_gen,
            "elapsed_render_s": elapsed_render,
            "error": str(e)[:1500],
            "stage": "render",
        }
        (out_dir / f"{slug}.error.json").write_text(json.dumps(result, indent=2))
        print(f"RENDER FAIL  ({str(e).splitlines()[0][:80]})  gen={elapsed_gen}s")

    return result


def write_comparison(out_dir: Path, prompt: str, results: list[dict]) -> None:
    lines = [
        "# multi-generator comparison\n",
        f"- prompt (first 200 chars): `{prompt[:200]}{'...' if len(prompt) > 200 else ''}`\n",
        "| model | outcome | gen (s) | render (s) |",
        "|---|---|---|---|",
    ]
    for r in results:
        if r.get("ok"):
            lines.append(f"| `{r['model']}` | OK | {r['elapsed_gen_s']} | {r['elapsed_render_s']} |")
        elif r.get("stage") == "render":
            lines.append(f"| `{r['model']}` | render fail | {r['elapsed_gen_s']} | {r['elapsed_render_s']} |")
        else:
            lines.append(f"| `{r['model']}` | gen fail: {r.get('error', '?')[:60]} | {r.get('elapsed_gen_s', '-')} | - |")
    (out_dir / "comparison.md").write_text("\n".join(lines))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", help="single model slug")
    p.add_argument("--models", help="comma-separated model slugs")
    p.add_argument("--prompt", required=True)
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--max-tokens", type=int, default=2048, help="upper bound on response tokens (reasoning models may need more)")
    args = p.parse_args()

    if not args.model and not args.models:
        print("error: pass --model or --models", file=sys.stderr)
        return 2

    models = [args.model] if args.model else [m.strip() for m in args.models.split(",") if m.strip()]

    load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("error: OPENROUTER_API_KEY not set", file=sys.stderr)
        return 2

    out_dir = args.out or Path("output/experiments") / f"multi-gen-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    out_dir.mkdir(parents=True, exist_ok=True)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/jmcpheron/pycon2026",
        "X-Title": "scadia multi-generator experiment",
    }

    results: list[dict] = []
    with httpx.Client(headers=headers) as client:
        for m in models:
            results.append(run_one(client, m, args.prompt, out_dir, args.max_tokens))

    write_comparison(out_dir, args.prompt, results)
    print(f"\n[multi_gen] wrote {out_dir}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
