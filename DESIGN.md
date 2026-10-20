---
name: Stridecraft
description: A gilt grimoire HUD where the strider is the only subject and the numbers read like engraved instruments.
colors:
  indigo-night: "#0a0b20"
  indigo-plate: "#14173f"
  indigo-void: "#070818"
  indigo-glow: "#1d2057"
  ivory-gold: "#efe7cf"
  lavender-mist: "#a8a5c8"
  antique-gold: "#cfa84e"
  antique-gold-dim: "#8f7435"
  antique-gold-faint: "rgb(207 168 78 / 0.28)"
  vermilion: "#e0674d"
typography:
  display:
    fontFamily: "Forum, 'Trajan Pro', Georgia, serif"
    fontSize: "clamp(1.75rem, 1.3rem + 2.6vw, 3.5rem)"
    fontWeight: 400
    lineHeight: 1.2
    letterSpacing: "0.06em"
  figure:
    fontFamily: "Forum, 'Trajan Pro', Georgia, serif"
    fontSize: "clamp(2rem, 1.6rem + 1.6vw, 2.75rem)"
    fontWeight: 400
    lineHeight: 1.1
    fontFeature: "tabular-nums lining-nums"
  body:
    fontFamily: "'Alegreya Sans', 'Gill Sans', system-ui, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Forum, 'Trajan Pro', Georgia, serif"
    fontSize: "0.8125rem"
    fontWeight: 400
    letterSpacing: "0.18em"
spacing:
  xs: "0.25rem"
  sm: "0.5rem"
  md: "1rem"
  lg: "2rem"
  xl: "3rem"
components:
  button:
    backgroundColor: "transparent"
    textColor: "{colors.antique-gold}"
    padding: "0.35rem 0.9rem"
  button-hover:
    backgroundColor: "{colors.antique-gold}"
    textColor: "{colors.indigo-night}"
  button-primary:
    backgroundColor: "{colors.antique-gold}"
    textColor: "{colors.indigo-night}"
    typography: "{typography.label}"
    padding: "0.6rem 1.25rem"
  button-primary-hover:
    backgroundColor: "{colors.ivory-gold}"
    textColor: "{colors.indigo-night}"
  gilt-frame:
    backgroundColor: "{colors.indigo-plate}"
    textColor: "{colors.ivory-gold}"
    padding: "1rem"
  stat-plaque-value:
    textColor: "{colors.ivory-gold}"
    typography: "{typography.figure}"
  stat-plaque-label:
    textColor: "{colors.lavender-mist}"
    typography: "{typography.label}"
  text-input:
    backgroundColor: "{colors.indigo-void}"
    textColor: "{colors.ivory-gold}"
    padding: "0.5rem 0.75rem"
  chevron-button:
    textColor: "{colors.antique-gold}"
    rounded: "50%"
    size: "2.75rem"
---

# Design System: Stridecraft

## Overview

**Creative North Star: "The Gilt Grimoire"**

A character sheet in an alchemist's gilt frame. Deep indigo ground, antique gold line work, pale ivory-gold text. The strider is the only subject: it stands on a summoning circle lying on the floor of a full-screen stage, and every panel is a hairline-gold plate floating over that scene. Numbers are set like engraved instruments, in a classical display face with tabular lining figures.

The mood is calm and rewarding, never loud. Nothing in the product decays, so nothing in the interface alarms; the one warning colour exists only for errors. Gold is line work and one filled action, not a surface colour. The world is recognisable with content removed by two things: the notched-corner frame and the sigil ring.

Phone and desktop are equal. Phone stacks bar, name plate, scene, then a compact 2x2 stat strip; desktop (62rem and up) moves the stats to a 22rem right column beside the scene.

**Key Characteristics:**
- Dark only (`color-scheme: dark`); indigo glow pooled behind the scene, faint gold bloom at the lower left.
- Hairline gilt frames with notched corner brackets; ornamental divider (diamond between two crescents).
- Sigil ring: circles, a hexagram, and a slowly turning tick ring, drawn in on load.
- Two faces only: Forum for display, labels and figures; Alegreya Sans for reading text.
- Square-cornered controls; the only round shapes are the ring, the creature slot and the chevron buttons.

## Colors

Restrained and tonal: indigo carries the surface, gold carries the line, ivory carries the text.

### Primary
- **Antique Gold** (#cfa84e): frame corners, ring strokes, link and button text, focus outline, the filled primary action, text selection.
- **Antique Gold Dim** (#8f7435): hairline borders on buttons and inputs, divider rules, ring tick marks, scrollbar thumb.
- **Antique Gold Faint** (rgb(207 168 78 / 0.28)): frame border and inner inset line, hairlines between stat cells.

### Secondary
- **Vermilion** (#e0674d): error and failed-sync text only.

### Neutral
- **Indigo Night** (#0a0b20): page ground and text-on-gold.
- **Indigo Plate** (#14173f): the raised-surface token; the frame itself paints the `plate` gradient from indigo (29 32 87 at 0.88) to night (10 11 32 at 0.92).
- **Indigo Void** (#070818): sunken wells (inputs, scrollbar track, scene floor fade).
- **Indigo Glow** (#1d2057): the light behind the scene and the top of the plate gradient.
- **Ivory Gold** (#efe7cf): primary text, stat figures, primary button hover fill.
- **Lavender Mist** (#a8a5c8): secondary text, labels, subtitles, the bar and sync line.

### Named Rules
**The Gold Is Line Rule.** Gold draws edges, rules and the single filled action. It is never a large background fill.
**The One Alarm Rule.** Vermilion is the only state colour and only marks errors. Success has no colour of its own; it is calm text.

## Typography

**Display Font:** Forum (with Trajan Pro, Georgia, serif)
**Body Font:** Alegreya Sans (with Gill Sans, system-ui, sans-serif), weights 400, 500, 700 loaded
**Label/Mono Font:** none; labels reuse Forum

**Character:** an inscribed Roman capital face paired with a warm humanist sans. Display carries everything that is engraved (names, labels, figures, primary button); the sans carries anything read as a sentence.

### Hierarchy
- **Display** (400, clamp(1.75rem, 1.3rem + 2.6vw, 3.5rem), 1.2, 0.06em tracking): the strider name on the banner; wraps anywhere so long names never overflow.
- **Figure** (400, clamp(2rem, 1.6rem + 1.6vw, 2.75rem), 1.1, tabular lining numerals): stat values.
- **Body** (400, 1.0625rem, 1.5): lore text, subtitles, messages. Lore capped at 65ch.
- **Label** (Forum 400, 0.8125rem, 0.18em tracking, uppercase): stat names, form labels, primary button (at 0.18em as well). The top bar and its quiet log-out button use the same size at 0.12em.

### Named Rules
**The Engraved Numerals Rule.** Every number that reports progress uses Forum with tabular lining figures, so columns of stats align.

## Layout

A full-screen scene (`min-height: 100svh`, overflow hidden): the stage is absolutely positioned behind, and a CSS grid of panels floats above it using named areas. Page padding is 1rem on phone, 2rem on desktop. Gaps use the 1rem step.

Spacing scale in use: 0.25, 0.5, 1, 2, 3rem. Breakpoint: one, at 62rem (desktop split to a content column plus a 22rem right column). Adoption mirrors the dashboard: banner on top, lore and name form in the right column on desktop, stacked below the scene on phone.

The stage floor holds the ring, tilted with a 72 degree perspective rotation. On phone it is 120vw wide and sits about a third up from the bottom (halfway up on adoption); on desktop its width is clamp(16rem, 100vw - 48rem, 52rem), anchored 6% from the bottom. Stat plaques on phone are a 2x2 grid with hairlines between cells; on desktop a single column with a rotated-diamond glyph beside label and value.

## Elevation & Depth

Tonal layering plus one soft shadow. Panels sit above the scene as translucent indigo plates; depth comes from the glow behind them, the dark fade at the bottom of the scene, and a floor pool of warm light under the ring.

### Shadow Vocabulary
- **Frame lift** (`box-shadow: 0 1.25rem 2.5rem -1rem rgb(0 0 0 / 0.7)`): under every gilt frame.
- **Slot well** (`box-shadow: inset 0 0 2.5rem rgb(0 0 0 / 0.55)`): the framed creature slot only.
- **Legibility shadow** (`text-shadow: 0 1px 6px #000`): the sync line over the scene.

### Named Rules
**The Plate Over Scene Rule.** Panels are translucent plates over the scene, never opaque cards; the ring and glow must stay visible around them.

## Shapes

Square corners on every control and frame; geometry comes from notched corner brackets (a 24px bracket with a small diamond inside) plus a second hairline inset 7px inside the frame border. Round only where the form is a circle: the sigil ring, the creature slot, the chevron buttons (50%). Ornament is geometric and linear (diamond, crescent, hexagram), stroked 0.6 to 2px, never filled blobs.

## Components

### Buttons
- **Shape:** square, 1px gold-dim border.
- **Default:** transparent, gold text, padding 0.35rem 0.9rem. Hover fills gold with night text over 0.2s ease-out; active nudges down 1px; disabled at 0.45 opacity.
- **Primary:** filled antique gold, night text, Forum uppercase at 0.18em tracking, padding 0.6rem 1.25rem. Hover turns ivory-gold.
- **Quiet (top bar log out):** label size, 0.12em tracking, faint gold border, 0.6 alpha night fill.
- **Focus:** 2px gold outline, 3px offset, on everything.

### Gilt Frame (signature)
Indigo plate gradient, 1px faint-gold border, a second faint hairline inset 7px, four notched corner brackets, 1rem padding, frame lift shadow. Used for the name banner and the stat panel.

### Banner
Frame holding a Forum heading, the ornamental divider (max 14rem), and a muted subtitle. One h1 per page.

### Stat Plaque
Label above value, hairline separators in faint gold. Desktop adds a 3rem diamond-rotated outline glyph with a stroke icon inside (1.4 stroke, round caps).

### Sigil Ring
Engraved circle set with a hexagram and four cardinal diamonds; tick ring rotates once per 240s, strokes draw in over 1.8s. Both stop under `prefers-reduced-motion`. Decorative, hidden from assistive tech.

### Inputs
Void-indigo fill, 1px gold-dim border, 1.25rem Alegreya text in ivory, square; focus keeps the gold outline flush (offset 0). Labels are Forum uppercase muted. Errors are vermilion text with `role="alert"`.

### Chevron Button
2.75rem circle, 0.7 alpha night fill, 1.5rem stroke chevron; picks the previous or next breed.

## Do's and Don'ts

### Do:
- **Do** draw edges with hairline gold (1px at faint, dim or full strength) and corner brackets.
- **Do** set all progress numbers in Forum with tabular lining numerals.
- **Do** place panels as translucent plates over the stage so the ring stays visible.
- **Do** keep copy and state calm; vermilion only for errors.
- **Do** read colours from the custom properties in `web/src/styles/tokens.css`; add new values there first.
- **Do** honour `prefers-reduced-motion` for any new looping or drawing animation.

### Don't:
- **Don't** fill large areas with gold or use glossy, bevelled gold ornament.
- **Don't** build a dark card grid with a neon accent; panels are framed plates, not cards.
- **Don't** round control corners; circles are reserved for the ring, slot and chevron buttons.
- **Don't** introduce a second state colour; success stays uncoloured.

## Known Gaps (not design decisions)

- The login page is not styled yet.
- The 3D scene is a placeholder (a creature-slot label standing in for the canvas); its look is undecided.
- Open finish-review items: on the adopt phone layout the placeholder label sits on the ring; the ring is small at 1024px; `stage.css` declares `.stage__floor` in two split rules.
- A verdigris success colour and a Greek-key motif were deliberately not added; do not treat their absence as an omission to fix.
