# Shareable CAD — the pattern this repo is built on

> *A pipeline for hand-printable, parametric, code-trackable, community-shareable 3D objects. Onshape is where the geometry lives. GitHub is the workshop. MakerWorld and Printables are the storefronts. Python sits in the middle and pulls everything apart so anyone can put it back together.*

This repo started as one small physical artifact — a credit-card-sized
five-gear reduction chain handed out at PyCon 2026 — and a Python
toolkit to deconstruct its STEP file into renders, exploded GIFs, and
generated explainer pages. Then we ran the same toolkit on a
[spiral-spring cat toy](docs/pounce-a-pult/README.md). Then we started
[an Adam Savage mini-vault-door study](docs/vault/). Three different
objects, same scaffolding, same kind of writeup.

At three projects the *pattern* is more interesting than any one of
them. This document is the pattern.

## TL;DR

```
   Onshape doc          ← source of truth (parametric CAD in the cloud)
       │ STEP export, committed to repo root
       ▼
   GitHub repo          ← Python tooling, parameters, history, issues
       │ auto-built artifacts (STL / GLB / GIF / SVG / explainer pages)
       ▼
   MakerWorld + Printables   ← consumer-facing sharing endpoints
                              (3MF bundle + slicer profile + photos)
```

You design in Onshape because it's the most painless cloud CAD tool
that produces clean STEP. You commit the STEP into git so the geometry
has a versioned home. You mirror the parameters into a Python file so
parameter changes show up as real diffs. You let CI rebuild every
derivative artifact on push. You ship a 3MF bundle to MakerWorld
because that's where consumer 3D printers actually look — and you
mirror to Printables (and link back to GitHub) because that's the open
door home. The Python tooling makes the whole loop reproducible.

The three projects so far:

| Project | Status | Lives on | Doc |
|---|---|---|---|
| Gear card | shipped | GitHub | [`README.md`](README.md) |
| Pounce-a-Pult | shipped | MakerWorld + GitHub | [`docs/pounce-a-pult/`](docs/pounce-a-pult/README.md) |
| Adam Savage vault | in progress | GitHub (sandbox printable now) | [`docs/vault/`](docs/vault/README.md) |

The vault is the spotlight worked example in this document — it's the
project where every pipeline stage is visible because we're walking
through it in real time.

## What makes something "shareable CAD" in this sense

The word "shareable" does a lot of work here. People share STLs on
Thingiverse every day; that's not what this is about. What we mean:

1. **Parametric.** The object isn't a frozen mesh — it's a small
   number of *parameters* that produce a mesh. Change a tooth count, a
   diameter, a thickness, and the whole thing re-derives.
2. **Single source of truth.** Every dimension lives in exactly one
   place. The Onshape document has it. A Python file mirrors it. Tests
   yell if a third file hardcodes one of those numbers.
3. **Code-trackable.** A parameter change is a one-line git diff with
   a commit message and a date. Not a screenshot of "revision 12 of
   the Onshape document, dated last spring."
4. **Derivable.** Every artifact a reader might want — exploded GIF,
   per-part STL, hero PNG, explainer page — is *built* by code that
   reads only from the source of truth. No artisanal copies.
5. **Printable.** The end-state of this whole loop is a 3D print
   someone else can produce in their own kitchen with a 3D printer
   they already own, without having to know any of the above.

The PyCon-talk kernel of all this is the **Python tooling that does
the deriving** — `cardlab`, `explainers`, `vault`. Those packages are
the *lab* where we work out what "processing 3D files at consumer
community level" actually means.

## The three projects so far

### Gear card — the kernel

[![Animated exploded view of the reduction-gear card](docs/assets/card/exploded.gif)](README.md)

A 78 × 44 mm card with five compound gears giving 256:1 reduction
input-to-output. The card itself lives in
[a public Onshape document](https://cad.onshape.com/documents/786fefdef357fb6860b54650/w/33fb9222a6752311e4f08c8b/e/da99fedbaeebf1422d4cb0d3);
its STEP export sits at the repo root as [`jmcpheron-card.step`](jmcpheron-card.step);
the Python parameter mirror lives at
[`src/explainers/card.py`](src/explainers/card.py); the
[`cardlab`](src/cardlab/) CLI deconstructs the STEP into per-part
renders + an exploded GIF + a manifest; the [`explainers`](src/explainers/)
CLI generates six writeup pages, every number on every page sourced
from `card.py`. This is the project where the pipeline was born.

Lives on GitHub. CC BY-SA 4.0 on the geometry — change-and-share-back.

### Pounce-a-Pult — the MakerWorld proof point

[![Six parts of the pounce-a-pult fanning radially outward and back](docs/pounce-a-pult/assets/exploded.gif)](docs/pounce-a-pult/README.md)

A spiral-spring cat toy. Second project. The
[Onshape document](https://cad.onshape.com/documents/01739d2a63dc91eaf28c2c62/w/a7c671d651186a5272cc789f/e/fdb2542c5ccec8040d59912a)
is its real home; the
[MakerWorld bundle](https://makerworld.com/en/models/2138778-pounce-a-pult-spiral-cat-toy)
is where actual humans go to print it. The STEP file
[`step-demo/pounce-a-pult.step`](step-demo/pounce-a-pult.step)
is the bridge: `cardlab inspect / render / explode` runs the *same
five-function pipeline* used on the gear card — no toy-specific code
— and the auto-committed artifacts under
[`docs/pounce-a-pult/assets/`](docs/pounce-a-pult/) feed the page on
github.io.

Lives on **MakerWorld + GitHub**. CC BY 4.0 — intentionally more
permissive than the gear card, no share-alike strings, because cat
toys travel better that way.

### Adam Savage mini vault door — the walkthrough in progress

[![12-pin vault door mechanism — ring gear, 12 spurs, 12 rack-and-pin assemblies](docs/vault/assets/vault-hero.gif)](docs/vault/README.md)

A fan study of the 1/12-scale vault-door mechanism Adam Savage
machined on
[Tested.com](https://www.tested.com/). The third project, and the
slowest — partly because it's the most ambitious (12 pins on a 72 mm
BCD, three nested taper stages, a satellite gear train), partly
because we're documenting *while* we model. Everything is here:

- The video research, transcribed and distilled into [`docs/vault/specs.md`](docs/vault/specs.md).
- An [Onshape workflow doc](docs/vault/onshape-workflow.md) and [Onshape notes](docs/vault/onshape-notes.md) covering the FeatureScripts, the variable sheet, the gear math.
- A parametric **OpenSCAD sandbox** at [`docs/vault/sandbox/`](docs/vault/sandbox/) with a three-stage tapered door body, a full assembly with imported gear STLs, a self-contained ring-gear `.scad`, and a rack `.scad` that meshes with the satellite spurs. STLs ready to print today.
- A side-by-side **[Onshape ↔ OpenSCAD comparison doc](docs/vault/onshape-vs-openscad.md)** covering the tradeoff between cloud-CAD ergonomics and code-trackable text files.
- A build123d render pipeline at [`src/vault/mechanism.py`](src/vault/mechanism.py) producing the hero GIF above.
- Five canonical part STLs exported by [`vault export-parts`](src/vault/cli.py) under [`docs/vault/assets/parts/`](docs/vault/assets/parts/).

What's left to ship: the Onshape model itself (in progress), a 3MF
bundle for MakerWorld, a Printables mirror, and a few open dimension
questions (the [12 mm vs 10 mm pin diameter](docs/vault/specs.md)
revision Adam shows in Part 4; the three-stage taper angles).

The vault is the project where every pipeline stage is in flight at
the same time — which is why it's the example I keep coming back to
below.

## The pipeline stages

### Onshape as the source of truth

Onshape isn't open source. It's a cloud CAD app owned by PTC. We
recommend it anyway, because for the audience this pipeline is aimed at
— people who want to design a parametric 3D object and put it in
front of other humans without negotiating five command-line tools — it
is the most painless entry point that produces clean STEP. The
specifics that earn it the spot:

- **Public-readable URLs.** You can paste an Onshape link in your
  README and anyone with a browser can spin your design around. The
  gear card and Pounce-a-Pult both do this.
- **FeatureScript standard library.** Standard features (spur gears,
  threads, weld beads) are a click away. We use the
  ["Spur Gear" FeatureScript](docs/vault/onshape-notes.md) directly for
  every gear in the vault. No hand-drawn involutes.
- **Mate and Gear Relation UX.** Onshape's Assembly tab is genuinely
  good at making 12 satellite spurs rotate at the right ratio against
  a central ring gear. Code-driven CAD tools cannot beat that for
  iteration speed.
- **STEP export.** AP242 STEP is the lingua franca that lets every
  downstream tool (build123d, cascadio, OpenSCAD via STL, FreeCAD,
  CAM packages) read what Onshape made.

The cost is real, and worth naming. Onshape documents aren't
git-trackable. If PTC raises prices or shuts the free tier, your
geometry doesn't *vanish* — STEP exports survive — but the editing
environment does. We acknowledge the lock-in honestly and mitigate it
two ways: (a) commit STEP exports into git so the geometry has a
versioned home outside Onshape, and (b) keep the *numbers* in a Python
file so changing a parameter is independent of the editing UI. More on
that below.

### The Python parameter mirror

Every project in this repo has a single Python module that holds every
dimension. Other code reads *only* from that module:

- Gear card: [`src/explainers/card.py`](src/explainers/card.py) — `BIG_TEETH`, `PINION_TEETH`, `MODULE_MM`, the lot.
- Vault: [`src/vault/vault.py`](src/vault/vault.py) — door diameter, pin count, BCD, ring-gear bore, pressure angle, every cam parameter.

You change a number there, you run `uv run explainers build` or
`uv run vault build`, and every page, diagram, and (for the vault)
every parametric `.scad` file re-derives. There's a test
([`test_no_drift_between_sections`](tests/test_explainers.py)) that
checks every explainer markdown still contains the textual value of
the canonical parameters — so a literal-number sneaking into the
prose fails CI.

The Python mirror is what lets a parameter change be a 1-line git diff
with a commit message and a date. The Onshape variables are still the
*editing surface*; the Python module is the *diffable record*. They
have to stay in sync, and right now that sync is by hand (you change
a number in Onshape, you also change it in `card.py` / `vault.py`).
The hand-sync is the friction point most worth automating eventually.

### The Python kernel

The three packages [`cardlab`](src/cardlab/), [`explainers`](src/explainers/),
and [`vault`](src/vault/) are the *lab* the PyCon talk is built
around — small CLIs that demonstrate "processing 3D files at
consumer-community level."

`cardlab` is the workhorse, because STEP processing is the part most
people don't already have a recipe for:

| Command | Does |
|---|---|
| `cardlab inspect` | AP242 schema, assembly tree, bounding box, tessellation stats |
| `cardlab build` | Tessellates STEP → STL or coloured GLB |
| `cardlab render` | Orthographic PNG via OpenSCAD (iso / top / edge / front / right) |
| `cardlab explode` | Pulls an assembly apart into per-part STL/GLB/PNG + exploded GLB + animated GIF + manifest |
| `cardlab assemble` | Glues multiple STEP parts into one assembly |
| `cardlab spin` | Renders a gear chain *running* — parametric gears, frame-by-frame OpenSCAD, PIL-stitched into a GIF |

`explainers` and `vault` generate the per-page writeups: SVG diagrams
via [`drawsvg`](https://github.com/cduck/drawsvg), charts via
matplotlib, markdown that reads from the parameter file.

The packages split into a **light toolchain** (drawsvg + matplotlib,
fast install, builds the explainer pages) and a **heavy toolchain**
(build123d + cadquery-ocp + OpenSCAD + xvfb, ~180 MB OpenCascade
wheel, builds the STEP-derived renders and the GIFs). Anyone who just
wants to fix a typo in an explainer page doesn't need OpenCascade.
The split is in
[`pyproject.toml`'s optional dependencies](pyproject.toml):
`--extra explainers` is the light one, `--extra step` is the heavy
one. CI uses both.

### GitHub as the workshop

This repo's working pattern, generalised:

1. **The README tells the story.** Hero GIF, what it is, how it
   works, how to print one. Not "documentation" — narrative. The
   [gear-card README](README.md) is the canonical example.
2. **CI auto-builds derived artifacts on push.** Three workflows
   ([`build-card.yml`](.github/workflows/build-card.yml),
   [`build-explainers.yml`](.github/workflows/build-explainers.yml),
   [`build-vault.yml`](.github/workflows/build-vault.yml)) each watch
   their own input paths and write to disjoint output paths. They each
   `git pull --rebase` and retry on push rejection, so they can race
   each other (and human pushes) without conflict.
3. **Issues are for design discussion.** "Should the pin be 10 mm or
   12 mm?" is an issue, not a Slack thread.
4. **PRs are for parameter changes.** Bump a number, regenerate the
   diagrams, look at the diff. The diagrams are part of the diff.
5. **GitHub Pages deploys `docs/`.** Anyone who doesn't have a clone
   can still read the markdown.

The auto-commit-on-push pattern is the one trick most other CAD repos
don't do — it's what makes "change one number, rebuild everything" a
real workflow instead of a documentation lie. It's worth copying.

### MakerWorld + Printables as the storefronts

Once a design is ready for non-programmer humans, ship it to the two
biggest FDM-hobbyist sharing sites:

- **MakerWorld** is owned by Bambu Lab, the dominant consumer
  3D-printer maker right now. It bundles slicer profiles with prints,
  which dramatically lowers the "first print works" failure rate. Its
  audience is enormous. It is also somewhat closed — login-gated,
  account-bound, with a points system tilted toward originating-on-MW.
  We share there because that's where the audience is.
- **Printables** is owned by Prusa. Looser, more open. The default
  share-licence is more permissive. Smaller audience but a sturdier
  community.

The pattern is to publish to **both**, with the 3MF bundle as the
binary artifact and the GitHub repo as the parametric source. Each
listing should link back to the others:

```
   MakerWorld listing ──► ──► ──► GitHub repo ──► Onshape doc
              ▲                       │
              └─── Printables listing ┘
```

The Pounce-a-Pult is the existing template here — its
[MakerWorld page](https://makerworld.com/en/models/2138778-pounce-a-pult-spiral-cat-toy)
is the bundle, [its GitHub page](docs/pounce-a-pult/README.md) carries
the parametric story, and the
[Onshape doc](https://cad.onshape.com/documents/01739d2a63dc91eaf28c2c62/w/a7c671d651186a5272cc789f/e/fdb2542c5ccec8040d59912a)
is where the geometry lives. The vault will follow the same pattern
once the Onshape model is finished.

## The open-source ↔ consumer-friendly tension

The pipeline forces a question: if MakerWorld is closed-ish, why
publish there at all? Why not just throw everything on Printables and
GitHub and tell people to clone the repo?

Because that's not where most consumers are. A first-time 3D printer
owner with a Bambu A1 in their kitchen is more likely to open the
Bambu Handy app and search MakerWorld than to type git URLs into a
terminal. Pretending otherwise just keeps a smaller audience.

The core belief this pipeline tries to live by:

- **The source of truth stays open.** The Onshape document is public.
  The Python parameter file is in git under MIT. The STEP file is in
  git under CC BY-SA 4.0 (or CC BY 4.0 for permissive cases like the
  Pounce-a-Pult). Anyone who wants to fork the *editable thing* can.
- **The derived bundle goes where the audience is.** MakerWorld gets
  a 3MF + slicer profile + photos. The bundle is the "click to print"
  consumer thing — it isn't where remixing happens, it's where the
  audience already lives.
- **Every listing links back to the others.** A MakerWorld viewer
  who wants to change the geometry sees, in the description, "Remix
  the CAD in Onshape" and "Full source on GitHub." A GitHub visitor
  sees the MakerWorld link in the README. Nobody is trapped in any
  single platform.

The licenses (MIT for code; CC BY-SA 4.0 or CC BY 4.0 for geometry;
see [`ACKNOWLEDGMENTS.md`](ACKNOWLEDGMENTS.md)) are the legal
expression of this stance. The dual-publish pattern is the practical
expression.

## Recommended repo layout

Generalised from what `pycon2026/` already does:

```
<project>/
├── README.md              # Project story. Hero GIF at the top. The story is the doc.
├── SHAREABLE-CAD.md       # This doc, or a pointer to it.
├── LICENSE                # MIT for code.
├── LICENSE-3D-FILES       # CC BY-SA 4.0 (default) or CC BY 4.0 (permissive variant).
├── ACKNOWLEDGMENTS.md     # Third-party tools + licenses + Onshape doc link.
├── <project>.step         # The Onshape STEP export. Lives at the root, gets committed.
├── docs/
│   ├── assets/<project>/  # Hero render, exploded GIF, per-part PNGs.
│   ├── explainers/        # Markdown + SVG, generated from src/explainers/.
│   ├── sandbox/           # OpenSCAD playground (optional, not auto-built).
│   └── makerworld/        # 3MF bundle source + slicer profile (when ready).
├── src/
│   ├── <thing>lab/        # Python CLI: inspect/build/render/explode/spin.
│   └── explainers/        # Parametric doc generator. Owns the parameter file.
├── tests/                 # Drift tests: numbers in markdown == numbers in parameters.py.
└── .github/workflows/     # Auto-build + auto-commit derived artifacts on push.
```

Canonical examples in *this* repo for each row:

- README pattern → [`README.md`](README.md) (gear card) and [`docs/pounce-a-pult/README.md`](docs/pounce-a-pult/README.md).
- License pair → [`LICENSE`](LICENSE) + [`LICENSE-3D-FILES`](LICENSE-3D-FILES).
- ACKNOWLEDGMENTS → [`ACKNOWLEDGMENTS.md`](ACKNOWLEDGMENTS.md).
- STEP at root → [`jmcpheron-card.step`](jmcpheron-card.step).
- Sandbox playground → [`docs/vault/sandbox/`](docs/vault/sandbox/).
- Python kernel → [`src/cardlab/`](src/cardlab/).
- Parameter file → [`src/explainers/card.py`](src/explainers/card.py), [`src/vault/vault.py`](src/vault/vault.py).
- Auto-commit workflows → [`.github/workflows/`](.github/workflows/).

## Onshape conventions

Pulled from
[`docs/vault/onshape-workflow.md`](docs/vault/onshape-workflow.md) and
[`docs/vault/onshape-notes.md`](docs/vault/onshape-notes.md), which
were written *while* modelling the vault and are the load-bearing
references:

1. **Make the document publicly readable.** Right-click → Share →
   anyone with the link. Put the URL in the README.
2. **Variables at the top of the Part Studio.** Every parameter the
   Python file has, define as an Onshape variable: `#door_diameter`,
   `#pin_count`, `#cam_rotation`. Drive every sketch dimension from
   the variable. This is your editing surface.
3. **Mirror the variables in your Python parameter file.** Same
   names, same units. They have to be kept in sync by hand — there's
   no automation for this yet — and the [Onshape ↔ Python table](docs/vault/onshape-workflow.md)
   is the canonical record of which mirrors which.
4. **Use FeatureScript for standard features.** Don't hand-draw
   involute gear teeth, threads, or splines. The Onshape standard
   library has them. [Spur Gear settings](docs/vault/onshape-notes.md)
   for our use cases are documented end-to-end.
5. **STEP export to repo root.** When a model is "ready enough,"
   export AP242 STEP, commit at the project root. Auto-commit
   workflows take over from there.

## GitHub conventions

What this repo does that's worth copying:

- **A front-door README that tells a story**, hero image first. The
  gear-card README opens with the exploded GIF before any prose — the
  GIF *is* the elevator pitch.
- **Auto-commit derived artifacts on push.** Three workflows
  ([`build-card.yml`](.github/workflows/build-card.yml),
  [`build-explainers.yml`](.github/workflows/build-explainers.yml),
  [`build-vault.yml`](.github/workflows/build-vault.yml)) each watch
  their own input paths, run their pipeline, and `git push` the
  output back to `main` with a rebase-and-retry loop. They write to
  disjoint paths so they can race.
- **Light vs heavy dependency extras** in `pyproject.toml` so
  contributors who only want to edit prose aren't forced into a 180
  MB OpenCascade wheel.
- **Pages workflow** publishes `docs/` to github.io for non-cloners.
- **A devlog**. [`docs/devlog/`](docs/devlog/) is where build journal
  entries live — informal, dated, the human story alongside the
  generated artifacts.

## MakerWorld + Printables prep

When a design is ready to ship to consumer 3D printer owners, the
bundle is:

1. **Hero render** — a single iso PNG that reads at thumbnail size.
   `cardlab render --angle iso` makes one.
2. **Per-part STLs** — what the slicer actually consumes. `cardlab
   explode` writes them under `assets/parts/`.
3. **3MF (preferred over STL)** — bundles part orientation,
   per-part colour, and printer-specific settings. Bambu Studio /
   PrusaSlicer both export.
4. **Slicer profile** — the `.gcode.3mf` or `.3mf` with the project's
   tested-good slicer settings baked in. MakerWorld highlights this.
5. **Photos in the wild** — a print on a desk, a cat playing with
   the toy, the card in someone's hand. Social proof that the design
   prints.
6. **Links back to GitHub and Onshape** — every consumer-site listing
   should have these in the description.

The [Pounce-a-Pult MakerWorld page](https://makerworld.com/en/models/2138778-pounce-a-pult-spiral-cat-toy)
is the existing template. Copy its structure.

## The vault as worked example

Where the Adam Savage vault is, as of this writing:

**Done.**

- Distilled five videos of source material into [`docs/vault/specs.md`](docs/vault/specs.md) with a per-row source tag and a "Discrepancies" table flagging the 12 mm vs 10 mm pin diameter question.
- Built an Onshape-conventions doc at [`docs/vault/onshape-notes.md`](docs/vault/onshape-notes.md) covering ring-gear and satellite-spur FeatureScript settings, the derived consistency-check numbers, and the four Assembly-tab operations (Revolute / Gear Relation / Rack-and-Pinion Relation / Circular Pattern) that turn one modelled spur into the timed 12-pin mechanism.
- A parametric OpenSCAD sandbox at [`docs/vault/sandbox/`](docs/vault/sandbox/) with:
  - [`door.scad`](docs/vault/sandbox/door.scad) — three-stage tapered puck, pin bores in the cylindrical back stage, ring-boss recess, spur-axle bolt circle.
  - [`assembly.scad`](docs/vault/sandbox/assembly.scad) — full mechanism using imported STLs for the gears, parametric pins, with a single `cam_progress` slider driving ring rotation, spur counter-rotation, and pin extension together.
  - [`ring_gear.scad`](docs/vault/sandbox/ring_gear.scad) — self-contained parametric spur gear, no libraries. Exports to STL.
  - [`rack.scad`](docs/vault/sandbox/rack.scad) — parametric rack meshing with the 24-tooth satellite spurs. Exports to STL.
- A side-by-side [Onshape ↔ OpenSCAD comparison](docs/vault/onshape-vs-openscad.md) covering the tradeoff between cloud-CAD ergonomics and code-trackable text files, with the ring gear as the worked example.
- A build123d render pipeline at [`src/vault/mechanism.py`](src/vault/mechanism.py) producing the hero GIF from `vault.py`.
- Five canonical printable part STLs at [`docs/vault/assets/parts/`](docs/vault/assets/parts/), exported by [`vault export-parts`](src/vault/cli.py).

**Next.**

- Finish the Onshape model. The geometry decisions (three-stage taper, pin diameter) get resolved in `specs.md` first; then they get into the Onshape variables, then into `vault.py`.
- Resolve the open dimension discrepancies in [`specs.md`'s Discrepancies table](docs/vault/specs.md).
- Bundle a 3MF + slicer profile.
- Publish to MakerWorld with the bundle.
- Mirror to Printables.
- Cross-link all three.

When that's done, the vault becomes the second project to fully
traverse the pipeline (after the Pounce-a-Pult). At that point this
doc gets updated with "the vault, as shipped."

## Starter checklist — kicking off your own project

Use this as the kickoff sequence for a new shareable-CAD project,
roughly in order:

1. **Pick a parametric CAD object.** Something small enough to print
   in one job. Something where changing a parameter is *interesting*
   to a remixer (a tooth count, a length, a bolt spacing).
2. **Build it in Onshape.** Make the document publicly readable.
   Put every dimension in a variable at the top of the Part Studio.
3. **Create a GitHub repo.** Mirror the layout in the "Recommended
   repo layout" section above. MIT for the code, CC BY-SA 4.0 (or
   CC BY 4.0 if you want permissive) for the geometry.
4. **Commit the STEP export at the repo root.** This is the bridge
   between Onshape and everything downstream.
5. **Write `parameters.py` (or `<project>.py`).** Mirror every
   Onshape variable as a Python constant. Use it from every other
   Python file in the repo. Reference [`src/vault/vault.py`](src/vault/vault.py)
   as the template.
6. **Wire up `cardlab` or a `cardlab`-style CLI.** At a minimum,
   `inspect` and `render`. `explode` if the design has multiple
   parts. (Copying `cardlab` and renaming `<thing>lab` is a fine
   starting point — it's not yet a published library; it's a pattern
   to fork.)
7. **Write your first explainer page** generated from the parameter
   file. Even if it's just one page that says "this has N teeth, here
   is what N teeth looks like, here is what changes if you change
   N." That page becomes the README's deep-link.
8. **Wire up auto-commit CI.** Copy [`build-card.yml`](.github/workflows/build-card.yml)
   as your starting point. Make it watch your STEP path and your
   Python kernel path. Make it write to disjoint output paths so it
   doesn't fight the human pushes.
9. **Ship a Printables listing** with the STEP file and the
   generated STLs. Link back to your GitHub repo and Onshape doc.
10. **Bundle a 3MF and ship a MakerWorld listing.** Test print first;
    include the slicer profile; include photos. Link back to
    Printables, GitHub, and Onshape.
11. **Open a [`docs/devlog/`](docs/devlog/) entry** for ongoing build
    notes. Future-you will thank present-you.
12. **Update the README's front-door story** as the project evolves.
    The README is not docs; it's the elevator pitch with a hero GIF.

That's the pattern. Three projects so far have used it; the vault is
the fourth in flight; this document is the first time it's been
written down. If you build something with this pipeline, please open
an issue and link back — the goal is for the pattern itself to be
remixable.

---

*Companion to [`README.md`](README.md). The vault project at
[`docs/vault/`](docs/vault/) is the spotlight worked example. The
gear card ([`README.md`](README.md)) and Pounce-a-Pult
([`docs/pounce-a-pult/`](docs/pounce-a-pult/README.md)) are the
already-shipped proof points.*
