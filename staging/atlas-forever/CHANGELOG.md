# Changelog

All notable changes to Atlas Forever are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses semantic versioning.

## [Unreleased]

## [0.1.0] - 2026-10-22

### Added

- **Browse client-listed dungeons and raids.** Filter the instance index by continent or type and see any level range the client provides.
- **See available entrance and creature data.** Set a waypoint or ask Shortest Path to guide you when an entrance position is available; optional QuestieDB rows add creature names without invented pins.
- **Read an honest map fallback.** This client build contains instance WDT asset IDs but does not expose interior UI map layers or floor names, so the viewer reports unavailable map art.

### For addon authors

- Added `AtlasForever.API` version 1.1 with ready gating, filtered copies, instance lookup and window open.
