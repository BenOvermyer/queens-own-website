# Queen's Own Website

Zola source for the Queen's Own website, migrated from the hand-coded archive and
organized into membership, personas, world reference, community, and publications.
The original blue backgrounds, links, artwork, tables, text, and page anchors are
preserved. Imported pages have TOML front matter and original HTML bodies inside
Markdown files; this deliberately retains their presentation rather than converting
the archive's complex layouts to Markdown tables. Shared templates live in `templates/`.

## Preview and build

Install Zola, then run `zola serve` for a development preview.

For deployment, run:

```sh
python3 scripts/build.py
python3 scripts/verify.py
```

Publish `public/`. Page URLs are descriptive and extensionless, such as
`/bards-faq/` and `/newsletters/2005/january/`. Zola builds directory indexes;
`static/_redirects` provides permanent redirects from old filenames on Netlify.
`zola serve` previews the canonical pages; Netlify handles the legacy redirects.
The verification script requires the migration Python dependencies below.

Netlify uses `netlify.toml` to run the same deployment build and publish `public/`.
It passes Netlify's `DEPLOY_PRIME_URL` to Zola so site links use the current
Netlify site, branch, or preview URL. The default URL in `config.toml` is localhost;
PDF downloads continue to use `files.queensown.org`.
The configuration pins Zola to 0.23.6, matching the locally tested version.
The deployment build uses Python's standard library and does not need the migration
dependencies or original archive directory.

For a manual deployment, specify its URL with
`python3 scripts/build.py --base-url https://YOUR-SITE.netlify.app`.

## Site structure and editing

[`docs/site-organization.md`](docs/site-organization.md) documents the sitemap,
publication indexes and redirect policy. `data/site-map.csv`
maps every imported page to its section, canonical path, content file, and redirect.
`data/site-routes.json` is the same mapping for tooling.

Source files live in native Zola sections under `content/`. Preserved source pages
retain `extra.legacy_source` for provenance; the membership landing pages and other
navigation hubs are separately maintained Markdown. Hub edits survive reorganization
and reimport. Ordinary new editorial pages do not need a legacy source identifier.

To regenerate canonical links, redirects, and publication indexes after changing
the preserved archive or refreshing PDF availability evidence:

```sh
python3 scripts/organize_site.py
python3 scripts/build.py
python3 scripts/verify.py
python3 -m unittest discover -s scripts -p 'test_*.py'
```

The organizer preserves original bodies, credits, and anchors. It updates source
metadata and internal URLs using explicit content rules. Month-only newsletter dates
use the first day for sorting, with `date_precision = "month"`; the UI shows the
known month/year, not an invented publication day. Missing issues retain unavailable
notices and unresolved inventory statuses.

## Reimport the archive

```sh
python3 -m pip install -r requirements-migration.txt
python3 scripts/migrate.py ../queens-own/queensown.org
```

Reimporting overwrites imported content and copied static assets. Edit the importer
for repeatable changes, or edit generated content directly and avoid reimporting
those changes. The original source directory is never modified.
Both importers use the section mapping and run the organizer, so they retain the
new paths and preserve the separate home page and curated navigation hubs.

`data/migration-report.json` lists repaired references and missing source files.
It is the original migration snapshot, rather than the current resolution status.
The current inventory and recovery dispositions are documented in
[`docs/content-inventory.md`](docs/content-inventory.md).
Missing newsletter content has canonical unavailable-notice pages; missing assets
retain their original-domain recovery targets. Neither is marked recovered by the
audit. `data/anchor-report.json` lists unresolved internal anchors.
The archive retains historical dates, contact details, copyright notices, and privacy text.

To check for new internal link failures using saved HTTP evidence, run
`python3 scripts/verify.py` after building. To refresh live PDF and original-host
availability, run `python3 scripts/audit_links.py --online` (requires network access).
Known historical gaps remain explicitly unresolved; a new missing target or new
page referring to an acknowledged gap fails validation. Online availability can
change, so an offline check does not establish that downloads are currently live.

`data/link-corrections.json` and `scripts/link_repairs.py` keep link fixes and anchor
aliases reproducible on reimport. `python3 scripts/repair_links.py` applies those fixes
and unavailable-content notices to existing pages without reimporting the archive.
After recovering a resource, remove its entry from `data/link-dispositions.json`
and its unavailable notice from the page, refresh live evidence where appropriate,
then rerun the organizer, rebuild, and verify.

## Content remaining on Dragonlords

[`docs/dragonlords-migration-inventory.md`](docs/dragonlords-migration-inventory.md)
identifies Queen's Own and Velgarth content left on the other site by the original
filename-based split. The complete file spreadsheet and page/dependency inventory
are in `data/dragonlords-file-inventory.csv` and
`data/dragonlords-content-inventory.json`.

To regenerate those data files from the local split archive:

```sh
python3 scripts/inventory_dragonlords.py ../queens-own/dragonlords.fans
```

This requires the migration Python dependencies. Install `pdftotext` (Poppler) to
include PDF keyword scanning; the JSON records whether PDF text was extracted.
Recommendations identify candidates for subsequent migration; they do not move
content or change either site's routes.

The selected club pages have been migrated under descriptive paths. The bookstore
and substantive Dragonlords material stay on the other site; shared hosting footers
and bookstore promotions were removed from imported copies. To repeat that import,
run `python3 scripts/migrate_dragonlords.py ../queens-own/dragonlords.fans`, then build
and verify. This overwrites the imported copies, so maintain repeatable changes in
the migration script. `data/dragonlords-route-map.json` records the initial imported paths;
`data/site-routes.json` records the organized content locations and canonical URLs,
and `static/_redirects` redirects old filenames on the Netlify site. Redirects on the
original Dragonlords host need a separate deployment there.

## PDF storage

The 120 PDFs (about 57 MiB) are intentionally excluded from the repository and build.
`data/pdf-manifest.json` records their original keys, sizes, and SHA-256 checksums.
PDF links use `https://files.queensown.org`, configured through `extra.pdf_base_url`
in `config.toml`. Filenames and their case are preserved, including links to PDFs
that were missing from the local source archive.

To preview future uploads to the backing bucket:

```sh
bash scripts/upload-pdfs.sh ../queens-own/queensown.org s3://YOUR-BUCKET \
  --endpoint-url https://YOUR-S3-ENDPOINT --profile YOUR-PROFILE
```

Add `--apply` immediately after the destination to upload. The script defaults to
dry-run, uploads PDFs only, and never deletes objects. It uses the AWS CLI and your
local credentials; credentials must not be committed. Optional destination prefixes
are supported, such as `s3://YOUR-BUCKET/archive`.

Set `extra.pdf_base_url` in `config.toml` to the corresponding public HTTPS URL
(including any prefix, without a trailing slash), then rebuild. The S3 API endpoint
and public download URL may be different. Preserve original filename case.
