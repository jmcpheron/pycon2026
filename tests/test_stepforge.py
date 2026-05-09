"""Tests for stepforge — STEP I/O, inspection, and assembly composition.

All tests skip cleanly when the optional ``step`` extra (build123d / OCP)
isn't installed, so they don't break the badgeforge-only ``ci.yml`` matrix.
"""

from __future__ import annotations

from pathlib import Path

import pytest

build123d = pytest.importorskip("build123d")


def _write_box_step(path: Path, x: float = 10, y: float = 10, z: float = 10) -> Path:
    from build123d.exporters3d import export_step

    box = build123d.Box(x, y, z)
    box.label = "test-box"
    export_step(box, str(path))
    return path


def test_synthetic_roundtrip(tmp_path: Path) -> None:
    """import_step → bbox should match the box we wrote."""
    from stepforge.inspect import inspect_step, parse_header

    src = _write_box_step(tmp_path / "box.step")

    header = parse_header(src)
    assert "AP" in header.schema or "AUTOMOTIVE" in header.schema or header.schema

    report = inspect_step(src)
    assert "Bounding box" in report
    assert "10.00" in report  # box is 10mm on a side
    assert "Solids: 1" in report


def test_tessellate_box_triangle_count(tmp_path: Path) -> None:
    """A box has 12 triangles regardless of deflection."""
    from stepforge.build import build
    from stepforge.inspect import _stl_triangle_count

    src = _write_box_step(tmp_path / "box.step")
    out = tmp_path / "box.stl"
    build(input_path=src, out=out)

    assert _stl_triangle_count(out) == 12


def test_assemble_manifest(tmp_path: Path) -> None:
    """Manifest with two parts composes into a Compound with two children."""
    from stepforge.assemble import assemble

    _write_box_step(tmp_path / "a.step", 5, 5, 5)
    _write_box_step(tmp_path / "b.step", 3, 3, 3)

    manifest = tmp_path / "assembly.toml"
    manifest.write_text(
        'name = "test"\n'
        '[[part]]\n'
        'path = "a.step"\n'
        'name = "alpha"\n'
        'xyz  = [0, 0, 0]\n'
        '[[part]]\n'
        'path = "b.step"\n'
        'name = "beta"\n'
        'xyz  = [10, 0, 0]\n'
    )
    out = tmp_path / "combined.step"
    assemble(manifest=manifest, out=out)

    assert out.exists() and out.stat().st_size > 0

    # Round-trip the result and confirm the children landed where we asked.
    from build123d import import_step
    combined = import_step(str(out))
    children = list(combined.children or [])
    assert len(children) == 2

    bbox = combined.bounding_box()
    # alpha (5mm cube centered at 0) + beta (3mm cube centered at +10) span
    # roughly X[-2.5, 11.5]. Loose tolerance — tessellation rounding is fine.
    assert bbox.max.X > 11
    assert bbox.min.X < -2
