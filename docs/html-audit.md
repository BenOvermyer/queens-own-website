# HTML audit and content-preservation baseline

Issue: https://github.com/BenOvermyer/queens-own-website/issues/5

## What this audit covers

The preserved content pages are Markdown with a small amount of retained HTML
(tables, images, `<dl>` lists, and named anchors). The audit reads `content/`, ignores
Markdown code spans/fences, and then reports two things per page: the problems in any
remaining HTML, and a content-preservation baseline (visible-text digest plus link,
image, anchor, table, and heading counts).

Run it with `python3 scripts/audit_html.py`. The machine-readable result is
`data/html-audit-report.json`; `--check` exits non-zero while unresolved structural
errors remain, and `scripts/verify.py` runs that check as part of deployment
verification. Regression tests live in `scripts/test_audit_html.py`.

## Result

There are **no unresolved structural errors**: no unclosed or mismatched tags, no
malformed attributes, and no duplicate anchor ids. The presentational HTML that the
archive relied on has been converted to Markdown or moved into shared stylesheet
classes.

## Repairs applied

**Malformed markup → clean HTML.** The original pages had mismatched or missing
attribute quotes (`href='page.htm">`, `href="mailto:a@b.com>a@b.com</a>`, links whose
`href` swallowed their own `</a>`, and malformed `<font=…>` tags), plus unescaped
`<` that turned emoticons (`<g>`) and broken links (`<http:>`) into bogus elements.
`scripts/markup_repairs.py` normalizes the quotes and broken fragments on the raw
archive bytes, and `scripts/markup_normalize.py` escapes the bogus elements back to
text.

**Nesting, headings, anchors.** `scripts/markup_normalize.py` moves named anchors and
table-of-contents links onto their headings, releases block content out of stray
anchors, removes targetless anchors, dedupes ids, starts content headings at `<h2>`
(the templates render the page `<h1>`), and fills skipped heading levels.

**Presentation.** `scripts/markup_destyle.py` converts the presentational markup that
survives inside kept HTML (tables and images) into `align-*`, `valign-*`,
`border-*`, `cellpadding-*`, `cellspacing-*`, `table-align-*`, and `float-*` classes
defined in `static/css/site.css`, and moves one-off dimensions to inline styles.

**HTML → Markdown.** `scripts/html_to_markdown.py` converts each page body to
Markdown: headings, paragraphs, lists, blockquotes, `<hr>`, emphasis, and links
become Markdown; `<div>`, `<center>`, and presentational wrappers are removed;
`<img>`, image-only links, named anchors, `<table>`, and `<dl>` stay HTML; `<xmp>`
becomes a fenced code block. PDF links that carry the `__PDF_BASE_URL__` token stay
HTML because the token is substituted after Markdown rendering. `markup_normalize`
runs the whole sequence over existing content, and both importers (`migrate.py`,
`migrate_dragonlords.py`) emit Markdown directly so a reimport stays correct.

A preservation check confirms every changed page keeps its prose, links, images, and
anchors, and every class used in the content is defined in the stylesheet.

## Remaining warnings

These are reported but are not structural errors.

| Rule | Occurrences | Files | Disposition |
| --- | ---: | ---: | --- |
| `table_without_header` | 149 | 62 | Editorial: most are genuine data tables with no header row (recipe ingredient lists, schedule grids); adding `<th>` automatically would corrupt data. |
| `nested_table` | 2 | 2 | Acceptable: a webring badge and one nested data table; retained. |

Every image carries an `alt` attribute (many are intentionally empty decorative
spacers), and no migrated image lacks `src`; unavailable-image placeholders use
`data-unavailable-target` and are recognized rather than reported.

## Intentional exceptions

`data/html-exceptions.json` is currently empty: the two `<xmp>` code-sample pages are
now fenced code blocks, so nothing needs to be preserved as escaped markup.

## Not yet covered

Rendering on desktop and mobile is a manual check against the built site; the audit
inspects source markup only. The table classification is editorial.
