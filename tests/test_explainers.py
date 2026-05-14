"""Tests for the engineering explainers.

Skip cleanly when the optional ``explainers`` extra (drawsvg / matplotlib)
isn't installed, so the badge-only ci.yml matrix doesn't break.
"""

from __future__ import annotations

from pathlib import Path

import pytest

# Skip the whole module if drawsvg / matplotlib aren't installed.
pytest.importorskip("drawsvg")
pytest.importorskip("matplotlib")

from explainers import card  # noqa: E402
from explainers.cli import EXPLAINERS  # noqa: E402


def test_card_constants_consistent() -> None:
    """The derived constants in card.py must match their formulae."""
    assert card.PITCH_DIA_BIG == card.MODULE_MM * card.BIG_TEETH
    assert card.PITCH_DIA_PINION == card.MODULE_MM * card.PINION_TEETH
    assert card.CENTER_DISTANCE_MM == (card.PITCH_DIA_BIG
                                       + card.PITCH_DIA_PINION) / 2
    assert card.RATIO_PER_STAGE == card.BIG_TEETH / card.PINION_TEETH
    assert card.TOTAL_RATIO == card.RATIO_PER_STAGE ** (card.N_STAGES - 1)


@pytest.mark.parametrize("name", EXPLAINERS)
def test_each_explainer_builds(name: str, tmp_path: Path) -> None:
    """Every registered explainer module must build without error."""
    import importlib

    module = importlib.import_module(f"explainers.{name}")
    md_path = module.build(tmp_path)
    assert md_path.exists(), f"{name}: no markdown produced"
    assert md_path.stat().st_size > 100, f"{name}: markdown is suspiciously short"

    assets = tmp_path / "assets"
    assert assets.exists(), f"{name}: no assets directory"
    svg_count = len(list(assets.glob(f"{module.SLUG}-*.svg")))
    assert svg_count >= 1, f"{name}: no SVG assets generated"


def test_animated_hero_speeds_compound_correctly(tmp_path: Path) -> None:
    """The animated gear-chain hero's SMIL durations must scale by the
    canonical RATIO_PER_STAGE between adjacent gears, and directions must
    alternate — or the rendered chain stops matching the gear math.
    """
    import re
    import xml.etree.ElementTree as ET

    from explainers.ratios import build, BASE_PERIOD_S

    build(tmp_path)
    svg_path = tmp_path / "assets" / "gear-ratios-animated.svg"
    assert svg_path.exists(), "animated hero SVG was not produced"

    ns = "{http://www.w3.org/2000/svg}"
    tree = ET.parse(svg_path)
    transforms = tree.getroot().findall(f".//{ns}animateTransform")
    assert len(transforms) == card.N_STAGES, (
        f"expected {card.N_STAGES} animateTransform elements (one per gear), "
        f"got {len(transforms)}"
    )

    # Durations: BASE_PERIOD_S × RATIO_PER_STAGE**i for i in 0..N-1.
    for i, t in enumerate(transforms):
        dur = t.attrib["dur"]
        m = re.fullmatch(r"([\d.]+)s", dur)
        assert m, f"gear {i + 1}: unparseable dur={dur!r}"
        expected = BASE_PERIOD_S * (card.RATIO_PER_STAGE ** i)
        assert float(m.group(1)) == pytest.approx(expected), (
            f"gear {i + 1}: dur {dur} != expected {expected}s"
        )

    # Direction reversal at each mesh — to-angle sign alternates.
    for i, t in enumerate(transforms):
        to_angle = float(t.attrib["to"].split()[0])
        expected_sign = 1 if i % 2 == 0 else -1
        assert (to_angle > 0) == (expected_sign > 0), (
            f"gear {i + 1}: rotation direction wrong (to={to_angle})"
        )


def test_no_drift_between_sections(tmp_path: Path) -> None:
    """The numbers in card.py should appear textually in every explainer.

    Catches the bug where an explainer hard-codes a number (e.g. 40 teeth)
    instead of pulling it from card.py — that hardcoded value would persist
    if card.py changed.
    """
    import importlib

    expected_strings = (
        str(card.BIG_TEETH),         # "40"
        str(card.PINION_TEETH),      # "10"
        f"{card.MODULE_MM}",         # "0.6"
    )

    for name in EXPLAINERS:
        module = importlib.import_module(f"explainers.{name}")
        md_path = module.build(tmp_path)
        text = md_path.read_text()
        for needle in expected_strings:
            assert needle in text, (
                f"{name}: expected to find {needle!r} (a card.py-derived "
                f"value) somewhere in the rendered markdown"
            )
