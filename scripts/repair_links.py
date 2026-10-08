#!/usr/bin/env python3
"""Apply documented link corrections and gap notices without reimporting content."""
import json
import tomllib
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from link_repairs import annotate_gaps, corrected_link, repair_anchors

ROOT = Path(__file__).resolve().parents[1]
dispositions_path = ROOT / 'data/link-dispositions.json'
dispositions = json.loads(dispositions_path.read_text()) if dispositions_path.exists() else {}
changed = []
for path in sorted((ROOT / 'content').rglob('*.md')):
    text = path.read_text()
    front, html = text.split('+++', 2)[1:]
    meta = tomllib.loads(front)
    page = meta.get('extra', {}).get('legacy_source')
    if not page:
        continue
    soup = BeautifulSoup(html, 'lxml')
    before = str(soup)
    repair_anchors(soup, page)
    for node in soup.select('[href], [src]'):
        for attr in ('href', 'src'):
            if not node.has_attr(attr):
                continue
            old = node[attr]
            new = corrected_link(old, page, node.get_text(' ', strip=True))
            if new != old:
                if urlsplit(new).scheme:
                    node[attr] = new
                elif new.endswith('.pdf'):
                    node[attr] = '__PDF_BASE_URL__/' + new
                else:
                    node[attr] = '/' + new.lstrip('/')
    annotate_gaps(soup, dispositions)
    if before != str(soup):
        rendered = '+++' + front + '+++\n\n' + soup.body.decode_contents().rstrip() + '\n'
        original_lines = text.splitlines()
        lines = [line.rstrip() for line in rendered.splitlines()]
        matcher = SequenceMatcher(a=[line.rstrip() for line in original_lines], b=lines, autojunk=False)
        for tag, start, end, new_start, new_end in matcher.get_opcodes():
            if tag == 'equal':
                lines[new_start:new_end] = original_lines[start:end]
        path.write_text('\n'.join(lines).rstrip() + '\n')
        changed.append(page)
print(f'Updated {len(changed)} pages:', ', '.join(changed))
if (ROOT / 'data/site-routes.json').exists():
    import organize_site
    organize_site.ROOT = ROOT
    organize_site.organize()
