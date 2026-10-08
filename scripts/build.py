#!/usr/bin/env python3
"""Build Zola and emit legacy .htm URLs as files instead of directories."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
subprocess.run(['zola', 'build', *sys.argv[1:]], cwd=ROOT, check=True)
output = ROOT / 'public'
for directory in sorted(output.rglob('*'), reverse=True):
    if directory.is_dir() and directory.suffix.lower() in ('.htm', '.html'):
        index = directory / 'index.html'
        if not index.is_file() or len(list(directory.iterdir())) != 1:
            raise RuntimeError(f'Unexpected legacy output contents: {directory}')
        html = index.read_bytes()
        index.unlink()
        directory.rmdir()
        directory.write_bytes(html)
print('Legacy HTML paths preserved as files in public/.')
