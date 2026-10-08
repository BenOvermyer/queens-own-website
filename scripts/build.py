#!/usr/bin/env python3
"""Build canonical Zola routes; Netlify serves legacy redirects from static/_redirects."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
subprocess.run(['zola', 'build', *sys.argv[1:]], cwd=ROOT, check=True)
output = ROOT / 'public'
legacy_directories = [p for p in output.rglob('*') if p.is_dir() and p.suffix.lower() in ('.htm', '.html')]
if legacy_directories:
    raise RuntimeError('Legacy page paths remain: ' + ', '.join(str(p.relative_to(output)) for p in legacy_directories))
print('Canonical routes built; legacy URL redirects are in public/_redirects.')
