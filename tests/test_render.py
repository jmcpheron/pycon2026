"""Render smoke test — does OpenSCAD actually produce non-empty PNG/STL on this machine?

This test does not need an Anthropic API key — it only exercises the OpenSCAD
subprocess wrapper, which is the highest-risk piece of scadia (headless
rendering on macOS has historically been brittle).
"""

from pathlib import Path

from scadia.render import scad_to_png, scad_to_stl


CUBE = "cube([20, 20, 20], center=true);"


def test_scad_to_png(tmp_path: Path) -> None:
    out = tmp_path / "cube.png"
    result = scad_to_png(CUBE, out)
    assert result.output == out
    assert out.exists()
    assert out.stat().st_size > 1000  # a real PNG, not a 0-byte stub


def test_scad_to_stl(tmp_path: Path) -> None:
    out = tmp_path / "cube.stl"
    result = scad_to_stl(CUBE, out)
    assert result.output == out
    assert out.exists()
    assert out.stat().st_size > 100
