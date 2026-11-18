# Contributing

1. **No invented facts.** Service times, names, ages, addresses and numbers must come from the
   church. Unknowns stay as `CHURCH TO CONFIRM` comments, never as made-up text.
2. **Real photos and paintings only** from `assets/`. No stock photos of people.
3. **Use the design tokens** in `assets/styles.css`. No ad-hoc colours or inline styles.
   Check contrast: dark text on light glass and orange, white only on deep purple or pink.
4. **Type:** Plus Jakarta Sans for headings, Inter for text. Keep one `h1` per page and do not
   skip heading levels.
5. **Change shared parts in one place.** Titles, descriptions, hero, menu and footer are edited in
   `scripts/sync_site.py`, then run `python3 scripts/sync_site.py`.
6. **Test before you push:**
   ```bash
   python3 scripts/sync_site.py --check
   python3 scripts/build_data.py --check
   python3 scripts/check_site.py
   python3 -m http.server 8123 &  node scripts/e2e_site.js   # needs Playwright
   ```

## Commit messages

Conventional Commits: `feat:`, `fix:`, `style:`, `docs:`, `test:`.
