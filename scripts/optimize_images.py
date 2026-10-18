#!/usr/bin/env python3
"""Serve the site's images as responsive WebP.

Runs after ``zola build`` (see ``scripts/build.py``). For every local raster
image referenced by an ``<img>`` that is at least ``MIN_WIDTH`` wide, it encodes
WebP variants at a few widths into ``public/images/responsive/`` and wraps the
``<img>`` in a ``<picture>`` whose ``<source>`` offers those variants, with the
original file kept as the fallback. Images narrower than ``MIN_WIDTH`` (bullets,
icons) are left alone.

The output lives in ``public/``, which is generated and git-ignored, so nothing
here is committed and ``zola serve`` keeps showing the originals.
"""
import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RASTER = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
WIDTHS = (480, 768, 1200)
MIN_WIDTH = 128
VARIANT_DIR = 'images/responsive'
SIZES = '(max-width: 968px) 100vw, 968px'

IMG_TAG = re.compile(r'<img\b[^>]*>', re.IGNORECASE)
SRC_ATTR = re.compile(r'''\bsrc\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))''', re.IGNORECASE)
SRCSET_ATTR = re.compile(r'''\bsrcset\s*=\s*(?:"([^"]*)"|'([^']*)')''', re.IGNORECASE)
# Regions whose contents are text or code, never rewritten.
RAW_TEXT = re.compile(r'(<(?:script|style|textarea|xmp|pre|code)\b.*?</(?:script|style|textarea|xmp|pre|code)>)',
                      re.IGNORECASE | re.DOTALL)


def local_path(src, output):
    """Return the on-disk path for a same-site image URL, or None."""
    if not src or src.startswith(('data:', '//')):
        return None
    url = urlsplit(src)
    if url.scheme and url.scheme not in ('http', 'https'):
        return None
    path = url.path if (url.scheme or url.netloc) else src.split('?', 1)[0].split('#', 1)[0]
    if not path.startswith('/'):
        return None
    candidate = output / path.lstrip('/')
    return candidate if candidate.is_file() else None


def variant_widths(width):
    """Widths to encode: the intrinsic width plus any smaller standard widths."""
    smaller = [w for w in WIDTHS if w < width]
    return sorted(set(smaller + [width]))


def encode_variants(src, output, cache):
    """Create the WebP variants for one image; return [(url, width), ...] or [].

    Variants are produced only when the full-size WebP is smaller than the
    source file, so the pipeline can never increase a page's image payload.
    """
    if src in cache:
        return cache[src]
    path = local_path(src, output)
    variants = []
    if path is not None and path.suffix.lower().lstrip('.') in RASTER:
        try:
            with Image.open(path) as image:
                width, height = image.size
                if width >= MIN_WIDTH:
                    rgb = image.convert('RGBA' if 'A' in image.getbands() else 'RGB')
                    stem = path.relative_to(output).as_posix().replace('/', '_')
                    # GIF and PNG are palette/graphic formats; lossless WebP still
                    # beats them. Photographs (JPEG) shrink best with lossy WebP.
                    options = ({'lossless': True, 'method': 5}
                               if path.suffix.lower() in ('.gif', '.png')
                               else {'quality': 82, 'method': 5})

                    def encode(target, frame):
                        name = f"{stem}.{target}.webp"
                        destination = output / VARIANT_DIR / name
                        if not destination.exists():
                            destination.parent.mkdir(parents=True, exist_ok=True)
                            frame.save(destination, 'WEBP', **options)
                        return f"/{VARIANT_DIR}/{name}", target, destination.stat().st_size, destination

                    candidates = [encode(width, rgb)]
                    for target in variant_widths(width):
                        if target < width:
                            frame = rgb.resize((target, max(1, round(height * target / width))), Image.LANCZOS)
                            candidates.append(encode(target, frame))
                    full_bytes = candidates[0][2]
                    if full_bytes < path.stat().st_size:
                        # Keep the full size plus any smaller variant that is also
                        # smaller in bytes (downscaling dithering can defeat that).
                        keep = [c for c in candidates if c[1] == width or c[2] < full_bytes]
                        for candidate in candidates:
                            if candidate not in keep:
                                candidate[3].unlink(missing_ok=True)
                        variants = sorted(((c[0], c[1]) for c in keep), key=lambda variant: variant[1])
        except Exception as error:  # unreadable image: leave the <img> untouched
            print(f"  skipping {src}: {error}", file=sys.stderr)
            variants = []
    cache[src] = variants
    return variants


def rewrite_tag(tag, output, cache):
    """Return a <picture> wrapper for one <img> tag, or the tag unchanged."""
    if '<picture' in tag:
        return tag
    match = SRC_ATTR.search(tag)
    src = (match.group(1) or match.group(2) or match.group(3)) if match else None
    if not src:
        return tag
    variants = encode_variants(src, output, cache)
    if not variants:
        return tag
    srcset = ', '.join(f'{url} {width}w' for url, width in variants)
    source = f'<source type="image/webp" srcset="{srcset}" sizes="{SIZES}">'
    return f'<picture>{source}{tag}</picture>'


def rewrite_page(text, output, cache):
    """Rewrite every <img> in a page, skipping raw-text and code regions."""
    parts = RAW_TEXT.split(text)
    for index in range(0, len(parts), 2):
        parts[index] = IMG_TAG.sub(lambda match: rewrite_tag(match.group(0), output, cache), parts[index])
    return ''.join(parts)


def optimize(output=None):
    output = Path(output or (ROOT / 'public'))
    cache = {}
    pages = rewritten = 0
    for page in sorted(output.rglob('*.html')):
        text = page.read_text()
        if '<img' not in text.lower():
            continue
        pages += 1
        new = rewrite_page(text, output, cache)
        if new != text:
            page.write_text(new)
            rewritten += 1
    generated = sum(len(v) for v in cache.values())
    with_variants = sum(1 for v in cache.values() if v)
    print(f"Responsive images: {generated} WebP variants for {with_variants} images; "
          f"{rewritten}/{pages} pages rewritten.")
    return rewritten, generated


def validate(output=None):
    """Return srcset URLs that do not exist on disk (for verification)."""
    output = Path(output or (ROOT / 'public'))
    missing = []
    for page in sorted(output.rglob('*.html')):
        text = page.read_text()
        if 'srcset' not in text:
            continue
        for match in SRCSET_ATTR.finditer(text):
            value = match.group(1) or match.group(2) or ''
            for part in value.split(','):
                url = part.strip().split(' ')[0]
                if url.startswith('/') and not (output / url.lstrip('/')).is_file():
                    missing.append(f'{page.relative_to(output)}: {url}')
    return missing


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Exit non-zero when a srcset file is missing')
    args = parser.parse_args()
    optimize()
    if args.check:
        missing = validate()
        for item in missing:
            print('  missing', item)
        if missing:
            raise SystemExit('srcset files missing')
