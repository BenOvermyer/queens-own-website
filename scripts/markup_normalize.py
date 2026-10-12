#!/usr/bin/env python3
"""Normalize legacy HTML nesting in preserved content.

The hand-authored archive often nests block content inside inline anchors, for
example a named-anchor idiom ``<a id="x"><h2>Title</h2></a>``, a table-of-contents
link ``<a href="#s"><h3>Section</h3></a>``, or a stray ``<a>`` whose closing tag was
lost so it wraps the rest of the page. ``normalize_soup`` repairs those:

* a single heading inside an anchor moves the anchor inside the heading, or moves
  the anchor's id onto the heading, so the heading stays a heading and the link or
  anchor target is preserved;
* any other block content inside an anchor is lifted back out after it, so the
  anchor wraps only its inline text;
* anchors with no target and no content are removed, and empty anchors keep their
  text but lose the meaningless tag.

Files listed in ``data/html-exceptions.json`` and files using the raw-text ``<xmp>``
element (whose escaped contents must survive verbatim) are left untouched.
"""
import json
from difflib import SequenceMatcher
from pathlib import Path
import re

from bs4 import BeautifulSoup

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


def normalize_soup(soup):
    """Repair heading order, block-in-anchor nesting, and empty anchors in place."""
    normalize_headings(soup)
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
    """Apply normalize_soup to every content document and report what changed."""
    exceptions = json.loads((ROOT / 'data/html-exceptions.json').read_text())
    skip = {entry['file'] for entry in exceptions}
    changed = []
    for path in sorted((ROOT / 'content').rglob('*.md')):
        text = path.read_text()
        if '+++' not in text:
            continue
        front, html = text.split('+++', 2)[1:]
        if '<' not in html or '<xmp' in html or path.relative_to(ROOT).as_posix() in skip:
            continue
        soup = BeautifulSoup(html, 'lxml')
        before = str(soup)
        normalize_soup(soup)
        if str(soup) == before:
            continue
        content = soup.body.decode_contents() if soup.body else str(soup)
        rendered = '+++' + front + '+++\n\n' + content.rstrip() + '\n'
        original_lines = text.splitlines()
        lines = [line.rstrip() for line in rendered.splitlines()]
        matcher = SequenceMatcher(a=[line.rstrip() for line in original_lines], b=lines, autojunk=False)
        for tag, start, end, new_start, new_end in matcher.get_opcodes():
            if tag == 'equal':
                lines[new_start:new_end] = original_lines[start:end]
        path.write_text('\n'.join(lines).rstrip() + '\n')
        changed.append(path.relative_to(ROOT).as_posix())
    print(f'Normalized {len(changed)} pages.')
    return changed


if __name__ == '__main__':
    run()
