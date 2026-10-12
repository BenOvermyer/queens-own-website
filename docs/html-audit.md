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

The imported markup is well-formed at the tag-token level and now has **no
unresolved structural errors**. The tag structure is balanced (no unclosed or
mismatched tags), every attribute parses, no anchor id is duplicated, and no
escaped markup remains outside the acknowledged exceptions below.

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
- The affected content pages were regenerated from the repaired source. Four pages
  needed a targeted edit beyond the general rules: the display-name `mailto:` on the
  chapters page, the Vanyel Fan Club chat link, a duplicate `special` anchor, and a
  Michigan Renaissance Festival link whose opening `<` had a space after it.
- `scripts/markup_normalize.py` repairs invalid block-in-anchor nesting: named
  anchors and table-of-contents links that wrapped headings become headings that
  carry the id or contain the link, stray anchors that wrapped whole sections
  release that content, and anchors with no target are removed. Both importers
  apply it before writing a page, and it can be rerun over existing content with
  `python3 scripts/markup_normalize.py`.

A content-preservation check compares each changed page against its committed
version: every page keeps its prose, links, images, and anchors, or gains them. The
only "losses" are the intended removals of mangled markup and one duplicate anchor.

## Remaining warnings

These are reported but not structural errors. They are candidates for the redesign
(#3) and a later semantics pass, not regressions.

| Rule | Occurrences | Files |
| --- | ---: | ---: |
| `obsolete_element` (`center`, `font`, `u`, `xmp`) | 3587 | 248 |
| `presentational_attribute` (`align`, `valign`, `size`, `border`, `face`…) | 8783 | 248 |
| `block_in_paragraph` | 1880 | 68 |
| `table_without_header` | 150 | 62 |
| `heading_level_skipped` | 36 | 33 |
| `multiple_h1` | 17 | 17 |
| `nested_table` | 2 | 2 |

Every image carries an `alt` attribute (many are intentionally empty decorative
spacers), and no migrated image lacks `src`; unavailable-image placeholders use
`data-unavailable-target` and are recognized rather than reported.

## Intentional exceptions

`data/html-exceptions.json` acknowledges findings that are deliberate. Each entry
names the file, the rule, and a reason; acknowledged findings are reported but do
not count as unresolved errors.

| File | Rule | Reason |
| --- | --- | --- |
| `content/membership/club-seal.md` | `escaped_markup_in_text` | The page intentionally shows the seal's HTML fragment as escaped text to copy. |
| `content/community/webring-code.md` | `escaped_markup_in_text` | The page intentionally shows the webring HTML fragment as escaped text to copy. |

## Not yet covered

Rendering on desktop and mobile is a manual check against the built site; the audit
inspects source markup only. The remaining warnings (presentation and headings)
belong to the redesign and a later semantics pass.
