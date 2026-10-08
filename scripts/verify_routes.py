"""Validate canonical destinations, permanent redirects, and published URL usage."""
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup


def output_file(output, path):
    target = output / unquote(urlsplit(path).path).lstrip('/')
    return target / 'index.html' if target.is_dir() else target


def validate(root):
    output = root / 'public'
    records = json.loads((root / 'data/site-routes.json').read_text())
    errors = []
    redirects = {}
    for line in (output / '_redirects').read_text().splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        fields = line.split()
        if len(fields) != 3 or fields[2].rstrip('!') != '301':
            errors.append('Invalid permanent redirect: ' + line)
            continue
        old, target, _ = fields
        if old in redirects:
            errors.append('Duplicate redirect: ' + old)
        redirects[old] = target
    destinations = set()
    for source, record in records.items():
        canonical = record['canonical_path']
        if canonical.lower().rstrip('/').endswith(('.htm', '.html')):
            errors.append('Noncanonical page path: ' + canonical)
        if canonical in destinations:
            errors.append('Duplicate canonical path: ' + canonical)
        destinations.add(canonical)
        if not (root / 'content' / record['content_file']).is_file():
            errors.append('Missing source placement: ' + record['content_file'])
        if not output_file(output, canonical).is_file():
            errors.append('Missing canonical destination: ' + canonical)
        for old in record['aliases']:
            if old != record['redirect_target'] and redirects.get(old) != record['redirect_target']:
                errors.append('Missing or incorrect legacy redirect: ' + old)
    for old, target in redirects.items():
        if target in redirects:
            errors.append('Redirect chain or loop: ' + old)
        if not output_file(output, target).is_file():
            errors.append('Missing redirect destination: ' + target)
    home = BeautifulSoup((output / 'index.html').read_text(), 'lxml')
    brand = home.select_one('.brand[href]')
    host = urlsplit(brand['href']).netloc if brand else ''
    for path in output.rglob('index.html'):
        soup = BeautifulSoup(path.read_text(), 'lxml')
        for node in soup.select('a[href]'):
            url = urlsplit(node['href'])
            if url.scheme in ('', 'http', 'https') and (not url.netloc or url.netloc == host):
                if url.path.lower().rstrip('/').endswith(('.htm', '.html')):
                    errors.append(str(path.relative_to(output)) + ': legacy internal link ' + node['href'])
    sitemap = ET.parse(output / 'sitemap.xml')
    for node in sitemap.iter():
        if node.tag.endswith('loc') and node.text and urlsplit(node.text).path.lower().rstrip('/').endswith(('.htm', '.html')):
            errors.append('Legacy sitemap URL: ' + node.text)
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'Checked {len(records)} content mappings and {len(redirects)} permanent redirects: all destinations exist; no chains or legacy internal/sitemap URLs.')
    return redirects


if __name__ == '__main__':
    validate(Path(__file__).resolve().parents[1])
