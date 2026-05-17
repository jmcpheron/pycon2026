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


def test_spin_part_construction() -> None:
    """The build123d + bd_warehouse compound gear / axle / plate must
    construct, union cleanly, and have plausible bboxes for the card's
    canonical module 0.6 mm geometry."""
    pytest.importorskip("bd_warehouse")
    from cardlab import spin
    from explainers import card as C

    compound = spin._build_compound_gear()
    axle = spin._build_axle_post()
    plate = spin._build_card_plate()

    # Compound bbox: footprint == big gear's outer dia ≈ 25.2 mm; height
    # spans big disc + layer gap + pinion ≈ 2.3 mm.
    cbb = compound.bounding_box()
    assert cbb.size.X == pytest.approx(C.OUTER_DIA_BIG, abs=0.5)
    assert cbb.size.Z == pytest.approx(
        2 * C.GEAR_THICKNESS_MM + C.LAYER_GAP_MM, abs=0.1
    )

    # Plate: full card outline.
    pbb = plate.bounding_box()
    assert pbb.size.X == pytest.approx(C.CARD_WIDTH_MM)
    assert pbb.size.Y == pytest.approx(C.CARD_HEIGHT_MM)

    # Axle: matches POST_DIAMETER_MM.
    abb = axle.bounding_box()
    assert abb.size.X == pytest.approx(C.POST_DIAMETER_MM)


def test_spin_rotation_cascade() -> None:
    """Each stage must rotate at 1 / RATIO_PER_STAGE the rate of the
    previous, with alternating direction. Verifies the 256:1 story at
    the math layer (cheaper than a full render)."""
    from cardlab.spin import _gear_rotation_deg
    from explainers import card as C

    t = 1.0  # full loop
    input_turns = 4.0
    rotations = [_gear_rotation_deg(k, t, input_turns) for k in range(C.N_STAGES)]

    # Stage 0 is the input: +360° × input_turns.
    assert rotations[0] == pytest.approx(input_turns * 360.0)

    # Each subsequent stage: magnitude divided by RATIO_PER_STAGE,
    # direction flipped.
    for k in range(1, C.N_STAGES):
        expected = -rotations[k - 1] / C.RATIO_PER_STAGE
        assert rotations[k] == pytest.approx(expected)

    # Total reduction at the output: 256:1 at the canonical 4 stages of
    # mesh — verifies the headline number stays true.
    expected_output = (
        rotations[0] / (C.RATIO_PER_STAGE ** (C.N_STAGES - 1))
        * (1 if (C.N_STAGES - 1) % 2 == 0 else -1)
    )
    assert rotations[-1] == pytest.approx(expected_output)


def test_spin_frame_scad_shape() -> None:
    """Each frame's SCAD shim should import (N+1) gear parts plus the
    plate plus N axles — one per stage — and contain a rotation per
    gear instance.

    Cheap check: ``_frame_scad`` is pure-text generation, no OpenSCAD
    invocation needed.
    """
    from cardlab.spin import _frame_scad
    from explainers import card as C

    scad = _frame_scad(
        compound_stl="compound.stl",
        axle_stl="axle.stl",
        plate_stl="plate.stl",
        t=0.5,
        input_turns=4.0,
    )
    # 1 plate + N axles + N compound gears = 1 + 2·N imports.
    assert scad.count("import(") == 1 + 2 * C.N_STAGES
    # One rotate per compound-gear instance.
    assert scad.count("rotate(") == C.N_STAGES
    # Plate (white) + each axle + each compound gear all get color() wrappers:
    # 1 (plate) + N (axles) + N (gears) = 2·N + 1.
    assert scad.count("color(") == 2 * C.N_STAGES + 1
    # And the per-stage palette must actually have one entry per stage so
    # we don't silently wrap around past the input gear.
    from cardlab.spin import STAGE_COLORS
    assert len(STAGE_COLORS) >= C.N_STAGES


def test_spin_smoke(tmp_path: Path) -> None:
    """End-to-end smoke: build a 2-frame spin GIF pair and confirm both land.

    Requires OpenSCAD on PATH — skipped otherwise. Mirrors
    ``test_explode_smoke``.
    """
    pytest.importorskip("bd_warehouse")
    import shutil
    if shutil.which("openscad") is None:
        pytest.skip("openscad not on PATH — needed for PNG rendering")

    from cardlab.spin import spin

    iso_gif, side_gif = spin(tmp_path, frames=2, input_turns=4.0)
    assert iso_gif.exists() and side_gif.exists()
    assert iso_gif.name == "spin-iso.gif"
    assert side_gif.name == "spin-side.gif"
    assert iso_gif.stat().st_size > 1000
    assert side_gif.stat().st_size > 1000


def test_assign_part_colors_card_layered() -> None:
    """Gears get the STAGE_COLORS palette in X-rank order; card halves
    (bbox X > threshold) stay uncolored so the default Cornfield yellow
    keeps reading as the card body. Pure-logic test — no build123d /
    cascadio / openscad needed."""
    from cardlab.explode import (
        CARD_PART_X_THRESHOLD_MM,
        ExplodedPart,
        _assign_part_colors,
    )
    from cardlab.palette import STAGE_COLORS, scad_color

    def make(slug: str, cx: float, x_span: float) -> ExplodedPart:
        return ExplodedPart(
            label=slug, slug=slug, centroid=(cx, 0.0, 0.0),
            bbox_size=(x_span, 10.0, 10.0), color_rgba=None,
            stl_path=Path(f"{slug}.stl"),
            glb_path=Path(f"{slug}.glb"),
            png_path=Path(f"{slug}.png"),
        )

    card_top = make("card_top", 0.0, CARD_PART_X_THRESHOLD_MM + 30.0)
    card_bot = make("card_bot", 0.0, CARD_PART_X_THRESHOLD_MM + 30.0)
    # Gears intentionally out of X order to exercise the sort.
    g2 = make("g2", 0.0, 25.0)
    g0 = make("g0", -30.0, 25.0)
    g4 = make("g4", 30.0, 25.0)
    g1 = make("g1", -15.0, 25.0)
    g3 = make("g3", 15.0, 25.0)

    colors = _assign_part_colors([card_top, g2, g0, g4, g1, g3, card_bot])

    # Card halves: not in the color map → render default Cornfield yellow.
    assert "card_top" not in colors
    assert "card_bot" not in colors
    # Gears: leftmost gets STAGE_COLORS[0], rightmost STAGE_COLORS[4].
    assert colors["g0"] == scad_color(STAGE_COLORS[0])
    assert colors["g1"] == scad_color(STAGE_COLORS[1])
    assert colors["g2"] == scad_color(STAGE_COLORS[2])
    assert colors["g3"] == scad_color(STAGE_COLORS[3])
    assert colors["g4"] == scad_color(STAGE_COLORS[4])


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
