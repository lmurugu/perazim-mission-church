# Shared content feed: format contract (schema version 1)

This is the contract between the feed in this folder and every client that
reads it: the website, the Perazim web app (`lmurugu/perazim-app`) and the
Android app (`lmurugu/perazim-android`, and any other Android build of it).
Keep a client in step with this file, and change this file first when the
format changes.

## Where to read it

| Format | URL | Used by |
|---|---|---|
| CSV, one file per tab | `<base>/csv/<tab>.csv` | Android (`SheetSyncManager`) |
| JSON, one file per tab | `<base>/<tab>.json` | Web app |
| Manifest | `<base>/manifest.json` | Any client: tab list, counts, schema version |

`<base>` is `https://lmurugu.github.io/perazim-mission-church/data` once
GitHub Pages serves this repo.

## Rules for every tab

- CSV is UTF-8 with a header row, RFC 4180 quoting (multi-line cells are
  quoted). Column names are lowercase and fixed. Clients must ignore columns
  they don't know, so new columns can be added safely.
- `id` is unique within its tab and never reused. (`verses` uses `date` and
  `config` uses `key` instead of `id`.)
- `active` is `TRUE` or `FALSE`. The CSV keeps inactive rows; the JSON
  leaves them out. Clients reading CSV must hide `active=FALSE` rows.
- Dates are `YYYY-MM-DD`. Date-times are `YYYY-MM-DD HH:mm` in Nairobi time
  (Africa/Nairobi, UTC+3).
- Each JSON file is `{"schema_version": 1, "<tab>": [...]}`, or
  `{"schema_version": 1, "config": {"key": "value"}}` for config. Booleans
  are JSON booleans; `bpm`, `xp` and `year` are numbers when the cell is
  a whole number.
- A client that sees an unexpected `schema_version` keeps the content it
  already has. An empty tab never clears a client's existing content.

## Tabs

| Tab | Columns (required) |
|---|---|
| `announcements` | `id`, `title`, `body`, `date` (date-time), `priority` (`NORMAL`/`HIGH`/`URGENT`), `campus`, `active` |
| `events` | `id`, `title`, `start`, `end` (date-times), `venue`, `campus`, `description`, `active` |
| `hymns` | `id`, `title`, `writer`, `year`, `key` (e.g. `D Major`), `bpm`, `tags` (comma separated), `lyrics`, `chords` (progression, e.g. `D - G - A`), `active` |
| `riddles` | `id`, `category` (`EASY`/`MEDIUM`/`HARD`), `question`, `answer`, `xp`, `active` |
| `jokes` | `id`, `text`, `active` |
| `sermons` | `id`, `title`, `speaker`, `date`, `series`, `scripture`, `youtube_url`, `audio_url`, `active` |
| `verses` | `date`, `reference`, `text` |
| `campuses` | `id`, `name`, `area`, `service_times`, `photo` (site-relative path), `active` |
| `config` | `key`, `value` |

`campus` in announcements and events is a campus `id` (currently only
`campus_embu`) or `all`.

`hymns.lyrics` holds blocks separated by a blank line. A block may start with
a header line such as `Verse 1:` or `Chorus:`.

### Config keys

| Key | Meaning |
|---|---|
| `church_name`, `motto`, `presiding_bishop` | Church identity |
| `pastoral_phone_e164` | Pastoral line, international format |
| `mpesa_paybill` | M-Pesa Paybill for giving |
| `email_info`, `email_bishop` | Church email addresses |
| `youtube_url`, `facebook_url` | Official channels |
| `min_app_version`, `ai_enabled`, `ai_daily_limit`, `community_enabled` | Android app switches |

## Changing the format

1. Adding a column or a config key is backward compatible: update this file,
   `scripts/build_data.py` if the column is required, and the CSV.
2. Renaming or removing a column, or changing a value's meaning, is a breaking
   change: bump `SCHEMA_VERSION` in `scripts/build_data.py`, update this file,
   and update the web app and Android clients in the same round of PRs.
