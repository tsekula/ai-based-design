---
name: figcraft
description: Design with FigCraft (a Figma-class interface design tool) through its MCP server, either headless via the figcraft-cli or attached to the running FigCraft app. Use this skill whenever the user mentions FigCraft or figcraft-cli, or asks to create, edit, inspect, screenshot or export frames, components, auto layout, styles, variables, prototypes or pages in FigCraft, or to set up / connect the FigCraft MCP server, even if they only say "make a frame in the app" or "design a screen".
---

# FigCraft

FigCraft exposes an MCP server (`figcraft-cli mcp`) so you can create and edit layers, run any menu command, and inspect results as JSON or PNG. This skill covers picking the right backend, the working loop, and the conventions that trip agents up. The full v0.6.0 reference is in `references/mcp-v0.6.0.md`; grep it by heading rather than reading it whole (it is ~125k chars).

## 1. Pick the backend

Two MCP servers may be registered. Check which tools are available (`mcp__figcraft__*` vs `mcp__figcraft-app__*`).

| Backend | Server name | Use when |
|---|---|---|
| Attached | `figcraft-app` (`figcraft-cli mcp --attach 7979`) | The user has the app open and wants to watch changes live, or says "in the app". Needs the app started with `figcraft --control 7979`. |
| Headless | `figcraft` (`figcraft-cli mcp`) | Scripted/CI work, batch export, or no app running. One untitled in-process document, no window. |

Default to the attached backend when the user says "in the app" / "on the current page"; otherwise headless. If both are present and the request is ambiguous, ask once.

The two expose identical tools, so everything below applies to both. Differences:
- Attached edits are never auto-retried. If a call errors with "may have completed", **inspect the document before retrying** or you may duplicate the edit.
- Attached uses the app's fonts; headless uses built-in plus system fonts (`--no-system-fonts` or `FIGCRAFT_NO_SYSTEM_FONTS=1` for reproducible renders).
- `screenshot {window: true}` only makes sense attached.

### Setup (if the server is not registered)
Build with `cargo build --release -p figcraft-cli`; the Linux AppImage also bundles it (`FigCraft.AppImage cli mcp`). Then:

```sh
claude mcp add figcraft -- /path/to/figcraft-cli mcp                  # headless
claude mcp add figcraft-app -- /path/to/figcraft-cli mcp --attach 7979  # attached (app: figcraft --control 7979)
```
Claude Desktop: add the same `command`/`args` under `mcpServers` in `claude_desktop_config.json`. The control channel listens on 127.0.0.1 only.

## 2. Working loop

1. **Orient**: `inspect_document` (layer tree, selection, styles) before editing, especially in the attached app where the user may already have content.
2. **Create** with `create_node` (`type`: frame, rectangle, ellipse, polygon, star, line, arrow, text, vector, section, component, slice). `type` is required; give `x`, `y`, `width`, `height` for frames. Put styling in `props`.
3. **Edit** with `set_properties {ids, props}` or `run_command`.
4. **Verify**: `get_node`/`inspect_document` for numbers, `screenshot {ids}` for pixels. Do this after meaningful steps, not only at the end.
5. Group related edits in `batch` so they are one undo step and all-or-nothing.

Every mutation is one undo step and a failed command leaves the document unchanged, so it is safe to experiment; use `undo` to back out.

## 3. Conventions that matter

- Coordinates are page units, **y down**. `x`/`y` in `create_node`/`set_properties` are **relative to the parent frame** (page coords with no parent). Groups have no coordinate space of their own.
- Children of an auto layout frame are positioned by the layout. Do not set x/y; set `layout` (`horizontal`/`vertical`/`grid`), `gap`, `padding`, `mainAlign`, `crossAlign`, `sizingH`/`sizingV` (`fixed`/`hug`/`fill`). A child cannot `fill` an axis its parent `hug`s.
- Colours: `"#RRGGBB"` or `"#RRGGBBAA"`. Gradients: `{"type":"linearGradient","stops":["#7048E8","#1098AD"]}`.
- New layers become the selection; commands act on `ids` if given, else on the selection. Pass `ids` explicitly so you don't act on a stale selection.
- Programmatic calls never open dialogs.
- Text props (`fontFamily`, `fontStyle`, `fontSize`, `lineHeight`, ...) apply to the whole layer, or to chars `start`..`end` when given.

### Property names (learned by testing)
- `fill` takes one colour only. Gradients and multiple paints go in `fills`: `"fills":[{"type":"linearGradient","stops":["#0F172A","#1E1B4B"]}]`; a translucent paint is just `"#FFFFFF12"`.
- Strokes: `"strokes":["#FFFFFF26"]` plus `strokeWeight` (not `strokeWidth`), `strokeAlign`.
- Text colour is `textFills`; set `sizingH:"fill"` on text inside an auto layout card so it wraps instead of overflowing.
- Unknown prop names fail with a message listing every valid one, so read that list instead of guessing.
- `type_text {id, text}` replaces a text layer's content and keeps its styling.

### Building many layers fast
`batch` accepts `{command:"node.create", params:{type, parent, name, text, props}}` items, so a whole card grid goes in one call and one undo step. It returns ids in order, so create containers first, then fill them in a second batch using those ids. The `commands` value must be a valid JSON array (no blank lines between items, balanced braces), otherwise validation reports "expected array, received string".

Layout pattern that worked well: root frame (`layout:"vertical"`, `sizingV:"hug"`, fixed width) → header texts → row frame (`layout:"horizontal"`, `sizingH:"fill"`, `sizingV:"hug"`) → cards (`sizingH:"fill"`, `sizingV:"hug"`). Keep copy lengths similar across sibling cards so hugging heights stay even. Check with a screenshot and trim text that wraps unevenly.

Example card:
```json
{"type":"frame","name":"Card","x":100,"y":100,"width":320,
 "props":{"fill":"#FFFFFF","cornerRadius":16,"layout":"vertical","padding":24,"gap":12,"sizingV":"hug",
          "effects":[{"type":"dropShadow","color":"#00000026","offset":[0,4],"radius":16}]}}
```
then `create_node {type:"text", parent:<card id>, text:"Ada Lovelace", props:{fontSize:24, fontStyle:"Bold"}}`.

## 4. Finding commands

Nearly every menu action is a command. Use `list_commands {filter}` (e.g. `"align"`, `"layout"`, `"variable"`) to get ids and params, then `run_command {command, params}`. Also available as resources: `figcraft://command/{id}`. Common ones: `align.*`, `distribute.*`, `layout.add`, `component.create`, `instance.create`, `style.create`, `variable.bind`, `proto.interaction.add`, `object.wrapInSection`, `file.newFromTemplate`.

Starting from a template: `run_command {command:"file.newFromTemplate", params:{template:"dashboard"}}` (templates: mobile-app, landing-page, dashboard, design-system, wireframe-kit, social-posts, slides, icon-set). This opens a new unsaved document and makes it active, so avoid it in the attached app unless the user wants a new document.

## 5. Other tools

`export {ids, format: png|jpg|svg|webp|pdf|fig, scale|size, path?}` (without `path`, images return inline), `open_file`/`save_file` (`.figcraft`, `.json`, `.fig`, `.svg`, images), `select`, `undo`/`redo`, `pointer`/`key`/`type_text` for canvas-level gestures and text editing, `inspect_ui` for tool/view state.

## 6. When you need more

Search `references/mcp-v0.6.0.md` by heading for: Keyboard shortcuts, Editing vectors, Prototypes, Local/Team libraries, Overrides and variants, Slots, Boolean groups, Importing SVG/.fig/REST JSON, Comments, Version history, Branches, Live sessions, Plugins, Dev Mode (code generation: React, Leptos, SwiftUI, Compose), Effects, Ruler guides. For example:

```sh
grep -n '^##' references/mcp-v0.6.0.md
```

The doc describes v0.6.0; if the installed version differs, trust `list_commands` output over the doc.
