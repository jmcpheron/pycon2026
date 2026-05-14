"""STEP file inspection — header metadata + assembly tree + bbox + tri count."""

from __future__ import annotations

import re
import struct
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path

# The HEADER section of a STEP file is plain text and almost always under
# a few KB. Parsing it with regex is faster, simpler, and dependency-free
# compared to spinning up the OCCT XCAF stack just to read the schema name.
_HEADER_FIELD_RE = re.compile(r"FILE_(NAME|SCHEMA|DESCRIPTION)\s*\(([^;]*)\);", re.S)


@dataclass(frozen=True)
class StepHeader:
    schema: str
    originating: str
    author: str
    timestamp: str
    description: str


def parse_header(path: Path) -> StepHeader:
    """Read just the HEADER section of a STEP file (text, top of file)."""
    with path.open("r", encoding="utf-8", errors="replace") as f:
        text = []
        for line in f:
            text.append(line)
            if line.strip().startswith("ENDSEC") and len(text) > 5:
                break
        head = "".join(text)

    fields: dict[str, str] = {}
    for match in _HEADER_FIELD_RE.finditer(head):
        fields[match.group(1)] = match.group(2)

    def _strs(blob: str) -> list[str]:
        return [s.strip() for s in re.findall(r"'([^']*)'", blob)]

    schema_strs = _strs(fields.get("SCHEMA", ""))
    name_strs = _strs(fields.get("NAME", ""))
    desc_strs = _strs(fields.get("DESCRIPTION", ""))

    # FILE_NAME positional layout: name, time_stamp, author, organization,
    # preprocessor_version, originating_system, authorisation.
    return StepHeader(
        schema=schema_strs[0] if schema_strs else "(unknown)",
        originating=name_strs[5] if len(name_strs) > 5 else "(unknown)",
        author=name_strs[2] if len(name_strs) > 2 else "",
        timestamp=name_strs[1] if len(name_strs) > 1 else "",
        description=desc_strs[0] if desc_strs else "",
    )


def _stl_triangle_count(stl_path: Path) -> int:
    """Read the 4-byte triangle count from a binary STL header (offset 80)."""
    with stl_path.open("rb") as f:
        f.seek(80)
        return struct.unpack("<I", f.read(4))[0]


def _walk_tree(node, depth: int, lines: list[str], is_last: bool, prefix: str) -> None:
    """Recursively format a build123d Compound/Part as a unicode tree."""
    label = getattr(node, "label", "") or "<unnamed>"
    kind = type(node).__name__
    loc = getattr(node, "location", None)
    if loc is not None:
        try:
            x, y, z = loc.position.X, loc.position.Y, loc.position.Z
            loc_str = f"  loc=({x:.2f}, {y:.2f}, {z:.2f})"
        except Exception:
            loc_str = ""
    else:
        loc_str = ""

    branch = "└─" if is_last else "├─"
    if depth == 0:
        lines.append(f"{label} <{kind}>{loc_str}")
        new_prefix = ""
    else:
        lines.append(f"{prefix}{branch} {label} <{kind}>{loc_str}")
        new_prefix = prefix + ("   " if is_last else "│  ")

    children = list(getattr(node, "children", []) or [])
    for i, child in enumerate(children):
        _walk_tree(child, depth + 1, lines, i == len(children) - 1, new_prefix)


def inspect_step(path: Path) -> str:
    """Build the multi-line inspection report (returned, not printed)."""
    from build123d import Compound, import_step

    header = parse_header(path)
    shape: Compound = import_step(str(path))

    bbox = shape.bounding_box()
    bx, by, bz = bbox.size.X, bbox.size.Y, bbox.size.Z
    extents = (
        f"X[{bbox.min.X:.2f}, {bbox.max.X:.2f}]  "
        f"Y[{bbox.min.Y:.2f}, {bbox.max.Y:.2f}]  "
        f"Z[{bbox.min.Z:.2f}, {bbox.max.Z:.2f}]"
    )

    # Count solids / parts at the top level by walking children.
    children = list(shape.children or [])
    solid_count = sum(1 for _ in shape.solids())

    # Tessellate to a tmp STL just to lift the triangle count; binary STL
    # stores the count in 4 bytes, so this is a couple-of-syscalls operation.
    from build123d.exporters3d import export_stl
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        export_stl(
            to_export=shape,
            file_path=str(tmp_path),
            tolerance=0.1,
            angular_tolerance=0.5,
            ascii_format=False,
        )
        tri_count = _stl_triangle_count(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    tree_lines: list[str] = []
    _walk_tree(shape, depth=0, lines=tree_lines, is_last=True, prefix="")

    lines = [
        f"File:          {path}",
        f"Schema:        {header.schema}",
        f"Originating:   {header.originating}",
        f"Timestamp:     {header.timestamp}",
        f"Top-level:     {len(children)} children   Solids: {solid_count}",
        f"Bounding box:  {extents}   "
        f"(size {bx:.2f} × {by:.2f} × {bz:.2f})",
        f"Tessellation:  {tri_count:,} triangles  "
        f"(linear=0.1 mm  angular=0.5 rad)",
        "",
        "Assembly tree:",
        *tree_lines,
    ]

    sidecar_lines = _format_sidecar(path)
    if sidecar_lines:
        lines.extend(["", *sidecar_lines])

    return "\n".join(lines)


def load_sidecar(step_path: Path) -> dict | None:
    """Look for `<stem>.meta.toml` next to the STEP and parse it.

    Returns None if absent. The schema is open-ended; the convention is a
    top-level `[card]` table plus a list of `[[part]]` entries that the
    explode subcommand joins to rendered parts by name.
    """
    sidecar = step_path.with_suffix(".meta.toml")
    if not sidecar.exists():
        return None
    return tomllib.loads(sidecar.read_text())


def _format_sidecar(step_path: Path) -> list[str]:
    """Format the sidecar metadata for inclusion in the inspect report."""
    data = load_sidecar(step_path)
    if data is None:
        return []

    out = ["Sidecar metadata:"]
    card = data.get("card") or {}
    for k, v in card.items():
        out.append(f"  {k}: {v}")

    parts = data.get("part") or []
    if parts:
        out.append(f"  parts: {len(parts)}")
        for p in parts:
            name = p.get("name", "?")
            extras = ", ".join(f"{k}={v}" for k, v in p.items() if k != "name")
            out.append(f"    - {name}  ({extras})" if extras else f"    - {name}")
    return out
