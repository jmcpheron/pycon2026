---
marp: true
theme: default
class: invert
paginate: true
footer: 'github.com/jmcpheron/pycon2026'
style: |
  section { padding: 40px 60px; }
  h1 { font-size: 1.55em; line-height: 1.2; border-bottom: 2px solid #4a9eff; padding-bottom: 0.2em; margin-bottom: 0.5em; }
  h2 { font-size: 1.3em; line-height: 1.3; }
  ul { font-size: 0.85em; line-height: 1.8; }
  p { font-size: 0.9em; line-height: 1.6; }
  .two-col { display: flex; gap: 1.5em; align-items: center; }
  .two-col > div { flex: 1; }
  .pipeline { font-family: monospace; font-size: 0.82em; line-height: 2.2; background: rgba(255,255,255,0.08); padding: 1em 1.5em; border-radius: 8px; margin: 0.8em 0; }
  .big-quote { font-size: 1.15em; line-height: 1.6; font-style: italic; margin: 0.8em 0; color: #a8d4ff; }
  .qr-wrap { text-align: center; margin-top: 0.5em; }
  .qr-wrap img { max-height: 340px; }
  .soft { color: #999; font-size: 0.8em; }
  footer { font-size: 0.65em; color: #6699cc; font-family: monospace; }
---

<!-- _class: lead -->

## I Made a Gearbox Business Card,<br>Then Made Python Explain It

**Jason McPheron** · PyCon US 2026 · Lightning Talk

<!--
[walk up, hold up the card if you have one]
-->

---

# Hi, I'm Jason.

<div class="two-col">
<div>

- IT work, California community college — mostly student systems
- This talk is about what I do when I should be relaxing: **3D printing little mechanical things and then overthinking them with Python**
- First PyCon — wanted something physical to bring
- Something more interesting than "here's my GitHub"

</div>
<div>

![w:360](../assets/card/photos/assembled.jpg)

</div>
</div>

<!--
I work in IT for a community college here in California, mostly around student systems.

But this talk is about one of my hobbies, which is 3D printing little mechanical things and then overthinking them with Python.

This is my first PyCon, and I wanted to make something physical to bring with me.

Partly because 3D printing is fun. Partly because I like making small mechanical objects. And partly because conferences full of strangers can be a little intimidating, so I wanted a conversation starter.

Something I could hand someone that was more interesting than just saying, "Here's my GitHub."
-->

---

# So I made a 3D printed business card.

It has my GitHub project on it.

It also has a **tiny gear mechanism** built into it.

You can spin one gear with your thumb, and the motion moves through the card.

<p class="big-quote">Part business card. Part fidget toy. Part tiny mechanical demo.</p>

At first, that was the whole project. Make a cool little object. Print it. Bring it to PyCon.

<!--
It has my GitHub project on it, but it also has a tiny gear mechanism built into it. You can spin one gear with your thumb, and the motion moves through the card.

It is part business card, part fidget toy, and part tiny mechanical demo.

At first, that was the whole project. Make a cool little object. Print it. Bring it to PyCon. Use it as an excuse to talk to people.
-->

---

# This is where I was happy with the design.

![w:860 center](../assets/card/photos/onshape-assembly.png)

<!--
The design started in Onshape. Parts, mate connectors, revolute joints so the gears actually spin, even the mesh ratios set up so Onshape knows how they drive each other.

When I got to this point — assembly done, gears moving, lid fitting — I was just happy with it as a 3D design. That felt like the project.

And then I had the thought that probably gets a lot of us into trouble: "This is nice, but how do I force Python into this?"

What could I actually do with it if I exported it and dropped it in a repo? How much Python tooling could I throw at a STEP file and get something interesting out?
-->

---

# The moment the project changed.

<div class="two-col">
<div>

Once I had the card assembled, I exported it as a **STEP file**.

<div class="pipeline">

Onshape assembly &nbsp;→&nbsp; STEP export &nbsp;→&nbsp; GitHub repo

</div>

Now I had **a single file** that represented the assembled physical object.

I could put it in a repo. Version it. Run tools against it. Treat the physical object a little more **like a software project**.

</div>
<div>

![w:380](../assets/card/exploded.gif)

</div>
</div>

<!--
Once I had the card assembled, I exported it as a STEP file.

That was the moment where the project changed for me. Because now I had a single file that represented the assembled physical object. I could put that file in a GitHub repo. I could version it. I could run tools against it. I could start treating the physical object a little more like a software project.
-->

---

# Python around the STEP file.

<div class="two-col">
<div>

Not replacing CAD.

**Tooling around the CAD export.**

- Inspect the file
- Take the assembly apart
- Generate renders
- Make exploded views
- Animate the mechanism
- Keep notes, journals, tolerance experiments

</div>
<div>

![w:380](../assets/card/spin.gif)

</div>
</div>

<!--
So the Python part became less about replacing CAD, and more about building tooling around the CAD export. The design still happens in Onshape. But once the STEP file is in the repo, Python can start doing useful things around it.

It can inspect the file. It can help take the assembly apart. It can generate renders. It can make exploded views. It can create animated GIFs that show the mechanism moving.

And it can help keep track of all the little notes around the object: explainers, development journals, tolerance problems, print settings, experiments, and the general story of how the thing changed over time.

That became the real project. Not just the card itself, but the workflow around the card.
-->

---

# A STEP file is not an explanation.

GIFs show *what* the object does. They don't say *why* it's shaped that way.

So the repo also writes **explainer pages** — short prose with diagrams:

<div class="two-col">
<div>

- `gear-ratios.md` — why **32 × 8**, four times, gives 256:1
- `decoding-gears.md` — recovering tooth counts from the STL geometry itself
- `stacking.md` — why the gears sit in a staircase, not a stack
- `printing.md` — what changed when the printer, rudely, obeyed physics

<p class="big-quote">The repo doesn't just show the object.<br>It teaches you what's going on inside it.</p>

</div>
<div>

![w:380](../explainers/assets/gear-ratios-animated.svg)

</div>
</div>

<!--
A GIF is great, but it only shows what the object does. It does not tell you why it is shaped the way it is. Why those tooth counts. Why those ratios. Why the gears are stacked the way they are.

So alongside the renders, the repo also writes explainer pages. Short prose with diagrams. Why 32 times 8, four times over, gives 256 to 1. How you can recover the tooth counts from the STL geometry itself, after the fact. Why the gears sit in a staircase instead of a clean stack. And what had to change when the printer, very rudely, obeyed physics.

The renders are the gallery. The explainers are the museum placard next to it.
-->

---

# GitHub Actions for physical objects.

The cool part isn't that Python *can* make these. It's that I never run it.

Push a change to the STEP file or the gear constants. A workflow regenerates the GIFs, the explainer pages, the diagrams — and **commits them back to main**.

<div class="pipeline">

`jmcpheron-card.step` &nbsp;changes&nbsp; →&nbsp; <strong>build-card.yml</strong> &nbsp;→&nbsp; new exploded GIF, spin GIF, parts<br>
`src/explainers/card.py` &nbsp;changes&nbsp; →&nbsp; <strong>build-explainers.yml</strong> &nbsp;→&nbsp; new pages + SVGs

</div>

<p class="big-quote">A README can quietly start lying about its object.<br>An auto-commit loop makes that a lot harder.</p>

<!--
Here is the part I actually like about using GitHub Actions for this. It is not that Python can make renders and exploded views and diagrams. We already saw that. It is that I almost never run any of it.

When I push a change to the STEP file, a workflow runs in the cloud, regenerates the exploded GIF and the spinning GIF, and commits the new files back to main. When I push a change to the gear constants in card.py, a different workflow rebuilds every explainer page and every SVG, and commits those back too.

Screenshots get stale. Documentation gets stale. A repo can quietly start lying about the object it contains. An auto-commit loop is my attempt to make that a little harder.
-->

---

# Paws for animals.

<div class="two-col">
<div>

Before this card, I made a 3D printed **cat toy** for my mom.

That project is where I really started enjoying designing separate parts and assembling them.

The only problem:

**I do not have a cat.**

I have a golden retriever named **Bowie**.

</div>
<div>

![w:400](bowie-makerworld.png)

<p class="soft" style="text-align:center;">The cat toy on MakerWorld. Bowie remains unimpressed.</p>

</div>
</div>

<!--
Before this card, I had another little Onshape project. For Christmas, my mom asked me to design a 3D printed cat toy. That project is where I really started learning how much I enjoy making separate parts in Onshape and then assembling them into a complete object.

There is something extremely satisfying about designing individual pieces, bringing them together, and then seeing the assembled product. It feels like the model becomes real before you ever print it.

The only problem is that I do not have a cat. I have a golden retriever named Bowie.

But that cat toy became useful for the Python side of the project too. It was a different STEP file. A different object. A different assembly. And I could try running it through a similar workflow. That helped me think about whether I was building tools for one very specific business card, or whether I was building a more general little pipeline for understanding 3D projects.
-->

---

# The tiny plastic maker version.

I am sure serious hardware fields have much more mature ways to do this.

Probably industry-standard workflows, best practices, blind spots I have not even learned enough to know I have.

Mine is:

- A 3D printed gearbox business card
- A public Onshape model
- A STEP export
- A Python CLI
- GitHub Actions making pictures

<p class="big-quote">Small enough to be playful.<br>Silly enough to experiment with.<br>Pointing at a serious idea.</p>

<!--
I do not want to oversell this. I am sure that in serious hardware, robotics, aerospace, manufacturing, and embedded systems, there are much more mature ways to do this. There are probably industry-standard workflows, best practices, blind spots I have not even learned enough to know I have, and whole categories of tooling that solve parts of this properly.

My version is the tiny plastic maker version. It is a 3D printed gearbox business card, a public Onshape model, a STEP export, a Python CLI, and GitHub Actions making pictures.

But that is what I like about it. It is small enough to be playful. It is silly enough to experiment with. And it points at a serious idea.
-->

---

# Physical open source borrows from software.

Version control · Generated documentation · Repeatable builds<br>Reviewable changes · Public artifacts

And maybe: **little sanity checks that help the object explain itself.**

---

One more thing: I'm also curious about **licensing**.

For code, we have familiar open-source licenses.

For functional 3D design files — STEP files, things you can print and use — I'm less sure what the right answer is.

Does Creative Commons make sense? Is CC BY-SA the right model? What does *sharing* mean when someone can download the geometry, modify it, print it, remix it?

Making those questions **part of the project** instead of something I figure out later in private.

<!--
Physical open-source projects can borrow some habits from software. Version control. Generated documentation. Repeatable builds. Reviewable changes. Public artifacts. And maybe even little sanity checks that help the object explain itself.

I am also interested in the licensing side of this. For code, we have a pretty familiar set of open-source licenses. For 3D design files, especially functional objects, I am less sure what the right answer is. Does Creative Commons make sense for STEP files? Is CC BY-SA the right model? What does sharing mean when someone can download the geometry, modify it, print it, remix it, or manufacture it?

I do not have a perfect answer to that. But it is one of the reasons I like having the project public. It makes those questions part of the project instead of something I figure out later in private.
-->

---

<!-- _class: lead -->

# Come find me.

Onshape · OpenSCAD · Python · gears · GitHub Actions<br>STEP files · licensing · cat toys · golden retrievers<br>*how much tooling is too much tooling for a tiny plastic business card*

<div class="qr-wrap">

![QR code](qr.png)

**github.com/jmcpheron/pycon2026** — I have cards, ask for one.

</div>

<!--
So if you see me around, come find me. I can show you the card. We can talk about Onshape, OpenSCAD, Python, gears, GitHub Actions, STEP files, licensing, cat toys, or how much tooling is too much tooling for a tiny plastic business card.

The repo is jmcpheron slash pycon2026.

Thank you.
-->
