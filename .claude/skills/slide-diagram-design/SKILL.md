---
name: slide-diagram-design
description: Art direction for attractive, eye-catching presentation diagrams built in Penpot (flywheels, flows, matrices, funnels, timelines, org charts), built design-system-first (tokens, library text styles, components) and verified by a compliance gate. Use whenever asked to design a slide, a diagram for a deck, or any presentation visual in Penpot — read it before creating the first shape.
---

# Slide Diagram Design

A slide diagram is read from across a room in under ten seconds. It must make
one idea obvious and look like a professional designer made it. "Correct but
bland" is a failure; so is "pretty but unclear."

## 1. Decide the one idea first

Before touching Penpot, write down:
- **The claim** — one sentence the viewer should leave with ("Each stage feeds the next, so growth compounds").
- **The shape of the idea** — cycle, sequence, hierarchy, comparison, proportion, or position. The diagram form follows from this, never the other way round.
- **The hero** — the single element the eye should land on first. Exactly one.

If you cannot name the hero, the slide has no focal point. Fix that before designing.

## 2. Canvas and grid

- Board: **1920×1080** (16:9), named for the slide. **Exception:** when the design system comes from
  a shared library whose type scale is web-sized (body 16-18, labels 11-14, largest heading ~76),
  build at **1280×720** (margin 64) so the library's own styles read at slide scale; never add
  off-system sizes to compensate. The scale rules below then apply at 2/3 size.
- Safe margin: **96px** all sides (64px on a 1280×720 board). Nothing important outside it.
- Work on an **8px grid**: all positions, sizes, and gaps are multiples of 8.
- Split the canvas deliberately. Strong defaults:
  - **Title left / diagram right** (≈ 38/62 split) for concept diagrams.
  - **Title top / diagram below** for wide flows and timelines.
- Leave **at least 30% of the canvas empty**. White space is what makes it look expensive.

## 3. Typography

- One family, two or three weights. Good choices: **Inter, Manrope, DM Sans, Work Sans**.
- Scale (at 1920×1080):
  - Eyebrow / kicker: 20–24px, bold or semibold, uppercase, letter-spacing +2 to +3, accent color.
  - Headline: 64–88px, bold/extrabold, tight line height (1.05–1.15), letter-spacing −1 to −2.
  - Node labels: 28–36px semibold.
  - Supporting text: 20–24px regular, muted color, max ~8 words per node.
- Headline states the claim, not the topic ("Growth that feeds itself", not "Our Flywheel").
- **Max ~40 words on the whole slide.** Cut ruthlessly.
- Left-align body copy; center only inside symmetric shapes.

## 4. Color

**Colors live in the design system, never on the slide.** The roles below are the semantic tokens
(`color.bg`, `color.text.primary|muted`, `color.accent.1–5.fill|tint|border`, `color.hero.fill|text|tint`).
If the file already has a token system, use it. If a role is missing, add the token first. Pick
Dark or Light by **theme**, not by repainting. The art direction below describes what good token
values look like when creating a new system:

- The palette has exactly:
  - **Background** — either deep (navy #0B1026-ish, near-black) or warm off-white (#F7F5F0-ish). Dark backgrounds make color glow and feel premium on projectors.
  - **Ink** — primary text (white on dark / #111 on light).
  - **Muted ink** — ~60% contrast version for secondary text.
  - **One accent ramp** — 3–5 steps of a related hue family (e.g. violet → blue → teal → green) for sequenced items. Adjacent hues read as "one system that progresses."
  - **One hot highlight** — a contrasting color (coral, amber) used only on the hero.
- Never use pure saturated defaults (#FF0000, #0000FF). Pick tuned colors.
- **No gradients in themed decks**: there is no gradient token, so gradients can't switch with the theme. Get depth from tinted glow shadows (`shadow.glow.N`) and a blurred `color.atmosphere` shape instead. (Both slides kept their polish this way.)
- Text on colored fills must hit 4.5:1 contrast **in every theme**. Use `color.text.on-accent` (white on deep accents in Light, navy on luminous accents in Dark) rather than assuming white.

## 5. Shape language

- Pick one corner style and keep it: fully round (pills/circles) **or** 16–24px radius. Don't mix sharp and round.
- Consistent stroke weight across all connectors (4–8px at slide scale) with round caps.
- Nodes of the same role are identical in size and style. Variation signals meaning, so don't add it by accident.
- Number sequenced items (01, 02, 03…). Numbers are fast to read and add rhythm.

## 6. Depth and polish — what makes it eye-catching

- **Soft glow / shadow** on the hero and nodes: large blur (40–80px), low opacity (20–35%), tinted with the node's own color, not grey.
- **A background accent**: one large, very low-opacity shape (a big ring, a blurred radial blob in the accent color at 10–20% opacity) behind the diagram adds atmosphere without noise.
- **Layering**: background → atmosphere → connectors → nodes → labels. Connectors pass *under* nodes.
- **Arrows show direction clearly**: arrowheads sized proportionally (~3× stroke width), and they are the same color as their stroke.
- A tiny detail rewards attention: a small footnote, source line, or slide number at 16–18px in muted ink, aligned to the margin.

## 7. Diagram-specific recipes

- **Cycle / flywheel**: nodes evenly on a circle (angle = 360/n, start at −90° so node 1 is at the top). Curved arcs between nodes, gap before each node so arrows don't collide. Hero metric or core concept in the center.
- **Sequence / timeline**: one horizontal axis, equal spacing, milestone dots on the line, labels alternating above/below only if crowded.
- **Funnel**: stacked tapering bars, widths proportional to the real numbers, conversion % in the gaps between bars.
- **2×2 matrix**: thin axis lines, axis labels at the ends, quadrant names in muted ink, "us" as the one highlighted dot.
- **Hierarchy**: orthogonal elbow connectors, consistent sibling spacing, levels on fixed y rows.
- **Comparison**: two identical columns; highlight the recommended one, don't just list both.

## 8. Penpot build discipline

Load the `penpot-mcp` skill for API mechanics, and **follow `penpot-mcp/references/design-system-gate.md`**
for the build order and helpers. This section only covers build habits.

**Build order: system → components → slide → gate → review.**

1. **System first.** Read the file's tokens, library text styles (`Text/…`) and components. Anything the slide needs that's missing (a color role, a type size, a node style) gets added to the system *before* the slide uses it.
2. **Components for anything repeated.** Nodes, chips, bars, footers are component copies (variants for accent/emphasis). Override only text and size on copies; restyle by editing the main.
3. **Slide from tokens only.** Use the token-only helpers (`storage.ds.fill/stroke/radius/shadow/text`). No hex values, font sizes or shadow values in slide code.
4. **Gate.** `storage.audit(board)` in a separate call must return `pass: true`.

Habits:
- Name every shape semantically (`Node 03 / Better Product`, `Arc 2→3`, `Headline`).
- Group each logical unit so it moves together (tokens bind to the children, not the group).
- Compute geometry in code (angles, positions), never by eye. Geometry is exempt from tokens.
- Store helper functions in `storage` and rebuild them in the first call of a session.

## 9. Review loop (mandatory)

First the **compliance gate** must pass (see §8). Then export the board **by id** and critique it honestly:
1. Where does the eye land first? Is that the hero?
2. Squint test: does the structure still read when blurred?
3. Is anything misaligned, cramped, colliding, or clipped? Any text overflowing its box?
4. Is any text too small to read at 50% zoom?
5. Would this look at home in a top-tier keynote? If it looks like a default template, push contrast, scale, and white space further.

6. **Theme test:** switch to the other theme and export again. A compliant slide restyles with zero edits and stays readable; if it breaks, fix the *tokens*, not the slide.

Fix what you find and export again. If a fix is reusable (a new size, a role, a variant), make it
in the system so every slide benefits. Do at least one revision pass before calling it done, and
re-run the gate after every fix.
