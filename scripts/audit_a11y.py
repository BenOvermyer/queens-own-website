#!/usr/bin/env python3
"""Accessibility checks for the built site.

Dependency-free rules over the rendered HTML, chosen to match WCAG 2.1 AA
concerns that affect this site (and the axe/Lighthouse rules that cover them):

  html-has-lang      <html> declares a language            (WCAG 3.1.1)
  document-title     non-empty <title>                     (WCAG 2.4.2)
  page-has-one-h1    exactly one <h1>                      (WCAG 1.3.1)
  heading-order      no skipped heading levels             (WCAG 1.3.1)
  image-alt          every <img> has an alt attribute      (WCAG 1.1.1)
  link-name          every link has an accessible name     (WCAG 2.4.4, 4.1.2)
  link-text          link text is not "here"/"click here"  (WCAG 2.4.4)
  landmark-one-main  exactly one <main> landmark           (WCAG 1.3.1, 2.4.1)
  skip-link          a skip link to #main is present       (WCAG 2.4.1)
  table-header       data tables have headers or are
                     marked role="presentation"            (WCAG 1.3.1)

Findings listed in data/a11y-exceptions.json (file + rule + reason) are
acknowledged and do not fail the build.
"""
import argparse
import json
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
EXCEPTIONS = ROOT / 'data/a11y-exceptions.json'
HEADINGS = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6')
GENERIC_LINK_TEXT = {'here', 'click here', 'read more', 'more', 'learn more', 'this link', 'link'}


def check_document(soup):
    """Return a list of {'rule', 'detail'} findings for one parsed document."""
    findings = []
    html = soup.find('html')
    if not (html and html.get('lang')):
        findings.append({'rule': 'html-has-lang', 'detail': '<html> has no lang attribute'})
    title = soup.find('title')
    if not (title and title.get_text(strip=True)):
        findings.append({'rule': 'document-title', 'detail': 'missing or empty <title>'})
    h1s = soup.find_all('h1')
    if len(h1s) != 1:
        findings.append({'rule': 'page-has-one-h1', 'detail': f'{len(h1s)} <h1> elements'})
    levels = [int(h.name[1]) for h in soup.find_all(HEADINGS)]
    for previous, current in zip(levels, levels[1:]):
        if current > previous + 1:
            findings.append({'rule': 'heading-order', 'detail': f'h{previous} to h{current}'})
            break
    for img in soup.find_all('img'):
        if img.get('alt') is None:
            findings.append({'rule': 'image-alt', 'detail': str(img.get('src', '(no src)'))})
    for link in soup.find_all('a', href=True):
        text = (link.get_text() or '').strip()
        images = link.find_all('img')
        named = bool(text) or any((i.get('alt') or '').strip() for i in images) or link.has_attr('aria-label')
        if not named:
            findings.append({'rule': 'link-name', 'detail': link['href']})
        elif text.lower() in GENERIC_LINK_TEXT:
            findings.append({'rule': 'link-text', 'detail': f'{text!r} -> {link["href"]}'})
    mains = soup.find_all('main')
    if len(mains) != 1:
        findings.append({'rule': 'landmark-one-main', 'detail': f'{len(mains)} <main> elements'})
    if not soup.find('a', href='#main'):
        findings.append({'rule': 'skip-link', 'detail': 'no skip link to #main'})
    for table in soup.find_all('table'):
        if table.find('th') or table.find('caption') or table.get('role') in ('presentation', 'none'):
            continue
        findings.append({'rule': 'table-header', 'detail': f'table of {len(table.find_all("tr"))} rows has no header cells'})
    return findings


def load_exceptions(path=None):
    path = path or EXCEPTIONS
    if not Path(path).exists():
        return {}
    acknowledged = {}
    for item in json.loads(Path(path).read_text()):
        acknowledged.setdefault((item['file'], item['rule']), item.get('reason', ''))
    return acknowledged


def audit(output=None, documents=None, exceptions=None):
    output = Path(output or (ROOT / 'public'))
    if documents is None:
        documents = {}
        for path in sorted(output.rglob('*')):
            if path.is_file() and path.suffix.lower() in ('.htm', '.html'):
                documents[path] = BeautifulSoup(path.read_text(), 'lxml')
    acknowledged = load_exceptions(exceptions)
    findings = []
    for path, soup in documents.items():
        name = path.relative_to(output).as_posix() if path.is_absolute() else Path(path).as_posix()
        for finding in check_document(soup):
            finding['file'] = name
            finding['acknowledged'] = acknowledged.get((name, finding['rule']))
            findings.append(finding)
    open_findings = [f for f in findings if not f['acknowledged']]
    by_rule = {}
    for finding in findings:
        by_rule[finding['rule']] = by_rule.get(finding['rule'], 0) + 1
    return {
        'summary': {'files_scanned': len(documents), 'findings': len(findings),
                    'acknowledged': len(findings) - len(open_findings),
                    'unacknowledged': len(open_findings), 'rules': by_rule},
        'findings': findings,
    }


def write_report(result, path=None):
    path = Path(path or (ROOT / 'data/a11y-report.json'))
    path.write_text(json.dumps(result, indent=2) + '\n')
    return path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Exit non-zero on unacknowledged findings')
    args = parser.parse_args()
    result = audit()
    write_report(result)
    summary = result['summary']
    print(f"Checked {summary['files_scanned']} documents: {summary['findings']} findings, "
          f"{summary['acknowledged']} acknowledged, {summary['unacknowledged']} unacknowledged.")
    for rule, count in sorted(summary['rules'].items()):
        print(f"  {rule}: {count}")
    for finding in result['findings']:
        if not finding['acknowledged']:
            print(f"  FAIL {finding['file']}: {finding['rule']} ({finding['detail']})")
    if args.check and summary['unacknowledged']:
        raise SystemExit('Unacknowledged accessibility findings')
