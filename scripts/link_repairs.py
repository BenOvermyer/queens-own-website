"""Shared, evidence-based corrections for imports and existing archive pages."""
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
CORRECTIONS = json.loads((ROOT / 'data/link-corrections.json').read_text())


def corrected_link(value, page, label=''):
    if value in CORRECTIONS['global']:
        return CORRECTIONS['global'][value]
    if value in CORRECTIONS['pages'].get(page, {}):
        return CORRECTIONS['pages'][page][value]
    url = urlsplit(value)
    if url.netloc in ('queensown.org', 'www.queensown.org'):
        key = unquote(url.path).lstrip('/')
        for old, new in {**CORRECTIONS['global'], **CORRECTIONS['pages'].get(page, {})}.items():
            if key == old or key == old.removeprefix('file:///'):
                return new
    else:
        key = value
    if key == 'mailto' and re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', label.strip()):
        return 'mailto:' + label.strip()
    if value.startswith('mailto:mailto:'):
        return value.replace('mailto:mailto:', 'mailto:', 1)
    return value


def repair_anchors(soup, page):
    for alias, destination in CORRECTIONS['anchors'].get(page, {}).items():
        if soup.find(id=alias):
            continue
        target = soup.find(id=destination) or soup.find('a', attrs={'name': destination})
        if target is None:
            target = next((h for h in soup.find_all(['h1', 'h2', 'h3', 'h4']) if h.get_text(' ', strip=True) == destination), None)
        if target is None:
            raise ValueError(f'Cannot locate {page}#{alias}: {destination}')
        anchor = soup.new_tag('a', id=alias)
        target.insert_before(anchor)


def annotate_gaps(soup, dispositions):
    for node in list(soup.select('[href], [src]')):
        value = node.get('href', node.get('src', ''))
        url = urlsplit(value.replace('__PDF_BASE_URL__', 'https://files.queensown.org'))
        key = value.replace('__PDF_BASE_URL__', 'https://files.queensown.org') if url.netloc == 'files.queensown.org' else unquote(url.path)
        if key not in dispositions:
            continue
        if node.name == 'img':
            node['alt'] = node.get('alt', '') + ' (image unavailable in archive)'
            node.attrs.pop('src', None)
            node['data-unavailable-target'] = value
        else:
            node['title'] = 'Unavailable in the preserved archive'
            node['data-unavailable-target'] = value
            if unquote(url.path) == '/mailto':
                node.attrs.pop('href', None)
            if not (node.next_sibling and 'unavailable in archive' in str(node.next_sibling)):
                label = soup.new_tag('span', attrs={'class': 'unavailable-note'})
                label.string = ' (unavailable in archive)'
                node.insert_after(label)
