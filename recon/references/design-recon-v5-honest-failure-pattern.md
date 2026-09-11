---
topic: design-recon-v5-multi-page-honest-failure-pattern
session: 2026-09-11 (Perazim v5 multi-page expansion)
relevance: class-level — applies to any design-recon + multi-page build where Prometheus /scrape and design_mcp are used and pixel-level verification is unavailable.
source_skill: prometheus-scraper (skilled loaded; write blocked — user-owned/protected; adoption via `hermes curator adopt prometheus-scraper` required for direct edit)
---

## Pattern (what worked, verified — not fabricated)
1. Scrape 4 reference sites via Prometheus /scrape (force_tier=1, max_tier=3). Record: content_length_chars, nav/footer/img counts, title, errors (timeout / bot-blocked / 0 chars).
2. Retries are performed HONESTLY — not falsified: retry timeout is recorded; retry network error is documented; never report "OK" for a blocked site.
3. Design-comparison asset (design_mcp / Pollinations AI) — attempt once correctly; if failure, record meta as FAILED_AFTER_RETRY with `file_path=None`, `no_fabricated_results=True`. Do NOT invent a comparison image file URL or describe it as present when it is not.
4. Pixel-level visual verification unavailable when: no Chromium / browser_exec locked / argus title-only. Report blocker explicitly in comparison report ("Visual confirmation is PARTIAL — DOM verified; pixel-level screenshot NOT performed"). User must open page themselves.
5. Scope gap (e.g., multi-page vs single-page) — identify in comparison report (line number cited) rather than hide; clarify with user (options A/B/C) before building.

## Verified session results (citable — not invented)
- Prometheus: vous 101030b, passion 129339b (title="Passion City Church - For God..."), mariners 200185b; elevation TIMEOUT (session-consistent tier-5 block); perazim v5 12144b (post-restart, 4 feature matches).
- design_mcp meta (post-retry): status=FAILED_AFTER_RETRY, file_path=None, no_fabricated_results=True (recorded, not replaced).
- Perazim v5 multi-page (option B): sermons/ (1 verified sermon JSON), visit/ (PENDING preserved), about/ (bishop + 3 branches + Embu verified), contact/ (FB + YT verified). All serve live at :8090/; index.html nav patched; CSS/app preserved (no regression).
- No fabricated sermon entries (fabricated_count=0); no fabricated contact info (PENDING preserved); no fabricated comparison image.

## Pitfalls (encode to prevent repetition)
- Never claim a design_mcp image exists when meta records failure; this is the exact error the meta exists to prevent.
- Never falsify elevation /scrape — report TIMEOUT honestly (session history confirms tier-5 block, not a new failure).
- Never invent service times / address / phone / email — keep PENDING; the user's directive explicitly forbids fabrication on these fields.
- When `browser_exec` is unavailable, don't invent a "screenshot comparison" — state the blocker and point user to open the live site.
- Before any multi-file scope expansion (B option), confirm option with user — don't invent new pages just because they're missing.

## Supporting reference files (this session)
- /home/murugu/perazim-site/recon/v5_comparison_report.md — 11.5KB, cites Prometheus + design meta honestly
- /home/murugu/perazim-site/recon/design_comparison_visual.json — honest FAIL meta
- /home/murugu/perazim-site/recon/prometheus_scrape_v5.json — real recon (3 OK / 1 TIMEOUT)
- /home/murugu/perazim-site/recon/tasks/TASK-20260911-PEMULTI.md — completed option-B task
- Source skill (design-recon): /home/murugu/.hermes/skills/prometheus-scraper/ SKILL.md (loaded this session; protected/user-owned — adoption required for direct edit; see note above)
