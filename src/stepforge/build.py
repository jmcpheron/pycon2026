"""STEP → STL / GLB conversion via build123d (OCCT) + cascadio for colored GLB."""

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

    out.parent.mkdir(parents=True, exist_ok=True)

    # GLB: route through cascadio when available. It wraps OCCT's
    # RWGltf_CafWriter and preserves XCAF part names + colors in one
    # call, which build123d's export_gltf does not. Fall back to
    # build123d if cascadio isn't installed (older venvs).
    if suffix == ".glb":
        try:
            import cascadio
        except ImportError:
            cascadio = None
        if cascadio is not None:
            cascadio.step_to_glb(
                str(input_path), str(out),
                tol_linear=linear_deflection,
                tol_angular=angular_deflection,
                include_materials=True,
            )
            return out

    # Fallback path: build123d / OCCT. Imported lazily so `stepforge --help`
    # doesn't pay the OCP wheel's ~2 s import cost.
    from build123d import Compound, import_step
    from build123d.exporters3d import export_gltf, export_stl

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
        export_gltf(
            to_export=shape,
            file_path=str(out),
            binary=(suffix == ".glb"),
            linear_deflection=linear_deflection,
            angular_deflection=angular_deflection,
        )

    return out
