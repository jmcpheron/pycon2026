"""Tests for the vault-door mechanism study.

The geometry tests have no drawsvg dependency and always run. The build
tests skip cleanly when the ``vault`` extra isn't installed, mirroring the
pattern from ``tests/test_explainers.py``.
"""

from __future__ import annotations

from math import pi, radians
from pathlib import Path

import pytest

from vault import vault as V
from vault.geometry import (
    angle_step,
    divisors,
    opposite_partner_index,
    pin_angles,
    polar_to_cartesian,
)


# ---------------------------------------------------------------------------
# Constants and pure-math helpers — no drawsvg required.
# ---------------------------------------------------------------------------

def test_vault_constants_consistent() -> None:
    """Derived constants in vault.py must match their formulae."""
    assert V.ANGLE_STEP_DEG == pytest.approx(360.0 / V.PIN_COUNT)
    assert V.PIN_CIRCUMFERENCE_MM == pytest.approx(2 * pi * V.PIN_RADIUS_MM)
    assert V.ARC_PER_STEP_MM == pytest.approx(V.PIN_CIRCUMFERENCE_MM / V.PIN_COUNT)
    assert V.ARC_AT_10DEG_MM == pytest.approx(
        V.PIN_RADIUS_MM * radians(V.CAM_ROTATION_DEG)
    )
    # Rack-and-pinion packing constraint:
    assert V.RACK_BUDGET_PER_PIN_MM == pytest.approx(
        2 * pi * V.CENTRAL_PINION_RADIUS_MM / V.PIN_COUNT
    )
    assert V.MAX_RACK_TANGENTIAL_THICKNESS_MM == pytest.approx(
        V.RACK_BUDGET_PER_PIN_MM - V.CLEARANCE_MM
    )
    # Sanity: must be positive — otherwise the pin count exceeds what the
    # pinion can physically accommodate.
    assert V.MAX_RACK_TANGENTIAL_THICKNESS_MM > 0


def test_angle_step() -> None:
    assert angle_step(12) == 30.0
    assert angle_step(24) == 15.0
    assert angle_step(13) == pytest.approx(360.0 / 13)


def test_angle_step_invalid() -> None:
    with pytest.raises(ValueError):
        angle_step(0)
    with pytest.raises(ValueError):
        angle_step(-3)


def test_pin_angles_length() -> None:
    for n in (3, 8, 12, 13, 24):
        assert len(pin_angles(n)) == n


def test_pin_angles_evenly_spaced() -> None:
    for n in (6, 8, 12, 13, 24):
        angles = pin_angles(n)
        step = angle_step(n)
        for prev, curr in zip(angles, angles[1:]):
            assert (curr - prev) == pytest.approx(step)


def test_pin_angles_start_default_is_top() -> None:
    assert pin_angles(12)[0] == -90.0


def test_polar_to_cartesian_known_points() -> None:
    # Right of centre.
    x, y = polar_to_cartesian(0, 0, 1, 0)
    assert x == pytest.approx(1.0)
    assert y == pytest.approx(0.0)
    # Top of circle (SVG y-down).
    x, y = polar_to_cartesian(0, 0, 1, -90)
    assert x == pytest.approx(0.0)
    assert y == pytest.approx(-1.0)
    # Offset centre.
    x, y = polar_to_cartesian(10, 20, 5, 0)
    assert x == pytest.approx(15.0)
    assert y == pytest.approx(20.0)


def test_opposite_partner_even() -> None:
    assert opposite_partner_index(0, 12) == 6
    assert opposite_partner_index(5, 12) == 11
    assert opposite_partner_index(11, 12) == 5
    assert opposite_partner_index(0, 8) == 4
    assert opposite_partner_index(0, 24) == 12


def test_opposite_partner_odd_is_none() -> None:
    assert opposite_partner_index(0, 13) is None
    assert opposite_partner_index(6, 13) is None
    assert opposite_partner_index(12, 13) is None
    assert opposite_partner_index(0, 7) is None


def test_opposite_partner_invalid() -> None:
    with pytest.raises(ValueError):
        opposite_partner_index(0, 0)
    with pytest.raises(ValueError):
        opposite_partner_index(12, 12)
    with pytest.raises(ValueError):
        opposite_partner_index(-1, 12)


def test_divisors() -> None:
    assert divisors(1) == [1]
    assert divisors(12) == [1, 2, 3, 4, 6, 12]
    assert divisors(13) == [1, 13]
    assert divisors(24) == [1, 2, 3, 4, 6, 8, 12, 24]
    assert divisors(36) == [1, 2, 3, 4, 6, 9, 12, 18, 36]


def test_divisors_invalid() -> None:
    with pytest.raises(ValueError):
        divisors(0)
    with pytest.raises(ValueError):
        divisors(-7)


# ---------------------------------------------------------------------------
# Build tests — require drawsvg (the ``vault`` extra).
# ---------------------------------------------------------------------------

pytest.importorskip("drawsvg")

from vault.cli import VAULT_TOPICS  # noqa: E402


@pytest.mark.parametrize("name", VAULT_TOPICS)
def test_each_vault_topic_builds(name: str, tmp_path: Path) -> None:
    """Every registered vault topic must build without error."""
    import importlib

    module = importlib.import_module(f"vault.{name}")
    md_path = module.build(tmp_path)
    assert md_path.exists(), f"{name}: no markdown produced"
    assert md_path.stat().st_size > 200, f"{name}: markdown is suspiciously short"

    # onshape_workflow is intentionally text-only; every other topic
    # must produce at least one SVG named after its slug.
    if name != "onshape_workflow":
        assets = tmp_path / "assets"
        assert assets.exists(), f"{name}: no assets directory"
        svg_count = len(list(assets.glob(f"{module.SLUG}-*.svg")))
        assert svg_count >= 1, f"{name}: no SVG assets generated"


def test_index_builds(tmp_path: Path) -> None:
    """The vault README.md landing page must build and link the topics."""
    from vault.index import build_index

    readme = build_index(tmp_path)
    assert readme.exists()
    assert readme.name == "README.md"
    text = readme.read_text()
    for topic_slug in (
        "symmetry.md",
        "thirteen-pin-problem.md",
        "pin-counts.md",
        "motion-and-travel.md",
        "onshape-workflow.md",
    ):
        assert topic_slug in text, f"README.md doesn't link {topic_slug}"

    # The README leads with the animated hero — verify it exists.
    hero = tmp_path / "assets" / "vault-hero-animated.svg"
    assert hero.exists(), "README build did not emit the animated hero SVG"
    assert hero.stat().st_size > 1000

    # CTA to the live interactive explorer must be present.
    assert "pin-explorer.html" in text
    # Maker-story open: the first-person observation should be there.
    assert "Adam Savage" in text


def test_animated_hero_has_smil() -> None:
    """The hero SVG must contain SMIL <animateTransform> elements — one
    rotate (cam) and N translate (pins). Mirrors the discipline of
    test_animated_hero_speeds_compound_correctly in test_explainers.py.
    """
    import xml.etree.ElementTree as ET
    from vault.svg_draw import draw_animated_hero
    from vault import vault as V

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        hero = draw_animated_hero(Path(td) / "hero.svg")
        ns = "{http://www.w3.org/2000/svg}"
        root = ET.parse(hero).getroot()
        transforms = root.findall(f".//{ns}animateTransform")
        rotates = [t for t in transforms if t.attrib.get("type") == "rotate"]
        translates = [t for t in transforms if t.attrib.get("type") == "translate"]
        assert len(rotates) == 1, (
            f"expected exactly 1 cam-rotate animateTransform, got {len(rotates)}"
        )
        assert len(translates) == V.PIN_COUNT, (
            f"expected {V.PIN_COUNT} pin-translate animateTransforms, "
            f"got {len(translates)}"
        )
        # All animations should loop indefinitely.
        for t in transforms:
            assert t.attrib.get("repeatCount") == "indefinite"


def test_animated_comparison_has_smil() -> None:
    """The 12/13/24 comparison SVG must contain three cam rotations and
    one pin-translate per pin across all three panels.
    """
    import xml.etree.ElementTree as ET
    from vault.svg_draw import draw_animated_comparison
    from vault import vault as V

    import tempfile
    with tempfile.TemporaryDirectory() as td:
        svg = draw_animated_comparison(Path(td) / "cmp.svg")
        ns = "{http://www.w3.org/2000/svg}"
        root = ET.parse(svg).getroot()
        transforms = root.findall(f".//{ns}animateTransform")
        rotates = [t for t in transforms if t.attrib.get("type") == "rotate"]
        translates = [t for t in transforms if t.attrib.get("type") == "translate"]
        assert len(rotates) == 3, (
            f"expected 3 cam-rotate animateTransforms (one per panel), "
            f"got {len(rotates)}"
        )
        expected_pins = V.PIN_COUNT + V.PRIME_PIN_COUNT + V.FRIENDLY_PIN_COUNT
        assert len(translates) == expected_pins, (
            f"expected {expected_pins} pin-translate animateTransforms "
            f"({V.PIN_COUNT}+{V.PRIME_PIN_COUNT}+{V.FRIENDLY_PIN_COUNT}), "
            f"got {len(translates)}"
        )
        # All animations share the same loop and run indefinitely.
        durs = {t.attrib.get("dur") for t in transforms}
        assert len(durs) == 1, f"animations have mismatched durations: {durs}"
        for t in transforms:
            assert t.attrib.get("repeatCount") == "indefinite"


def test_pin_explorer_html_exists() -> None:
    """The hand-written interactive explorer must be present and wired.

    Checks structure rather than implementation: required IDs, the
    geometry helpers that drive the live updates, and the link back
    into the docs.
    """
    explorer = Path(__file__).resolve().parents[1] / "docs" / "vault" / "pin-explorer.html"
    assert explorer.exists(), "docs/vault/pin-explorer.html is missing"
    html = explorer.read_text()

    # Slider + output + readout fields the JS depends on.
    for needle in (
        'id="pin-count"',
        'id="pin-count-out"',
        'id="angle-step"',
        'id="divisors"',
        'id="pair-count"',
        'id="rack-budget"',
        'id="verdict"',
        'id="vault-svg"',
    ):
        assert needle in html, f"explorer is missing {needle}"

    # Geometry helpers — these must stay in sync with src/vault/geometry.py.
    for fn in ("function angleStep", "function pinAngles",
               "function polar", "function divisors", "function rackBudgetMm"):
        assert fn in html, f"explorer is missing geometry helper {fn!r}"

    # Style integration with the rest of the site.
    assert 'href="../assets/styles.css"' in html
    # Navigation back into the study.
    assert 'href="README.md"' in html


def test_no_drift_between_sections(tmp_path: Path) -> None:
    """Vault constants should appear textually in every topic markdown that
    discusses them.

    Catches the bug where a topic hard-codes a pin count (e.g. ``"12"``)
    instead of importing from ``vault.py``. The set of needles is scoped
    per-page because not every page compares all three pin counts —
    e.g. ``motion-and-travel.md`` is about ``arc = r·θ`` for one radius
    and one rotation, not a pin-count comparison.
    """
    import importlib

    # Pages that compare pin counts must show all three: PIN_COUNT,
    # PRIME_PIN_COUNT, FRIENDLY_PIN_COUNT. Motion-and-travel is scoped to
    # the geometry constants it actually uses.
    needles_per_topic = {
        "symmetry": (
            str(V.PIN_COUNT),
            str(V.PRIME_PIN_COUNT),
            str(V.FRIENDLY_PIN_COUNT),
        ),
        "thirteen_pin": (
            str(V.PIN_COUNT),
            str(V.PRIME_PIN_COUNT),
            str(V.FRIENDLY_PIN_COUNT),
        ),
        "pin_counts": (
            str(V.PIN_COUNT),
            str(V.PRIME_PIN_COUNT),
            str(V.FRIENDLY_PIN_COUNT),
            # Rack-packing note must reference the central pinion radius.
            f"{V.CENTRAL_PINION_RADIUS_MM:g}",
        ),
        "motion": (
            str(int(V.PIN_RADIUS_MM)),
            f"{V.CAM_ROTATION_DEG:g}",
        ),
        "onshape_workflow": (
            str(V.PIN_COUNT),
            str(V.PRIME_PIN_COUNT),
            str(V.FRIENDLY_PIN_COUNT),
            str(int(V.DOOR_DIAMETER_MM)),
        ),
    }

    # Also enforce no-drift on the README — it mentions multiple
    # source-of-truth values in its parameters block.
    from vault.index import build_index
    readme_text = build_index(tmp_path).read_text()
    for needle in (
        str(V.PIN_COUNT),
        str(V.PRIME_PIN_COUNT),
        str(V.FRIENDLY_PIN_COUNT),
        f"{V.CENTRAL_PINION_RADIUS_MM:g}",
        str(int(V.DOOR_DIAMETER_MM)),
        str(int(V.PIN_RADIUS_MM)),
        f"{V.CAM_ROTATION_DEG:g}",
    ):
        assert needle in readme_text, (
            f"README.md: expected {needle!r} (a vault.py-derived value) "
            f"somewhere in the rendered landing page"
        )

    for name in VAULT_TOPICS:
        module = importlib.import_module(f"vault.{name}")
        md_path = module.build(tmp_path)
        text = md_path.read_text()
        for needle in needles_per_topic[name]:
            assert needle in text, (
                f"{name}: expected {needle!r} (a vault.py-derived value) "
                f"somewhere in the rendered markdown"
            )


def test_door_geometry_in_appropriate_pages(tmp_path: Path) -> None:
    """The door / radius / cam-rotation constants must appear where they matter."""
    import importlib

    # motion-and-travel must mention pin radius + cam rotation
    mod = importlib.import_module("vault.motion")
    text = mod.build(tmp_path).read_text()
    assert str(int(V.PIN_RADIUS_MM)) in text
    assert f"{V.CAM_ROTATION_DEG:g}" in text

    # onshape-workflow must mention door diameter
    mod = importlib.import_module("vault.onshape_workflow")
    text = mod.build(tmp_path).read_text()
    assert str(int(V.DOOR_DIAMETER_MM)) in text
    assert str(int(V.PIN_RADIUS_MM)) in text
