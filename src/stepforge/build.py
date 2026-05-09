"""STEP → STL / GLB conversion via build123d (OCCT)."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# OCCT tessellation parameters. These deflections are tight enough that the
# pounce-a-pult comes out smooth in GitHub's STL viewer, loose enough that
# tessellation finishes in a few seconds.
DEFAULT_LINEAR_DEFLECTION = 0.1   # mm — max chord error from the true surface
DEFAULT_ANGULAR_DEFLECTION = 0.5  # rad — max angle between adjacent facets


def build(
    input_path: Path,
    out: Path,
    linear_deflection: float = DEFAULT_LINEAR_DEFLECTION,
    angular_deflection: float = DEFAULT_ANGULAR_DEFLECTION,
    binary: bool = True,
) -> Path:
    """Convert a STEP file to STL or GLB.

    Output format inferred from the ``out`` extension.
    """
    suffix = out.suffix.lower()
    if suffix not in {".stl", ".glb", ".gltf"}:
        raise ValueError(
            f"unsupported output extension {suffix!r}; want .stl, .glb, or .gltf"
        )

    # Imported lazily so `stepforge --help` doesn't pay the OCP wheel's
    # ~2 s import cost when the user is just exploring the CLI.
    from build123d import Compound, import_step
    from build123d.exporters3d import export_gltf, export_stl

    out.parent.mkdir(parents=True, exist_ok=True)

    shape: Compound = import_step(str(input_path))

    if suffix == ".stl":
        export_stl(
            to_export=shape,
            file_path=str(out),
            tolerance=linear_deflection,
            angular_tolerance=angular_deflection,
            ascii_format=not binary,
        )
    else:
        # GLB / glTF — uses OCCT's RWGltf_CafWriter under the hood.
        export_gltf(
            to_export=shape,
            file_path=str(out),
            binary=(suffix == ".glb"),
            linear_deflection=linear_deflection,
            angular_deflection=angular_deflection,
        )

    return out
