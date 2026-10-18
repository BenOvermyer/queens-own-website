# Queen's Own Website

Zola source for the Queen's Own website, migrated from the hand-coded archive and
organized into membership, personas, world reference, community, and publications.
The original blue backgrounds, links, artwork, tables, text, and page anchors are
preserved. Imported pages are TOML front matter plus Markdown; images, `<dl>` lists,
named anchors, and genuine data tables stay HTML because Markdown has no equivalent for
them, while layout tables are converted to Markdown. Shared templates live in
`templates/`.

## Preview and build

Install Zola, then run `zola serve` for a development preview.

For deployment, run:

```sh
python3 -m pip install -r requirements.txt
python3 scripts/build.py
python3 scripts/verify.py
```

Publish `public/`. Page URLs are descriptive and extensionless, such as
`/bards-faq/` and `/newsletters/2005/january/`. Zola builds directory indexes;
`static/_redirects` provides permanent redirects from old filenames on Netlify.
`zola serve` previews the canonical pages; Netlify handles the legacy redirects.
The verification script requires the migration Python dependencies below.

Netlify uses `netlify.toml` to run the same deployment build and publish `public/`.
Production builds use the canonical host from `config.toml`
(`https://www.queensown.org`), so page and asset URLs — including the preloaded
fonts — stay same-origin however the site is reached. Set `www.queensown.org` as
the primary domain in Netlify so the apex and `*.netlify.app` hostnames redirect
there. Preview and branch deploys override `base_url` with Netlify's
`DEPLOY_PRIME_URL` so links stay on the preview site; `static/_headers` allows
font requests across those hostnames. PDF downloads continue to use
`files.queensown.org`.
The configuration pins Zola to 0.23.6, matching the locally tested version.
The deployment build installs `requirements.txt` (Pillow, for the responsive
image pipeline) and otherwise needs no migration dependencies or the original
archive directory.

For a manual deployment, specify its URL with
`python3 scripts/build.py --base-url https://YOUR-SITE.netlify.app`.

## Responsive images

`scripts/optimize_images.py` runs at the end of `scripts/build.py`, after Zola.
For every image a page references that is at least 128 px wide it encodes WebP
variants into `public/images/responsive/`, then wraps the `<img>` in a `<picture>`
whose `<source>` offers those variants with `sizes`, keeping the original file as
the fallback. GIF and PNG sources are encoded lossless, photographs lossily, and
a variant is only kept when it is smaller than the file it replaces, so the
pipeline cannot increase a page's image payload.

Images under 128 px (bullets, icons), external images, unavailable-image
placeholders, and `<img>` inside `<pre>`/`<code>` samples are left alone. The
output lives in `public/`, which is generated and git-ignored, so the source
keeps its original `<img>` tags and `zola serve` shows the originals. AVIF is not
emitted (it needs an extra Pillow plugin); WebP is supported by every current
browser. `scripts/verify.py` fails if a `srcset` target is missing.

## Site structure and editing

[`docs/site-organization.md`](docs/site-organization.md) documents the sitemap,
publication indexes and redirect policy. `data/site-map.csv`
maps every imported page to its section, canonical path, content file, and redirect.
`data/site-routes.json` is the same mapping for tooling.

Source files live in native Zola sections under `content/`. Preserved source pages
retain `extra.legacy_source` for provenance; the membership landing pages and other
navigation hubs are separately maintained Markdown. Hub edits survive reorganization.
Ordinary new editorial pages do not need a legacy source identifier.

Member names and contact addresses for the persona and NPC directories are kept in
`data/persona-directory.json` and `data/npc-directory.json`. Those private sources are
not rendered. After editing them, regenerate the public pages with
`python3 scripts/sanitize_persona_directories.py`; the script writes
`content/personas/persona-directory.md` and `content/personas/npc-directory.md`
without member names or email addresses. Each JSON source has `schema_version = 2`
and `sections` containing a stable `id` and persona `entries`. Entries carry
`persona`, optional `persona_url`, `player`, `email`, and a `details` list of
`date`, `gifts`, `note`, or `raw` fragments. The renderer omits `player` and `email`.

Only persona lists are generated. Each list in the Markdown is enclosed by
`<!-- persona-list:SECTION-ID:start -->` and `<!-- persona-list:SECTION-ID:end -->`.
Keep those markers when editing. Front matter, headings, section notes, preambles,
and closing copy live only in Markdown and survive regeneration unchanged. To add
a section, add its ID and entries to JSON and a matching marker pair in Markdown.

Club pages close with a shared sign-off: “Zhai’helleva, Herald-Mage Adept Danya
Winterborn”. Its salutation, name, and address live in `config.toml` under
`[extra.signoff]`, and the `signoff` component in `templates/components.html` renders
them, so pages simply write `{{ <signoff /> }}`. Change the config values to update
the coda everywhere. The signature uses the self-hosted Great Vibes script
(`static/fonts`, OFL); layout and type are styled by `.signoff` in
`static/css/site.css`.

Artwork with a title and artist credit uses the `artwork` component in
`templates/components.html`:

```text
{{ <artwork src="/cc2a.gif" title="Danya Winterborn and Bard Kestran" artist="Laura Cameron" alt="Danya and Kestran" /> }}
```

An optional `note="..."` adds provenance below the credit. Use `href="/path/"`
to link the image and `artist_url="/path/"` to link the artist credit. Supply descriptive
`alt` text for the image. Shared `.artwork` rules in `static/css/site.css` control
the responsive image, centered caption, title, and attribution.

Every page declares the club crest as its site icon. `templates/base.html` links the
multi-resolution `static/favicon.ico`, the PNG sizes in `static/icons/`, and
`static/site.webmanifest`; the browser-chrome color comes from the Valdemar blue in the
`theme-color` meta tag. Those raster files are cropped from the transparent
`static/images/queens-own-crest.webp`, so replace them alongside that crest if the
artwork changes.

To regenerate canonical links, redirects, and publication indexes after changing
the preserved archive or refreshing PDF availability evidence:

```sh
python3 scripts/organize_site.py
python3 scripts/build.py
python3 scripts/verify.py
python3 -m unittest discover -s scripts -p 'test_*.py'
```

The organizer preserves original bodies, credits, and anchors. It updates source
metadata and internal URLs using explicit content rules. Link text that was a legacy
URL or path is replaced with the destination page's title, so labels stay readable and
survive future path changes; a link whose text named a different page than its
destination is pointed at the page it names. Month-only newsletter dates
use the first day for sorting, with `date_precision = "month"`; the UI shows the
known month/year, not an invented publication day. Missing issues retain unavailable
notices and unresolved inventory statuses.

## Import provenance

The club content was imported once from the hand-coded archive
(`../queens-own/queensown.org`) and the selected Dragonlords pages. The importer and
the archive-to-Markdown conversion pipeline that produced the preserved content have
since been removed, because the import is not repeated; those pages are now maintained
as ordinary Markdown and HTML. Preserved pages retain `extra.legacy_source` for
provenance, and the original source directory was never modified.

`data/migration-report.json` lists references repaired during that import and missing
source files.
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

`data/link-corrections.json` records the link fixes and anchor aliases applied during
the one-time import; the preserved pages already carry them. After recovering a
resource, remove its entry from `data/link-dispositions.json` and its unavailable
notice from the page, refresh live evidence where appropriate, then rerun the
organizer, rebuild, and verify.

## HTML audit

The original pages contained malformed attribute quoting and unescaped `<`. The pages
predate emoji, so they use ``<g>`` (grin) and similar letter emoticons as text, which a
lenient parser reads as unknown elements and can turn into swallowed links, escaped
markup, and bogus tags. Those defects were repaired during the one-time import, which
also moved the presentational markup that survives inside kept HTML (tables and images)
into shared classes in `static/css/site.css`; the repair and conversion pipeline has
been retired.

`scripts/audit_html.py` audits the remaining HTML for structural, presentational, and
semantic problems and records a content-preservation baseline.
`python3 scripts/audit_html.py --check` fails while unresolved structural errors
remain, and `scripts/verify.py` runs it, plus a scan of the built pages for unrendered
Markdown, during deployment verification. Intentional
exceptions are listed in `data/html-exceptions.json` and documented in
[`docs/html-audit.md`](docs/html-audit.md).

## Accessibility audit

`scripts/audit_a11y.py` checks the built pages for accessibility problems, and
`scripts/verify.py` runs it during deployment verification, so a regression fails
the build. The rules are:

| Rule | Checks |
| --- | --- |
| `html-has-lang` | `<html>` declares a language |
| `document-title` | the page has a non-empty title |
| `page-has-one-h1` | exactly one `<h1>` |
| `heading-order` | no skipped heading levels |
| `image-alt` | every `<img>` has an `alt` attribute |
| `link-name` | every link has an accessible name |
| `link-text` | link text is not "here" or "click here" |
| `landmark-one-main` | exactly one `<main>` landmark |
| `skip-link` | a skip link to `#main` is present |
| `table-header` | data tables have header cells, or are marked `role="presentation"` |

Run it directly with `python3 scripts/audit_a11y.py --check`. The machine-readable
result is `data/a11y-report.json`, and `data/a11y-exceptions.json` lists any
acknowledged exceptions (currently empty).

## Content on Dragonlords

[`docs/dragonlords-migration-inventory.md`](docs/dragonlords-migration-inventory.md)
identifies Queen's Own and Velgarth content left on the other site by the original
filename-based split. The complete file spreadsheet and page/dependency inventory
are in `data/dragonlords-file-inventory.csv` and
`data/dragonlords-content-inventory.json`; these are one-time migration snapshots, and
the inventory and import tooling has been retired.

The selected club pages were migrated under descriptive paths. The bookstore
and substantive Dragonlords material stay on the other site; shared hosting footers
and bookstore promotions were removed from imported copies.
`data/dragonlords-route-map.json` records the imported paths;
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
