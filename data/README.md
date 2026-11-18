# Shared content feed

This folder is the one place where Perazim's public content lives. The
website, the Perazim web app and the Android app all read it, so a change
made here shows up everywhere.

| Tab | What it holds | Who reads it |
|---|---|---|
| `sermons` | Sermon and teaching videos | Website `/sermons/`, web app, Android |
| `hymns` | Hymn lyrics and chord charts | Website `/hymns/`, web app, Android |
| `riddles` | Bible riddles | Website `/riddles/`, web app, Android |
| `jokes` | Clean Christian jokes | Website `/jokes/`, web app, Android |
| `verses` | Verse of the day, one row per date | Web app, Android |
| `events` | Services and gatherings | Web app, Android (website page to follow) |
| `announcements` | Notices and bulletins | Web app, Android (website page to follow) |
| `campuses` | Campus names and areas | Web app (website and Android to follow) |
| `config` | Church contacts, giving details and app switches | Web app, Android |

## How to change content

1. Edit the CSV in `data/csv/`. A spreadsheet program works; keep the
   header row exactly as it is, and keep every `id` unique.
2. Set `active` to `FALSE` to hide a row without deleting it.
3. Run `python3 scripts/build_data.py`. It checks the CSVs, rewrites
   `data/*.json`, and refreshes the website pages that show the content.
4. Commit and open a pull request. The **Content feed** check fails if step 3
   was skipped.

Only publish content you have checked is true and that we have the right to
publish. This folder is public.

## Published URLs

Once GitHub Pages deploys `main`, each tab is available at:

- JSON (web app): `https://<site>/data/<tab>.json`
- CSV (Android): `https://<site>/data/csv/<tab>.csv`

The CSV columns match the Android app's Google Sheet tabs
(`perazim-android/docs/CONTENT_GUIDE.md`), so the Android app reads these
URLs with its existing sync code. `data/manifest.json` lists every tab.

## Notes on the current content

- Sermons: only the one verified YouTube message is listed.
- Hymns: writer and year were corrected. *Great Is Thy Faithfulness* and
  *How Great Thou Art* are still under copyright, so they are switched off
  (`active=FALSE`) until a licence is confirmed.
- Events and announcements are empty on purpose: the Android seed entries are
  sample data, not real church events.
- Campuses follow the website (Embu Central, Mwea, Rombo). The Android server
  and the web app list different campuses; these need confirming.
