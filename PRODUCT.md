# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary user is the author, an intermediate runner who logs runs in Strava. Multi-user is a later possibility (`user_id` is in the schema), not a current audience. They open the app in two moments: a quick check right after a run, and longer sessions managing the strider, loadout and quests. Phone and desktop matter equally.

## Product Purpose

Stridecraft turns real runs into a creature-collecting RPG in the spirit of Pokemon, Palworld, WoW and Ark. The user adopts one strider (a Greek-mythology creature chosen by breed, plus a name) that grows stronger because they train together. Success: the user feels their running effort become the strider's power, with no extra logging.

## Positioning

Progression comes from performance (pace, PBs, volume, elevation, streaks), not from "you ran today". The strider is its own creature, not an avatar of the runner: it has its own base stats and only runs after adoption count. Nothing decays.

## Operating Context

- Runs arrive from Strava (OAuth login, sync). Effortless UX: the app asks for no manual logging.
- Flow: Strava login, then adoption (pick breed and name) if no strider exists, then dashboard.
- Four stats: Speed, Endurance, Hills, Consistency. All are running totals that never decay.
- Skills are unlocked once, kept forever, and equipped into limited slots. They affect boss fights only.
- Quests are hand-authored. Quests and bosses grant skills and outfits. Boss fights are auto-battles the user watches; training and loadout beforehand decide the outcome.
- Content (breeds, skills, quests, bosses, outfits) is data authored in YAML on the server; the frontend never reads the YAML. Binary assets (3D models) come to the frontend as URLs from the API.

## Capabilities and Constraints

- Frontend: Vite + React + TypeScript in `web/`, currently unstyled (login, adoption, dashboard; the 3D strider is a placeholder square). Tokens file exists at `web/src/styles/tokens.css`.
- Breeds are looks only to start (about 4-6 pre-made, 3D models). Current breeds in content: Cetus, Cerberus, Chimera, Griffin, Ladon, Pegasus. Outfits are pre-made variants.
- No character level or XP. Stats are uncapped for now.
- Not yet built: boss-fight UI, skill loadout UI, quest log, fighter selection, Strava webhook.
- Undecided: skill slot count and tiers, combat formulas, boss design.

## Brand Commitments

- Name: Stridecraft. Tagline in README: "Your effort becomes their power."
- Terminology: strider, breed, skills, quests, trophies, bosses.
- Visual direction is an **open lean, not binding**: dark alchemy with Greek-mythology references. Two inspiration images are in `references/`: `ui_ref_1.png` (cute 3D-character RPG UI with a customization scene and a ranked list) and `ui_ref_2.jpg` (gold-filigree "Dark Alchemy UI" frames, sigils and dividers on deep indigo). The visual world is decided in the design step, not here.

## Evidence on Hand

- 3D breed assets in `assets/breeds/`, plus `references/cetus.jpg`.
- Real run data from the author's Strava. No testimonials, other users or usage numbers exist; do not invent any.

## Product Principles

- Effortless: the user runs and logs in Strava; the app never asks for extra input.
- Performance over presence: progression language celebrates pace, PBs, volume, elevation and streaks, not mere attendance.
- Progress is kept: no decay, no penalties, no guilt mechanics. Missing training never hurts the strider.
- The strider is its own creature: copy and UI treat it as a companion that grows alongside the user, not as a mirror of the user.
- Win with preparation: the player's decisions are training and loadout; battles are watched, not played.

## Accessibility & Inclusion

No product-specific requirement established. Phone and desktop must both work.
