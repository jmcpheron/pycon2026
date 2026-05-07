"""Anthropic API helpers.

Three calls:
  - generate_scad: text-in, SCAD-out. Initial pass.
  - refine_scad: text-in, SCAD-out. Takes the prior SCAD plus signals from
    both sensors (critic + technical validation).
  - critique_image: vision-in, structured Critique-out via tool-use.

Design choices worth knowing:
  - Each call is fresh — no conversation history accumulation across iterations.
    Avoids anchoring on earlier wrong attempts and keeps token cost flat.
  - The critic uses tool-use rather than free text, so its output is
    structured signal the controller can reason over (not text to parse).
"""

from __future__ import annotations

import base64
from pathlib import Path

from anthropic import Anthropic

from .models import Critique, ValidationReport
from .prompts import SYSTEM_CRITIQUE, SYSTEM_GENERATE, SYSTEM_REFINE

MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 4096

CRITIQUE_TOOL = {
    "name": "submit_critique",
    "description": (
        "Submit your structured assessment of how well the rendered 3D model "
        "matches the user's original request. You are a sensor, not a judge — "
        "the controller decides whether to iterate further."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "done": {
                "type": "boolean",
                "description": (
                    "True if the model credibly depicts the requested object "
                    "with no blocking issues. False if any blocking issue remains."
                ),
            },
            "score": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10,
                "description": "Overall fidelity to the request, 1 (unrelated) to 10 (perfect).",
            },
            "blocking_issues": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "Problems that prevent the model from credibly depicting the "
                    "requested object. Each entry is one concrete, actionable issue."
                ),
            },
            "nonblocking_issues": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "Minor or stylistic concerns. The model is still recognizable "
                    "even if these are not fixed."
                ),
            },
            "suggested_next_action": {
                "type": ["string", "null"],
                "description": (
                    "One-sentence concrete change to try next, or null if you have "
                    "no actionable suggestion. Null tells the controller you have "
                    "no more useful signal — use it honestly."
                ),
            },
            "summary": {
                "type": "string",
                "description": "One-sentence overall assessment.",
            },
        },
        "required": [
            "done", "score", "blocking_issues", "nonblocking_issues",
            "suggested_next_action", "summary",
        ],
    },
}

# Tokens the model sometimes emits as a stand-in for null.
_NULL_TOKENS = {"", "null", "none", "n/a", "no suggestion", "(none)"}


def _client() -> Anthropic:
    return Anthropic()


def generate_scad(user_prompt: str) -> str:
    """Initial text→SCAD pass."""
    msg = _client().messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_GENERATE,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return _extract_text(msg).strip()


def refine_scad(
    user_prompt: str,
    prior_scad: str,
    critique: Critique,
    validation: ValidationReport,
) -> str:
    """Refinement pass given signals from both sensors."""
    blocking = _bullet_list(critique.blocking_issues)
    nonblocking = _bullet_list(critique.nonblocking_issues)
    warnings = _bullet_list(validation.warnings)
    next_action = critique.suggested_next_action or "(no suggestion provided)"

    user_content = (
        f"Original request:\n{user_prompt}\n\n"
        f"Your previous OpenSCAD program:\n```\n{prior_scad}\n```\n\n"
        f"Critic's overall: {critique.summary} (score {critique.score}/10)\n\n"
        f"Blocking issues:\n{blocking}\n\n"
        f"Non-blocking issues:\n{nonblocking}\n\n"
        f"OpenSCAD compiler warnings:\n{warnings}\n\n"
        f"Critic's suggested next action: {next_action}\n\n"
        f"Produce a revised OpenSCAD program that addresses the blocking "
        f"issues and any compiler warnings."
    )
    msg = _client().messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_REFINE,
        messages=[{"role": "user", "content": user_content}],
    )
    return _extract_text(msg).strip()


def critique_image(user_prompt: str, scad_source: str, png_path: Path) -> Critique:
    """Vision call: look at the render, judge against the prompt, return structured Critique."""
    image_b64 = base64.standard_b64encode(png_path.read_bytes()).decode("ascii")
    user_content = [
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": image_b64,
            },
        },
        {
            "type": "text",
            "text": (
                f"Original request: {user_prompt}\n\n"
                f"OpenSCAD source that produced the image:\n```\n{scad_source}\n```\n\n"
                "Critique the rendered image against the original request. "
                "Call the submit_critique tool with your assessment."
            ),
        },
    ]
    msg = _client().messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_CRITIQUE,
        tools=[CRITIQUE_TOOL],
        tool_choice={"type": "tool", "name": "submit_critique"},
        messages=[{"role": "user", "content": user_content}],
    )
    return _extract_critique(msg)


def _bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) or "(none)"


def _extract_text(msg) -> str:
    for block in msg.content:
        if getattr(block, "type", None) == "text":
            return block.text
    raise RuntimeError(f"no text block in response: {msg}")


def _extract_critique(msg) -> Critique:
    for block in msg.content:
        if getattr(block, "type", None) == "tool_use" and block.name == "submit_critique":
            data = block.input
            return Critique(
                done=bool(data["done"]),
                score=int(data["score"]),
                blocking_issues=list(data.get("blocking_issues", [])),
                nonblocking_issues=list(data.get("nonblocking_issues", [])),
                suggested_next_action=_normalize_next_action(data.get("suggested_next_action")),
                summary=str(data.get("summary", "")),
            )
    raise RuntimeError(f"no submit_critique tool_use in response: {msg}")


def _normalize_next_action(value) -> str | None:
    """Accept null, missing, or stringly-null values — normalize to real None.

    Models occasionally emit the string 'null' or an empty string instead of
    a JSON null. We treat those as the controller-stop signal too, since
    semantically they're saying the same thing.
    """
    if value is None:
        return None
    if isinstance(value, str) and value.strip().lower() in _NULL_TOKENS:
        return None
    return str(value)
