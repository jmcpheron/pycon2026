"""Tests for cardlab — STEP I/O, inspection, and assembly composition.

All tests skip cleanly when the optional ``step`` extra (build123d / OCP)
isn't installed, so they don't gate the default ``ci.yml`` matrix.
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
    from cardlab.inspect import inspect_step, parse_header

    src = _write_box_step(tmp_path / "box.step")

    header = parse_header(src)
    assert "AP" in header.schema or "AUTOMOTIVE" in header.schema or header.schema

    report = inspect_step(src)
    assert "Bounding box" in report
    assert "10.00" in report  # box is 10mm on a side
    assert "Solids: 1" in report


def test_tessellate_box_triangle_count(tmp_path: Path) -> None:
    """A box has 12 triangles regardless of deflection."""
    from cardlab.build import build
    from cardlab.inspect import _stl_triangle_count

    src = _write_box_step(tmp_path / "box.step")
    out = tmp_path / "box.stl"
    build(input_path=src, out=out)

    assert _stl_triangle_count(out) == 12


def test_assemble_manifest(tmp_path: Path) -> None:
    """Manifest with two parts composes into a Compound with two children."""
    from cardlab.assemble import assemble

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


def test_glb_via_cascadio_preserves_geometry(tmp_path: Path) -> None:
    """GLB built via cascadio should round-trip into a trimesh Scene.

    We don't assert non-default colors here because build123d's
    ``export_step`` doesn't emit XCAF color metadata for synthetic boxes,
    so cascadio has nothing to preserve. We assert geometry survives:
    the box loaded out of the GLB has the same volume.
    """
    pytest.importorskip("cascadio")
    trimesh = pytest.importorskip("trimesh")
    from cardlab.build import build

    src = _write_box_step(tmp_path / "box.step", 8, 8, 8)
    out = tmp_path / "box.glb"
    build(input_path=src, out=out)
    assert out.exists() and out.stat().st_size > 0

    scene = trimesh.load(str(out), force="scene")
    # cascadio's GLB is in meters; the box was 8mm so its bbox should be
    # ~0.008 across after the m-unit GLB load.
    bbox = scene.bounding_box.extents
    span = max(bbox)
    assert 0.005 < span < 0.012, f"expected ~0.008 m span, got {span}"


def test_inspect_merges_sidecar(tmp_path: Path) -> None:
    """A `<stem>.meta.toml` next to the STEP should appear in inspect output."""
    from cardlab.inspect import inspect_step

    src = _write_box_step(tmp_path / "card.step")
    sidecar = src.with_suffix(".meta.toml")
    sidecar.write_text(
        '[card]\n'
        'title = "Test card"\n'
        'stages = 3\n'
        '[[part]]\n'
        'name = "test-box"\n'
        'teeth = 40\n'
    )
    report = inspect_step(src)
    assert "Sidecar metadata" in report
    assert "Test card" in report
    assert "teeth=40" in report


def test_explode_smoke(tmp_path: Path) -> None:
    """End-to-end smoke: explode on a synthetic 2-box assembly STEP.

    Verifies: per-part STL/GLB/PNG written, exploded.glb produced,
    manifest.toml has N entries with the expected slugs and displacements.
    Skips the GIF step (--no-gif equivalent) to avoid the OpenSCAD
    runtime cost — covered separately by the local e2e run.
    """
    pytest.importorskip("cascadio")
    pytest.importorskip("trimesh")
    import shutil
    if shutil.which("openscad") is None:
        pytest.skip("openscad not on PATH — explode smoke needs it for PNGs")

    from cardlab.assemble import assemble
    from cardlab.explode import explode

    _write_box_step(tmp_path / "a.step", 8, 8, 4)
    _write_box_step(tmp_path / "b.step", 6, 6, 4)
    manifest = tmp_path / "assembly.toml"
    manifest.write_text(
        '[[part]]\npath = "a.step"\nname = "alpha"\nxyz = [0, 0, 0]\n'
        '[[part]]\npath = "b.step"\nname = "beta"\nxyz = [15, 0, 0]\n'
    )
    src = tmp_path / "combined.step"
    assemble(manifest=manifest, out=src)

    out_dir = tmp_path / "out"
    result = explode(
        input_path=src, out_dir=out_dir, strategy="radial",
        frames=4, gif=False, size="320x240",
    )
    assert len(result.parts) >= 2
    assert result.assembly_glb.exists()
    assert result.exploded_glb.exists()
    assert result.manifest_path.exists()
    for p in result.parts:
        assert p.stl_path.exists()
        assert p.glb_path.exists()
        assert p.png_path.exists()
        # Radial strategy must produce a non-zero displacement.
        assert any(abs(v) > 0.001 for v in p.displacement)
