"""The scadia controller loop.

Two sensors, one controller:
  - Vision critic produces a `Critique` (structured, via tool-use).
  - Technical validator produces a `ValidationReport` (parsed from OpenSCAD stderr).
  - The controller (this module) decides whether another iteration is worth spending.

Kept short on purpose — readable top-to-bottom in a conference talk.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from . import client, render, validate
from .models import Iteration


# CONTROLLER ─────────────────────────────────────────────────────────────────
# The interesting question is not "do we trust the critic?" — it's
# "is there evidence another iteration would improve the model?"
#
# We continue only when there is a concrete reason to spend another iteration.
# We stop when the critic has nothing actionable left to suggest, when quality
# is acceptable with no blocking issues, when we plateau, or when we run out
# of budget. The critic does not unilaterally decide "we're done"; the
# controller reasons over both sensors.
def should_continue(iterations: list[Iteration], max_iterations: int) -> bool:
    if len(iterations) >= max_iterations:
        return False

    last = iterations[-1]
    critique = last.critique

    # Critic explicitly has no concrete change to suggest.
    if critique.suggested_next_action is None:
        return False
    if critique.done:
        return False

    # Acceptable score and no blocking issues — even if the critic is still
    # offering nits, they don't justify spending another full iteration.
    if critique.score >= 8 and not critique.blocking_issues:
        return False

    # Let the first couple of iterations breathe before plateau-checking —
    # early scores are noisy.
    if len(iterations) < 3:
        return True

    prev = iterations[-2].critique

    # Quality is not improving.
    if critique.score <= prev.score:
        return False

    # Stuck: the same blocking issue surfaced two iterations in a row.
    if set(critique.blocking_issues) & set(prev.blocking_issues):
        return False

    return True
# ─────────────────────────────────────────────────────────────────────────────


def run(user_prompt: str, max_iterations: int = 3, output_root: Path = Path("output")) -> Path:
    """Run the bounded design loop.

    Returns the path to the run directory containing every iteration's
    artifacts plus a manifest.json.
    """
    run_dir = output_root / f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"[scadia] run dir: {run_dir}")

    iterations: list[Iteration] = []
    scad = client.generate_scad(user_prompt)

    for i in range(max_iterations):
        iter_dir = run_dir / f"iter-{i:02d}"
        iter_dir.mkdir(parents=True, exist_ok=True)
        png_path = iter_dir / "render.png"

        render_result = render.scad_to_png(scad, png_path)
        validation = validate.parse_stderr(render_result.stderr)
        critique = client.critique_image(user_prompt, scad, png_path)

        print(f"[scadia] iter {i}: score={critique.score}/10  "
              f"done={critique.done}  blocking={len(critique.blocking_issues)}  "
              f"warnings={len(validation.warnings)}")
        for issue in critique.blocking_issues:
            print(f"           ✗ {issue}")
        for warning in validation.warnings:
            print(f"           ⚠ {warning}")
        if critique.suggested_next_action:
            print(f"           → {critique.suggested_next_action}")

        iterations.append(Iteration(
            index=i,
            scad_source=scad,
            png_path=png_path,
            critique=critique,
            validation=validation,
        ))

        if not should_continue(iterations, max_iterations):
            break
        scad = client.refine_scad(user_prompt, scad, critique, validation)

    final = iterations[-1]
    stl_path = run_dir / "final.stl"
    render.scad_to_stl(final.scad_source, stl_path)
    (run_dir / "final.scad").write_text(final.scad_source)
    print(f"[scadia] final STL: {stl_path}")

    _write_manifest(run_dir, user_prompt, iterations, stl_path)
    return run_dir


def _write_manifest(run_dir: Path, user_prompt: str, iterations: list[Iteration], stl_path: Path) -> None:
    manifest = {
        "prompt": user_prompt,
        "stl": str(stl_path.relative_to(run_dir)),
        "stop_reason": _stop_reason(iterations),
        "iterations": [
            {
                "index": it.index,
                "png": str(it.png_path.relative_to(run_dir)),
                "scad": _save_scad_alongside(run_dir, it),
                "critique": asdict(it.critique),
                "validation": asdict(it.validation),
            }
            for it in iterations
        ],
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))


def _stop_reason(iterations: list[Iteration]) -> str:
    """Human-readable reason the loop terminated. Useful for the demo reveal."""
    if not iterations:
        return "no iterations ran"
    last = iterations[-1].critique
    if last.suggested_next_action is None:
        return "critic had no actionable suggestion"
    if last.done:
        return "critic marked design done"
    if last.score >= 8 and not last.blocking_issues:
        return "score >= 8 with no blocking issues"
    if len(iterations) >= 2:
        prev = iterations[-2].critique
        if last.score <= prev.score:
            return "score did not improve"
        if set(last.blocking_issues) & set(prev.blocking_issues):
            return "same blocking issue across consecutive iterations"
    return "iteration cap reached"


def _save_scad_alongside(run_dir: Path, it: Iteration) -> str:
    scad_path = it.png_path.with_name("model.scad")
    scad_path.write_text(it.scad_source)
    return str(scad_path.relative_to(run_dir))
