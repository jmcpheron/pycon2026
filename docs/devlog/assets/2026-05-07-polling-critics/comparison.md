# multi-critic comparison

- render: `docs/devlog/assets/2026-05-07-scadvil-anvil/render.png`
- prompt (first 200 chars): `Create a 3D-printable OpenSCAD calibration anvil.

Design constraints to keep render time low:
- Use only cube(), cylinder(), and sphere() primitives.
- Do NOT use minkowski() or hull() — they are too...`
- augment: (none — SYSTEM_CRITIQUE verbatim)

| model | done | score | blocking | non-blocking | source | t(s) |
|---|---|---|---|---|---|---|
| `google/gemini-2.5-flash` | False | 4 | 3 | 0 | tool_call | 2.5 |
| `anthropic/claude-haiku-4.5` | False | 7 | 3 | 3 | tool_call | 6.37 |
| `qwen/qwen3-vl-8b-instruct` | False | 4 | 5 | 5 | tool_call | 3.35 |
| `openai/gpt-5-mini` | — | — | — | — | unparsed | 29.8 |
| `meta-llama/llama-4-scout` | — | — | — | — | error | 0.72 |
| `google/gemma-4-31b-it` | False | 4 | 1 | 1 | tool_call | 28.22 |

## blocking issues by model

### `google/gemini-2.5-flash` — score 4
_summary:_ The model currently lacks a tapered horn and legible text, and the tolerance hole is missing. These critical issues prevent it from matching the request.

- **blocking:** The horn is not tapered as requested; it is a rectangular block.
- **blocking:** The text is not legible as "PYCON"; it is a collection of cuboids and has been placed on the wrong face of the object (it is on the larger face instead of the side).
- **blocking:** The tolerance hole is not visible or properly placed; it should be drilled through the body in a visible location on the top face.

### `anthropic/claude-haiku-4.5` — score 7
_summary:_ The model credibly depicts a calibration anvil with all major requested components (base, body, horn, heel, tolerance hole, and embossed text), though some details need refinement for print accuracy.

- **blocking:** Horn taper is not visually tapered—it appears as a blocky rectangular mass because the difference operation removes corner material but doesn't create a smooth wedge shape; for a calibration tool this defeats the typical anvil horn form.
- **blocking:** Embossed text positioning is off-target and appears distorted; the letters should sit flat on the top face of the body but their placement puts them partially out of bounds relative to the body geometry.
- **blocking:** Tolerance hole appears to be drilled from bottom (z = -1) through top (+11), but the hole should be drilled cleanly through the center of the main body block (which sits at z = 2 to z = 16); recalculate the hole height and z-position.
- nonblocking: Horn shape is geometrically functional but crude; a true wedge taper would improve aesthetics and print quality.
- nonblocking: Text emboss uses stacked cubes which produce a pixelated appearance rather than smooth letter forms, but it is still legible as 'PYCON'.
- nonblocking: Base cube dimensions (55 × 35 × 4) are reasonable but could be verified to ensure sufficient contact area for FDM printing stability.

### `qwen/qwen3-vl-8b-instruct` — score 4
_summary:_ The model is not a credible calibration anvil — the horn, heel, text, and hole are all incorrectly implemented.

- **blocking:** The horn is not a tapered wedge as requested — it's a cube with a corner removed, which looks more like a truncated pyramid than a smooth taper.
- **blocking:** The heel block is misaligned and too small — it's placed at [-26, 0, 9] but should be on the opposite side of the horn, and its dimensions are too small for a functional heel.
- **blocking:** The embossed text "PYCON" is not recessed into the side face — it's rendered as a separate module subtracted from the anvil, but the positioning and shape don't match the request for embossed text.
- **blocking:** The tolerance hole is not centered vertically through the body — it's offset by the translate([0, 0, -1]) in the tolerance_hole() module, which may not align with the body's center.
- **blocking:** The base is too wide (55x35) and the body is too tall (14) — the request asks for ~50 mm wide, and the proportions don't match a typical calibration anvil.
- nonblocking: The model uses only cube(), cylinder(), and sphere() primitives as requested.
- nonblocking: The model avoids minkowski() and hull() as requested.
- nonblocking: $fn = 24 is set globally.
- nonblocking: The model has sharp edges as requested.
- nonblocking: The model is simple and printable on FDM at 0.2 mm layers.

### `google/gemma-4-31b-it` — score 4
_summary:_ The model has the general shape of an anvil, but the requested tolerance hole is a protruding cylinder instead of a hole.

- **blocking:** The 4mm tolerance hole is rendered as a positive cylinder sticking out of the top instead of a hole drilled through the body.
- nonblocking: The 'PYCON' text is not visible in the render because it is placed on the top surface rather than a side face, or it is too shallow/small to be seen from this angle.

### `meta-llama/llama-4-scout` — ERROR
```
HTTP 429: {"error":{"message":"Provider returned error","code":429,"metadata":{"raw":"meta-llama/llama-4-scout is temporarily rate-limited upstream. Please retry shortly, or add your own key to accumulate your 
```
