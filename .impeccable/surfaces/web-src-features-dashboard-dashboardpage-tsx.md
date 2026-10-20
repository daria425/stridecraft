---
version: 1
slug: "web-src-features-dashboard-dashboardpage-tsx"
primary_target: "web/src/features/dashboard/DashboardPage.tsx"
related_targets: ["web/src/features/adopt/AdoptPage.tsx","web/src/features/auth/LoginPage.tsx"]
---

# Dashboard surface brief

Scope: Dashboard (`/`), the screen after every run; Login and Adopt inherit its world. Mode: Operate (game HUD, strider leads). Phone and desktop equal. Build path: code-led. Avoid: generic dark dashboard, cheap fantasy/mobile-game look. Unresolved: font choice and delivery (needs user approval), 3D rendering inside the sigil ring.

## Direction contract

THESIS: A character sheet in an alchemist's gilt frame, where the strider is the only subject and numbers read like engraved instruments. Refuses the dark card grid with neon accent and glossy cartoon-gold ornament.
OWN-WORLD: Deep indigo ground (#0c0d24 to #1d2057), muted antique gold (#c9a24a) for line work and frames, pale ivory-gold text, one verdigris or vermilion for state. Thin hairline gilt frames with notched corners, sigil ring around the creature, ornamental dividers, engraved gauges for stats. Recognisable with content removed by frame geometry and ring.
STORY: The user sees their strider has grown, reads four stats at a glance, and knows sync status. Nothing decays, so copy stays calm and rewarding.
FIRST VIEWPORT: Strider centred in a large sigil ring (about 60% of viewport height on desktop, full width on phone), name above on a gilt plate. Four stats as engraved gauges flanking the ring on desktop, stacked beneath it on phone. Sync status as a small line under the frame. Log out is a quiet corner control.
FORM: Gilt Grimoire HUD, the model's pick (my own top candidate, position 1 of 7). Seed key b7d3f06b.
FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
