# Design-System-First Build & Compliance Gate

How to build Penpot designs that are **provably** on-system, not just "asked to be". Every
pattern here was verified live on this instance (2026-10-11); the gotchas it works around are
listed in `SKILL.md` §"Verified on this instance".

## The rule

A design is **done** only when (1) the compliance gate below returns `pass: true` **and**
(2) the visual review (export + critique) passes. Prompting "follow the design system" is not
enough. The gate is what makes it true.

## 1. Architecture

| Concern | Mechanism | Why |
| --- | --- | --- |
| Color, radius, stroke width, spacing, opacity, shadows | **Design tokens** | Apply reliably; switch with themes |
| Text styles | **Library typographies** (`Text/…`) | Composite typography tokens apply unreliably via the plugin API (see gotchas) |
| Repeated elements | **Components + variants** (mains on a `Components` page) | Changes to a main propagate; copies keep text overrides |
| Gradients | Avoid in themed work. If needed, a **library color** with `gradient` (auditable via `fillColorRefId`, but it does **not** switch with themes) | No gradient token type |
| Geometry (x/y/w/h, path data), blur | Computed in code; exempt from the gate | Not tokenizable / layout-specific |

### Token sets and themes

```
slides/primitives      raw values: color.navy.950 …, space.base = 8, space.N = {space.base} * N,
                       radius.md / radius.full, stroke.hairline / connector / node
slides/theme/dark      semantic: color.bg, color.surface, color.text.primary|muted|on-accent|on-hero,
slides/theme/light       color.accent.N.fill|tint|border, color.hero.fill|text|tint,
                         color.track, color.atmosphere, shadow.glow.N, shadow.hero, shadow.chip
Themes (group "Mode"):  Dark = primitives + theme/dark;  Light = primitives + theme/light
```

- Semantic tokens reference primitives (`{color.indigo.700}`); designs use **only semantic tokens**.
- **Every theme must include the shared sets** (primitives). Activating a theme deactivates sets that
  aren't in it.
- Themes are **file-wide**: one deck = one active theme. Don't try to put a dark and a light slide
  in one file on the same tokens.
- Transparent colors: write `rgba(r, g, b, a)` **directly in the theme set**. It applies with alpha
  even though `resolvedValue` displays the hex without alpha. Hex8 (`#RRGGBBAA`) loses its alpha.

## 2. Token-only helpers (load into `storage` in the first call of every session)

```javascript
const T = n => { const t = penpotUtils.findTokenByName(n); if (!t) throw new Error('missing token ' + n); return t; };
const RADIUS = ['borderRadiusTopLeft', 'borderRadiusTopRight', 'borderRadiusBottomRight', 'borderRadiusBottomLeft'];
const lib = penpot.library.local;
const full = t => (t.path ? t.path + '/' : '') + t.name;
const TY = n => { const t = lib.typographies.find(x => full(x) === n); if (!t) throw new Error('missing typography ' + n); return t; };
storage.ds = {
  T, TY, RADIUS,
  // placeholder value is immediately replaced by the token binding
  fill: (s, n) => { s.fills = [{ fillColor: '#000000', fillOpacity: 1 }]; s.applyToken(T(n), ['fill']); },
  stroke: (s, colorTok, widthTok, align = 'inner', extra = {}) => {
    s.strokes = [{ strokeColor: '#000000', strokeOpacity: 1, strokeWidth: 1, strokeAlignment: align, ...extra }];
    s.applyToken(T(colorTok), ['strokeColor']); s.applyToken(T(widthTok), ['strokeWidth']);
  },
  radius: (s, n) => s.applyToken(T(n), RADIUS),
  shadow: (s, n) => s.applyToken(T(n), ['shadow']),
  // applyTypography drops lineHeight (and may drop textTransform): sync from the SAME style
  applyStyle: (t, name) => { const ty = TY(name); t.applyTypography(ty); t.lineHeight = ty.lineHeight; if (ty.textTransform) t.textTransform = ty.textTransform; },
  text: (parent, chars, typo, colorTok, o = {}) => {
    const t = penpot.createText(chars); if (!t) throw new Error('createText null');
    parent.appendChild(t);
    storage.ds.applyStyle(t, typo);
    t.fills = [{ fillColor: '#000000', fillOpacity: 1 }]; t.applyToken(T(colorTok), ['fill']);
    t.align = o.align || 'left';
    if (o.x != null) { t.x = o.x; t.y = o.y; }
    if (o.w) { t.resize(o.w, 40); t.growType = 'auto-height'; } else t.growType = 'auto-width';
    if (o.name) t.name = o.name;
    return t;
  }
};
```

Rules: never call `applyToken` twice with the same token on the same shape (it **toggles the binding
off**); never set a hex/size directly except the placeholder above.

## 3. Components

- Mains live on a `Components` page; build each variant as a board, `createComponent([board])`,
  then `penpotUtils.createVariantContainer([{ shape, properties: { Accent: '1' } }, …])`.
- Use flex-layout boards for components whose size varies per copy (bars, chips), so a copy's
  `resize()` keeps content centered.
- Look up a variant: `container.variants.variantComponents().find(v => v.variantProps.Accent === '3').instance()`.
  `library.components` lists **only one entry per variant group**, so go through the container.
- Override per copy: text `characters`, size. Don't override styling on copies; change the main.
- Editing a main requires its page to be **active** (`openPage` in its own call, edit in the next,
  switch back). Changes propagate to copies on other pages; text overrides survive.

## 4. The compliance gate

Run in a **separate call after the last write** (token bindings land asynchronously; same-call
audits report false violations).

```javascript
storage.audit = (root) => {
  const lib = penpot.library.local;
  const typos = lib.typographies.map(t => ({ ff: t.fontFamily, fs: String(t.fontSize), fw: String(t.fontWeight),
    lh: String(Number(t.lineHeight)), ls: String(Number(t.letterSpacing)), tt: t.textTransform || 'none' }));
  const v = [], seen = { shapes: 0 };
  const pathOf = s => { const p = []; let c = s; while (c && c.id !== root.id) { p.unshift(c.name); c = c.parent; } return p.join(' > '); };
  const walk = s => {
    if (s.type !== 'group') {                       // tokens can't bind to groups; check their children
      seen.shapes++;
      const tk = s.tokens || {}, issue = m => v.push({ path: pathOf(s) || root.name, issue: m });
      const fills = (s.fills || []).filter(f => !f.fillImage);
      if (fills.length > 1) issue('multiple fills (only first can be token-bound)');
      if (fills.length && !tk.fill && !fills[0].fillColorRefId) issue('hard-coded fill');
      const strokes = (s.strokes || []).filter(st => st.strokeStyle !== 'none');
      if (strokes.length && !tk.strokeColor) issue('hard-coded stroke color');
      if (strokes.length && !tk.strokeWidth) issue('hard-coded stroke width');
      if ((s.shadows || []).length && !tk.shadow) issue('hard-coded shadow');
      if (['rectangle', 'board'].includes(s.type) && (s.borderRadiusTopLeft || 0) > 0 && !tk.borderRadiusTopLeft) issue('hard-coded radius');
      if (s.opacity != null && s.opacity < 1 && !tk.opacity) issue('hard-coded opacity');
      if (s.type === 'text') {                      // must exactly match a library style
        const cur = { ff: s.fontFamily, fs: String(s.fontSize), fw: String(s.fontWeight), lh: String(Number(s.lineHeight)),
          ls: String(Number(s.letterSpacing)), tt: s.textTransform || 'none' };
        if (Object.values(cur).some(x => x == null || x === 'null' || x === 'NaN' || x === 'mixed')) issue('mixed text styles in one layer');
        else if (!typos.some(t => Object.keys(cur).every(k => t[k] === cur[k]))) issue(`text matches no library style (${JSON.stringify(cur)})`);
      }
    }
    (s.children || []).forEach(walk);               // includes component copies: overrides can break compliance
  };
  walk(root);
  const top = root.children || [];
  const inst = top.filter(c => c.isComponentInstance?.() || (c.children || []).some(k => k.isComponentInstance?.()));
  return { pass: v.length === 0, shapesChecked: seen.shapes, violations: v.length, details: v.slice(0, 40),
    componentBacked: `${inst.length}/${top.length} top-level elements use components` };
};
```

**Calibrate before trusting it:** it must FAIL a known hard-coded design and PASS the component
mains. (Here: v1 slides failed with 74/82 violations; all 13 mains passed. It also caught a real
bug, `applyTypography` dropping line height.)

## 5. Workflow

```
1. READ    tokens (penpotUtils.tokenOverview()), library typographies, components, pages
2. SYSTEM  add any missing tokens / styles / components FIRST (never one-off values on a slide)
3. BUILD   slide from semantic tokens, library styles, component copies only
4. GATE    storage.audit(board) in a separate call → must pass
5. REVIEW  export_shape(board id) → visual critique → fix in the SYSTEM if the fix is reusable
6. THEME   toggle the theme and export again: a compliant design restyles with zero edits
```

If a slide needs a value the system lacks, add it to the system (as was done with
`Text/Node Label`), not to the slide.
