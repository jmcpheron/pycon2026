"""Tests for the technical-validation sensor."""

from scadia.validate import parse_stderr


def test_clean_stderr_has_no_warnings() -> None:
    stderr = (
        "Geometries in cache: 1\n"
        "Geometry cache size in bytes: 728\n"
        "Total rendering time: 0:00:00.000\n"
        "   Top level object is a 3D object:\n"
        "   Facets:          6\n"
    )
    report = parse_stderr(stderr)
    assert report.warnings == []
    assert not report.has_warnings


def test_real_warning_is_captured() -> None:
    stderr = (
        "WARNING: Point index 3 is out of bounds (from faces[0][3])\n"
        "Geometries in cache: 1\n"
    )
    report = parse_stderr(stderr)
    assert len(report.warnings) == 1
    assert "Point index 3" in report.warnings[0]
    assert report.has_warnings


def test_ui_noise_is_filtered() -> None:
    stderr = (
        "UI-WARNING: Some Qt-related complaint\n"
        "WARNING: font 'Helvetica' not found, falling back\n"
        "WARNING: Object may not be a valid 2-manifold\n"
    )
    report = parse_stderr(stderr)
    # Only the manifold warning should survive.
    assert len(report.warnings) == 1
    assert "manifold" in report.warnings[0]


def test_error_lines_are_signal_too() -> None:
    stderr = "ERROR: Parser error in file foo.scad, line 42\n"
    report = parse_stderr(stderr)
    assert len(report.warnings) == 1
    assert report.warnings[0].startswith("ERROR:")
