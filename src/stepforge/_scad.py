"""Small OpenSCAD utilities shared between stepforge's explode/render paths."""

from __future__ import annotations


class OpenSCADNotFound(RuntimeError):
    pass


def _scad_string(value: str) -> str:
    # OpenSCAD's -D parser accepts a quoted string literal. Escape backslashes
    # and double quotes; everything else passes through as-is.
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'
