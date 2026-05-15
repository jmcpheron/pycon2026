"""Side-by-side pin-count comparison: 6, 8, 12, 13, 24."""

from __future__ import annotations

from math import pi
from pathlib import Path

from vault import diagrams as D
from vault import style as S
from vault import vault as V
from vault.geometry import angle_step, divisors
from vault.svg_draw import CANVAS, DOOR_R, HUB_R, PIN_R, WHEEL_R, draw_rack_packing


def _rack_budget_mm(n: int) -> float:
    """Per-rack tangential thickness budget for ``n`` racks on the default pinion."""
    return 2 * pi * V.CENTRAL_PINION_RADIUS_MM / n - V.CLEARANCE_MM


SLUG = "pin-counts"


def _grid_svg(out_path: Path) -> Path:
    """Six small layouts in a 3x2 grid for the comparison page."""
    counts = V.COMPARED_PIN_COUNTS  # (6, 8, 12, 13, 24)
    cols = 3
    rows = (len(counts) + cols - 1) // cols
    cell = CANVAS // 2
    pad = 8
    width = cols * cell
    height = rows * cell + 24

    d = D.new_drawing(width, height)
    door_r = cell / 2 - 24
    pin_r = 3
    hub_r = 8
    wheel_r = 11

    for i, n in enumerate(counts):
        row, col = divmod(i, cols)
        cx = col * cell + cell / 2
        cy = row * cell + cell / 2 + 16
        D.door_outline(d, cx, cy, door_r)
        D.cam_wheel(d, cx, cy, wheel_r)
        D.hub(d, cx, cy, hub_r)
        highlight = 0 if n % 2 == 1 else None
        D.pin_circle(d, cx, cy,
                     door_r=door_r - 6, pin_r=pin_r, pin_count=n,
                     highlight_idx=highlight)
        D.title(d, cx, row * cell + 16,
                f"{n} pins  ·  {angle_step(n):.2f}°")
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    d.save_svg(str(out))
    return out


def _divisors_svg(out_path: Path) -> Path:
    """Divisor strips for 12, 13, 24 — visualises 'composite vs. prime'."""
    rows = [(V.PIN_COUNT, divisors(V.PIN_COUNT)),
            (V.PRIME_PIN_COUNT, divisors(V.PRIME_PIN_COUNT)),
            (V.FRIENDLY_PIN_COUNT, divisors(V.FRIENDLY_PIN_COUNT))]
    width = 360
    row_h = 56
    height = row_h * len(rows) + 24

    d = D.new_drawing(width, height)
    label_x = 16
    chip_x0 = 90
    chip_w = 30
    chip_h = 22

    for ri, (n, divs) in enumerate(rows):
        y = 24 + ri * row_h
        # Row label
        import drawsvg as dw
        d.append(dw.Text(f"{n}", S.FONT_SIZE_TITLE,
                         x=label_x, y=y + chip_h - 4,
                         font_family=S.FONT_FAMILY,
                         fill=S.INK, font_weight="bold"))
        # Divisor chips
        is_prime = len(divs) == 2 and divs[0] == 1 and divs[1] == n
        chip_fill = S.ACCENT_FAIL if is_prime else S.GEAR_PINION
        for ci, dv in enumerate(divs):
            cx = chip_x0 + ci * (chip_w + 4)
            d.append(dw.Rectangle(cx, y, chip_w, chip_h,
                                  rx=4, ry=4,
                                  fill=chip_fill, stroke=S.INK,
                                  stroke_width=S.STROKE_THIN))
            d.append(dw.Text(str(dv), S.FONT_SIZE_LABEL,
                             x=cx + chip_w / 2, y=y + chip_h - 6,
                             text_anchor="middle",
                             font_family=S.FONT_FAMILY, fill=S.INK))
        d.append(dw.Text(f"{len(divs)} divisors",
                         S.FONT_SIZE_DIM,
                         x=label_x, y=y + chip_h + 14,
                         font_family=S.FONT_FAMILY, fill=S.INK_MUTED,
                         font_style="italic"))
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    d.save_svg(str(out))
    return out


def build(out_dir: Path) -> Path:
    assets = out_dir / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    grid = _grid_svg(assets / f"{SLUG}-grid.svg")
    div = _divisors_svg(assets / f"{SLUG}-divisors.svg")
    packing = draw_rack_packing(assets / f"{SLUG}-rack-packing.svg")

    md_path = out_dir / f"{SLUG}.md"
    md_path.write_text(f"""# Pin counts — comparing {", ".join(str(n) for n in V.COMPARED_PIN_COUNTS)}

A circular vault door doesn't care what pin count you pick — they all add
up to {V.PIN_COUNT * 30}° eventually. The mechanism around the door cares
a lot.

![small-multiples grid of 6, 8, 12, 13, and 24 pin layouts](assets/{grid.name})

## The comparison table

| Pin Count | Angle Step | Opposing Pairs? | Clean Quadrants? | Notes |
|----------:|----------:|:---------------:|:----------------:|-------|
| 6  | {angle_step(6):.3f}° | yes | no  | hex-like; only 2- and 3-fold symmetry |
| 8  | {angle_step(8):.3f}° | yes | yes | clean diagonal symmetry |
| {V.PIN_COUNT} | {angle_step(V.PIN_COUNT):.3f}° | yes | yes | clock-like, very friendly |
| {V.PRIME_PIN_COUNT} | {angle_step(V.PRIME_PIN_COUNT):.3f}° | **no** | **no** | possible, but awkward |
| {V.FRIENDLY_PIN_COUNT} | {angle_step(V.FRIENDLY_PIN_COUNT):.3f}° | yes | yes | very flexible and divisible |

## Divisors at a glance

![divisor chips for 12, 13, 24](assets/{div.name})

Composite pin counts give the mechanism designer many ways to divide,
mirror, and repeat a design. Prime pin counts (red row) give two: 1, and
the count itself.

That's not a bug in primes — it's the *definition* of prime. It just means
a {V.PRIME_PIN_COUNT}-pin mechanism either uses {V.PRIME_PIN_COUNT}
identical individually-routed actuators, or one custom shape. There's no
elegant middle ground.

## Picking a pin count

If your design doesn't have a strong reason to pick a prime, pick a
composite. {V.PIN_COUNT} is the obvious starting point — it inherits all
the readability of a clock face.

If you want twice the resolution but the same friendliness, jump to
{V.FRIENDLY_PIN_COUNT}.

If you want a conversation piece, pick {V.PRIME_PIN_COUNT} on purpose and
[lean into the constraint](thirteen-pin-problem.md).

## A note from watching Adam Savage's mini vault build

> *Watching Adam Savage machine the pins for his mini vault door build, I
> kept staring at one detail and not getting it: each pin had a section
> of straight gear teeth cut into it, and the **back** of that section —
> the spine, opposite the teeth — was machined surprisingly thin. Way
> more material removed than you'd expect for weight savings. Then I saw
> the parts assembled inside the door and it clicked. He didn't choose
> that shape; the pin count chose it for him.*

The build style is a **rack-and-pinion central drive**: each pin carries
a section of straight gear teeth (a *rack*) along one face, and a single
central pinion gear at the hub meshes with **all N racks at once**. Turn
the handle, the pinion rotates, every pin translates radially in unison.

![the same pinion driving N=6, 12, 24 racks — each rack body shrinks as N grows](assets/{packing.name})

For all N racks to engage the same pinion, they have to share the
perimeter of the pinion's pitch circle. That perimeter is `2π · r`, and
the N rack bodies — each with some tangential thickness `t` — must fit
side-by-side around it without colliding:

```
N · (t + clearance)  ≤  2π · r_pinion
```

Re-arranged, the upper bound on each rack body's tangential thickness is

```
t  ≤  (2π · r_pinion / N)  −  clearance
```

So the central pinion's circumference is a **budget** the N racks split
between them. Halve the pinion radius, halve the budget. Double the pin
count, halve the budget. There is nowhere else for the material to go,
so you machine the spine of every rack thinner until it fits its slice.
The teeth themselves have to stay full-profile to mesh — *the spine is
the only place material can come from.*

For this study's parameters — a central pinion of radius **{V.CENTRAL_PINION_RADIUS_MM:g} mm**
driving **{V.PIN_COUNT}** racks with {V.CLEARANCE_MM:g} mm clearance —
each rack body gets at most **{V.MAX_RACK_TANGENTIAL_THICKNESS_MM:.2f} mm**
of tangential thickness:

| Pin count N | Rack body budget `t ≤ 2π·{V.CENTRAL_PINION_RADIUS_MM:g}/N − {V.CLEARANCE_MM:g}` |
|------------:|-------------------------------------------------------------------:|
| 6  | {_rack_budget_mm(6):.2f} mm |
| 8  | {_rack_budget_mm(8):.2f} mm |
| {V.PIN_COUNT} | {V.MAX_RACK_TANGENTIAL_THICKNESS_MM:.2f} mm |
| {V.PRIME_PIN_COUNT} | {_rack_budget_mm(V.PRIME_PIN_COUNT):.2f} mm |
| {V.FRIENDLY_PIN_COUNT} | {_rack_budget_mm(V.FRIENDLY_PIN_COUNT):.2f} mm |

That is what **"design tax"** looks like in metal. Pin count doesn't just
choose where each pin lives on the door — it dictates how much *meat*
every rack body is allowed to keep.

(Adam Savage's video is a great public reference for the build style;
the specific mechanism geometry is not reproduced here. This is a
fan-made educational study, not affiliated with Tested.)

---

*Generated by `src/vault/pin_counts.py`. Pin counts and the central
pinion radius come from `src/vault/vault.py`.*
""")
    return md_path
