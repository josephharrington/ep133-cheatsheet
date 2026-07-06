# EP-133 KO2 Cheat Sheet - Agent Context

## What this is

A single self-contained HTML cheat sheet for the Teenage Engineering EP-133 K.O. II sampler.
Hosted (or to be hosted) on GitHub Pages. Designed to be both interactive in the browser and
print-friendly (A4, 2-column layout). No build step, no dependencies except Google Fonts CDN.

File: `index.html` — everything is in this one file.

---

## Architecture

### Data layer

All shortcut entries live in a `DATA` array of objects:

```js
{
  s: 'record',       // section id — must match a SECTIONS entry
  c: '[SHIFT] + [ERASE]',  // combo string (see rendering below)
  d: 'Description text',
  sub: true,         // optional: indented sub-row (used in system settings)
  sep: true,         // optional: adds a separator line above this row
  code: '101',       // optional: system settings shortcode (system section only)
  n: true,           // optional: marks entry as new in v2.5 (shows badge)
}
```

Sections are defined in a `SECTIONS` array. The `system` section id has special rendering behavior.

### Combo string rendering

`renderCombo(str)` parses combo strings into styled HTML via a single regex:

```
/\[([^\]]+)\]|(→|\+)|\(([^)]+)\)/g
```

- `[BUTTON]` → `.key` chip (dark pad style). `[SHIFT]` gets `.ks` (red).
- `+` or `→` → `.op` (gray operator)
- `(text)` → `.ctx` (italic muted context) — **gotcha**: the whole `(...)` is consumed as one
  span, so `[KEY]` tokens inside parentheses do NOT render as chips. If you need keys inside
  a parenthetical, use `→` or `+` instead of wrapping in parens.
- Bare text → `.ctx`

Menu paths like `mid → clk → off` render fully as ctx+op+ctx+op+ctx — all muted italic
with gray arrows. This is intentional for the system settings section.

### Sections

15 sections total. The `system` section is special:
- Gets class `full-width` on its wrapper div
- Contains a `rows-grid` div with an auto-generated header row (`.sys-head-row`)
- Sub-rows use flexbox with `order` to put the code column first in print
- In print: forced onto its own page via `break-before:page`, spans full width via `column-span:all`

All other sections flow in a standard 2-column CSS print layout.

### Static sections (hardcoded HTML, not DATA-driven)

Three panels above the main shortcuts grid are hardcoded HTML:
- **Orientation** — hierarchy diagram + commit loop explainer
- **From-scratch workflow** — collapsible `<details>` with 10 steps; key chips injected via `injectCombo(id, str)`
- **Quick reference** — 3 panels: punch-in FX numpad, sample library ranges + fader modes, tips list

---

## Print layout

- `@page { size: A4; margin: 10mm 12mm }`
- `main` uses `column-count: 2` with `column-gap: 13mm`
- Each `.section-group` has `break-inside: avoid`
- System settings: `column-span: all` + `break-before: page`
- Key chips need `-webkit-print-color-adjust: exact` to print backgrounds — this is already set
- FX numpad bottom row (`.fx-key.sp`) uses a warm cream tint in print instead of the dark
  background used on screen (dark doesn't print reliably without special settings)

---

## Fader modes (quick reference panel)

The 12 fader modes are hardcoded in the HTML fader table, not in the DATA array. The correct
modes (labeled on the device above each numpad key) are:

| Pad | Mode  | What it does           |
|-----|-------|------------------------|
| 7   | LEVEL | group/pattern volume (default ★) |
| 8   | PITCH | semitone pitch shift   |
| 9   | TIME  | playback speed/stretch |
| 4   | LPF   | low-pass filter        |
| 5   | HPF   | high-pass filter       |
| 6   | →FX   | FX bus send level      |
| 1   | ATK   | envelope attack        |
| 2   | REL   | envelope release       |
| 3   | PAN   | stereo panning         |
| .   | TUNE  | fine pitch             |
| 0   | VEL   | pad pressure response  |
| ENT | MOD   | modulation/LFO         |

An earlier version of this cheat sheet had these wrong (reverb, delay, distortion, etc.).
The above list is correct per the physical device.

---

## System settings codes

Codes (e.g. `101`, `320-331`) are shortcodes you type on the numpad once inside system
settings to jump directly to a setting. They're shown in the `code` field of each DATA entry
and rendered in a dedicated column in both screen and print views.

The `code` field accepts ranges like `'111-126'` — rendered as plain text, not parsed further.

---

## SEO / meta

Added in final session:
- `<title>EP-133 KO2 Cheat Sheet</title>`
- `<meta name="description">` and Open Graph tags
- Logo text is an `<h1>` (with CSS reset to match the original span styling)
- No em dashes anywhere — all replaced with ` - ` (hyphens) to avoid AI-generated feel
- Numeric range en-dashes (e.g. `001–099`) intentionally preserved

---

## Favicon

Inline SVG data URI in the `<link rel="icon">` tag — no external file needed. Cream background,
dark rounded square (like a device pad), "ko" in cream monospace text.

---

## Visual design language

The aesthetic is deliberately modeled on the EP-133 device itself: cream body, black pads,
red logo. This isn't arbitrary — it's the core design intent, and changes should stay within it.

**Palette (CSS variables):**
- `--bg: #f0ebe0` — warm cream, the dominant background (matches the device's body)
- `--card: #faf7f2` — slightly lighter cream for inset panels
- `--key-bg: #1a1a18` — near-black for key chips (matches the device's rubber pads)
- `--key-text: #ede8dd` — cream text on dark key chips
- `--red: #f15a22` — TE's button/control accent orange (verified against TE's official illustration
  assets), used sparingly: section numbers, filter active state, SHIFT key. The SHIFT key's darker
  bottom-border shade (`#b8380c`) is a proportionally-darkened variant of this color — keep them in
  sync if `--red` ever changes again.
- `--muted / --dim` — warm grays for secondary text, never cool/blue-toned

**Typography:**
- Space Mono (monospace) — used for all key chips, labels, section headers, codes. Chosen because
  it reads like device labeling.
- Inter (sans-serif) — body text, descriptions. Light weight (300) for most content.
- No system fonts in the primary UI — the font pairing is intentional and worth preserving.

**Key chips:**
- Dark background, cream text, 2px bottom border (gives a physical keycap feel)
- SHIFT key specifically uses red (`.ks` class) — it's the modifier, visually distinct
- In print: chips lighten to `#eceae6` background with `#999` borders (dark doesn't print
  reliably, but the keycap shape and bottom border are preserved)

**Tone:**
- All labels and UI text lowercase — matches the device's own screen typography
- No em dashes, no excessive punctuation — the cheat sheet should feel hand-made, not generated
- Section numbers use `((01))` format with double parens — a TE-ism referencing their UI style

**What to avoid:**
- Don't introduce blue, green, or other hues — the palette is red/orange, cream, and black.
  This is a working default, not a locked-in rule: it's held so far because it matches the
  physical device, but revisit it if a better device-accurate reference turns up (as happened
  when the accent shifted from red to orange after checking TE's own reference art)
- Don't add rounded cards, shadows, or gradients — the design is deliberately flat and typographic
- Don't switch to a sans-serif for labels or codes — monospace is load-bearing for the aesthetic
- Don't make it look like a generic dark-mode developer tool or a Notion page

---

## Known quirks / things to watch out for

1. **Combo string parentheses eat key chips.** `(+ [−] / [+])` renders the brackets as literal
   text, not chips. Use `→` or `+` outside parens if you need actual key chips.

2. **CSS vendor prefixes.** The file uses `-webkit-print-color-adjust` and
   `-webkit-column-break-inside`. Be careful with any automated find/replace that touches
   hyphens — a prior sed command accidentally turned these into `- webkit-` etc.

3. **System settings screen vs print.** Screen mode uses CSS grid for sub-rows
   (`minmax(140px,auto) 1fr auto auto`). Print mode overrides to flexbox with `order` to
   resequence columns. Both are in separate rule blocks — don't merge them.

4. **`sep-row` and `break-before`** — `.sep-row` adds a visual separator within the system
   settings table. The `.section-group.full-width` has `break-inside: auto` (not `avoid`) so
   the table can span multiple print pages if needed.

5. **The `.sys-head-row` is `display:none` in screen CSS** and `display:flex !important` in
   print CSS. It's generated dynamically in the `render()` function inside the `rows-grid` for
   the system section only.

6. **Badge column** — the fourth div in every row (`.row-badge`) holds the `v2.5` new-feature
   badge for entries with `n: true`. It exists in every row even if empty, to maintain grid
   alignment. In system sub-rows the flex `order` puts it last (order:4).

---

## Things that could still be improved

- The Google Fonts CDN dependency means the page doesn't work fully offline. Could be inlined
  as base64 data URIs for a fully self-contained file.
- No structured data / schema markup (could add `FAQPage` or `HowTo` schema for better Google
  rich results).
- The tips list and workflow steps are hardcoded HTML — not driven by the DATA array, so they
  can't be searched or filtered. Could be refactored if the search/filter scope needs to expand.
- Some descriptions could be tighter — written in a hurry and could use a human editing pass.
