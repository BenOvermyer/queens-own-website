#!/usr/bin/env python3
"""Inventory internal links. --online refreshes HTTP evidence; offline checks regressions."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import posixpath
from pathlib import Path
import tomllib
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def http_check(url):
    result = {'checked_at': datetime.now(timezone.utc).isoformat(), 'url': url}
    try:
        request = Request(url, method='HEAD', headers={'User-Agent': 'QueensOwn-link-audit/1.0'})
        with urlopen(request, timeout=15) as response:
            result.update(status=response.status, final_url=response.url,
                          content_type=response.headers.get('Content-Type', ''))
    except HTTPError as error:
        result.update(status=error.code, final_url=error.url)
    except (URLError, TimeoutError, OSError) as error:
        result.update(status=None, error=str(error))
    return result


def crawl(output):
    config = tomllib.loads((ROOT / 'config.toml').read_text())
    pdf_base = config['extra']['pdf_base_url'].rstrip('/')
    site_host = urlsplit(config['base_url']).netloc
    # Also recognize the deployment URL supplied at build time.
    home = BeautifulSoup((output / 'index.html').read_text(), 'lxml')
    brand = home.select_one('.brand[href]')
    hosts = {'queensown.org', 'www.queensown.org', site_host}
    if brand:
        hosts.add(urlsplit(brand['href']).netloc)
    pdf_host = urlsplit(pdf_base).netloc
    manifest = {x['key'] for x in json.loads((ROOT / 'data/pdf-manifest.json').read_text())}
    documents = {}
    for path in sorted(output.rglob('*')):
        if path.is_file() and path.suffix.lower() in ('.htm', '.html'):
            documents[path.relative_to(output).as_posix()] = BeautifulSoup(path.read_text(), 'lxml')
    records = {}
    for page, soup in documents.items():
        for node in soup.select('[href], [src], [data-unavailable-target]'):
            for attr in ('href', 'src', 'data-unavailable-target'):
                if not node.has_attr(attr):
                    continue
                if attr == 'data-unavailable-target' and (node.has_attr('href') or node.has_attr('src')):
                    continue
                value = node[attr]
                url = urlsplit(value)
                if url.scheme not in ('', 'http', 'https', 'file'):
                    continue
                if url.netloc and url.netloc not in hosts | {pdf_host}:
                    continue
                decoded = unquote(url.path)
                local = posixpath.normpath(decoded if decoded.startswith('/') else posixpath.join('/' + posixpath.dirname(page), decoded)) if decoded else '/' + page
                fragment = unquote(url.fragment)
                suffix = Path(local).suffix.lower()
                kind = 'pdf' if suffix == '.pdf' else 'page' if suffix in ('', '.htm', '.html') else 'asset'
                target = local + ('#' + fragment if fragment else '')
                if kind == 'pdf':
                    # Keep the actual public host and filename, rather than folding external PDFs into site paths.
                    target = urlunsplit(('https', pdf_host, url.path, url.query, url.fragment)) if url.netloc == pdf_host else pdf_base + '/' + quote(local.lstrip('/'), safe='/')
                record = records.setdefault(target, {'target': target, 'type': kind, 'references': [], 'local_present': False})
                reference = {'page': page, 'attribute': attr, 'url': value}
                if reference not in record['references']:
                    record['references'].append(reference)
                if kind == 'pdf':
                    record['local_present'] = unquote(urlsplit(target).path).lstrip('/') in manifest
                    record['http_url'] = target.split('#')[0]
                    continue
                disk = output / local.lstrip('/')
                if disk.is_dir():
                    disk = disk / 'index.html'
                record['local_present'] = disk.is_file()
                record['status'] = 'local_available' if disk.is_file() else 'missing_file'
                if not disk.is_file():
                    record['http_url'] = 'https://queensown.org' + quote(local, safe='/')
                elif fragment:
                    destination = documents.get(disk.relative_to(output).as_posix())
                    if destination is None or not (destination.find(id=fragment) or destination.find('a', attrs={'name': fragment})):
                        record['status'] = 'missing_anchor'
    return [records[key] for key in sorted(records)]


def audit(online=False):
    output = ROOT / 'public'
    records = crawl(output)
    evidence_path = ROOT / 'data/link-http-evidence.json'
    evidence = json.loads(evidence_path.read_text()) if evidence_path.exists() else {}
    if online:
        urls = {r['http_url'] for r in records if 'http_url' in r}
        # Check recovery candidates on the original host for PDFs absent locally.
        urls.update('https://queensown.org' + urlsplit(r['http_url']).path
                    for r in records if r['type'] == 'pdf' and not r['local_present'])
        urls = sorted(urls)
        with ThreadPoolExecutor(max_workers=8) as pool:
            for url, result in zip(urls, pool.map(http_check, urls)):
                evidence[url] = result
        evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + '\n')
    dispositions_path = ROOT / 'data/link-dispositions.json'
    dispositions = json.loads(dispositions_path.read_text()) if dispositions_path.exists() else {}
    failures = []
    for record in records:
        if 'http_url' in record:
            record['http'] = evidence.get(record['http_url'], {'status': None, 'error': 'Not checked'})
            code = record['http'].get('status')
            available = code is not None and 200 <= code < 300
            if record['type'] == 'pdf':
                available = available and 'application/pdf' in record['http'].get('content_type', '').lower()
                record['status'] = 'remote_available' if available else 'missing_pdf' if code in (404, 410) else 'unverified_pdf'
            elif available:
                record['status'] = 'recoverable_remote'
            if record['type'] == 'pdf' and not record['local_present']:
                recovery_url = 'https://queensown.org' + urlsplit(record['http_url']).path
                record['recovery_http'] = evidence.get(recovery_url, {'status': None, 'error': 'Not checked'})
        if record['target'] in dispositions:
            disposition = dispositions[record['target']]
            record['disposition'] = disposition
            unexpected = {r['page'] for r in record['references']} - set(disposition['referring_pages'])
            if unexpected:
                failures.append(record['target'] + ' newly referenced by ' + ', '.join(sorted(unexpected)))
        if record['status'] not in ('local_available', 'remote_available') and 'disposition' not in record:
            failures.append(record['target'])
    counts = {}
    for record in records:
        counts[record['status']] = counts.get(record['status'], 0) + 1
    manifest = {x['key'] for x in json.loads((ROOT / 'data/pdf-manifest.json').read_text())}
    linked_pdfs = {unquote(urlsplit(r['target']).path).lstrip('/') for r in records if r['type'] == 'pdf'}
    report = {'summary': counts, 'pdf_reconciliation': {
        'linked_filenames': len(linked_pdfs), 'manifest_filenames': len(manifest),
        'linked_without_source_file': sorted(linked_pdfs - manifest),
        'source_files_without_link': sorted(manifest - linked_pdfs),
    }, 'targets': records}
    (ROOT / 'data/link-inventory.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Link inventory:', counts)
    if failures:
        raise SystemExit('Unaccounted link failures:\n' + '\n'.join(failures))
    print('No unaccounted failures. Acknowledged gaps remain unresolved in the inventory.')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--online', action='store_true', help='Refresh live HTTP evidence (requires network access)')
    args = parser.parse_args()
    audit(args.online)
