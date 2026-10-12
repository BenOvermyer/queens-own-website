# HTML audit and content-preservation baseline

Issue: https://github.com/BenOvermyer/queens-own-website/issues/5

## What this audit covers

The repaired scope is the preserved HTML in `content/`. Those bodies are what the
importer regenerates and what repairs must change, so the audit reads the source
Markdown documents rather than the rendered `public/` tree. It scans every content
document that contains HTML — 249 documents — and reports two things per page: the
structural, presentational, and semantic problems in its markup, and a
content-preservation baseline (visible-text digest plus link, image, anchor, table,
and heading counts) so repairs can be shown to lose no prose, artwork, links, or
anchors.

Run it with `python3 scripts/audit_html.py`. The machine-readable result is
`data/html-audit-report.json`; `--check` exits non-zero while unresolved structural
errors remain, and `scripts/verify.py` runs that check as part of deployment
verification. Regression tests live in `scripts/test_audit_html.py`.

## Result

The imported markup is well-formed at the tag-token level and has **no unresolved
structural errors**: no unclosed or mismatched tags, no malformed attributes, no
duplicate anchor ids, and no escaped markup outside the acknowledged exceptions
below. Heading order is consistent and anchors no longer wrap block content.

## Repairs applied

The source of the corruption was mismatched or missing attribute quotes in the
original pages (for example `href='page.htm">`, `href="mailto:a@b.com>a@b.com</a>`,
or a link whose `href` swallowed its own `</a>`). A lenient parser read the value as
everything up to the next quote, swallowing the link text and following markup; on
serialization the swallowed tags returned as escaped `&lt;`/`&gt;` text. This
affected the 2000–2005 convention listings most heavily.

- `scripts/markup_repairs.py` normalizes those quotes and a few exact broken
  fragments on the raw archive bytes. `scripts/migrate.py` and
  `scripts/migrate_dragonlords.py` apply it before parsing, so a reimport no longer
  restores the broken markup. The importer also drops duplicate named anchors
  instead of emitting a duplicate `id`.
- `scripts/markup_normalize.py` repairs invalid block-in-anchor nesting and heading
  order: named anchors and table-of-contents links that wrapped headings become
  headings carrying the id or containing the link; stray anchors that swallowed
  whole sections release that content; targetless anchors are removed; content
  headings start at `<h2>` (the templates already render the page `<h1>`) with no
  skipped levels and no empty headings. Both importers apply it before writing a
  page, and it is idempotent over existing content
  (`python3 scripts/markup_normalize.py`).
- The affected content pages were regenerated from the repaired source. Four pages
  needed a targeted edit beyond the general rules: the display-name `mailto:` on the
  chapters page, the Vanyel Fan Club chat link, a duplicate `special` anchor, and a
  Michigan Renaissance Festival link whose opening `<` had a space after it. The two
  `<xmp>` code-sample pages were edited by hand so their escaped contents survive
  verbatim.

A content-preservation check compares each changed page against its committed
version: every page keeps its prose, links, images, and anchors, or gains them.

## Remaining warnings

These are reported but are not structural errors. Each is either presentational work
owned by the redesign (#3) or needs editorial judgment; none is a regression.

| Rule | Occurrences | Files | Disposition |
| --- | ---: | ---: | --- |
| `obsolete_element` (`center`, `font`, `xmp`) | 3563 | 248 | Redesign (#3): replace with shared styles. `xmp` is the intentional code-sample element. |
| `presentational_attribute` (`align`, `valign`, `size`, `border`, `face`…) | 8783 | 248 | Redesign (#3): move into shared styles. |
| `block_in_paragraph` | 1540 | 62 | Redesign (#3): caused by presentational `<font>`/`<center>` wrappers and implicit `<p>` closing; browsers render it correctly, so it follows the same wrapper cleanup. |
| `table_without_header` | 150 | 62 | Editorial: most are genuine data tables with no header row (recipe ingredient lists, schedule grids); adding `<th>` automatically would corrupt data. |
| `nested_table` | 2 | 2 | Acceptable: a webring badge and one nested data table; retained. |

Every image carries an `alt` attribute (many are intentionally empty decorative
spacers), and no migrated image lacks `src`; unavailable-image placeholders use
`data-unavailable-target` and are recognized rather than reported.

A deliberate exception is made for obsolete `u` and `s`, which are valid in HTML5
and carry semantics, so they are not treated as obsolete here.

## Intentional exceptions

`data/html-exceptions.json` acknowledges findings that are deliberate and must
survive verbatim. Each entry names the file, the rule, and a reason.

| File | Rule | Reason |
| --- | --- | --- |
| `content/membership/club-seal.md` | `escaped_markup_in_text` | The page intentionally shows the seal's HTML fragment as escaped text to copy. |
| `content/community/webring-code.md` | `escaped_markup_in_text` | The page intentionally shows the webring HTML fragment as escaped text to copy. |

The normalizer skips these files (and any file using `<xmp>`) so their escaped
contents are not re-serialized.

## Not yet covered

Rendering on desktop and mobile is a manual check against the built site; the audit
inspects source markup only. The presentational warnings above belong to the
redesign (#3), and the table classification is editorial.
