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

The imported markup has **no unresolved structural errors**: no unclosed or
mismatched tags, no malformed attributes, no duplicate anchor ids, and no escaped
markup outside the acknowledged exceptions below. Obsolete and presentation-only
markup has been moved out of the content into shared stylesheet classes.

## Repairs applied

**Malformed markup.** The original pages contained mismatched or missing attribute
quotes (for example `href='page.htm">`, `href="mailto:a@b.com>a@b.com</a>`, or a link
whose `href` swallowed its own `</a>`), plus a handful of malformed `<font>` tags. A
lenient parser read the value as everything up to the next quote, swallowing the link
text and following markup; on serialization the swallowed tags returned as escaped
`&lt;`/`&gt;` text. This affected the 2000–2005 convention listings most heavily.

- `scripts/markup_repairs.py` normalizes those quotes and fragments on the raw archive
  bytes. `scripts/migrate.py` and `scripts/migrate_dragonlords.py` apply it before
  parsing, so a reimport no longer restores the broken markup. The importer also drops
  duplicate named anchors instead of emitting a duplicate `id`.

**Nesting and headings.**

- `scripts/markup_normalize.py` repairs invalid block-in-anchor nesting and heading
  order: named anchors and table-of-contents links that wrapped headings become
  headings carrying the id or containing the link; stray anchors that swallowed whole
  sections release that content; targetless anchors are removed; content headings
  start at `<h2>` (the templates already render the page `<h1>`) with no skipped
  levels and no empty headings.

**Presentation.**

- `scripts/markup_destyle.py` replaces obsolete and presentational markup with classes
  defined in `static/css/site.css`: `<font face size color>` becomes `<span>` with
  `ff-*`, `fs-*` and `c-*` classes; `<center>` becomes `<div class="center">`;
  `align`/`valign` become `align-*`/`valign-*` (or `float-*` on images and
  `table-align-*` on tables); table `border`/`cellpadding`/`cellspacing` become
  matching classes; and one-off `width`/`height`/`bgcolor` values become inline
  styles. Valid `<u>`/`<s>` and the intentional `<xmp>` code-sample element are left
  alone.

**Unescaped pseudo-tags.**

- Unescaped `<` in the source turned emoticons (`<g>`, `<grin>`, `<sigh>`) and
  malformed links (`<http:>`, `<mailto:…>`, `<ahref="http:">`) into bogus elements
  that hid their text. `markup_normalize` escapes them back to text, and the audit
  reports any such element as `unknown_element`.

`markup_normalize.run()` applies all three transforms and is idempotent over existing
content (`python3 scripts/markup_normalize.py`). The two `<xmp>` pages are processed
with their `<xmp>` blocks protected, so their escaped contents survive verbatim.

Four pages needed a targeted edit beyond the general rules: the display-name
`mailto:` on the chapters page, the Vanyel Fan Club chat link, a duplicate `special`
anchor, and a Michigan Renaissance Festival link whose opening `<` had a space after
it.

A content-preservation check compares each changed page against its committed
version: every page keeps its prose, links, images, and anchors, or gains them. Every
generated class is defined in `static/css/site.css`.

## Remaining warnings

These are reported but are not structural errors.

| Rule | Occurrences | Files | Disposition |
| --- | ---: | ---: | --- |
| `table_without_header` | 150 | 62 | Editorial: most are genuine data tables with no header row (recipe ingredient lists, schedule grids); adding `<th>` automatically would corrupt data. |
| `nested_table` | 2 | 2 | Acceptable: a webring badge and one nested data table; retained. |

The audit models HTML's implicit paragraph closing, so a `<p>` followed by a block
element is not reported as a nesting error; only a block that cannot close a
paragraph (such as the obsolete `<center>`) is.

Every image carries an `alt` attribute (many are intentionally empty decorative
spacers), and no migrated image lacks `src`; unavailable-image placeholders use
`data-unavailable-target` and are recognized rather than reported.

## Intentional exceptions

`data/html-exceptions.json` acknowledges findings that are deliberate and must
survive verbatim. Each entry names the file, the rule, and a reason.

| File | Rule | Reason |
| --- | --- | --- |
| `content/membership/club-seal.md` | `escaped_markup_in_text` | The page intentionally shows the seal's HTML fragment as escaped text to copy. |
| `content/community/webring-code.md` | `escaped_markup_in_text` | The page intentionally shows the webring HTML fragment as escaped text to copy. |

`<xmp>` is retained deliberately as the code-sample element, so it is not treated as
obsolete, and the two pages that use it are handled with the block protected.

## Not yet covered

Rendering on desktop and mobile is a manual check against the built site; the audit
inspects source markup only. The table classification is editorial.
