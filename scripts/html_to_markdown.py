#!/usr/bin/env python3
"""Convert preserved legacy HTML bodies to Markdown.

Rules:

* headings, paragraphs, lists, blockquotes, ``<hr>``, ``<pre>`` and inline emphasis
  become Markdown;
* ``<div>``/``<center>`` and presentational wrappers (``<span>``, ``<font>``, ``<u>``,
  ``<big>``, ``<tt>``, ``<small>``) are removed while keeping their text;
* ``<a>`` with an ``href`` becomes a Markdown link, except an image-only link, which
  stays HTML; a named anchor with no ``href`` stays HTML so fragment targets survive;
* ``<img>`` stays HTML;
* ``<table>`` stays HTML when it is a genuine data table (consistent multi-column rows
  with inline cells); a layout table (single-column or block-containing cells) is
  converted to Markdown. ``<dl>`` stays HTML;
* ``<xmp>`` becomes a fenced code block;
* a ``<br>`` becomes a soft line break (joined text), and Markdown metacharacters in
  text are escaped with entities rather than backslashes.

Text is escaped for Markdown so leftover ``<g>``-style text renders literally.
"""
import html
import re

from bs4 import BeautifulSoup, Comment, NavigableString

BLOCK_TAGS = {
    'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'table', 'dl', 'dt', 'dd',
    'blockquote', 'pre', 'hr', 'div', 'center', 'section', 'article', 'header', 'footer',
    'main', 'aside', 'nav', 'figure', 'figcaption', 'fieldset', 'form', 'address', 'xmp',
    'details', 'summary',
}
HEADING_TAGS = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}
WRAPPER_TAGS = {'div', 'center', 'span', 'font', 'u', 'big', 'tt', 'small'}
DROP_TAGS = {'script', 'style', 'iframe', 'object', 'embed'}
HTML_TAGS = {'table', 'dl', 'dt', 'dd', 'sub', 'sup'}
# Escape only what Markdown would otherwise interpret, using entities rather than
# backslashes so the source stays readable.
ESCAPE_TABLE = str.maketrans({'\\': '&#92;', '<': '&lt;', '*': '&#42;', '`': '&#96;'})


def _escape(text):
    return text.translate(ESCAPE_TABLE)


def _collapse(text):
    return re.sub(r'[ \t\r\n]+', ' ', text).strip()


def _inline_node(node):
    name = node.name
    if name == 'br':
        return ' '
    if name in ('b', 'strong'):
        return '**' + _inline(node).strip() + '**'
    if name in ('i', 'em'):
        return '*' + _inline(node).strip() + '*'
    if name == 'a':
        return _anchor(node)
    if name == 'img':
        return str(node)
    if name == 'code':
        return '`' + node.get_text() + '`'
    if name in HTML_TAGS:
        return _html(node)
    if name in WRAPPER_TAGS:
        return _inline(node)
    if name in DROP_TAGS:
        return ''
    if name in BLOCK_TAGS:
        return ' ' + _block(node) + ' '
    # Unknown element (normally already unescaped upstream): render it literally.
    return _escape(f'<{name}>') + _inline(node)


def _inline(node):
    """Render the inline children of a node."""
    parts = []
    for child in node.children:
        if isinstance(child, Comment):
            continue
        parts.append(_escape(str(child)) if isinstance(child, NavigableString) else _inline_node(child))
    return _collapse(''.join(parts))


def _anchor(anchor):
    href = (anchor.get('href') or '').strip()
    identifier = anchor.get('id') or anchor.get('name')
    if not href:
        return f'<a id="{identifier}"></a>' if identifier else _inline(anchor)
    if '__PDF_BASE_URL__' in href:
        # The token is substituted after Markdown rendering, which would otherwise
        # resolve the relative destination first, so this link stays HTML.
        return _html(anchor)
    if not anchor.get_text(strip=True) and anchor.find('img'):
        return _html(anchor)
    destination = href.replace(' ', '') if href.lower().startswith('mailto:') else href.replace(' ', '%20')
    return f'[{_inline(anchor)}]({destination})'


def _html(node):
    clone = BeautifulSoup(str(node), 'lxml').find(node.name)
    for tag in clone.find_all(list(WRAPPER_TAGS) + list(DROP_TAGS)):
        if tag.name in DROP_TAGS:
            tag.decompose()
        else:
            tag.unwrap()
    return str(clone)


def _heading(heading):
    prefix = f'<a id="{heading["id"]}"></a>\n\n' if heading.get('id') else ''
    return prefix + '#' * int(heading.name[1]) + ' ' + _inline(heading)


def _code_block(element):
    return '```\n' + html.unescape(element.get_text()).strip('\n') + '\n```'


def _list_item(item):
    parts = []
    buffer = []

    def flush():
        text = _collapse(''.join(buffer)).strip()
        if text:
            parts.append(text)
        buffer.clear()

    for child in item.children:
        if isinstance(child, Comment):
            continue
        if isinstance(child, NavigableString):
            buffer.append(_escape(str(child)))
        elif child.name in BLOCK_TAGS or (child.name in WRAPPER_TAGS and child.find(LAYOUT_BLOCK_TAGS)):
            flush()
            block = _block(child) if child.name in BLOCK_TAGS else _render(child)
            if block.strip():
                parts.append(block)
        else:
            buffer.append(_inline_node(child))
    flush()
    rendered = parts[0] if parts else ''
    for block in parts[1:]:
        rendered += '\n' + '\n'.join('  ' + line for line in block.splitlines())
    return rendered


def _list(element):
    ordered = element.name == 'ol'
    items = []
    loose = []

    def flush_loose():
        if loose:
            holder = BeautifulSoup('<li></li>', 'html.parser').li
            for node in loose:
                holder.append(node.extract() if hasattr(node, 'extract') else node)
            items.append(holder)
            loose.clear()

    for child in list(element.children):
        if isinstance(child, Comment):
            continue
        if getattr(child, 'name', None) == 'li':
            flush_loose()
            items.append(child)
        elif isinstance(child, NavigableString) and not child.strip():
            continue
        else:
            loose.append(child)
    flush_loose()
    lines = []
    for index, item in enumerate(items, 1):
        marker = f'{index}.' if ordered else '-'
        lines.append(marker + ' ' + _list_item(item))
    return '\n'.join(lines)


LAYOUT_BLOCK_TAGS = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'dl', 'table', 'blockquote', 'pre'}


def _is_data_table(table):
    """A genuine data table has consistent multi-column rows and no block-level cells."""
    rows = table.find_all('tr')
    if not rows:
        return False
    counts = [len(row.find_all(['td', 'th'], recursive=False)) for row in rows]
    if min(counts) < 2 or len(set(counts)) > 1:
        return False
    return not any(cell.find(LAYOUT_BLOCK_TAGS) for cell in table.find_all(['td', 'th']))


def _layout_table(table):
    """Render a layout table's cells as Markdown blocks in document order."""
    blocks = []
    for row in table.find_all('tr'):
        for cell in row.find_all(['td', 'th'], recursive=False):
            rendered = _render(cell)
            if rendered.strip():
                blocks.append(rendered)
    return '\n\n'.join(blocks)


def _block(element):
    name = element.name
    if name == 'p':
        return _inline(element)
    if name in HEADING_TAGS:
        return _heading(element)
    if name == 'hr':
        return '---'
    if name in ('pre', 'xmp'):
        return _code_block(element)
    if name == 'table':
        return _html(element) if _is_data_table(element) else _layout_table(element)
    if name == 'dl':
        return _html(element)
    if name in ('ul', 'ol'):
        return _list(element)
    if name == 'blockquote':
        inner = _render(element)
        return '\n'.join('> ' + line if line else '>' for line in inner.splitlines())
    if name in WRAPPER_TAGS:
        return _render(element)
    if name in DROP_TAGS:
        return ''
    if name in BLOCK_TAGS:
        return _render(element)
    return _inline(element)


def _render(container):
    blocks = []
    buffer = []

    def flush():
        text = _collapse(''.join(buffer)).strip()
        if text:
            blocks.append(text)
        buffer.clear()

    for child in container.children:
        if isinstance(child, Comment) or child.name in DROP_TAGS:
            continue
        if isinstance(child, NavigableString):
            buffer.append(_escape(str(child)))
        elif child.name in BLOCK_TAGS:
            flush()
            block = _block(child)
            if block.strip():
                blocks.append(block)
        elif child.name in WRAPPER_TAGS and child.find(LAYOUT_BLOCK_TAGS):
            flush()
            block = _render(child)
            if block.strip():
                blocks.append(block)
        else:
            buffer.append(_inline_node(child))
    flush()
    return '\n\n'.join(blocks)


def convert(source):
    """Convert an HTML body (Markdown string or a parsed Tag) to Markdown."""
    if isinstance(source, str):
        soup = BeautifulSoup(source, 'lxml')
        root = soup.body or soup
    else:
        root = source.body or source
    return _render(root).strip() + '\n'
