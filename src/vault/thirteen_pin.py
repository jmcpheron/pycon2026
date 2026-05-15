"""The fun one — 13 pins is mathematically clean and mechanically valid;
it just gives up specific shortcuts.
"""

from __future__ import annotations

from pathlib import Path

from vault import vault as V
from vault.geometry import angle_step, divisors
from vault.svg_draw import (
    draw_13_pin_problem,
    draw_animated_comparison,
    draw_opposing_pairs,
    draw_vault_pin_layout,
)

SLUG = "thirteen-pin-problem"


def build(out_dir: Path) -> Path:
    assets = out_dir / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    animated = draw_animated_comparison(assets / f"{SLUG}-animated.svg")
    layout = draw_vault_pin_layout(V.PRIME_PIN_COUNT,
                                   assets / f"{SLUG}-layout.svg")
    orphan = draw_opposing_pairs(V.PRIME_PIN_COUNT,
                                 assets / f"{SLUG}-orphan.svg")
    side_by_side = draw_13_pin_problem(assets / f"{SLUG}-side-by-side.svg")

    twelve_div = ", ".join(str(x) for x in divisors(V.PIN_COUNT))
    thirteen_div = ", ".join(str(x) for x in divisors(V.PRIME_PIN_COUNT))
    twentyfour_div = ", ".join(str(x) for x in divisors(V.FRIENDLY_PIN_COUNT))

    md_path = out_dir / f"{SLUG}.md"
    md_path.write_text(f"""# The {V.PRIME_PIN_COUNT}-pin vault problem

![animated comparison — {V.PIN_COUNT}, {V.PRIME_PIN_COUNT}, {V.FRIENDLY_PIN_COUNT} pins all locking and unlocking on the same loop](assets/{animated.name})

> *Three doors, one cycle. Every pin in every panel locks and unlocks.
> The middle panel's darker-brass pin is the one with **no mirror twin**
> across the diameter — the dashed marker shows where its partner would
> have to sit. The mechanism still works; it just can't share parts the
> way 12 and 24 can.*

A {V.PRIME_PIN_COUNT}-pin vault door **works**. In CAD, placing
{V.PRIME_PIN_COUNT} equally spaced pins around a circle is one circular
pattern. Mechanically, a central pinion driving {V.PRIME_PIN_COUNT} racks
locks and unlocks the door exactly the way {V.PIN_COUNT} or
{V.FRIENDLY_PIN_COUNT} racks would. The geometry doesn't refuse the
prime.

What {V.PRIME_PIN_COUNT} refuses is a **set of design shortcuts** —
optimizations that composite pin counts get for free and prime pin
counts have to pay full price for. That's the real story, and it's
worth being precise about it.

## Tricks the geometry allows

For any N (prime or composite), all of these work:

* a single central pinion driving N racks — Adam Savage's mini-vault
  pattern, see [pin-counts.md](pin-counts.md)
* a cam plate with N follower slots
* a worm-gear ring driving each pin off its own pinion
* N independent levers, each with its own cam profile

For composite N (like {V.PIN_COUNT} or {V.FRIENDLY_PIN_COUNT}), these
*also* work:

* **one shared rack driving two opposite pins** — needs an exact pair
  across the diameter, so N must be even
* **a mirror-image sub-assembly used N/2 times** — needs bilateral
  symmetry through pin centres, so N must be even
* **cyclic sub-symmetry actuation** — lock half, then the other half;
  lock thirds; lock quarters. Needs a non-trivial subgroup of C_N,
  which exists exactly when N has divisors other than 1 and N

For {V.PRIME_PIN_COUNT}, none of those three are available. {V.PRIME_PIN_COUNT}
is prime — its only divisors are {thirteen_div}.

## The math, fully

{V.PRIME_PIN_COUNT} pins can be spaced exactly evenly:

```
360 / {V.PRIME_PIN_COUNT} = {angle_step(V.PRIME_PIN_COUNT):.3f}°
```

Place pin 0 at the top, walk {angle_step(V.PRIME_PIN_COUNT):.3f}° around
the circle for each subsequent pin, and the {V.PRIME_PIN_COUNT}th pin
lands exactly where you started. The radial forces from all
{V.PRIME_PIN_COUNT} pins acting symmetrically on the hub **sum to zero**
— same as any regular N-gon arrangement; primality doesn't break force
balance.

What primality breaks is the **opposing-pair relation**. A pin at angle
A on a {V.PRIME_PIN_COUNT}-pin door has no other pin at angle A + 180°.
The closest two pins land off by half an angle step
({angle_step(V.PRIME_PIN_COUNT) / 2:.3f}°).

![pin 0 highlighted; the would-be mirror partner falls between two real pins](assets/{orphan.name})

The dashed marker is where pin 0's mirror twin *would* have to sit on a
{V.PIN_COUNT}-pin door. On {V.PRIME_PIN_COUNT} pins it falls between two
real pins, off by half an angle step. The pin itself isn't broken — it
just has nothing to be paired with.

![side-by-side: {V.PIN_COUNT} pins resolve into 6 chord pairs; {V.PRIME_PIN_COUNT} pins have no chord that lands on another pin](assets/{side_by_side.name})

## Where it actually hurts

Whether you care depends on the design you wanted to build:

| Design trick                                    | Works for {V.PIN_COUNT}? | Works for {V.PRIME_PIN_COUNT}? |
|-------------------------------------------------|---:|---:|
| Central pinion + N independent racks            | ✓ | **✓** |
| Cam plate with N follower slots                 | ✓ | **✓** |
| Independent levers, one cam profile per pin     | ✓ | **✓** |
| One shared rack driving two opposite pins       | ✓ | ✗ |
| Mirror sub-assembly fixtured & cast N/2 times   | ✓ | ✗ |
| Multi-stage lock — wave of N/2, then N/2        | ✓ | ✗ |
| Multi-stage lock — wave of N/3, three times     | ✓ | ✗ |

The first three rows are the "no-tricks" path. They work for any N.
That's the path that lets a {V.PRIME_PIN_COUNT}-pin door function.

The last four are the optimizations a composite count buys you — shared
parts, mirrored fixtures, sub-symmetric actuation. {V.PRIME_PIN_COUNT}
locks you out of all of them.

## Divisors at a glance

```
divisors({V.PIN_COUNT})  = {twelve_div}
divisors({V.PRIME_PIN_COUNT})  = {thirteen_div}
divisors({V.FRIENDLY_PIN_COUNT})  = {twentyfour_div}
```

Composite numbers give mechanical designers many ways to divide, mirror,
and repeat a design. Prime numbers give two: 1, and the number itself.

That's not a bug in primes — it's the *definition* of prime. It just
means a {V.PRIME_PIN_COUNT}-pin design either uses {V.PRIME_PIN_COUNT}
identical, individually-fitted actuators, or one custom geometry.
There's no elegant middle ground.

## Picking {V.PRIME_PIN_COUNT} on purpose

If you want the elegance, pick {V.PIN_COUNT} or {V.FRIENDLY_PIN_COUNT}.
You'll have more design options.

If you want a conversation piece — a door that genuinely doesn't admit
mirror simplification, where every part is unique by necessity — pick
{V.PRIME_PIN_COUNT} and lean into it.

What you don't have to choose between is "works" and "doesn't work."
Both work. The honest framing is:

> Prime pin counts aren't mechanically broken. They just don't share.

---

*Generated by `src/vault/thirteen_pin.py`. Pin counts come from
[`src/vault/vault.py`](../../src/vault/vault.py).*
""")
    return md_path
