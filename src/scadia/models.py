"""Typed structures shared between the agent loop, the API client, the
validation sensor, and the CLI.

The architecture is sensor-and-controller, not critic-as-judge:
  - `Critique` is the vision sensor's structured output.
  - `ValidationReport` is the technical sensor's structured output.
  - The controller (agent.should_continue) reasons over both.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Critique:
    """Vision sensor: how does the rendered image compare to the request?

    `suggested_next_action` is the controller's most informative signal:
    if it's None, the critic is explicitly saying "I have nothing concrete
    to suggest" — which is much cleaner than inferring "done" from heuristics.
    """
    done: bool
    score: int                                  # 1-10, higher is better
    blocking_issues: list[str] = field(default_factory=list)
    nonblocking_issues: list[str] = field(default_factory=list)
    suggested_next_action: str | None = None
    summary: str = ""


@dataclass
class ValidationReport:
    """Technical sensor: meaningful warnings parsed from OpenSCAD stderr.

    A second signal alongside the vision critic. If the renderer emitted
    geometry warnings (degenerate triangles, non-manifold edges, etc.),
    they show up here for both the controller and the refiner to act on.
    """
    warnings: list[str] = field(default_factory=list)

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0


@dataclass
class Iteration:
    """One loop pass. Carries the inputs (scad + render) and both sensor outputs."""
    index: int
    scad_source: str
    png_path: Path
    critique: Critique
    validation: ValidationReport
