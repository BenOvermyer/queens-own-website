#!/usr/bin/env python3
"""Organize preserved club content, canonical routes, redirects, and publication indexes."""
import calendar
import csv
from datetime import date
import html
import json
from pathlib import Path
import posixpath
import re
import tomllib
from urllib.parse import unquote, urlsplit, urlunsplit

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
TOPICS = {
    'membership': 'Membership', 'personas': 'Personas', 'world': 'World reference',
    'community': 'Community', 'publications': 'Publications', 'archive': 'Archive',
}
RULES = {
    'qojoin.htm': ('membership', 'how-to-join', 'How to join'),
    'qofaqqo.htm': ('membership', 'club-faq', 'Queen’s Own FAQ'),
    'qomentor.htm': ('membership', 'mentors', 'Mentors'),
    'qoseal.htm': ('membership', 'club-seal', 'Queen’s Own seal'),
    'qohandouts.htm': ('personas', 'persona-handouts', 'Persona handouts and submission instructions'),
    'qob.htm': ('personas', 'bard-handout', 'Bard handout'),
    'qoba.htm': ('personas', 'northern-barbarian-handout', 'Northern Barbarian handout'),
    'qobl.htm': ('personas', 'blues-handout', 'Blues handout'),
    'qog.htm': ('personas', 'guild-handout', 'Guild handout'),
    'qohe.htm': ('personas', 'healer-handout', 'Healer handout'),
    'qohh.htm': ('personas', 'herald-handout', 'Herald handout'),
    'qohm.htm': ('personas', 'herald-mage-handout', 'Herald-Mage handout'),
    'qok.htm': ('personas', 'kalen-edral-handout', 'Kal’enedral handout'),
    'qom.htm': ('personas', 'military-handout', 'Military handout'),
    'qorel.htm': ('personas', 'priest-and-priestess-handout', 'Priest and priestess handout'),
    'qos.htm': ('personas', 'shina-in-handout', 'Shin’a’in handout'),
    'qot.htm': ('personas', 'tayledras-handout', 'Tayledras handout'),
    'qoww.htm': ('personas', 'sorcerer-handout', 'Sorcerer and sorceress handout'),
    'qolist.htm': ('personas', 'persona-directory', 'Persona directory'),
    'qonpc.htm': ('personas', 'npc-directory', 'Non-player character directory'),
    'qojust.htm': ('world', 'world-reference-guide', 'Velgarth reference guide'),
    'qofaqa.htm': ('world', 'fauna-faq', 'Fauna FAQ'),
    'qofaqb.htm': ('world', 'bards-faq', 'Bards FAQ'),
    'qofaqba.htm': ('world', 'northern-barbarians-faq', 'Northern Barbarians FAQ'),
    'qofaqbl.htm': ('world', 'blues-and-blue-bloods-faq', 'Blues and blue bloods FAQ'),
    'qofaqc.htm': ('world', 'cooking-velgarth-style', 'Cooking Velgarth style'),
    'qofaqg.htm': ('world', 'guilds-faq', 'Guilds FAQ'),
    'qofaqgarb.htm': ('world', 'garb-faq', 'Garb FAQ'),
    'qofaqgifts.htm': ('world', 'gifts-faq', 'Gifts FAQ'),
    'qofaqh.htm': ('world', 'heralds-faq', 'Heralds FAQ'),
    'qofaqhe.htm': ('world', 'healers-faq', 'Healers FAQ'),
    'qofaqm.htm': ('world', 'military-faq', 'Military FAQ'),
    'qofaqp.htm': ('world', 'plants-faq', 'Plants FAQ'),
    'qofaqrel.htm': ('world', 'religions-faq', 'Religions FAQ'),
    'qofaqs.htm': ('world', 'shina-in-faq', 'Shin’a’in FAQ'),
    'qofaqt.htm': ('world', 'tayledras-faq', 'Tayledras FAQ'),
    'qofaqtr.htm': ('world', 'travel-guide', 'Velgarth travel guide'),
    'qochap.htm': ('community', 'chapters', 'Chapter directory'),
    'qochat.htm': ('community', 'club-chat', 'Club chat guidance'),
    'qodelphi.htm': ('community', 'delphi-forum', 'Delphi forum'),
    'qofun.htm': ('community', 'fun-stuff', 'Fun stuff'),
    'qolinks.htm': ('community', 'mercedes-lackey-links', 'Mercedes Lackey links'),
    'qorpg.htm': ('community', 'role-playing', 'Role-playing instructions'),
    'qoring.htm': ('community', 'club-webring', 'Club webring'),
    'qoring1.htm': ('community', 'webring-code', 'Webring code'),
    'qonews.htm': ('newsletters', 'newsletter-guidance', 'Newsletter publication and submission guidance'),
    'qojournal.htm': ('compass-rose', 'compass-rose/about', 'About The Compass Rose'),
    'qofanfic.htm': ('fan-fiction', 'fan-fiction', 'Fan fiction archive'),
    'qozine.htm': ('fan-fiction', 'children-of-velgarth', 'Children of Velgarth'),
    'qomlrel2.htm': ('fan-fiction', 'release-form-instructions', 'Release form instructions'),
}
MONTHS = {name.lower()[:3]: n for n, name in enumerate(calendar.month_name) if name}
NEWSLETTER = re.compile(r'^qo(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)(\d{2})\.htm$', re.I)
HOSTS = {'queensown.org', 'www.queensown.org'}
DRAGON_HOSTS = {'dragonlords.fans', 'www.dragonlords.fans', 'dragonlordsnet.com', 'www.dragonlordsnet.com'}


def read_document(path):
    text = path.read_text()
    _, front, body = text.split('+++', 2)
    return tomllib.loads(front), body.lstrip('\n')


def toml_value(value):
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, list):
        return '[' + ', '.join(toml_value(v) for v in value) + ']'
    return json.dumps(value, ensure_ascii=False)


def write_document(path, meta, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    front = ['+++']
    for key, value in meta.items():
        if key != 'extra':
            front.append(key + ' = ' + toml_value(value))
    if meta.get('extra'):
        front.append('[extra]')
        for key, value in meta['extra'].items():
            front.append(key + ' = ' + toml_value(value))
    front.append('+++')
    path.write_text('\n'.join(front) + '\n\n' + body.rstrip() + '\n')


def classify(source, meta, dragon_routes):
    match = NEWSLETTER.fullmatch(source)
    issue = None
    kind = 'page'
    if match:
        month, short_year = MONTHS[match[1].lower()], int(match[2])
        year = 2000 + short_year if short_year < 80 else 1900 + short_year
        title = f'Queen’s Own newsletter — {calendar.month_name[month]} {year}'
        route = f'/newsletters/{year}/{calendar.month_name[month].lower()}/'
        topic, section = 'publications', 'newsletters'
        content_file = f'newsletters/{year}/{calendar.month_name[month].lower()}.md'
        issue = {'year': year, 'month': month, 'label': f'{calendar.month_name[month]} {year}'}
    elif source in RULES:
        section, slug, title = RULES[source]
        topic = 'publications' if section in ('newsletters', 'compass-rose', 'fan-fiction') else section
        route = '/' + slug + '/'
        content_file = section + '/' + slug.split('/')[-1] + '.md'
        if source == 'qofanfic.htm':
            kind, content_file = 'section', 'fan-fiction/_index.md'
    elif source in dragon_routes:
        route = dragon_routes[source]
        title = re.sub(r'<[^>]+>', '', meta['title']).replace('Queen\'s Own--', '').strip()
        if source.startswith('cr'):
            section, topic = 'compass-rose', 'publications'
            pieces = route.strip('/').split('/')
            if source in ('crtoc.htm', 'cr2toc.htm'):
                kind = 'section'
                content_file = '/'.join(pieces) + '/_index.md'
                title = 'Summer 2000' if source == 'crtoc.htm' else 'Spring 2002'
            else:
                content_file = '/'.join(pieces[:2]) + '/' + '--'.join(pieces[2:]) + '.md'
                title = re.sub(r'^The Compass Rose:\s*', '', title)
        elif source.startswith('vfc'):
            section, topic = 'vanyel-fan-club', 'community'
            kind = 'section' if source == 'vfcindex.htm' else 'page'
            title = 'Vanyel Fan Club' if kind == 'section' else title
            content_file = 'vanyel-fan-club/' + ('_index.md' if kind == 'section' else route.strip('/').split('/')[-1] + '.md')
        elif source == 'mlrelease.htm':
            section, topic = 'fan-fiction', 'publications'
            content_file = section + '/mercedes-lackey-release-form.md'
        elif source in ('dcpawn.htm', 'dcprom.htm', 'dcprice.htm'):
            section, topic = 'dream-casts', 'community'
            content_file = section + '/' + route.strip('/').split('/')[-1] + '.md'
        else:
            section = 'world' if source in ('danc.htm', 'danhc.htm', 'danmag1.htm', 'danp.htm', 'danr.htm', 'dantime.htm') else 'community'
            topic = section
            content_file = section + '/' + route.strip('/').replace('/', '--') + '.md'
    else:
        raise ValueError('Unmapped legacy content: ' + source)
    aliases = ['/' + source, '/' + source + '/']
    if source == 'danyagg.htm':
        aliases += ['/qogg.htm', '/qogg.htm/']
    previous = meta.get('path', '').strip('/')
    if previous and '/' + previous + '/' != route:
        aliases += ['/' + previous, '/' + previous + '/']
    return {'source': source, 'title': title, 'topic': topic, 'section': section,
            'canonical_path': route, 'content_file': content_file, 'kind': kind,
            'redirect_target': route,
            'aliases': sorted(set(aliases)), 'issue': issue, 'source_present': True}


def route_aliases(records):
    # The source homepage has been replaced by the editorial homepage.
    aliases = {path: '/' for path in ('/index.html', '/index.htm', '/qo.htm')}
    for record in records.values():
        target = record['redirect_target']
        for old in record['aliases']:
            normalized = old.rstrip('/') or '/'
            if normalized in aliases and aliases[normalized] != target:
                raise ValueError('Conflicting redirect: ' + old)
            aliases[normalized] = target
    return aliases


def rewrite_url(value, source, aliases, dragon_routes):
    decoded = html.unescape(value)
    url = urlsplit(decoded)
    if url.scheme not in ('', 'http', 'https', 'file') or not url.path:
        return value
    if url.netloc and url.hostname not in HOSTS | DRAGON_HOSTS:
        return value
    path = unquote(url.path)
    key = posixpath.normpath(path if path.startswith('/') else '/' + posixpath.join(posixpath.dirname(source), path))
    if url.hostname in DRAGON_HOSTS and key.lstrip('/') not in dragon_routes and not key.lstrip('/').startswith('qo'):
        return value
    target = aliases.get(key.rstrip('/') or '/')
    if target is None:
        return value
    fragment = 'ren' if source == 'crrev.htm' and url.fragment == 'red' else url.fragment
    return html.escape(urlunsplit(('', '', target, url.query, fragment)), quote=True)


def rewrite_body(body, source, aliases, dragon_routes):
    attribute = re.compile(r'(\b(?:href|src|background|data-unavailable-target)\s*=\s*")([^"]*)(")', re.I)
    body = attribute.sub(lambda m: m[1] + rewrite_url(m[2], source, aliases, dragon_routes) + m[3], body)
    # Historical URL labels should point readers at the same canonical destinations.
    old_url = re.compile(r'https?://(?:www\.)?(?:queensown\.org|dragonlords\.fans|dragonlordsnet\.com)/[^\s<>"\)]+')
    body = old_url.sub(lambda m: rewrite_url(m[0], source, aliases, dragon_routes), body)
    # Some source buttons say Queen's Own but were mistakenly split onto Dragonlords' home.
    if 'dragonlords.fans/index.htm' in body:
        soup = BeautifulSoup(body, 'lxml')
        changed = False
        for a in soup.select('a[href]'):
            if urlsplit(a['href']).hostname in DRAGON_HOSTS and urlsplit(a['href']).path == '/index.htm' and re.search(r"Queen.?s Own.*Home Page", a.get_text(' ', strip=True)):
                a['href'] = '/'
                changed = True
        if changed:
            body = soup.body.decode_contents()
    return '\n'.join(line.rstrip() for line in body.splitlines()) + '\n'


def pdf_period(filename, label):
    match = re.search(r'(19|20)\d{2}', filename)
    if not match:
        raise ValueError('Newsletter has no year: ' + filename)
    year = int(match[0])
    prefix = filename[:match.start()].lower().removeprefix('qo')
    month = next((n for key, n in MONTHS.items() if prefix.startswith(key)), None)
    if month is None:
        month = next((n for season, n in [('winter', 1), ('spring', 3), ('summer', 6), ('fall', 9), ('autumn', 9)] if prefix.startswith(season)), None)
    if month is None:
        raise ValueError('Newsletter has no period: ' + filename)
    return year, month, label + ' ' + str(year)


def publication_index(documents, records):
    evidence = json.loads((ROOT / 'data/link-http-evidence.json').read_text())
    pdf_base = tomllib.loads((ROOT / 'config.toml').read_text())['extra']['pdf_base_url'].rstrip('/')
    issues = []
    for record in records.values():
        if record['issue']:
            issues.append({**record['issue'], 'path': record['canonical_path'], 'format': 'HTML',
                           'available': record['source_present'], 'source': record['source']})
    pdf_rows, fiction = {}, {}
    for source, destination in [('qonews.htm', pdf_rows), ('qofanfic.htm', fiction)]:
        soup = BeautifulSoup(documents[source][2], 'lxml')
        for a in soup.select('a[href]'):
            value = a['href'].replace('__PDF_BASE_URL__', pdf_base)
            url = urlsplit(value)
            if not url.path.lower().endswith('.pdf') or url.hostname != urlsplit(pdf_base).hostname:
                continue
            filename = unquote(url.path).split('/')[-1]
            label = a.get_text(' ', strip=True)
            if not label:
                continue
            saved = evidence.get(value, {})
            code = saved.get('status')
            available = isinstance(code, int) and 200 <= code < 300 and 'application/pdf' in saved.get('content_type', '').lower()
            row = {'filename': filename, 'title': label, 'available': available, 'format': 'PDF'}
            if source == 'qonews.htm':
                year, month, period = pdf_period(filename, label)
                row.update(year=year, month=month, label=period)
            destination[filename] = row
    issues += list(pdf_rows.values())
    issues.sort(key=lambda row: (-row['year'], row['month'], row.get('source', row.get('filename', ''))))
    years = [{'year': year, 'issues': [row for row in issues if row['year'] == year]} for year in sorted({row['year'] for row in issues}, reverse=True)]
    return {'years': years, 'fiction': sorted(fiction.values(), key=lambda row: row['title']),
            'summary': {'preserved_html_newsletters': sum(r['format'] == 'HTML' and r['available'] for r in issues),
                        'unavailable_html_newsletters': sum(r['format'] == 'HTML' and not r['available'] for r in issues),
                        'pdf_newsletters': len(pdf_rows), 'fiction_pdfs': len(fiction)}}


def ensure_hub(relative, title, body, template='section.html', **extra):
    path = ROOT / 'content' / relative
    if path.exists():
        return
    meta = {'title': title, 'template': template, 'sort_by': 'title', 'extra': {'navigation_hub': True, **extra}}
    if 'year' in extra:
        meta['weight'] = 10000 - extra['year']
        meta['sort_by'] = 'date'
    write_document(path, meta, body)


def organize():
    documents = {}
    for path in sorted((ROOT / 'content').rglob('*.md')):
        meta, body = read_document(path)
        source = meta.get('extra', {}).get('legacy_source')
        if source == 'index.html':
            # Do not recreate the retired source homepage from an old import.
            if path != ROOT / 'content/_index.md':
                path.unlink()
            continue
        if source:
            if source in documents:
                raise ValueError('Duplicate source content: ' + source)
            documents[source] = (path, meta, body)
    if not documents:
        raise ValueError('No preserved content found')
    dragon_routes = json.loads((ROOT / 'data/dragonlords-route-map.json').read_text())
    records = {source: classify(source, meta, dragon_routes) for source, (_, meta, _) in documents.items()}
    for source, month in [('qonov98.htm', 11), ('qodec98.htm', 12)]:
        if source not in records:
            records[source] = classify(source, {'title': ''}, dragon_routes)
            records[source]['source_present'] = False
    records = dict(sorted(records.items()))
    aliases = route_aliases(records)
    catalog = publication_index(documents, records)
    # Build every destination before removing superseded source paths.
    for source, record in records.items():
        if source in documents:
            old_path, original, body = documents[source]
            meta = dict(original)
            meta['extra'] = dict(original.get('extra', {}))
            body = rewrite_body(body, source, aliases, dragon_routes)
        else:
            meta = {'extra': {}}
            body = '# ' + record['issue']['label'] + '\n\nThis issue was linked from the archive, but its content was not present in the recovered files. It remains unavailable pending recovery.\n'
        meta['title'] = record['title']
        meta.pop('aliases', None)
        meta['extra'].update(historical=True, topic=record['topic'], canonical_path=record['canonical_path'])
        if record['source_present']:
            meta['extra'].pop('missing_source', None)
            meta['extra']['legacy_source'] = source
        else:
            meta['extra']['missing_source'] = source
        if record['kind'] == 'section':
            meta.pop('path', None)
            meta['sort_by'] = 'title'
            meta['template'] = 'fan-fiction.html' if source == 'qofanfic.htm' else 'section.html'
            if source in ('crtoc.htm', 'cr2toc.htm'):
                meta['weight'] = 24 if source == 'crtoc.htm' else 22
        else:
            meta['path'] = record['canonical_path'].strip('/')
            meta['template'] = 'page.html'
        if record['issue']:
            period = record['issue']
            meta['date'] = date(period['year'], period['month'], 1)
            meta['extra']['publication_period'] = period['label']
            meta['extra']['date_precision'] = 'month'
        write_document(ROOT / 'content' / record['content_file'], meta, body)
    destinations = {ROOT / 'content' / r['content_file'] for r in records.values()}
    for old_path, _, _ in documents.values():
        if old_path not in destinations:
            old_path.unlink()
    old_archive = ROOT / 'content/archive.md'
    if old_archive.exists():
        old_archive.unlink()
    ensure_hub('_index.md', 'Queen’s Own', 'A gathering place for Mercedes Lackey readers: membership resources, personas, Velgarth reference material, and decades of fan publications.\n', 'index.html')
    ensure_hub('membership/_index.md', 'Membership', 'Start with [how to join](/how-to-join/), the [club FAQ](/club-faq/), and [persona resources](/personas/). The [community directory](/community/) includes the club’s social links.\n')
    ensure_hub('personas/_index.md', 'Personas', 'Explore [persona handouts and submission instructions](/persona-handouts/), then consult the [world reference library](/world/). Browse the persona and NPC directories.\n')
    ensure_hub('world/_index.md', 'World reference', 'Reference material for Velgarth, its peoples, Gifts, magic, and everyday life. Browse the FAQs or begin with the [reference guide](/world-reference-guide/).\n')
    ensure_hub('community/_index.md', 'Community', '[Queen’s Own Facebook page](https://www.facebook.com/queensownfanclub) · [Published Facebook chat group](https://www.facebook.com/groups/1607409292715707/)\n\nExplore [chapters](/chapters/), [Golden Grove](/golden-grove/), the [Vanyel Fan Club archive](/vanyel-fan-club/), and [fan activities](/fun-stuff/). \n')
    ensure_hub('dream-casts/_index.md', 'Valdemar dream casts', 'Proposed casts for the Last Herald-Mage trilogy.\n', topic='community')
    ensure_hub('publications/_index.md', 'Publications', 'Browse the [newsletter archive](/newsletters/), [The Compass Rose](/compass-rose/), and the [fan fiction archive](/fan-fiction/). Publications retain their authors’ credits and original notices.\n')
    ensure_hub('newsletters/_index.md', 'Newsletter archive', 'Browse issues by year, from the earliest preserved newsletters through the later PDF editions. Unavailable issues are identified in each year’s list. [Original publication and submission guidance](/newsletter-guidance/) is preserved separately.\n', 'newsletters.html', topic='publications')
    ensure_hub('compass-rose/_index.md', 'The Compass Rose', 'Queen’s Own’s nonfiction journal. Read [about the journal and its original submission guidance](/compass-rose/about/), or browse the preserved issues below.\n', topic='publications')
    ensure_hub('archive/_index.md', 'Complete archive', 'Every page is listed by topic below.\n', 'archive.html')
    for year in catalog['years']:
        ensure_hub(f'newsletters/{year["year"]}/_index.md', str(year['year']) + ' newsletters', 'Issues are listed in calendar order. PDF files are hosted in the separate files archive; unavailable editions remain explicitly marked.\n', 'newsletter-year.html', year=year['year'], topic='publications')
    # Preserve known gaps under the new referring-page URLs, including new archive indexes.
    dispositions_path = ROOT / 'data/link-dispositions.json'
    dispositions = json.loads(dispositions_path.read_text())
    updated = {}
    for target, disposition in dispositions.items():
        new_target = html.unescape(rewrite_url(target, '', aliases, dragon_routes)).rstrip('/')
        revised = dict(disposition)
        revised['referring_pages'] = sorted({
            (records[p]['canonical_path'].strip('/') + '/index.html') if p in records else p
            for p in disposition['referring_pages']
        })
        if target in ('/qonov98.htm', '/qodec98.htm'):
            revised['original_target'] = target
            revised['referring_pages'].append('newsletters/1998/index.html')
        if revised.get('original_target') in ('/qonov98.htm', '/qodec98.htm'):
            revised['referring_pages'].append('archive/index.html')
        if target.startswith('https://') and target.lower().endswith('.pdf'):
            filename = unquote(urlsplit(target).path).split('/')[-1]
            for year in catalog['years']:
                if any(row.get('filename') == filename for row in year['issues']):
                    revised['referring_pages'].append(f'newsletters/{year["year"]}/index.html')
            if any(row['filename'] == filename for row in catalog['fiction']):
                revised['referring_pages'].append('fan-fiction/index.html')
        revised['referring_pages'] = sorted(set(revised['referring_pages']))
        updated[new_target] = revised
    dispositions_path.write_text(json.dumps(updated, indent=2, sort_keys=True) + '\n')
    (ROOT / 'data/site-routes.json').write_text(json.dumps(records, indent=2, ensure_ascii=False, default=str) + '\n')
    (ROOT / 'data/publication-index.json').write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + '\n')
    navigation = {'topics': []}
    for topic, title in TOPICS.items():
        if topic == 'archive':
            continue
        entries = [r for r in records.values() if r['topic'] == topic]
        entries.sort(key=lambda r: (1, -r['issue']['year'], r['issue']['month']) if r['issue'] else (0, r['title'].casefold(), 0))
        navigation['topics'].append({'key': topic, 'title': title, 'entries': entries})
    (ROOT / 'data/navigation-index.json').write_text(json.dumps(navigation, indent=2, ensure_ascii=False) + '\n')
    redirects = {path + suffix: '/' for path in ('/index.html', '/index.htm', '/qo.htm') for suffix in ('', '/')}
    for record in records.values():
        for alias in record['aliases']:
            if alias != record['redirect_target']:
                redirects[alias] = record['redirect_target']
    (ROOT / 'static/_redirects').write_text('# Canonical content paths; preserve old bookmarks and inbound fragments.\n' + '\n'.join(f'{old} {new} 301!' for old, new in sorted(redirects.items())) + '\n')
    with (ROOT / 'data/site-map.csv').open('w', newline='') as handle:
        fields = ['source', 'title', 'topic', 'section', 'canonical_path', 'content_file', 'kind', 'source_present', 'redirect_target']
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction='ignore', lineterminator='\n')
        writer.writeheader()
        writer.writerows(sorted(records.values(), key=lambda r: (r['topic'], r['canonical_path'])))
    print(f'Organized {sum(r["source_present"] for r in records.values())} preserved pages and {sum(not r["source_present"] for r in records.values())} unavailable issue notices.')
    print('Publication index:', catalog['summary'])


if __name__ == '__main__':
    organize()
