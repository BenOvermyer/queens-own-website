#!/usr/bin/env python3
"""Repair legacy HTML and convert the preserved content to Markdown.

`markup_normalize.run()` reads each preserved page, applies `markup_repairs`,
`normalize_soup` (heading order, anchor nesting, duplicate ids, pseudo-tags), and
`destyle_soup` (presentational markup inside retained HTML), then converts the body to
Markdown with `html_to_markdown`. The raw-text `<xmp>` element becomes a fenced code
block, and `data/html-exceptions.json` lists any pages to leave untouched (currently
none).
"""
import re
from pathlib import Path

from bs4 import BeautifulSoup
from bs4.element import NavigableString

from audit_html import KNOWN_HTML_ELEMENTS
from markup_destyle import destyle_soup
from markup_repairs import repair_markup

ROOT = Path(__file__).resolve().parents[1]

HEADING_PATTERN = re.compile(r'^h[1-6]$')
BLOCK_ELEMENTS = {
    'address', 'article', 'aside', 'blockquote', 'center', 'div', 'dl', 'fieldset',
    'figure', 'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'hr',
    'main', 'nav', 'ol', 'p', 'pre', 'section', 'table', 'ul',
}
HEADING_ELEMENTS = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}


def _meaningful(anchor):
    return [child for child in anchor.contents
            if getattr(child, 'name', None) or (isinstance(child, str) and child.strip())]


def _is_topmost_within(anchor, element):
    parent = element.parent
    while parent is not None and parent is not anchor:
        if getattr(parent, 'name', None) in BLOCK_ELEMENTS:
            return False
        parent = parent.parent
    return True


def normalize_headings(soup):
    """Start content headings at <h2> (templates render the page <h1>) and avoid skipped levels."""
    for heading in list(soup.find_all(HEADING_PATTERN)):
        if not heading.get_text(strip=True) and not heading.find(True):
            heading.decompose()
    for heading in soup.find_all(HEADING_PATTERN):
        if heading.name == 'h1':
            heading.name = 'h2'
    previous = 1
    for heading in soup.find_all(HEADING_PATTERN):
        level = int(heading.name[1])
        if level > previous + 1:
            level = previous + 1
            heading.name = f'h{level}'
        previous = level


def _unescape_unknown(soup):
    """Turn unescaped pseudo-tags (emoticons such as <g>, malformed links) back into text."""
    while True:
        unknown = [element for element in soup.find_all(True) if element.name not in KNOWN_HTML_ELEMENTS]
        if not unknown:
            return
        for element in unknown:
            element.insert_before(NavigableString(f'<{element.name}>'))
            element.unwrap()


def normalize_soup(soup):
    """Repair heading order, block-in-anchor nesting, and empty anchors in place."""
    seen_ids = set()
    for element in soup.find_all(True):
        for attribute in ('id', 'name'):
            if element.has_attr(attribute):
                if element[attribute] in seen_ids:
                    del element[attribute]
                else:
                    seen_ids.add(element[attribute])
    normalize_headings(soup)
    _unescape_unknown(soup)
    for anchor in list(soup.find_all('a')):
        if not anchor.get('href') and not anchor.get('id') and not anchor.get('name'):
            if not anchor.find(True) and not anchor.get_text(strip=True):
                anchor.decompose()
            elif not anchor.get('id') and not anchor.get('name'):
                anchor.unwrap()
    for anchor in list(soup.find_all('a')):
        if anchor.parent is None:
            continue
        if not any(getattr(child, 'name', None) in BLOCK_ELEMENTS for child in anchor.find_all(True)):
            continue
        meaningful = _meaningful(anchor)
        if len(meaningful) == 1 and getattr(meaningful[0], 'name', None) in HEADING_ELEMENTS:
            heading = meaningful[0]
            if anchor.get('href'):
                heading.extract()
                anchor.clear()
                for child in list(heading.contents):
                    anchor.append(child.extract())
                anchor.replace_with(heading)
                heading.append(anchor)
            else:
                heading.extract()
                anchor_id = anchor.get('id') or anchor.get('name')
                if anchor_id and not heading.get('id'):
                    heading['id'] = anchor_id
                anchor.replace_with(heading)
            continue
        last = anchor
        for element in [node for node in anchor.find_all(True)
                        if getattr(node, 'name', None) in BLOCK_ELEMENTS and _is_topmost_within(anchor, node)]:
            element.extract()
            last.insert_after(element)
            last = element
    return soup


def run():
    """Convert preserved HTML content documents to Markdown."""
    from html_to_markdown import convert
    changed = []
    for path in sorted((ROOT / 'content').rglob('*.md')):
        text = path.read_text()
        if '+++' not in text:
            continue
        front, html = text.split('+++', 2)[1:]
        if '<div class="original-page">' not in html:
            continue
        soup = BeautifulSoup(repair_markup(html.encode()).decode(), 'lxml')
        normalize_soup(soup)
        destyle_soup(soup)
        body = soup.body or soup
        rendered = '+++' + front + '+++\n\n' + convert(body)
        path.write_text(rendered)
        changed.append(path.relative_to(ROOT).as_posix())
    print(f'Converted {len(changed)} pages to Markdown.')
    return changed


if __name__ == '__main__':
    run()
