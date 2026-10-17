#!/usr/bin/env python3
"""Render the public persona directories from the private JSON sources.

The JSON files under data/ retain member names and contact addresses. This
script writes the Markdown pages that Zola builds, omitting those private
fields.
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
        'please contact [me](mailto:Legend@malcor.com).',
        'please contact the club.',
    )
    return re.sub(r'\[([^\]]*)\]\(mailto:[^)]*\)', r'\1', text)


def toml_literal(value: Any) -> str:
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return '[' + ', '.join(toml_literal(item) for item in value) + ']'
    raise TypeError(f'unsupported front matter value: {value!r}')


def render_front_matter(front_matter: dict[str, Any]) -> str:
    lines = ['+++']
    for key, value in front_matter.items():
        if key == 'extra':
            continue
        lines.append(f'{key} = {toml_literal(value)}')
    if 'extra' in front_matter:
        lines.append('[extra]')
        for key, value in front_matter['extra'].items():
            lines.append(f'{key} = {toml_literal(value)}')
    lines.append('+++')
    return '\n'.join(lines)


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


def render_document(document: dict[str, Any]) -> str:
    blocks = [render_front_matter(document['front_matter'])]
    blocks.extend(document['preamble'])
    for section in document['sections']:
        if section.get('url'):
            blocks.append(f"## [{section['title']}]({section['url']})")
        else:
            blocks.append(f"## {section['title']}")
        blocks.extend(section['notes'])
        if section['entries']:
            blocks.append('\n'.join(
                f'{number}. {render_entry(entry)}'
                for number, entry in enumerate(section['entries'], 1)
            ))
        blocks.append('<img alt="" loading="lazy" src="/barcomp.gif"/>')
    blocks.extend(document['postamble'])
    return sanitize_public_text('\n\n'.join(blocks).rstrip() + '\n')


def render_source(path: Path) -> str:
    document = json.loads(path.read_text())
    if document.get('schema_version') != 1:
        raise ValueError(f'unsupported persona directory schema in {path}')
    return render_document(document)


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
