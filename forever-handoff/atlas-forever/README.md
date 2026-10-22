# Atlas Forever

A standalone map and navigation companion for **WoW: Forever** (Interface 16001): every map the client has in one
browsable window, a live coordinate readout, saved bookmarks and waypoints.

Part of the WoW: Forever suite, and it works on its own: nothing else has to be installed.

## What it does

- **The atlas.** Every continent, zone, dungeon and raid map the client knows, browsable in one window with a
  breadcrumb back up and search by name. The shape of the client's world map is small and keyboard-hostile; this is
  the same maps, bigger, and without the clicking.
- **Coordinates.** The zone and your position as `x, y`, on screen or in a copyable line.
- **Bookmarks.** Name a place, keep it, and jump back to it. Bookmarks are per account, saved as plain data.
- **Waypoints.** Send the game's own waypoint to your position or to a bookmark.

## What it never does

Atlas Forever draws maps and keeps places you named. It does not plan routes, order stops or estimate travel time
(that is [Shortest Path](../shortest-path-forever)), does not choose quests (that is
[Adventure Guide](../adventure-guide-forever)), does not own the pins other addons register, and does not show loot
tables (that is Adventure Guide's AtlasLoot readiness). See `forever-handoff/boundaries.md` in
[cjber/skills](https://github.com/cjber/skills) for the suite's ownership rules.

## Install

Copy the `AtlasForever` folder into `World of Warcraft/_classic_beta_/Interface/AddOns/`, or install it from
CurseForge or Wago once it is published.

## Commands

`/atlas` prints the loaded state; the window itself opens from the minimap button and a key binding.

## Development

See `AGENTS.md` for the local gate, the layout, and the rules this repository is held to.
