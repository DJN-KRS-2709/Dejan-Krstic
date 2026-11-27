---
name: ui-designer
description: "Visual design rules for building, styling or reviewing any screen: spacing system, type scale, color proportions, elevation, component sizing, layout, responsive behavior, dark mode, motion and a pre-ship polish checklist. Use when someone says 'make it look good', 'it looks off', 'style this', 'fix the spacing', or asks for a design system, component library, landing page, course page or prototype polish. Hand flow and user psychology questions to ux-designer."
user_invocable: true
argument-hint: "[url, file path or component]"
---

# UI Designer

Interfaces look professional when every value comes from a system and every detail is deliberate. This skill sets up that system, applies it while building, and checks the result before anyone sees it.

If you got a URL, file or component name, open it first and work from what is actually there.

## House style first

When the work is for Dejan's own site, courses or prototypes, use the existing dejan-krstic.com design system (its color tokens, fonts, buttons and footer) instead of the generic defaults below. Read the tokens from the site repo or the course pack's design system page; do not guess hex values. The rules in this skill then govern how those tokens are applied. For a client, use the client's system if one exists.

## Step 1: Set the system before drawing anything

**Spacing.** Base unit 8px, with 4px allowed for tight adjustments inside a component. A practical scale: 4, 8, 12, 16, 24, 32, 48, 64, 96, 128. Distance signals relationship: 8 to 16 between things that belong together, 24 to 32 for loose groups, 48 to 64 between sections, 64 and up between major areas. Padding inside a box must never be larger than the gap around it, or the content looks like it is escaping its container.

**Type.** Pick one ratio and derive every size from it: about 1.125 for dense dashboards, 1.2 for most apps, 1.25 for marketing and editorial, 1.333 for loud hero pages. Use four sizes on most screens and never more than six. Body line height 1.4 to 1.6, headings 1.1 to 1.3. Bigger text wants slightly tighter tracking; uppercase labels want looser tracking. Two families at most. Build hierarchy with weight before reaching for italics or new fonts.

**Color.** Roughly 60% neutral canvas, 30% surfaces one step away from it, 10% accent for the things you want clicked. Up to three hues plus neutrals. Avoid pure black and pure white; use near versions. Every status color (success, warning, error, info) needs a background, border, text and icon variant. Body text contrast at least 4.5:1. Keep grays all warm or all cool.

**Depth.** Higher layers get softer, larger shadows. Hover lifts an element one step. In dark mode, show depth with lighter surfaces instead of shadows. Use shadows sparingly.

**Corners.** Choose one family and stick to it: tight (0 to 4px) for serious and editorial, medium (8 to 12px) for friendly product UI, large or pill (16px and up) for playful or bold brands. A child element always has a smaller radius than its parent.

Write these as CSS custom properties (or the project's token format) before building components. A compact starting set lives in the appendix below.

## Step 2: Components

- **Shared heights.** Buttons and inputs use the same height steps (for example 32, 36 or 40, 48). A button next to an input should read as one unit. Horizontal button padding is about twice the vertical.
- **Button ranks.** One filled primary per section. Secondary is outlined or softly filled. Tertiary is text only. Destructive is a red version of primary. Leading icons add meaning (add, search); trailing icons describe behavior (opens new tab, dropdown, next). Icon only buttons need an accessible label and a tooltip.
- **Forms.** Always a visible label above the field; placeholder text is a hint, never the label. Label to field gap 4 to 6px; field to field gap 16 to 24px. Errors appear in place of helper text, in red, with an icon.
- **Cards.** Same padding for every card in a view (16 to 24px), gaps between cards larger than that padding, one job per card, actions grouped in the header or footer.
- **Tables.** Text left, numbers right, stable column widths, sortable headers with a clear arrow, sticky header when scrolling, row hover, and either stripes or dividers but not both.
- **Navigation.** Top bar 48 to 64px. Sidebar about 240 to 280px open and 64 to 72px collapsed. The active item must be obvious at a glance. Icons 20 to 24px with one stroke weight.
- **Dialogs.** Width by purpose (around 400 to 480px for confirmations and short forms, about 640px for content, up to roughly 960px for complex work). 24 to 32px padding, dimmed backdrop, close control top right, actions bottom right with the primary on the right, focus kept inside, Escape closes.

## Step 3: Layout

- A 12 column grid splits cleanly into halves, thirds, quarters and sixths. Gutters come from the spacing scale.
- Left align body text. Share left edges. Trust your eye over the math for optical centering (a play triangle needs a nudge).
- White space is a tool: more space around something makes it more important. Prefer space over divider lines; if a line is needed, keep it faint.
- Start with the phone layout and add for bigger screens. Common breakpoints: 640, 768, 1024, 1280, 1536. Phones: one column, full width buttons, big tap targets, no hover dependent features. Tablets: two columns where useful. Desktop: sidebars, hover states, more density.

## Step 4: Polish

Small touches that lift the whole thing, used with taste:
- Lists and cards enter with a 50 to 80ms stagger.
- Shadows tinted toward the element color instead of flat gray.
- On dark themes, a hairline light border on raised surfaces.
- Sticky headers with a light background blur.
- Nested radii always step down.
- One icon set, one stroke weight.
- Gradient text only on a hero line, if at all.

**Dark mode** is its own palette, not an inversion: soften saturated brand colors, lighten surfaces as they come forward, use off white text, and use translucent light borders. Check it in a dim room.

**Motion.** Ease out for things arriving, ease in for things leaving, ease in out for things moving. Linear only for progress bars and loaders. Animate transform and opacity, never width, height, top or left. Every interactive element needs default, hover, pressed, focus, disabled, loading, error and success states.

## Step 5: Borrow principles, never brands

Learn from great products by naming the principle, then expressing it in your own colors, type and voice. Examples: restraint (every element must justify itself; one accent on a quiet base), clarity (one hero per view; type carries most of the weight), speed as design (remove friction, keep power), and platform respect (follow native conventions; motion that feels physical). Copying a look wholesale is off limits.

## Step 6: Check before showing anything

Fix every failure first.

- [ ] All spacing on the scale
- [ ] All font sizes from the chosen ratio
- [ ] Color split close to 60/30/10
- [ ] Clear, limited elevation levels
- [ ] One corner family, nested radii step down
- [ ] Buttons and inputs share heights
- [ ] The point of the screen is obvious in three seconds
- [ ] Icons consistent
- [ ] Inside padding never larger than outside gap
- [ ] Dark mode works (if in scope)
- [ ] Checked at every breakpoint
- [ ] Tap targets at least 44 by 44px
- [ ] Contrast meets WCAG AA (4.5:1 text, 3:1 large text and UI parts)
- [ ] Nothing relies on color alone

For reviews of existing screens, use this shape:

```
Visual review: <name>
Score: <n>/10  <one line verdict>
Broken (fix now): <issue, where, fix>
Inconsistent (fix soon): <issue, where, fix>
Polish (nice to have): <issue, where, fix>
Working well: <at least one specific thing>
```

## Appendix: starter tokens

```css
:root {
  --space-1: 4px;  --space-2: 8px;  --space-3: 12px; --space-4: 16px;
  --space-5: 24px; --space-6: 32px; --space-7: 48px; --space-8: 64px;
  --text-sm: 0.833rem; --text-base: 1rem; --text-lg: 1.2rem;
  --text-xl: 1.44rem;  --text-2xl: 1.728rem; --text-3xl: 2.074rem;
  --leading-body: 1.5; --leading-tight: 1.2;
  --radius-sm: 4px; --radius-md: 8px; --radius-lg: 12px; --radius-pill: 999px;
  --shadow-1: 0 1px 2px rgb(0 0 0 / 0.06);
  --shadow-2: 0 4px 12px rgb(0 0 0 / 0.08);
  --shadow-3: 0 12px 32px rgb(0 0 0 / 0.12);
  --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
  --ease-in: cubic-bezier(0.55, 0, 1, 0.45);
  --dur-fast: 120ms; --dur-base: 200ms; --dur-slow: 320ms;
}
```

Type scale above uses a 1.2 ratio. Swap values to match the chosen ratio and the brand.

## Never

- Values off the spacing scale or sizes off the type ratio
- Pure #000 or #FFF
- More than three hues plus neutrals
- Animating layout properties
- Linear easing outside progress indicators
- A child radius larger than its parent
- Padding larger than the surrounding gap
- Color as the only signal

## Related skills

- `ux-designer` owns flows, structure and user psychology. Once the flow is agreed, this skill makes it look right.
- `copywriting` owns the words on the page.
