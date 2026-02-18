# Changelog

All notable changes to this project are documented in this file.

## [0.1.0] - 2026-02-18

### Added

- `pyproject.toml` with project metadata and lint configuration.
- Repository standards files: `.gitignore`, `.editorconfig`.
- Documentation set:
  - `CONTRIBUTING.md`
  - `CODE_OF_CONDUCT.md`
  - `SECURITY.md`
  - `docs/ARCHITECTURE.md`
- GitHub automation and templates:
  - CI workflow
  - bug report template
  - feature request template
  - pull request template

### Changed

- Refactored CLI entrypoint in `main.py` for clearer structure.
- Improved type hints and validation in `reuse_detector.py`.
- Improved password generator validation and secure shuffling in `generator.py`.
- Hardened and documented storage behavior in `storage.py`.
- Refactored GUI theming logic in `gui.py` to remove duplicate style code.
- Fixed password masking output in GUI list rendering.
- Expanded test coverage in `tests.py` (storage and validation cases).
