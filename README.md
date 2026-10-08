# Queen's Own Website

Zola source for the Queen's Own website, migrated from the hand-coded archive.
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

Publish `public/`. Use the build script for deployment: it converts Zola's
`.htm/index.html` directories into the original `.htm` files so legacy URLs work
on object-storage hosting too. `zola serve` uses directories during preview.
The verification script requires the migration Python dependencies below.

Netlify uses `netlify.toml` to run the same deployment build and publish `public/`.
The configuration pins Zola to 0.23.6, matching the locally tested version.
The deployment build uses Python's standard library and does not need the migration
dependencies or original archive directory.

## Reimport the archive

```sh
python3 -m pip install -r requirements-migration.txt
python3 scripts/migrate.py ../queens-own/queensown.org
```

Reimporting overwrites imported content and copied static assets. Edit the importer
for repeatable changes, or edit generated content directly and avoid reimporting
those changes. The original source directory is never modified.

`data/migration-report.json` lists repaired references and missing source files.
Missing non-PDF files remain linked to the original domain pending recovery; their
availability has not been verified. `data/anchor-report.json` lists unresolved internal anchors.
The archive retains historical dates, contact details, copyright notices, and privacy text.

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
