#!/usr/bin/env python3
"""Check generated legacy paths, local links, anchors, and PDF exclusion."""
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
output = ROOT / 'public'
errors = []
anchor_warnings = []
documents = {}
for path in output.rglob('*'):
    if path.is_file() and path.suffix.lower() in ('.htm', '.html'):
        documents[path] = BeautifulSoup(path.read_text(), 'lxml')
for path, soup in documents.items():
    if '__PDF_BASE_URL__' in str(soup):
        errors.append(f'Unresolved PDF host in {path}')
    for node in soup.select('[href], [src]'):
        value = node.get('href', node.get('src', ''))
        url = urlsplit(value)
        if url.scheme or url.netloc:
            continue
        target = output / unquote(url.path).lstrip('/') if url.path.startswith('/') else path.parent / unquote(url.path) if url.path else path
        if target.is_dir():
            target = target / 'index.html'
        if not target.is_file():
            errors.append(f'{path.relative_to(output)}: missing {value}')
        elif url.fragment and target in documents:
            fragment = unquote(url.fragment)
            target_soup = documents[target]
            if not target_soup.find(id=fragment) and not target_soup.find('a', attrs={'name': fragment}):
                anchor_warnings.append({'page': str(path.relative_to(output)), 'target': value})
if list(output.rglob('*.pdf')):
    errors.append('PDF files unexpectedly present in site output')
(ROOT / 'data' / 'anchor-report.json').write_text(json.dumps(anchor_warnings, indent=2) + '\n')
if errors:
    raise SystemExit('\n'.join(errors))
print(f'Checked {len(documents)} HTML files: all local files resolve, PDF host substituted, no bundled PDFs.')
print(f'{len(anchor_warnings)} unresolved original anchor references listed in data/anchor-report.json.')
