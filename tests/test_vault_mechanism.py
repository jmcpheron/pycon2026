"""Tests for the detailed build123d mechanism animation.

This module tests ``src/vault/mechanism.py`` — the heavyweight pipeline
that renders ``docs/vault/assets/vault-hero.gif`` via build123d +
bd_warehouse + OpenSCAD + Pillow. Skips cleanly when any of those
aren't available, mirroring ``tests/test_cardlab.py``'s discipline.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

# Hard dependencies — skip the whole module if either is missing.
pytest.importorskip("build123d")
pytest.importorskip("bd_warehouse")
pytest.importorskip("PIL")


def test_constants_consistent() -> None:
    """Mechanism constants in vault.py must be internally consistent."""
    from vault import vault as V

    # Ring teeth must be divisible by pin count so the spur gears land at
    # symmetric tooth boundaries (5 teeth per spur centre at 60:12).
    assert V.MECH_RING_GEAR_TEETH % V.PIN_COUNT == 0

    # Gear ratio ring:spur must be 5:1 — same as Adam's actual 120:24.
    assert V.MECH_RING_GEAR_TEETH // V.MECH_SPUR_GEAR_TEETH == 5

    # Spur gear teeth are derived from the BCD geometry:
    # ring_pitch_r = module * ring_teeth / 2
    # spur_pitch_r = BCD/2 - ring_pitch_r
    # spur_teeth   = 2 * spur_pitch_r / module
    ring_pitch_r = V.MECH_GEAR_MODULE_MM * V.MECH_RING_GEAR_TEETH / 2
    spur_pitch_r = V.MECH_SPUR_GEAR_BCD_MM / 2 - ring_pitch_r
    derived_teeth = round(2 * spur_pitch_r / V.MECH_GEAR_MODULE_MM)
    assert derived_teeth == V.MECH_SPUR_GEAR_TEETH


def test_module_exposes_build_signature() -> None:
    """The module must expose ``SLUG`` and ``build(out_dir, ...)`` so the
    CLI dispatch matches every other vault module."""
    from vault import mechanism

    assert mechanism.SLUG == "mechanism"
    assert callable(mechanism.build)


def test_lock_cycle_endpoints() -> None:
    """The lock cycle must start and end at 0 (fully retracted) and hit 1
    (fully extended) at the holding plateau."""
    from vault.mechanism import _lock_cycle

    assert _lock_cycle(0.0) == pytest.approx(0.0)
    assert _lock_cycle(0.4) == pytest.approx(1.0)
    assert _lock_cycle(0.6) == pytest.approx(1.0)
    assert _lock_cycle(1.0) == pytest.approx(0.0)


def test_pin_count_drives_instance_count() -> None:
    """Editing ``PIN_COUNT`` must change the rendered instance count
    without code changes in mechanism.py — verified at the SCAD-shim
    layer (cheaper than a full render)."""
    from vault import vault as V
    from vault.mechanism import _frame_scad

    scad = _frame_scad(
        door_stl="door.stl", ring_stl="ring.stl",
        spur_stl="spur.stl", rack_stl="rack.stl", pin_stl="pin.stl",
        theta_deg=5.0, pin_extension_mm=4.0,
    )
    # 1 door + 1 ring + N spurs + N racks + N pins = 2 + 3·N
    expected_imports = 2 + 3 * V.PIN_COUNT
    assert scad.count("import(") == expected_imports


def test_build_smoke(tmp_path: Path) -> None:
    """End-to-end smoke test: build a 2-frame GIF and confirm it lands.

    Requires OpenSCAD on PATH — skipped otherwise. Frame count is kept
    tiny so CI completes fast; we only assert that the pipeline runs
    end-to-end, not that pixels look right.
    """
    if shutil.which("openscad") is None:
        pytest.skip("openscad not on PATH — needed for PNG rendering")

    from vault.mechanism import build

    gif = build(tmp_path, frames=2, hold=0)
    assert gif.exists()
    assert gif.name == "vault-hero.gif"
    assert gif.stat().st_size > 1000
