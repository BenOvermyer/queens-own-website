#!/usr/bin/env python3
"""Inventory the local Dragonlords split archive and evidence for Queen's Own candidates."""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import posixpath
import re
import shutil
import subprocess
from urllib.parse import quote, unquote, urlsplit

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
PAGE_EXTENSIONS = {'.htm', '.html', '.shtml', '.php', '.php3', '.cgi', '.com'}
TERMS = {
    'Velgarth': r'\bVelgarth\b', 'Valdemar': r'\bValdemar(?:an)?\b',
    "Queen's Own": r'\bQueen[’\']?s\s+Own\b', 'Vanyel': r'\bVanyel\b',
    'Herald-Mage': r'\bHerald[- ]Mage\b', 'Tayledras': r'\bTayledras\b',
    "Shin'a'in": r'\bShin[’\']?a[’\']?in\b',
}
CORE = {
    **{n + '.htm': 'Shared club resources' for n in ['recipes', 'mlrelease']},
    **{n + '.htm': 'Queen’s Own chapters' for n in ['danyagg', 'danyacc', 'danyasc']},
    **{n + '.htm': 'Vanyel Fan Club' for n in ['vfcindex', 'vfcqa', 'vfcjoin', 'vfcnews', 'vfcpres', 'vfcchat', 'vfcgate', 'vfcgates']},
    **{n + '.htm': 'Velgarth reference and fan activities' for n in ['danc', 'danhc', 'danmag1', 'danp', 'danr', 'dantime', 'danya', 'danspell', 'dcpawn', 'dcprom', 'dcprice']},
}
INTERNAL_HOSTS = {'dragonlords.fans', 'www.dragonlords.fans', 'dragonlordsnet.com', 'www.dragonlordsnet.com'}


def resolve(value, page, files):
    url = urlsplit(value.strip().replace('\\', '/'))
    if url.scheme not in ('', 'http', 'https', 'file') or url.netloc and url.hostname not in INTERNAL_HOSTS:
        return None
    if not url.path:
        return page
    path = unquote(url.path)
    target = posixpath.normpath(path.lstrip('/') if path.startswith('/') else posixpath.join(posixpath.dirname(page), path))
    if target.startswith('../'):
        return None
    if target in files:
        return target
    for index in ('index.html', 'index.htm'):
        candidate = target.rstrip('/') + '/' + index
        if candidate in files:
            return candidate
    return target


def inventory(source):
    files = {p.relative_to(source).as_posix(): p for p in source.rglob('*') if p.is_file()}
    queen = ROOT.parent / 'queens-own/queensown.org'
    queen_files = {p.relative_to(queen).as_posix(): p for p in queen.rglob('*') if p.is_file()}
    incoming = defaultdict(set)
    fun_targets = set()
    routes_path = ROOT / 'data/dragonlords-route-map.json'
    routes = json.loads(routes_path.read_text()) if routes_path.exists() else {}
    by_route = {route.strip('/'): name for name, route in routes.items()}
    for p in (ROOT / 'content').rglob('*.md'):
        soup = BeautifulSoup(p.read_text().split('+++', 2)[-1], 'lxml')
        for node in soup.select('[href], [src]'):
            value = node.get('href', node.get('src', ''))
            url = urlsplit(value)
            local_source = by_route.get(unquote(url.path).strip('/')) if not url.netloc else None
            if url.hostname in INTERNAL_HOSTS or local_source:
                target = local_source or unquote(url.path).lstrip('/')
                incoming[target].add(p.relative_to(ROOT / 'content').as_posix())
                if p.name == 'qofun.htm.md':
                    fun_targets.add(target)
    pages = []
    for name, path in sorted(files.items()):
        if path.suffix.lower() not in PAGE_EXTENSIONS:
            continue
        data = path.read_bytes()
        if b'<' not in data:
            continue
        soup = BeautifulSoup(data, 'lxml')
        body = soup.body or soup
        text = body.get_text(' ', strip=True)
        title = soup.title.get_text(' ', strip=True) if soup.title else name
        matches = {term: len(re.findall(pattern, text, re.I)) for term, pattern in TERMS.items() if re.search(pattern, text, re.I)}
        group = CORE.get(name)
        if 'The Compass Rose' in title:
            group = 'The Compass Rose journal'
        qo_service = bool(re.search(r'(?:qopending|vanyelfanclub|queensown)', name, re.I))
        if group:
            disposition, reason = 'migrate', 'Dedicated club, chapter, publication, persona, or Velgarth material.'
        elif qo_service:
            disposition, reason, group = 'review', 'Related mailing-list archive or service; decide its archival scope and static replacement separately.', 'Mailing-list archives and services'
        elif matches:
            disposition, reason, group = 'review', 'Related terms appear, but this may be mixed content, a generic resource, or an incidental reference.', 'Mixed or incidental references'
        else:
            disposition, reason, group = 'retain', 'No identified Queen’s Own or Velgarth evidence in this page.', 'Dragonlords or unrelated content'
        links = set()
        asset_links = set()
        for node in soup.select('[href], [src], [background], [action], [data], [lowsrc]'):
            for attr in ('href', 'src', 'background', 'action', 'data', 'lowsrc'):
                if node.has_attr(attr):
                    target = resolve(node[attr], name, files)
                    if target and target != name:
                        links.add(target)
                        if attr in ('src', 'background', 'data', 'lowsrc'):
                            asset_links.add(target)
        pages.append({'path': name, 'title': title, 'recommendation': disposition, 'group': group,
                      'reason': reason, 'matched_terms': matches, 'linked_from_fun_stuff': name in fun_targets,
                      'queen_referring_pages': sorted(incoming[name]),
                      'linked_pages': sorted(n for n in links if Path(n).suffix.lower() in PAGE_EXTENSIONS),
                      'asset_dependencies': sorted(n for n in links if n in asset_links or Path(n).suffix.lower() not in PAGE_EXTENSIONS),
                      'missing_local_dependencies': sorted(n for n in links if n not in files)})
    candidates = {p['path'] for p in pages if p['recommendation'] == 'migrate'}
    asset_referrers = defaultdict(set)
    for page in pages:
        if page['path'] in candidates:
            for asset in page['asset_dependencies']:
                asset_referrers[asset].add(page['path'])
    all_rows = []
    by_page = {p['path']: p for p in pages}
    assets = []
    for name, path in sorted(files.items()):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        queen_match = name in queen_files and hashlib.sha256(queen_files[name].read_bytes()).hexdigest() == digest
        current = ROOT / 'static' / name
        current_match = current.is_file() and hashlib.sha256(current.read_bytes()).hexdigest() == digest
        page = by_page.get(name)
        recommendation = page['recommendation'] if page else 'dependency' if name in asset_referrers else 'shared_existing' if queen_match else 'retain'
        row = {'path': name, 'bytes': path.stat().st_size, 'sha256': digest,
               'type': 'page' if page else 'pdf' if path.suffix.lower() == '.pdf' else 'asset',
               'recommendation': recommendation, 'queen_source_identical': queen_match,
               'current_static_identical': current_match, 'candidate_referring_pages': sorted(asset_referrers.get(name, set()))}
        if page:
            row.update(title=page['title'], group=page['group'], reason=page['reason'],
                       matched_terms=list(page['matched_terms']), queen_referring_pages=page['queen_referring_pages'])
        if path.suffix.lower() == '.pdf' and shutil.which('pdftotext'):
            result = subprocess.run(['pdftotext', str(path), '-'], text=True, capture_output=True)
            row['pdf_text_extracted'] = result.returncode == 0
            row['matched_terms'] = [term for term, pattern in TERMS.items() if re.search(pattern, result.stdout, re.I)]
            if row['matched_terms'] and not queen_match and recommendation == 'retain':
                row['recommendation'] = 'review'
                row['reason'] = 'PDF mentions related terms; review its purpose before migration (Vita2022.pdf is an author CV).'
        all_rows.append(row)
        if name in asset_referrers:
            assets.append(row)
    report = {'source': '../queens-own/dragonlords.fans', 'scope': 'Local split archive; not a live-site crawl.',
              'summary': {'files': len(files), 'pages': len(pages),
                          'page_recommendations': dict(Counter(p['recommendation'] for p in pages)),
                          'velgarth_pages': sum('Velgarth' in p['matched_terms'] for p in pages),
                          'candidate_assets': len(assets), 'candidate_assets_already_in_static': sum(a['current_static_identical'] for a in assets)},
              'pages': pages, 'candidate_asset_dependencies': assets,
              'pdfs': [r for r in all_rows if r['type'] == 'pdf']}
    (ROOT / 'data/dragonlords-content-inventory.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    with (ROOT / 'data/dragonlords-file-inventory.csv').open('w', newline='') as handle:
        fields = ['path', 'title', 'type', 'group', 'recommendation', 'reason', 'matched_terms', 'queen_referring_pages', 'bytes', 'sha256', 'queen_source_identical', 'current_static_identical', 'candidate_referring_pages']
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction='ignore', lineterminator='\n')
        writer.writeheader()
        for row in all_rows:
            csv_row = dict(row)
            for key in ('candidate_referring_pages', 'matched_terms', 'queen_referring_pages'):
                csv_row[key] = '; '.join(row.get(key, []))
            writer.writerow(csv_row)
    print(json.dumps(report['summary'], indent=2))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, nargs='?', default=ROOT.parent / 'queens-own/dragonlords.fans')
    args = parser.parse_args()
    inventory(args.source.resolve())
