"""Technical-validation sensor.

OpenSCAD writes informational, warning, and error lines to stderr. We extract
the actionable subset (WARNING/ERROR) and filter out UI/font noise that
isn't useful to the controller or the refiner.

This is the second signal the controller reasons over alongside the vision
critic. Two sensors, one controller — the critic doesn't get to decide
unilaterally that "we're done" if OpenSCAD is also complaining about
non-manifold geometry.
"""

from __future__ import annotations

import re

from .models import ValidationReport

# Lines to drop even if they're tagged WARNING/ERROR — UI plumbing, not signal.
_NOISE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^UI-WARNING:"),
    re.compile(r"font.*not found", re.IGNORECASE),
    re.compile(r"libfontconfig", re.IGNORECASE),
)

_SIGNAL_PREFIXES = ("WARNING:", "ERROR:")


def parse_stderr(stderr: str) -> ValidationReport:
    """Return a ValidationReport derived from one OpenSCAD invocation's stderr."""
    warnings: list[str] = []
    for raw in stderr.splitlines():
        line = raw.strip()
        if not line.startswith(_SIGNAL_PREFIXES):
            continue
        if any(p.search(line) for p in _NOISE_PATTERNS):
            continue
        warnings.append(line)
    return ValidationReport(warnings=warnings)
