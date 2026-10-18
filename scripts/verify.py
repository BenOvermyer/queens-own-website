#!/usr/bin/env python3
"""Check canonical routes, redirects, local links, anchors, and acknowledged gaps."""
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
from bs4 import BeautifulSoup
import audit_html
from audit_links import audit
from sanitize_persona_directories import SOURCES, render_source
from verify_routes import validate

ROOT = Path(__file__).resolve().parents[1]
output = ROOT / 'public'
errors = []
anchor_warnings = []
documents = {}
# Markdown that the renderer left as literal text means an HTML block swallowed the
# content that followed it. Raw headings and destinations without spaces are reliable
# signals; literal "[Ed. note ...](call ...)" prose is not.
RAW_MARKDOWN = re.compile(r'(?m)^[ \t]{0,3}#{1,6} |\]\([^\s)]+\)')


def raw_markdown(text):
    """Return Markdown artifacts still visible in rendered HTML."""
    text = re.sub(r'<pre\b.*?</pre>', '', text, flags=re.S)
    text = re.sub(r'<code\b.*?</code>', '', text, flags=re.S)
    text = re.sub(r'<table\b.*?</table>', '', text, flags=re.S)
    return RAW_MARKDOWN.findall(text)


for source, destination in SOURCES.items():
    rendered = render_source(source)
    if destination.read_text() != rendered:
        errors.append(
            f'{destination.relative_to(ROOT)} is not the rendered output of '
            f'{source.relative_to(ROOT)}; run scripts/sanitize_persona_directories.py'
        )


for path in output.rglob('*'):
    if path.is_file() and path.suffix.lower() in ('.htm', '.html'):
        documents[path] = BeautifulSoup(path.read_text(), 'lxml')
for path, soup in documents.items():
    if '__PDF_BASE_URL__' in str(soup):
        errors.append(f'Unresolved PDF host in {path}')
    artifacts = raw_markdown(path.read_text())
    if artifacts:
        errors.append(f'{path.relative_to(output)}: unrendered Markdown {artifacts[:3]}')
    duplicate_ids = audit_html.duplicate_ids(soup)
    if duplicate_ids:
        errors.append(f'{path.relative_to(output)}: duplicate ids {duplicate_ids}')
    dimensionless = audit_html.images_without_dimensions(soup)
    if dimensionless:
        errors.append(f'{path.relative_to(output)}: images without width/height {dimensionless[:3]}')
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
descriptions = {}
for path, soup in documents.items():
    meta = soup.find('meta', attrs={'name': 'description'})
    text = ((meta.get('content') or '').strip()) if meta else ''
    if not text:
        errors.append(f'{path.relative_to(output)}: missing meta description')
        continue
    if len(text) > 156:
        errors.append(f'{path.relative_to(output)}: meta description is {len(text)} characters')
    descriptions.setdefault(text, []).append(str(path.relative_to(output)))
duplicates = {text: pages for text, pages in descriptions.items() if len(pages) > 1}
if duplicates:
    sample = '; '.join(f'{text[:40]!r} x{len(pages)}' for text, pages in list(duplicates.items())[:3])
    errors.append(f'{len(duplicates)} duplicated meta descriptions: {sample}')
for path, soup in documents.items():
    if path.name == '404.html':
        continue
    canonical = soup.find_all('link', attrs={'rel': 'canonical'})
    if len(canonical) != 1 or not (canonical[0].get('href') or '').startswith('http'):
        errors.append(f'{path.relative_to(output)}: expected exactly one absolute canonical link')
if list(output.rglob('*.pdf')):
    errors.append('PDF files unexpectedly present in site output')
(ROOT / 'data' / 'anchor-report.json').write_text(json.dumps(anchor_warnings, indent=2) + '\n')
if errors:
    raise SystemExit('\n'.join(errors))
print(f'Checked {len(documents)} HTML files: all local files resolve, PDF host substituted, no bundled PDFs.')
print(f'{len(anchor_warnings)} unresolved original anchor references listed in data/anchor-report.json.')
audit()
html_report = audit_html.audit()
if html_report['summary']['unresolved_errors']:
    raise SystemExit('Unresolved HTML structural errors: see data/html-audit-report.json')
print(f"HTML audit: {html_report['summary']['files_scanned']} documents, "
      f"{html_report['summary']['acknowledged_findings']} acknowledged exceptions, no unresolved structural errors.")
if (ROOT / 'data/site-routes.json').exists():
    validate(ROOT)
