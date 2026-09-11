# Contributing to Perazim Mission Church Web Platform

Thank you for contributing to the official web platform for Perazim Mission Church.

## Guidelines

1. **Zero Fabrication**: Never introduce placeholder text, mock schedules, stock photos, or non-verified personnel. All photography must use authentic church assets from `assets/`.
2. **Design Tokens**: Do not use ad-hoc hex colors or inline style overrides. Always reference CSS variables defined in `assets/styles.css`.
3. **Typography**: Display titles must follow the `Plus Jakarta Sans` 900 + `Instrument Serif` italic pairing.
4. **Testing**: Run `python3 recon/verify_v5upgrade.py` before committing. Ensure all 86 checks pass.

## Commit Message Convention

We follow Conventional Commits:
- `feat: ...` for new user-facing features or pages.
- `fix: ...` for bug fixes or layout repairs.
- `style: ...` for visual adjustments without logical changes.
- `docs: ...` for documentation updates.
- `test: ...` for audit or test additions.
