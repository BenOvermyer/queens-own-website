#!/usr/bin/env python3
"""Audit imported legacy HTML for malformed markup, obsolete presentation, and semantic gaps.

The audit reads the preserved HTML bodies in `content/` rather than the built site, because
that is what the importer regenerates and what repairs must change. It records a
content-preservation baseline (visible-text digest and structural counts) so later repair
steps can prove they lost no prose, links, artwork, or anchors.

Unresolved structural errors fail with `--check`; acknowledged exceptions are listed in
`data/html-exceptions.json` and documented in `docs/html-audit.md`.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import tomllib
from html.parser import HTMLParser

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]

# HTML elements that never have an end tag; they must not be pushed on the open-element stack.
VOID_ELEMENTS = {
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
    'meta', 'param', 'source', 'track', 'wbr',
}
# Elements whose end tag may be omitted; their absence is not malformed markup.
OPTIONAL_END_ELEMENTS = {
    'p', 'li', 'td', 'tr', 'th', 'option', 'dt', 'dd', 'thead', 'tbody',
    'tfoot', 'colgroup', 'caption', 'html', 'head', 'body', 'rt', 'rp', 'optgroup',
}
BLOCK_ELEMENTS = {
    'address', 'article', 'aside', 'blockquote', 'center', 'div', 'dl', 'fieldset',
    'figure', 'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'hr',
    'main', 'nav', 'ol', 'p', 'pre', 'section', 'table', 'ul',
}
# Obsolete or presentation-only elements that modern HTML replaced with CSS.
# `u` and `s` remain valid HTML5 elements; `xmp` is retained deliberately as the
# code-sample element, so both are excluded.
OBSOLETE_ELEMENTS = {
    'applet', 'basefont', 'big', 'blink', 'center', 'dir', 'font', 'frame',
    'frameset', 'isindex', 'marquee', 'menu', 'nobr', 'noembed', 'noframes',
    'plaintext', 'strike', 'tt',
}
# Attributes that carry presentation rather than meaning.
PRESENTATIONAL_ATTRIBUTES = {
    'align', 'alink', 'background', 'bgcolor', 'border', 'bordercolor', 'cellpadding',
    'cellspacing', 'char', 'charoff', 'clear', 'color', 'compact', 'face', 'height',
    'hspace', 'language', 'link', 'nowrap', 'size', 'text', 'valign', 'version',
    'vlink', 'vspace', 'width',
}
VALID_ATTRIBUTE_NAME = re.compile(r'^[A-Za-z_:][-A-Za-z0-9_:.]*$')
# Escaped markup that leaked into text, e.g. "&lt;/a&gt;" from a link whose tag was mangled.
# Only escaped opening angle brackets count: a bare "&gt;" is an ordinary quoted-reply marker
# or an emoticon such as "&lt;g&gt;", not malformed markup.
ESCAPED_MARKUP = re.compile(r'&lt;\s*/?\s*(?:a|img|font|center|table|tr|td|th|li|ul|ol|p|div|br|b|i|h[1-6]|pre|span|blockquote|dl|dt|dd)\b', re.I)


def read_body(text):
    """Return the HTML/Markdown body after TOML front matter, or the whole text."""
    if text.startswith('+++'):
        _, front, body = text.split('+++', 2)
    else:
        front, body = '', text
    try:
        meta = tomllib.loads(front)
    except tomllib.TOMLDecodeError:
        meta = {}
    return meta, body


class MarkupChecker(HTMLParser):
    """Track tag structure and malformed attributes in a raw HTML fragment."""

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.stack = []
        self.unclosed = []
        self.mismatched = []
        self.suspect_attributes = []
        self.block_in_paragraph = []
        self.block_in_anchor = []

    def _check_attributes(self, tag, attrs):
        for name, value in attrs:
            if not VALID_ATTRIBUTE_NAME.match(name) or (value is not None and ('<' in value or '>' in value)):
                self.suspect_attributes.append({'tag': tag, 'attribute': name, 'value': (value or '')[:120]})

    def handle_starttag(self, tag, attrs):
        self._check_attributes(tag, attrs)
        if tag in BLOCK_ELEMENTS:
            open_tags = [entry[0] for entry in self.stack]
            if 'a' in open_tags:
                self.block_in_anchor.append(tag)
            # A <p> opened inside a <p> is an implicit close, not a structural error.
            if 'p' in open_tags and tag != 'p':
                self.block_in_paragraph.append(tag)
        if tag not in VOID_ELEMENTS:
            self.stack.append([tag])

    def handle_startendtag(self, tag, attrs):
        self._check_attributes(tag, attrs)

    def handle_endtag(self, tag):
        if tag in VOID_ELEMENTS:
            return
        if any(entry[0] == tag for entry in self.stack):
            while self.stack:
                if self.stack.pop()[0] == tag:
                    break
        else:
            self.mismatched.append(tag)

    def finish(self):
        self.unclosed = [entry[0] for entry in self.stack if entry[0] not in OPTIONAL_END_ELEMENTS]
        return self


def audit_file(path, text, root):
    meta, body = read_body(text)
    if '<' not in body:
        return None
    soup = BeautifulSoup(body, 'lxml')
    checker = MarkupChecker()
    checker.feed(body)
    checker.close()
    checker.finish()

    findings = []

    def add(rule, severity, examples, note=None, count=None):
        finding = {'rule': rule, 'severity': severity,
                   'count': count if count is not None else len(examples),
                   'examples': examples[:8]}
        if note:
            finding['note'] = note
        findings.append(finding)

    if checker.mismatched:
        add('mismatched_end_tag', 'error', checker.mismatched)
    if checker.unclosed:
        add('unclosed_element', 'error', checker.unclosed)
    if checker.suspect_attributes:
        add('malformed_attribute', 'error',
            [f"<{row['tag']} {row['attribute']}=\"{row['value']}\">" for row in checker.suspect_attributes])
    escaped = [body[match.start():match.start() + 100].strip() for match in ESCAPED_MARKUP.finditer(body)]
    if escaped:
        add('escaped_markup_in_text', 'error', escaped,
            'Escaped tags in text; usually a link or element whose source was already broken.')
    if checker.block_in_anchor:
        add('block_in_anchor', 'warning', checker.block_in_anchor,
            'Block element nested in <a>; the legacy named-anchor idiom, repairable by moving the id to the block.')
    if checker.block_in_paragraph:
        add('block_in_paragraph', 'warning', checker.block_in_paragraph,
            'Block element opened while a <p> is open; close the paragraph first.')

    obsolete = sorted({node.name for node in soup.find_all(True) if node.name in OBSOLETE_ELEMENTS})
    if obsolete:
        counts = sorted(({name: len(soup.find_all(name)) for name in obsolete}).items(), key=lambda item: -item[1])
        add('obsolete_element', 'warning', [f'{name} x{count}' for name, count in counts], count=sum(count for _, count in counts))

    presentational = sorted({attr for node in soup.find_all(True) for attr in node.attrs if attr in PRESENTATIONAL_ATTRIBUTES})
    if presentational:
        counts = sorted(({attr: sum(1 for n in soup.find_all(True) if attr in n.attrs) for attr in presentational}).items(), key=lambda item: -item[1])
        add('presentational_attribute', 'warning', [f'{attr} x{count}' for attr, count in counts], count=sum(count for _, count in counts))

    missing_alt = ['<img>'] * sum(1 for img in soup.find_all('img') if not img.has_attr('alt'))
    if missing_alt:
        add('image_missing_alt', 'warning', missing_alt)

    images_without_src = ['<img>'] * sum(1 for img in soup.find_all('img') if not img.get('src') and not img.has_attr('data-unavailable-target'))
    if images_without_src:
        add('image_missing_src', 'error', images_without_src)

    fragment_links = [a.get('href') for a in soup.find_all('a', href=True) if a['href'].strip() in ('', '#')]
    if fragment_links:
        add('empty_link', 'warning', fragment_links)

    anchor_no_target = ['<a>'] * sum(1 for a in soup.find_all('a') if not a.get('href') and not a.get('name') and not a.get('id'))
    if anchor_no_target:
        add('anchor_without_target', 'warning', anchor_no_target)

    headings = [h.name for h in soup.find_all(re.compile(r'^h[1-6]$'))]
    levels = [int(h[1]) for h in headings]
    if levels.count(1) > 1:
        add('multiple_h1', 'warning', [f'h1 x{levels.count(1)}'],
            'Templates already render the page title as <h1>.')
    skipped = [f'h{a}->h{b}' for a, b in zip(levels, levels[1:]) if b > a + 1]
    if skipped:
        add('heading_level_skipped', 'warning', skipped)

    duplicate_ids = [value for value, count in _counts(n.get('id') for n in soup.find_all(id=True)).items() if count > 1]
    if duplicate_ids:
        add('duplicate_id', 'error', duplicate_ids)
    duplicate_names = [value for value, count in _counts(n.get('name') for n in soup.find_all('a', attrs={'name': True})).items() if count > 1]
    if duplicate_names:
        add('duplicate_anchor_name', 'error', duplicate_names)

    tables = soup.find_all('table')
    if tables:
        without_header = [f'table {i + 1} ({len(t.find_all("tr"))} rows)' for i, t in enumerate(tables) if not t.find('th')]
        if without_header:
            add('table_without_header', 'warning', without_header,
                'Candidate data table; confirm whether it is layout or should gain <th>.')
        nested = sum(len(t.find_all('table')) for t in tables)
        if nested:
            add('nested_table', 'warning', ['nested <table>'] * nested)

    baseline = {
        'visible_text_sha256': hashlib.sha256(re.sub(r'\s+', ' ', soup.get_text(' ')).strip().encode()).hexdigest(),
        'links': len(soup.find_all('a')),
        'images': len(soup.find_all('img')),
        'anchors': sorted({v for v in (n.get('id') for n in soup.find_all(id=True)) if v}) + sorted({n.get('name') for n in soup.find_all('a', attrs={'name': True}) if n.get('name')}),
        'tables': len(tables),
        'headings': headings,
        'legacy_source': meta.get('extra', {}).get('legacy_source'),
    }
    return {'path': path.relative_to(root).as_posix(), 'findings': findings, 'baseline': baseline}


def _counts(values):
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts


def load_exceptions():
    path = ROOT / 'data/html-exceptions.json'
    if not path.exists():
        return []
    return json.loads(path.read_text())


def is_acknowledged(finding, file_path, exceptions):
    for entry in exceptions:
        if entry.get('file') == file_path and entry.get('rule') == finding['rule']:
            return entry.get('reason', '')
    return None


def audit():
    """Audit every content document and write data/html-audit-report.json."""
    content = ROOT / 'content'
    exceptions = load_exceptions()
    files = []
    rule_counts = {}
    rule_files = {}
    unresolved_errors = []
    acknowledged = 0
    for source in sorted(content.rglob('*.md')):
        result = audit_file(source, source.read_text(), ROOT)
        if result is None:
            continue
        for finding in result['findings']:
            rule_counts[finding['rule']] = rule_counts.get(finding['rule'], 0) + finding['count']
            rule_files.setdefault(finding['rule'], set()).add(result['path'])
            reason = is_acknowledged(finding, result['path'], exceptions)
            if reason is not None:
                finding['acknowledged'] = reason
                acknowledged += 1
            elif finding['severity'] == 'error':
                unresolved_errors.append({'file': result['path'], 'rule': finding['rule'], 'count': finding['count']})
        files.append(result)
    report = {
        'summary': {
            'files_scanned': len(files),
            'rules': {rule: {'occurrences': rule_counts[rule], 'files': len(rule_files[rule])} for rule in sorted(rule_counts)},
            'acknowledged_findings': acknowledged,
            'unresolved_errors': len(unresolved_errors),
        },
        'unresolved_errors': unresolved_errors,
        'files': files,
    }
    (ROOT / 'data/html-audit-report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Exit non-zero when unresolved structural errors remain')
    args = parser.parse_args()
    result = audit()
    print(f"Audited {result['summary']['files_scanned']} documents with HTML bodies.")
    for rule, stats in result['summary']['rules'].items():
        print(f"  {rule}: {stats['occurrences']} in {stats['files']} files")
    print(f"Acknowledged exceptions: {result['summary']['acknowledged_findings']}")
    print(f"Unresolved structural errors: {result['summary']['unresolved_errors']}")
    if args.check and result['summary']['unresolved_errors']:
        raise SystemExit('Unresolved structural errors; see data/html-audit-report.json')
