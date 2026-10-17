#!/usr/bin/env python3
"""Render the public persona directories from the private JSON sources.

The JSON files under data/ retain member names and contact addresses. This
script updates only marked lists in the Markdown pages, omitting those private
fields. Front matter, headings, notes, and surrounding copy are maintained in Markdown.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    ROOT / 'data/persona-directory.json': ROOT / 'content/personas/persona-directory.md',
    ROOT / 'data/npc-directory.json': ROOT / 'content/personas/npc-directory.md',
}


def sanitize_public_text(text: str) -> str:
    """Remove contact addresses from public prose blocks."""
    text = text.replace(
        'please contact [me](mailto:shashtah@gmail.com).',
        'please contact the club.',
    )
    return re.sub(r'\[([^\]]*)\]\(mailto:[^)]*\)', r'\1', text)


def render_entry(entry: dict[str, Any]) -> str:
    """Render one public directory entry, omitting player and email fields."""
    if entry.get('persona_url'):
        line = f"[{entry['persona']}]({entry['persona_url']})"
    else:
        line = entry['persona']
    for detail in entry.get('details', []):
        if detail['type'] == 'raw':
            line += detail['text'].rstrip()
        else:
            line += f" ({detail['text']})"
    return line


def render_document(document: dict[str, Any], markdown: str) -> str:
    """Replace only marked persona lists; all other Markdown stays untouched."""
    for section in document['sections']:
        ident = section['id']
        start = f'<!-- persona-list:{ident}:start -->'
        end = f'<!-- persona-list:{ident}:end -->'
        if markdown.count(start) != 1 or markdown.count(end) != 1:
            raise ValueError(f'expected exactly one list marker pair for {ident}')
        pattern = re.escape(start) + r'.*?' + re.escape(end)
        entries = '\n'.join(
            f'{number}. {render_entry(entry)}'
            for number, entry in enumerate(section['entries'], 1)
        )
        replacement = start + '\n' + sanitize_public_text(entries) + ('\n' if entries else '') + end
        markdown, count = re.subn(pattern, lambda match: replacement, markdown, flags=re.S)
        if count != 1:
            raise ValueError(f'invalid list marker order for {ident}')
    return markdown


def render_source(path: Path, destination: Path | None = None) -> str:
    document = json.loads(path.read_text())
    if document.get('schema_version') != 2:
        raise ValueError(f'unsupported persona directory schema in {path}')
    if destination is None:
        destination = SOURCES[path]
    return render_document(document, destination.read_text())


def main() -> int:
    check = '--check' in sys.argv[1:]
    stale = []
    for source, destination in SOURCES.items():
        rendered = render_source(source)
        if check:
            if destination.read_text() != rendered:
                stale.append(str(destination.relative_to(ROOT)))
        else:
            destination.write_text(rendered)
            print(f'Wrote {destination.relative_to(ROOT)} from {source.relative_to(ROOT)}')
    if stale:
        raise SystemExit('Out-of-date public persona files: ' + ', '.join(stale))
    if check:
        print('Public persona directories are up to date.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
