---
name: penpot-mcp
description: >
  Use whenever working in Penpot through the Penpot MCP tools (the "Penpot Design at SkyOverHill"
  connector: execute_code, export_shape, penpot_api_info, high_level_overview). Triggers include:
  creating or editing designs, slides, diagrams or boards in Penpot; design systems, tokens,
  library colors/typographies/components and variants; auditing or renaming layers; prototyping
  (flows, interactions, overlays, animations); exporting shapes; design-to-code from a Penpot file;
  and troubleshooting the Penpot MCP connection. Read before the first execute_code call.
---

# Penpot MCP Skill

Workflows for creating, auditing and maintaining designs and design systems in Penpot via the
official Penpot MCP Server. Forked from [`ar27111994/penpot-mcp`](https://github.com/ar27111994/penpot-mcp)
v1.6.0 (MIT, see `LICENSE-UPSTREAM`), trimmed to this environment and corrected where upstream
contradicted this instance. For **visual quality** of slides and diagrams, also load the
`slide-diagram-design` skill. This skill covers mechanics; that one covers art direction.

## Verified on this instance (2026-10-11), takes precedence over everything below

| Topic | Upstream said | What's actually true here | Evidence |
| --- | --- | --- | --- |
| Child `x`/`y` | Read-only for parented shapes | Writable, **absolute page coords** | Server overview; flywheel build positioned ~40 children this way |
| `appendChild` z-order | Ignores order | Appends **on top**; use `setParentIndex(i)` / `insertChild(i, s)` to go lower | Arcs needed `setParentIndex` to sit under nodes; everything else stacked in append order |
| Blur | `shape.blurs = [{ type:'layer-blur', value }]` | `shape.blur = { value }` and `shape.backgroundBlur = { value }`, single objects | `penpot_api_info ShapeBase.blur` / `Blur` |
| `export_shape` | Unreliable, don't use for verification | Worked every time (PNG of a 1920×1080 board) | 3/3 exports succeeded |
| Batch size | ~10 ops per call max | ~60 shape ops in one call succeeded. Still keep one logical unit per call so failures are easy to localize | Flywheel build |
| Tools | 5 incl. `import_image` | **4 only** (remote): `execute_code`, `export_shape`, `penpot_api_info`, `high_level_overview` | Tool list |
| Tab suspension | n/a | `"plugin tab appears to be suspended (no heartbeat for Ns)"` happens when the Penpot tab is backgrounded. Ask the user to focus the tab; `penpot_api_info` still works meanwhile | Observed mid-session |
| `toLocaleString` | n/a | **Silently a no-op** in the plugin sandbox: `(10000).toLocaleString('en-US')` returns `"10000"`. Format numbers with a regex: `String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ',')` | Funnel build: values rendered without separators until fixed |
| `storage` lifetime | Resets on server restart | Also empty after a reconnect or tab resume. Every build must re-create its helpers in the first call | Empty after the tab-suspension episode |
| Text bounds right after creation | n/a | `auto-height` text keeps its `resize()` height until the layout pass, so containment checks in the same call can false-positive. Re-check in a later call or trust the export | Slide number flagged outside safe area; export showed it fine |
| Token API in plugins | Docs: "coming soon" | **Works** for color, spacing (math like `{space.base} * 3`), borderRadius, borderWidth, opacity, shadow, number, and sets/themes. Theme switching re-skins bound shapes | Design-system build, 2026-10-11 |
| Typography tokens | n/a | **Unreliable via plugin**: composite typography tokens (and `fontSizes` tokens named `fs.*`) often bind (`shape.tokens` shows them) but **don't apply** (text stays Source Sans 14). Results varied run to run. **Use library typographies** for text instead | ~20 isolated probes |
| `applyTypography` | n/a | Applies family/size/weight/letter-spacing but **drops lineHeight**. Re-set `t.lineHeight = typo.lineHeight` from the same style | Gate caught 1.2 vs 1.15 |
| `LibraryTypography` fields | `typo.fontFamilies` | Field is `fontFamily`; set font via `typo.setFont(font, variant)`. Text layers expose **no reference** to their library style, so audit by value match | API docs + probe |
| `applyToken` twice | n/a | Applying the **same token again toggles the binding off** | Re-apply left `tokens: {}` |
| Tokens on groups | n/a | `applyToken` on a group **silently does nothing**. Bind children instead | Probe |
| Token name prefixes | n/a | A name can't be both a token and a group prefix (`color.hero` + `color.hero.text` → error). Use leaf names like `color.hero.fill` | Error on create |
| Alpha in color tokens | n/a | `rgba(...)` keeps alpha when applied; hex8 loses it; `resolvedValue` shows hex **without** alpha either way. Verify on the shape | Shadow opacity probe |
| Themes vs sets | n/a | Activating a theme **deactivates sets not in it**; include shared sets (primitives) in every theme. Themes are file-wide (one look per file) | Probe |
| Cross-page edits | n/a | Modifying a shape on a non-active page throws `Cannot modify a page that is not currently active`. `openPage` first (own call) | Editing component mains from Deck |
| Variant listing | n/a | `library.components` lists **one entry per variant group**; enumerate via `container.variants.variantComponents()` | 4 listed vs 13 mains |
| `export_shape('page')` | n/a | Can time out (500, `locator.waitFor`). Export boards by id instead; `'selection'` exports whatever the user has selected | Observed |
| Token bindings timing | Async | Bindings land after the call returns, so **run audits in a separate call** | Same-call audit: 10 false violations; next call: 0 |

When something here and the plugin API docs disagree, **the API docs (`penpot_api_info`) and a
live probe win**. Update this table when you learn something new.

### Other confirmed mechanics

- Gradients (`fillColorGradient` / `strokeColorGradient`) use **0–1 coordinates relative to the
  shape's bounding box**. For a path stroke, compute start/end from the path's actual endpoints
  within `path.bounds`.
- Arrowheads: stroke caps `strokeCapEnd: 'triangle-arrow'` (also `line-arrow`, `circle-marker`,
  `diamond-marker`, `square-marker`, `round`, `square`). Head size scales with `strokeWidth`.
- Curves: set `path.content = "M x y C x1 y1 x2 y2 x y"` in absolute coordinates. For circular
  arcs, use a cubic Bézier approximation (`k = 4/3·tan(Δθ/4)`) rather than SVG `A` commands.
- Shadows: `color: { color: '#HEX', opacity: n }`. Tinted, large-blur shadows give a glow.
- Text: `penpot.fonts.all.find(f => f.name === 'Inter')` then `font.applyToText(text, variant)`; set
  `fontSize`/`lineHeight`/`letterSpacing` as strings; after `resize()` always reset `growType`.
  **`findByName` matches by substring (verified):** `findByName('Inter')` returned **Inter Tight**, and the v1 flywheel shipped in the wrong font unnoticed. Always use `penpot.fonts.all.find(f => f.name === 'Inter')`.

---

## 1. Connection

MCP acts on the **currently focused page** of the Penpot tab that owns the connection
(**File → MCP Server → Connect**, or the MCP plugin). Only one tab can own it.

**Always check first:** call `high_level_overview` (once per session) or `penpot_api_info`. If
it works, skip setup. If `execute_code` fails with the suspended-tab error, ask the user to click
into the Penpot tab and retry. Don't diagnose further until they have.

Troubleshooting (from upstream):
- `No Penpot instance connected for user token`: plugin not connected, or key mismatch
- `Already connected to a transport`: close other MCP clients/tabs
- Expired MCP key: regenerate in Penpot → Your account → Integrations; update client config
- After a Penpot server upgrade, stale plugin code can look like a suspended tab: clear site
  data, hard-reload, reconnect

Setting up a new Claude Code connection: `claude mcp add --transport http penpot <URL>`, or a
project `.mcp.json` with `{"mcpServers":{"penpot":{"type":"http","url":"<URL>"}}}`. The URL is
`https://<penpot-domain>/mcp/stream?userToken=<MCP_KEY>`. **Never commit the key**; keep it in
user-scoped config or an env var.

## 2. Tools

| Tool | Use |
| --- | --- |
| `high_level_overview` | Read once per session before other tools |
| `penpot_api_info` | Look up a type/member (`type`, optional `member`). Use it whenever unsure of a property |
| `execute_code` | Run JS in the plugin context: `penpot`, `penpotUtils`, `storage` |
| `export_shape` | PNG/SVG of a shape (`shapeId`, or `'page'` / `'selection'`) for visual review |

Read `references/penpot-api-patterns.md` before non-trivial `execute_code` work (tokens,
libraries, pages, effects, interactions, idempotency helpers).

## 3. Safety-first workflow

```
1. READ   → inspect pages, structure, library, tokens (never skip)
2. PLAN   → state intended changes before applying (no undo via MCP)
3. WRITE  → one logical unit per call (e.g. "all arcs", "the left text column")
4. VERIFY → structural read (names, counts, bounds) AND export_shape for visual work
```

- **Pages:** switch with `await penpot.openPage(page)` in one call, write in the next (defensive;
  older Penpot versions write to the wrong page otherwise). Confirm `penpot.currentPage?.name` first.
- **`remove()`** can appear to succeed and the shape can reappear in later reads. Re-check in a
  separate call.
- **`storage`** persists helpers and data across calls but resets on server restart. Always read
  with a fallback (`storage.x || default`) and re-resolve shapes by id/name rather than trusting
  stale references.
- **Idempotency:** check-before-create for pages, boards, colors, typographies, token sets
  (helpers in the API reference §10). Re-runs should never duplicate.
- **Selection:** copy `penpot.selection` into `storage` immediately; it changes under you.

## 4. Briefing an agent (prompt engineering)

Define the role precisely:

```
GOOD: "You are a Senior Product Designer expert in design systems, WCAG accessibility,
       Penpot plugin API constraints and Penpot-to-code workflows. You never invent tokens,
       colors or components not present in the file. You work in small reversible batches."
```

Brief template:

```
CONTEXT: [product, audience, current state of file]
GOAL: [specific outcome]
INPUTS: [page/board/component names, token paths, brand colors, real copy]
CONSTRAINTS:
  - One logical unit per execute_code call; verify after each
  - Check-before-create (idempotent helpers)
  - Never switch page and write in the same call
  - Only font weights confirmed installed for the family
  - Shared data/helpers in `storage`
QUALITY CRITERIA: [how we'll know it's done; for visuals, an export reviewed against the brief]
```

Always-include negatives: no invented colors outside the token set (when one exists); no
duplicate colors/typographies; no unconfirmed font weights.

### Token-aware RULESET (prepend for design-system work)

```
SOURCE: Penpot MCP only · NO_GUESSING · IF_MISSING: mark TODO · PREFER: structured data
OUTPUT: deterministic, stable ordering · PAGE_SWITCH: separate call · IDEMPOTENCY: check-before-create
```

Token tiers: Global (`color.base.neutral.100`) → Semantic (`color.text.primary`) → Component
(`color.button.primary.bg`). References use `{token.path}`. Token application is async: read
`shape.tokens` in a later call.

## 5. Workflow recipes: read the matching reference first

- **Any new design or slide → `references/design-system-gate.md` (mandatory)**: token/typography/component
  architecture, token-only helpers, and the compliance gate that must pass before work is "done"
- API, tokens, pages, effects, storage, idempotency → `references/penpot-api-patterns.md`
- Design system build / audit / migration / rebrand → `references/design-system-workflows.md`
- Design → HTML/CSS/React, token extraction, handoff → `references/design-to-code-workflows.md`
- Flows, interactions, overlays, animations → `references/prototyping-workflows.md`
- Slides and presentation diagrams → `slide-diagram-design` skill

## 6. File best practices

- **Naming:** function-based (`label-primary`, `Node 03 / Richer Data`), never `Rectangle 23`;
  hierarchy with `/` (`component/card/default`, `overlay/confirm-delete`).
- **Structure:** group each logical unit (node = disc + number + label). Use flex/grid layout for
  rows/columns with consistent spacing, and absolute placement for computed geometry (cycles, arcs).
- **Spacing:** 8px base unit; no invisible spacer rectangles.
- **Components:** register via `createComponent([shapes])` (array); variants via
  `penpotUtils.createVariantContainer([...])`.
- **Prototyping:** flow entry boards `/flows/<journey>-start`; overlays `overlay/<name>`.
- **Accessibility:** WCAG AA contrast for all text; never color alone for status; 44px touch targets.
- **Handoff:** developer-readable names, no duplicates, one source of truth.

## 7. API gotchas (upstream list, filtered to what still applies)

| Gotcha | Mitigation |
| --- | --- |
| `width`/`height` read-only | `shape.resize(w, h)` |
| `parentX`/`parentY`/`bounds` read-only | `penpotUtils.setParentXY`, or set absolute `x`/`y` |
| Children of flex/grid boards ignore x/y | Use layout props, or `layoutChild.absolute = true` |
| `createText` may return null | Guard before styling |
| Text clips after `resize()` | Reset `growType` after every resize; `textBounds` for rendered size |
| Fill/stroke arrays are immutable inside | Replace the whole array |
| Colors | Uppercase hex strings (`'#FF5533'`) |
| Font weight rejected | Only weights in `font.variants` |
| Library typography | `fontFamilies` (not `fontFamily`); `fontSize` as string |
| `LibraryColor` hex | `.color = '#HEX'` (not `.fillColor`) |
| `Page.findShapes()` | Takes a criteria object (`{ type: 'board' }`), not a predicate. `penpotUtils.findShapes` takes a predicate |
| `horizontalSizing = 'fill'` may set `flipX` (unverified) | Read `flipX` back after sizing changes |
| Layout reads right after changes | `await board.waitForLayoutUpdate()` (≥ 2.17) instead of sleeping |
