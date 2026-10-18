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
`<` that turned the era's ``<g>`` "grin" emoticon (shorthand that predates emoji) and
broken links (`<http:>`) into bogus elements.
The one-time import normalized the quotes and broken fragments on the raw archive
bytes and escaped the emoticons and fragments back to literal text. The repair and
conversion pipeline has since been retired.

**Emoticons read as tags.** A ``<g>`` (grin) is text, not a tag, but a lenient parser
reads it as an unknown element and can nest the content that follows inside it — an
unclosed `<font>` can likewise wrap the rest of a page. During the import, list items
nested this way were released, and block content found inside a paragraph was rendered
as blocks instead of flattening it into one line, so a single stray emoticon or tag no
longer collapses a long newsletter.

**HTML blocks that would swallow Markdown.** A standalone `<img>` (or other block
tag) placed immediately before prose starts an HTML block that hides every following
Markdown line until a blank line. The import separated a list item's trailing block
from the text that follows it, and `scripts/verify.py` scans the built pages for
unrendered Markdown headings or link syntax so the problem cannot quietly return.

**Nesting, headings, anchors.** The import moved named anchors and
table-of-contents links onto their headings, released block content out of stray
anchors, removed targetless anchors, deduped ids, started content headings at `<h2>`
(the templates render the page `<h1>`), and filled skipped heading levels.

**Presentation.** The import converted the presentational markup that
survives inside kept HTML (tables and images) into `align-*`, `valign-*`,
`border-*`, `cellpadding-*`, `cellspacing-*`, `table-align-*`, and `float-*` classes
defined in `static/css/site.css`, and moved one-off dimensions to inline styles.

**HTML → Markdown.** The import converted each page body to
Markdown: headings, paragraphs, lists, blockquotes, `<hr>`, emphasis, and links
become Markdown; `<div>`, `<center>`, and presentational wrappers are removed;
`<img>`, image-only links, named anchors, `<dl>`, and genuine **data tables** stay
HTML; **layout tables** are converted to Markdown, or — where the boxed table
styling is part of the preserved look — kept as HTML with `role="presentation"` so
assistive technology ignores their table structure; `<xmp>`
becomes a fenced code block. PDF links that carry the `__PDF_BASE_URL__` token stay
HTML because the token is substituted after Markdown rendering. The conversion ran
once during the import; the preserved pages carry its output.

A preservation check confirms every changed page keeps its prose, links, images, and
anchors, and every class used in the content is defined in the stylesheet.

## Remaining warnings

These are reported but are not structural errors.

| Rule | Occurrences | Files | Disposition |
| --- | ---: | ---: | --- |
| `table_without_header` | 0 | 0 | Resolved: genuine data tables carry a `<caption>` and header cells, and layout tables are marked `role="presentation"`, which the rule skips. |
| `nested_table` | 1 | 1 | Acceptable: one nested data table; retained. |

Every image carries an `alt` attribute (many are intentionally empty decorative
spacers), and no migrated image lacks `src`; unavailable-image placeholders use
`data-unavailable-target` and are recognized rather than reported.

## Intentional exceptions

`data/html-exceptions.json` is currently empty: the two `<xmp>` code-sample pages are
now fenced code blocks, so nothing needs to be preserved as escaped markup.

## Not yet covered

Rendering on desktop and mobile is still a manual check against the built site.
`scripts/verify.py` runs automated checks against the built pages (unresolved PDF
hosts, missing local links and anchors, unrendered Markdown, duplicate IDs, and
local `<img>` elements without intrinsic `width`/`height`), and the audit
inspects source markup for structural, presentational, and semantic problems;
the table classification (data vs. layout) is editorial.
