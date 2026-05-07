"""Poll multiple OpenRouter multimodal models with the same critique task.

Sends one render + the SCAD source + the user prompt to each model, asks each
to call submit_critique via OpenAI-format tool-calling, and saves a per-model
JSON plus a comparison.md side-by-side.

Reuses scadia's CRITIQUE_TOOL schema and SYSTEM_CRITIQUE prompt so this is an
apples-to-apples evaluation against the existing critic.

Usage:
    uv run python scripts/multi_critic.py \\
        --render docs/devlog/assets/2026-05-07-scadvil-anvil/render.png \\
        --scad   models/scadvil.scad \\
        --prompt "$(cat path/to/prompt.txt)"
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import httpx
from dotenv import load_dotenv

from scadia.client import CRITIQUE_TOOL
from scadia.models import Critique
from scadia.prompts import SYSTEM_CRITIQUE

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODELS = [
    "google/gemini-2.5-flash",
    "anthropic/claude-haiku-4.5",
    "qwen/qwen3-vl-8b-instruct",
    "openai/gpt-5-mini",
    "meta-llama/llama-4-scout",
    "google/gemma-4-31b-it",
]


def to_openai_tool(anthropic_tool: dict) -> dict:
    return {
        "type": "function",
        "function": {
            "name": anthropic_tool["name"],
            "description": anthropic_tool["description"],
            "parameters": anthropic_tool["input_schema"],
        },
    }


def build_payload(model: str, render_b64: str, scad: str, prompt: str, augment: str) -> dict:
    user_text = (
        f"Original request: {prompt}\n\n"
        f"OpenSCAD source that produced the image:\n```\n{scad}\n```\n\n"
        "Critique the rendered image against the original request. "
        "Call the submit_critique tool with your assessment."
    )
    if augment:
        user_text += f"\n\nAdditional guidance: {augment}"
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_CRITIQUE},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{render_b64}"}},
                    {"type": "text", "text": user_text},
                ],
            },
        ],
        "tools": [to_openai_tool(CRITIQUE_TOOL)],
        "tool_choice": {"type": "function", "function": {"name": "submit_critique"}},
        "max_tokens": 1024,
    }


def parse_critique(resp: dict) -> tuple[Critique | None, str]:
    """Return (critique, source). source is 'tool_call', 'json_text', or 'error'."""
    try:
        msg = resp["choices"][0]["message"]
    except (KeyError, IndexError, TypeError):
        return None, "error"

    for call in msg.get("tool_calls") or []:
        if call.get("function", {}).get("name") == "submit_critique":
            try:
                return _critique_from_dict(json.loads(call["function"]["arguments"])), "tool_call"
            except (json.JSONDecodeError, KeyError, ValueError, TypeError):
                continue

    text = msg.get("content") or ""
    if isinstance(text, list):
        text = " ".join(p.get("text", "") for p in text if isinstance(p, dict))
    match = re.search(r"\{[\s\S]*\}", str(text))
    if match:
        try:
            return _critique_from_dict(json.loads(match.group(0))), "json_text"
        except (json.JSONDecodeError, KeyError, ValueError, TypeError):
            pass

    return None, "error"


def _critique_from_dict(d: dict) -> Critique:
    return Critique(
        done=bool(d.get("done", False)),
        score=int(d.get("score", 0)),
        blocking_issues=list(d.get("blocking_issues", [])),
        nonblocking_issues=list(d.get("nonblocking_issues", [])),
        suggested_next_action=d.get("suggested_next_action") or None,
        summary=str(d.get("summary", "")),
    )


def write_comparison_md(out_dir: Path, prompt: str, render_path: Path, augment: str, rows: list[dict]) -> None:
    lines: list[str] = []
    lines.append("# multi-critic comparison\n")
    lines.append(f"- render: `{render_path}`")
    lines.append(f"- prompt (first 200 chars): `{prompt[:200]}{'...' if len(prompt) > 200 else ''}`")
    lines.append(f"- augment: {('`' + augment + '`') if augment else '(none — SYSTEM_CRITIQUE verbatim)'}\n")
    lines.append("| model | done | score | blocking | non-blocking | source | t(s) |")
    lines.append("|---|---|---|---|---|---|---|")
    for row in rows:
        if "error" in row:
            lines.append(f"| `{row['model']}` | — | — | — | — | error | {row['elapsed_s']} |")
            continue
        c = row.get("critique")
        if not c:
            lines.append(f"| `{row['model']}` | — | — | — | — | unparsed | {row['elapsed_s']} |")
            continue
        lines.append(
            f"| `{row['model']}` | {c['done']} | {c['score']} "
            f"| {len(c['blocking_issues'])} | {len(c['nonblocking_issues'])} | {row['source']} | {row['elapsed_s']} |"
        )
    lines.append("\n## blocking issues by model\n")
    for row in rows:
        if "error" in row or not row.get("critique"):
            continue
        c = row["critique"]
        lines.append(f"### `{row['model']}` — score {c['score']}")
        lines.append(f"_summary:_ {c['summary']}\n")
        if c["blocking_issues"]:
            for b in c["blocking_issues"]:
                lines.append(f"- **blocking:** {b}")
        if c["nonblocking_issues"]:
            for b in c["nonblocking_issues"]:
                lines.append(f"- nonblocking: {b}")
        if not (c["blocking_issues"] or c["nonblocking_issues"]):
            lines.append("- (no issues reported)")
        lines.append("")
    for row in rows:
        if "error" in row:
            lines.append(f"### `{row['model']}` — ERROR")
            lines.append(f"```\n{row['error']}\n```\n")
    (out_dir / "comparison.md").write_text("\n".join(lines))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--render", required=True, type=Path)
    p.add_argument("--scad", required=True, type=Path)
    p.add_argument("--prompt", required=True, help="original user prompt that produced the render")
    p.add_argument("--models", default=",".join(DEFAULT_MODELS))
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--augment", default="")
    args = p.parse_args()

    load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("error: OPENROUTER_API_KEY not set in .env", file=sys.stderr)
        return 2

    out_dir = args.out or Path("output/experiments") / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir.mkdir(parents=True, exist_ok=True)

    render_b64 = base64.standard_b64encode(args.render.read_bytes()).decode("ascii")
    scad_text = args.scad.read_text()
    models = [m.strip() for m in args.models.split(",") if m.strip()]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/jmcpheron/pycon2026",
        "X-Title": "scadia multi-critic experiment",
    }

    rows: list[dict] = []
    with httpx.Client(headers=headers, timeout=90.0) as client:
        for model in models:
            slug = model.replace("/", "_")
            print(f"[multi_critic] {model:<40} ", end="", flush=True)
            t0 = time.monotonic()
            try:
                resp = client.post(OPENROUTER_URL, json=build_payload(model, render_b64, scad_text, args.prompt, args.augment))
                resp.raise_for_status()
                data = resp.json()
                crit, source = parse_critique(data)
                row = {
                    "model": model,
                    "elapsed_s": round(time.monotonic() - t0, 2),
                    "source": source,
                    "critique": asdict(crit) if crit else None,
                    "raw": data,
                }
            except httpx.HTTPStatusError as e:
                row = {"model": model, "elapsed_s": round(time.monotonic() - t0, 2), "error": f"HTTP {e.response.status_code}: {e.response.text[:200]}"}
            except Exception as e:
                row = {"model": model, "elapsed_s": round(time.monotonic() - t0, 2), "error": f"{type(e).__name__}: {e}"}

            (out_dir / f"{slug}.json").write_text(json.dumps(row, indent=2))
            if "error" in row:
                print(f"error  ({row['error'][:60]})")
            elif row["critique"]:
                c = row["critique"]
                print(f"score={c['score']}  done={c['done']}  blocking={len(c['blocking_issues'])}  via={row['source']}  ({row['elapsed_s']}s)")
            else:
                print(f"no critique parsed  ({row['elapsed_s']}s)")
            rows.append(row)

    write_comparison_md(out_dir, args.prompt, args.render, args.augment, rows)
    print(f"\n[multi_critic] wrote {out_dir}/ (comparison.md + per-model JSON)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
