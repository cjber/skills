# Changelog

All notable changes to Atlas Forever are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses semantic versioning.

## [Unreleased]

### Added

- Repository scaffold: the TOC at Interface 16001, the Forever suite's shared configuration, CI, the release workflow and the spec harness.
- `Core/Model.lua`, the pure bookmark arithmetic the window draws from: coordinate formatting, adding, removing and searching bookmarks, with duplicate places refused.
- `Core/Core.lua`, which owns the saved variables, the ready callbacks and the `/atlas` slash command, and `Core/API.lua`, the versioned contract other Forever addons read.
