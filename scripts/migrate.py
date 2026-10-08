#!/usr/bin/env python3
"""Reproducibly import the original archive; never copy PDFs into the repository."""
import argparse
import hashlib
import json
import posixpath
import re
import shutil
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit

from bs4 import BeautifulSoup
from link_repairs import annotate_gaps, corrected_link, repair_anchors

ROOT = Path(__file__).resolve().parents[1]


def migrate(source):
    files = {p.relative_to(source).as_posix(): p for p in source.rglob('*') if p.is_file()}
    by_name = {}
    for name in files:
        by_name.setdefault(Path(name).name.lower(), []).append(name)
    pages = sorted(n for n in files if Path(n).suffix.lower() in ('.htm', '.html'))
    missing = []
    repairs = []
    pdfs = []
    for name, path in sorted(files.items()):
        if path.suffix.lower() == '.pdf':
            pdfs.append({'key': name, 'bytes': path.stat().st_size,
                         'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        elif path.suffix.lower() not in ('.htm', '.html'):
            target = ROOT / 'static' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)

    def rewrite(value, origin):
        if re.fullmatch(r'[^\s/@:]+@[^\s/]+\.[^\s/]+', value.strip()):
            repairs.append({'page': origin, 'original': value, 'resolved': 'mailto:' + value.strip()})
            return 'mailto:' + value.strip()
        parsed = urlsplit(value.strip())
        if parsed.scheme and parsed.scheme not in ('file', 'http', 'https'):
            return value
        if parsed.netloc and parsed.netloc.lower() not in ('queensown.org', 'www.queensown.org'):
            return value
        if not parsed.path:
            return value
        path = unquote(parsed.path).replace('\\', '/')
        local = posixpath.normpath(posixpath.join(posixpath.dirname(origin), path)).lstrip('/')
        if parsed.scheme == 'file' or local not in files:
            candidates = by_name.get(posixpath.basename(path).lower(), [])
            if len(candidates) == 1:
                old = local
                local = candidates[0]
                if old != local:
                    repairs.append({'page': origin, 'original': value, 'resolved': local})
        if local not in files:
            missing.append({'page': origin, 'target': value})
            if Path(local).suffix.lower() == '.pdf':
                return '__PDF_BASE_URL__/' + quote(local, safe='/') + ('?' + parsed.query if parsed.query else '') + ('#' + parsed.fragment if parsed.fragment else '')
            # Point missing archive files at the original host rather than a new broken local URL.
            return urlunsplit(('https', 'queensown.org', '/' + quote(local, safe='/'), parsed.query, parsed.fragment))
        prefix = '__PDF_BASE_URL__/' if Path(local).suffix.lower() == '.pdf' else '/'
        return prefix + quote(local, safe='/') + ('?' + parsed.query if parsed.query else '') + ('#' + parsed.fragment if parsed.fragment else '')

    listing = []
    for name in pages:
        soup = BeautifulSoup(files[name].read_bytes(), 'lxml')
        title = soup.title.get_text(' ', strip=True) if soup.title else Path(name).stem
        body = soup.body or soup
        repair_anchors(soup, name)
        for node in list(body.find_all(['script', 'style', 'iframe', 'object', 'embed'])):
            node.decompose()
        for node in list(body.find_all(True)):
            if node.name == 'a' and node.get('name'):
                node['id'] = node['name']
            for attr in list(node.attrs):
                if attr in ('href', 'src'):
                    node[attr] = rewrite(corrected_link(node[attr], name, node.get_text(' ', strip=True)), name)
                elif attr not in ('id', 'name', 'alt', 'title', 'colspan', 'rowspan', 'align', 'valign', 'width', 'height', 'border', 'cellspacing', 'cellpadding', 'size', 'color', 'face', 'style'):
                    del node[attr]
            if node.name == 'img':
                node['loading'] = 'lazy'
                if not node.has_attr('alt'):
                    node['alt'] = ''
        dispositions = json.loads((ROOT / 'data/link-dispositions.json').read_text()) if (ROOT / 'data/link-dispositions.json').exists() else {}
        annotate_gaps(soup, dispositions)
        html = body.decode_contents()
        # Raw HTML inside Zola Markdown preserves the hand-authored archive layout.
        converted = '<div class="original-page">\n' + html + '\n</div>\n'
        home = name == 'index.html'
        target = ROOT / 'content' / ('_index.md' if home else name + '.md')
        target.parent.mkdir(parents=True, exist_ok=True)
        front = '+++\ntitle = ' + json.dumps(title, ensure_ascii=False) + '\n'
        if not home:
            front += 'path = ' + json.dumps(name) + '\ntemplate = "page.html"\n'
        front += '[extra]\nlegacy_source = ' + json.dumps(name) + '\n'
        for key, default in [('bgcolor', 'blue'), ('text', 'white'), ('link', 'aqua'), ('vlink', 'silver')]:
            front += key + ' = ' + json.dumps(body.get(key, default)) + '\n'
        front += '+++\n\n'
        target.write_text(front + converted)
        if not home:
            listing.append(f'- [{title.replace("[", "").replace("]", "")}](/{quote(name, safe="/")})')
    (ROOT / 'content' / 'archive.md').write_text('+++\ntitle = "Website archive"\npath = "archive"\ntemplate = "page.html"\n+++\n\n# Website archive\n\nBrowse every preserved page. Publication dates and contact details are historical.\n\n' + '\n'.join(listing) + '\n')
    report = {'html_pages': len(pages), 'pdf_count': len(pdfs), 'pdf_bytes': sum(p['bytes'] for p in pdfs),
              'repaired_links': repairs, 'missing_local_links': missing}
    (ROOT / 'data' / 'migration-report.json').write_text(json.dumps(report, indent=2) + '\n')
    (ROOT / 'data' / 'pdf-manifest.json').write_text(json.dumps(pdfs, indent=2) + '\n')
    print(f'Imported {len(pages)} pages; inventoried {len(pdfs)} PDFs; repaired {len(repairs)} links; {len(missing)} missing references.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, nargs='?', default=ROOT.parent / 'queens-own' / 'queensown.org')
    args = parser.parse_args()
    migrate(args.source.resolve())
