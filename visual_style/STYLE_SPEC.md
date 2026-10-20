# Marketing Data Visual Style — Spec for AI agents

Read this before creating any visualisation (diagram, explainer, slide) for the
marketing data knowledge base. It describes the **Light** style in full and the
**Vibrant** style briefly. Everything here exists as tokens, styles and
components in the template file, so build with those rather than raw values.

- **Template:** [`marketing-data-style-template.figcraft`](marketing-data-style-template.figcraft) (open in FigCraft)
- **Audience:** non-technical marketing business users. Plain language, one idea per frame.
- **Default style:** Light. Use Vibrant only when asked for "vibrant", "bold" or slide/presentation styling.

## Template contents

| Page | What it is | Edit? |
|---|---|---|
| Style Guide - Light | Light guide + all main components (dashed purple outlines) | No — read and place instances only |
| Style Guide - Vibrant | Vibrant guide + `Background / Haze` component | No |
| Example - Light explainers (Data Retention) | 8 finished Light illustrations | No — copy patterns from here |
| Example - Slides (Vector and Graph DB) | Light and Vibrant 1920×1080 slides | No |

Add new work on a **new page** (`page.add`). Never modify the guide pages or the main components.

## Workflow (FigCraft MCP)

1. `open_file` the template (headless), or open it in the app and use the attached server.
2. `page.add {name}` then `page.select {id}`.
3. Create the root frame with the frame recipe below.
4. `component.list` → find components by name → `instance.create {component: <id>, parent}`.
   - For a variant set, pass the **set id**, then `instance.setProperties {ids, properties: {Type: "Focus", Name: "Braze"}}`. Variant and text properties are set the same way.
   - Components without text properties: edit the text layers inside the instance with `node.set {ids:[<child id>], characters}`.
5. Any layer you draw yourself must be bound: `variable.bind` for fills, strokes, radius, gap and padding; `style.apply` for text, then bind the text colour with `variable.bind {field: "fills/0/color"}`. Use only the semantic `color/...` variables below, never primitives or hex.
6. Verify with `screenshot`, then check the rules in [Writing rules](#writing-rules).

### FigCraft gotchas

- New frames default to a **white fill and clip on**. Use `fills: []` for layout-only frames, and set `clip: false` on any frame whose children have shadows or glows, otherwise you get square artefacts at rounded corners.
- Text inside auto-layout cards needs `sizingH: "fill"` to wrap.
- Children of auto-layout frames are positioned by the layout; only diagram canvases (`layout: none`) use x/y.
- `variable.setMode` must always be given `ids`; without them it changes the whole page.

## Frame recipe (Light)

| Element | Values |
|---|---|
| Illustration frame | width 1400, vertical auto layout, fill `color/bg/canvas`, stroke `color/border/default` 1px, radius `radius/lg`, padding `space/xl`, gap `space/lg` |
| Header | `Explainer / Illustration header` instance, sizing Fill |
| Content cards | fill `color/bg/surface`, stroke `color/border/default`, radius `radius/md`, padding `space/lg`, gap `space/md` |
| Footer | `Explainer / Source line` instance, sizing Fill (always last) |
| Slide | 1920×1080, padding 64, same tokens |

## Tokens (Theme collection, mode **Light**)

### Colour roles

| Variable | Light | Meaning in network diagrams | Meaning in explainers |
|---|---|---|---|
| `color/author/fill` · `tint` · `ink` | #2F5BEA · #EAF0FE · #1F3FB0 | Author (researcher) | People, sources, explicit consent |
| `color/connector/fill` · `tint` · `ink` | #E8622C · #FEF0E8 · #B24418 | Connector / hub — who to reach first | **Focus**, enforcement, outcomes, eyebrows |
| `color/journal/fill` · `tint` · `ink` | #12A594 · #E3F6F3 · #0B7468 | Journal | Legitimate interest, platforms, "Yes" |
| `color/institution/fill` · `tint` · `ink` | #7B5CD6 · #F0EBFB · #5638A8 | Institution | Relationships, ownership |
| `color/status/positive` | #1E9E5A | — | Live / in use today |
| `color/status/negative` | #D64545 | — | Lapsed, expired, blocked |
| `color/edge/default` · `strong` · `highlight` | #C5CCD8 · #8A93A6 · #E8622C | Co-authorship · strong · influence path | Arrows (default/strong), enforced path |
| `color/bg/canvas` · `surface` · `subtle` | #F7F8FA · #FFFFFF · #EEF1F5 | Page/canvas · cards · subtle bands | Same; subtle = banners, record boxes, neutral chips |
| `color/border/default` · `strong` | #E2E6EC · #C5CCD8 | Card outlines · dashed out-of-scope | Same |
| `color/text/primary` · `secondary` · `muted` · `on-accent` | #1B2233 · #5B6478 · #8A93A6 · #FFFFFF | Headings · body · captions/sources · text on solid fills | Same |

Rules: **orange marks the one or two things to look at** — never decorate with it. Grey dashed means absent or out of scope; never use colour for absent things. Every colour must also be explained by shape, text or a legend.

### Spacing, radius, stroke

`space/xs` 4 · `space/sm` 8 · `space/md` 16 · `space/lg` 24 · `space/xl` 40 —
`radius/sm` 6 · `radius/md` 12 · `radius/lg` 20 · `radius/pill` 999 —
`stroke/hairline` 1 · `stroke/edge` 2

### Text styles (Inter in Light)

| Style | Size / weight | Use |
|---|---|---|
| Page title | 32 Bold | Guide or deck title only |
| Title | 28 Bold | Illustration headline (the takeaway) |
| Heading | 28 SemiBold | Card headings ("What Segment does next") |
| Metric | 52 Bold | Big numbers in metric cards |
| Subtitle | 24 Regular | Slide subtitles |
| Body | 20 Regular | Explanations, bullet text |
| Label | 18 SemiBold | Eyebrows, row labels, node names, caps headers |
| Caption | 14 Regular | Notes, axis ticks, legends, sources |

Text colour: primary for headings, secondary for body, muted for captions and sources; eyebrows use `color/connector/ink`.

## Components (page "Style Guide - Light")

Text properties are listed in brackets; set them with `instance.setProperties`.

### Explainer layout

| Component | Variants | Use when |
|---|---|---|
| `Explainer / Illustration header` | — [Eyebrow, Title, Subtitle] | Top of every illustration. Eyebrow `NN · TOPIC`, Title = takeaway |
| `Explainer / Source line` | — [Text] | Last line of every illustration |
| `Explainer / Metric card` | Accent: Blue, Teal, Orange [Metric, Caption] | 3–5 headline numbers in a row |
| `Explainer / Out-of-scope banner` | — [Label, Left, Right] | Stating what the illustration does not cover |

### Explainer building blocks

| Component | Variants | Use when |
|---|---|---|
| `Explainer / System node` | Type: Default, Focus, Out of scope [Name, Role] | Boxes in a system/data-flow diagram |
| `Explainer / Legend` | — | Key under every diagram (edit items inside) |
| `Explainer / Process step` | Role: Source, Step, Outcome | Building process lanes: route start → actions → end state |
| `Explainer / Process lane` | — | A complete example lane to copy |
| `Explainer / State pill` | State: Active, Off, Final [Label] | Before → after state changes (pair with a labelled grey arrow) |
| `Explainer / Status pill` | State: Live, Pending [Label] | Status column in tables, column headers |
| `Explainer / Chip` | Value: Yes, No, Neutral [Label] | Cells of comparison matrices (Neutral = Only, n/a, partial) |
| `Explainer / Tag` | Style: Version, Purple, Teal, Blue [Label] | Version labels (V1…) and role/topic tags above card titles |
| `Explainer / Matrix column header` | Status: Live, Planned [Version, Title, Status text] | Comparing options or phases side by side |
| `Explainer / Direction arrow` | — [Label] | Showing the direction of change across matrix columns |
| `Explainer / Timeline bar header` + `Explainer / Timeline bar row` | — [Category, Sublabel, Bar label, Note] | Durations/retention periods on a shared axis (resize the Bar) |
| `Explainer / Event timeline` | — | Events over months: periods, actions, lapses |
| `Explainer / Numbered rule` | — [Number, Title, Body] | 3–5 rules that always apply |
| `Explainer / Open item` | — [Number, Text, Ref] | Open decisions / to-dos with Jira keys |
| `Explainer / Result callout` | — [Title, Body] | Outcome of a worked example |
| `Explainer / Note card` | — [Title, Body] | Side notes under a diagram, rows of three |
| `Explainer / Bullet group` | — [Heading] | Grouped bullet lists with a coloured caps heading |
| `Explainer / Record card` | — | What a log/audit record contains (illustrative values) |
| `Explainer / Colour key` | — | Final "terms and colours" frame |
| `Explainer / Glossary column` | — | Term + definition list |

### Network diagrams

| Component | Variants | Use when |
|---|---|---|
| `Network / Node` | Type: Author, Connector, Journal, Institution | Nodes on a network canvas (frame, `layout: none`, fill `color/bg/canvas`, clip on). Scale Author size with degree |
| `Network / Edge` | Type: Default, Strong, Influence | Links; draw before nodes so nodes sit on top |
| `Network / Name pill` | — [Label] | Labels for hubs, journals and institutions only — never every author |

## Choosing a pattern

| The message is about… | Use |
|---|---|
| Who influences whom / communities | Network canvas + `Network / *` |
| Where data flows between systems | `Explainer / System node` + arrows + `Explainer / Legend` |
| A process with several entry routes | Lanes of `Explainer / Process step` |
| How long something lasts | `Explainer / Timeline bar row` table |
| What happens over time for one person | `Explainer / Event timeline` |
| Before vs after / reversible vs final | `Explainer / State pill` pairs |
| Comparing options or phases | `Explainer / Matrix column header` + `Explainer / Chip` |
| Rules or principles | `Explainer / Numbered rule` |
| Headline numbers | `Explainer / Metric card` row |
| Who owns what | Cards with `Explainer / Tag` + bullets, grey arrows between |

## Writing rules

1. **One idea per frame.** Number illustrations `NN · TOPIC` in the eyebrow.
2. **Headline = takeaway**, sentence case ("One valid basis is enough to stay contactable"), not a topic label.
3. Subtitle: one or two plain-language lines. No jargon without a glossary entry.
4. **Orange = focus**: at most one or two highlighted elements per diagram.
5. **Every diagram has a legend**; every frame ends with a `Source:` line naming the document and sections.
6. Mark example data as illustrative. Keep sibling card copy at similar lengths so heights align.
7. Abbreviations (E.C., L.I., CDI, SNID…) are spelled out on first use or in a glossary frame.

## Vibrant style (summary)

Switch a root frame with `variable.setMode {ids:[<frame>], collection:"Theme", mode:"Vibrant"}`: Montserrat
Black/ExtraBold Italic, saturated palette (author blue, connector magenta, journal green, institution violet),
rounder radii, `Shadow/Tile` on cards, `Glow/Node` on hubs, gradient styles (`Gradient/Cool` authors,
`Gradient/Warm` hubs). Pills, badges and callouts use a solid `color/bg/pill` fill with a white rim and
`Glow/Soft pill`, black text. Put a `Background / Haze` instance (Arrangement A/B/C, varied across slides) as the
locked bottom layer. Headlines use the `Hero` style (uppercase), badges the `Badge` style. Full rules are on the
"Style Guide - Vibrant" page.
