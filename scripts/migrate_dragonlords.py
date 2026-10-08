#!/usr/bin/env python3
"""Import approved static club pages from the Dragonlords archive, keeping its bookstore."""
import argparse
import json
from pathlib import Path
import posixpath
import re
import shutil
import tomllib
from urllib.parse import quote, unquote, urlsplit, urlunsplit

from bs4 import BeautifulSoup
from inventory_dragonlords import INTERNAL_HOSTS

ROOT = Path(__file__).resolve().parents[1]
ROUTES = {
    'danyagg.htm': 'golden-grove', 'danyacc.htm': 'pacific-northwest-collegium', 'danyasc.htm': 'sonoran-collegium',
    'vfcindex.htm': 'vanyel-fan-club', 'vfcqa.htm': 'vanyel-fan-club/faq',
    'vfcjoin.htm': 'vanyel-fan-club/join', 'vfcnews.htm': 'vanyel-fan-club/newsletter',
    'vfcpres.htm': 'vanyel-fan-club/president', 'vfcchat.htm': 'vanyel-fan-club/chat',
    'vfcgate.htm': 'vanyel-fan-club/heralds-haven-gate', 'vfcgates.htm': 'vanyel-fan-club/heralds-haven',
    'danc.htm': 'companions-choices', 'danhc.htm': 'heralds-and-companions',
    'danmag1.htm': 'magic-of-velgarth', 'danp.htm': 'proverbs-of-velgarth',
    'danr.htm': 'reincarnated-characters', 'dantime.htm': 'valdemar-timeline',
    'danya.htm': 'danya-winterborn', 'danspell.htm': 'science-and-magic-tricks',
    'dcpawn.htm': 'dream-casts/magics-pawn', 'dcprom.htm': 'dream-casts/magics-promise',
    'dcprice.htm': 'dream-casts/magics-price',
    'recipes.htm': 'danyas-cookbook', 'mlrelease.htm': 'mercedes-lackey-release-form',
    'crtoc.htm': 'compass-rose/summer-2000', 'crle.htm': 'compass-rose/summer-2000/editorial',
    'crfrm.htm': 'compass-rose/summer-2000/from-reptile-to-mammal',
    'crfrm1.htm': 'compass-rose/summer-2000/from-reptile-to-mammal/references',
    'crc.htm': 'compass-rose/summer-2000/in-the-name-of-god',
    'crc1.htm': 'compass-rose/summer-2000/in-the-name-of-god/references',
    'crbi.htm': 'compass-rose/summer-2000/either-or', 'crbi1.htm': 'compass-rose/summer-2000/either-or/references',
    'crsos.htm': 'compass-rose/summer-2000/sink-or-swim', 'crrev.htm': 'compass-rose/summer-2000/reviews',
    'cr2toc.htm': 'compass-rose/spring-2002', 'cr2le.htm': 'compass-rose/spring-2002/editorial',
    'cr2sim.htm': 'compass-rose/spring-2002/music-in-medieval-ireland',
    'cr2sim1.htm': 'compass-rose/spring-2002/music-in-medieval-ireland/references',
    'cr2tat.htm': 'compass-rose/spring-2002/arthurian-tales',
    'cr2tat1.htm': 'compass-rose/spring-2002/arthurian-tales/references',
    'cr2ddl.htm': 'compass-rose/spring-2002/diversity-in-libraries',
    'cr2ddl1.htm': 'compass-rose/spring-2002/diversity-in-libraries/references',
    'cr2rev.htm': 'compass-rose/spring-2002/reviews',
}


def dragonlords_references(soup):
    reasons = []
    if re.search(r'dragonlords', soup.get_text(' ', strip=True), re.I):
        reasons.append('Visible text references Dragonlords.')
    for node in soup.select('[href], [src], [action]'):
        for attr in ('href', 'src', 'action'):
            value = node.get(attr, '')
            if 'dragonlords' in value.lower():
                reasons.append('URL references Dragonlords: ' + value)
            url = urlsplit(value)
            basename = posixpath.basename(url.path)
            if not url.netloc and (basename.startswith('bk') or basename in ('index.htm', 'index.html')):
                reasons.append('Links to the Dragonlords bookstore or homepage: ' + value)
    return sorted(set(reasons))


def remove_shared_promotions(soup, page):
    """Remove shared hosting/commerce furniture while retaining writing and credits."""
    for p in list(soup.find_all('p')):
        text = p.get_text(' ', strip=True)
        if page == 'danya.htm' and 'personal portion' in text:
            html = p.decode_contents()
            html = re.sub(r'This is my .*? site\.', '', html, count=1, flags=re.S)
            html = re.sub(r'\(Click\s+on the book covers.*?Bookstore\.\)', '', html, flags=re.S)
            p.clear()
            for child in list(BeautifulSoup(html, 'html.parser').contents):
                p.append(child)
        elif page == 'danya.htm' and 'main webring section of the Dragonlords site' in text:
            p.string = 'The following webrings are Valdemar-related.'
        elif 'Dragonlords' in text and 'Webdesign for this issue' in text:
            credit = p.find('a', href=re.compile('^mailto:'))
            if credit:
                credit.extract()
                p.clear()
                p.append('Webdesign for this issue by ')
                p.append(credit)
                p.append('.')
        elif page == 'vfcqa.htm' and 'Are there any club dues?' in text:
            p.clear()
            p.append('Q: Are there any club dues?')
            p.append(soup.new_tag('br'))
            p.append("A: No. The VFC is a chapter of Queen's Own. Membership is free.")
        elif 'Dragonlords' in text and any(word in text.lower() for word in ('bookstore', 'proceeds', 'purchases')):
            p.decompose()
    for a in list(soup.select('a[href]')):
        url = urlsplit(a['href'])
        basename = posixpath.basename(url.path).lower()
        bookstore = basename.startswith('bk') and (not url.netloc or url.hostname in INTERNAL_HOSTS)
        affiliate = 'dragonlordsofdum' in a['href'].lower()
        footer = basename in ('index.htm', 'index.html') and 'dragonlords' in a.get_text(' ', strip=True).lower()
        if footer:
            a.decompose()
        elif bookstore or affiliate:
            # Book covers were supplied for sales links; remove those commerce images.
            for image in a.find_all('img'):
                image.decompose()
            a.unwrap()


def refresh_archive_links():
    archive = ROOT / 'content/archive.md'
    if not archive.exists():
        return
    entries = []
    for page in sorted((ROOT / 'content').glob('imported-*.md')):
        meta = tomllib.loads(page.read_text().split('+++', 2)[1])
        title = re.sub(r'<[^>]+>', '', meta['title']).replace('[', '').replace(']', '')
        entries.append('- [' + title + '](/' + meta['path'].strip('/') + '/)')
    block = '<!-- migrated-club-pages:start -->\n\n## Additional club archives\n\n' + '\n'.join(entries) + '\n\n<!-- migrated-club-pages:end -->'
    text = archive.read_text()
    if '<!-- migrated-club-pages:start -->' in text:
        text = re.sub(r'<!-- migrated-club-pages:start -->.*?<!-- migrated-club-pages:end -->', lambda _: block, text, flags=re.S)
    else:
        text = text.rstrip() + '\n\n' + block + '\n'
    archive.write_text(text)


def migrate(source):
    files = {p.relative_to(source).as_posix(): p for p in source.rglob('*') if p.is_file()}
    decision = []
    soups = {}
    for name, route in ROUTES.items():
        soup = BeautifulSoup(files[name].read_bytes(), 'lxml')
        reasons = dragonlords_references(soup)
        # These groups are dedicated club publications and activities. Dragonlords
        # appearances are shared hosting/commerce furniture, not its own-world content.
        decision.append({'source': name, 'route': '/' + route + '/', 'decision': 'migrate',
                         'removed_shared_references': reasons,
                         'reason': 'Dedicated Queen’s Own content; remove shared Dragonlords hosting/commerce furniture.'})
        soups[name] = soup
    selected = {r['source']: r['route'] for r in decision if r['decision'] == 'migrate'}
    previous_report = ROOT / 'data/dragonlords-migration-report.json'
    previous = json.loads(previous_report.read_text()) if previous_report.exists() else {}
    copied = set(previous.get('copied_assets', []))
    missing = []
    aliases = {'sim1.htm': 'cr2sim1.htm', 'president.html': 'vfcpres.htm'}

    def rewrite(value, page, attr):
        url = urlsplit(value)
        if url.scheme not in ('', 'http', 'https', 'file'):
            if url.scheme == 'mailto':
                return value.rstrip('"')
            return value
        if url.hostname in ('queensown.org', 'www.queensown.org'):
            return urlunsplit(('', '', url.path or '/', url.query, url.fragment))
        if url.netloc and url.hostname not in INTERNAL_HOSTS:
            return value
        if not url.path:
            return value
        path = unquote(url.path)
        target = posixpath.normpath(path.lstrip('/') if path.startswith('/') else posixpath.join(posixpath.dirname(page), path))
        target = aliases.get(target, target)
        suffix = ('?' + url.query if url.query else '') + ('#' + url.fragment if url.fragment else '')
        if target in selected:
            if target == 'crrev.htm' and url.fragment == 'red':
                return selected[target] + '#ren'
            return selected[target] + suffix
        if target in files and Path(target).suffix.lower() not in ('.htm', '.html', '.php', '.php3', '.cgi', '.com'):
            if target.lower().endswith('.pdf'):
                return '__PDF_BASE_URL__/' + quote(target, safe='/') + suffix
            destination = ROOT / 'static' / target
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists() and destination.read_bytes() != files[target].read_bytes():
                raise ValueError('Asset conflicts with existing file: ' + target)
            if not destination.exists():
                shutil.copyfile(files[target], destination)
                copied.add(target)
            return '/' + quote(target, safe='/') + suffix
        if target not in files:
            missing.append({'page': page, 'target': target, 'attribute': attr})
        return 'https://dragonlords.fans/' + quote(target, safe='/') + suffix

    for name, route in selected.items():
        soup = soups[name]
        remove_shared_promotions(soup, name)
        body = soup.body or soup
        if name == 'danya.htm' and not body.find(id='Herald'):
            body.insert(0, soup.new_tag('a', id='Herald'))
        if name == 'vfcindex.htm':
            for a in body.select('a[href]'):
                if '<' in a['href']:
                    a['href'] = 'vfcchat.htm'
                    a.string = 'VFC Chat List'
                    parent = a.parent
                    qa = soup.new_tag('a', href='vfcqa.htm')
                    qa.string = 'Q & A'
                    parent.append(soup.new_tag('br'))
                    parent.append(qa)
        if name == 'cr2sim1.htm' and not soup.find('a', attrs={'name': 'altramar'}):
            original = soup.find('a', attrs={'name': 'alramar'})
            if original:
                original.insert_before(soup.new_tag('a', id='altramar'))
            for alias, existing in [('cailin', 'caillin'), ('richter', 'richter2')]:
                target = soup.find('a', attrs={'name': existing})
                if target:
                    target.insert_before(soup.new_tag('a', id=alias))
        for node in list(body.find_all(['script', 'style', 'iframe', 'object', 'embed'])):
            node.decompose()
        for node in body.find_all(True):
            if node.name == 'a' and node.get('name'):
                node['id'] = node['name']
            for attr in list(node.attrs):
                if attr in ('href', 'src', 'background'):
                    old = node[attr]
                    if name == 'vfcjoin.htm' and attr == 'src' and old == 'vfcjoin.jpg':
                        node.name = 'span'
                        node.attrs.clear()
                        node.string = 'Join the Vanyel Fan Club'
                        break
                    if name == 'danspell.htm' and old == 'danyahm.htm':
                        node[attr] = '/qohm.htm'
                    else:
                        node[attr] = rewrite(old, name, attr)
                    if node.name == 'a' and node.get_text(strip=True) == old and node[attr] != old:
                        node.string = node[attr]
                elif attr.lower().startswith('on'):
                    del node[attr]
            if node.name == 'img':
                node['loading'] = 'lazy'
                if not node.has_attr('alt'):
                    node['alt'] = ''
        title = soup.title.get_text(' ', strip=True) if soup.title else name
        front = '+++\ntitle = ' + json.dumps(title, ensure_ascii=False) + '\npath = ' + json.dumps(route.strip('/')) + '\ntemplate = "page.html"\n[extra]\nlegacy_source = ' + json.dumps(name) + '\nsource_site = "dragonlords.fans"\n'
        for key, default in [('bgcolor', 'blue'), ('text', 'white'), ('link', 'aqua'), ('vlink', 'silver')]:
            value = body.get(key, default)
            if re.fullmatch(r'[0-9a-fA-F]{6}', value):
                value = '#' + value
            front += key + ' = ' + json.dumps(value) + '\n'
        front += '+++\n\n'
        destination = ROOT / 'content' / ('imported-' + route.strip('/').replace('/', '--') + '.md')
        rendered = front + '<div class="original-page">\n' + body.decode_contents().strip() + '\n</div>\n'
        for old_name, new_route in selected.items():
            rendered = re.sub(r'https?://(?:www\.)?(?:dragonlords\.fans|dragonlordsnet\.com)/' + re.escape(old_name) + r'(?=[#?"\s<>]|$)', new_route, rendered)
        destination.write_text('\n'.join(line.rstrip() for line in rendered.splitlines()) + '\n')
    # Rewrite only links to imported resources in existing club pages.
    count = 0
    existing_pages = []
    local_links = 0
    for path in (ROOT / 'content').rglob('*.md'):
        if path.name.startswith('imported-'):
            continue
        text = path.read_text()
        updated = text
        for name, route in selected.items():
            updated, n = re.subn(r'https?://(?:www\.)?(?:dragonlords\.fans|dragonlordsnet\.com)/' + re.escape(name) + r'(?=[#?"\s<>]|$)', route, updated)
            count += n
        if path.name == 'qochap.htm.md' and 'qogg.htm' in updated:
            front, html = updated.split('+++', 2)[1:]
            soup = BeautifulSoup(html, 'lxml')
            for a in soup.select('a[href]'):
                if unquote(urlsplit(a['href']).path) == '/qogg.htm':
                    a['href'] = selected['danyagg.htm']
                    a.attrs.pop('data-unavailable-target', None)
                    a.attrs.pop('title', None)
                    a.string = 'Golden Grove'
                    if a.next_sibling and getattr(a.next_sibling, 'name', None) == 'span' and 'unavailable-note' in a.next_sibling.get('class', []):
                        a.next_sibling.decompose()
            updated = '+++' + front + '+++\n\n' + soup.body.decode_contents().strip() + '\n'
        if updated != text:
            before_lines = text.splitlines()
            after_lines = updated.splitlines()
            if len(before_lines) == len(after_lines):
                updated = '\n'.join(old if old == new else new.rstrip() for old, new in zip(before_lines, after_lines)) + '\n'
            path.write_text(updated)
        linked = sum(len(re.findall(r'href="' + re.escape(route) + r'(?:[?#][^"]*)?"', updated)) for route in selected.values())
        if linked:
            existing_pages.append(path.relative_to(ROOT / 'content').as_posix())
            local_links += linked
    report = {'boundary': 'Retain substantive Dragonlords content and the bookstore. Migrate dedicated club material after removing shared hosting footers and bookstore promotions.',
              'pages': decision, 'copied_assets': sorted(copied), 'local_links_to_migrated_pages': local_links,
              'updated_existing_pages': sorted(existing_pages), 'missing_dependencies': missing}
    inventory_path = ROOT / 'data/dragonlords-content-inventory.json'
    if inventory_path.exists():
        inventory = json.loads(inventory_path.read_text())
        report['retained_source_pages'] = [
            {'source': p['path'], 'group': p['group'],
             'decision': 'retain',
             'reason': 'Keep the original publication/service on Dragonlords; it is outside the dedicated static club-page migration.'}
            for p in inventory['pages'] if p['path'] not in selected
        ]
    (ROOT / 'data/dragonlords-migration-report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    (ROOT / 'data/dragonlords-route-map.json').write_text(json.dumps(selected, indent=2, sort_keys=True) + '\n')
    (ROOT / 'static/_redirects').write_text('# Imported club pages now use descriptive paths.\n' + '\n'.join('/' + source + ' ' + route + ' 301' for source, route in sorted(selected.items())) + '\n')
    refresh_archive_links()
    print(f'Imported {len(selected)} pages; retained {len(decision) - len(selected)} candidates; copied {len(copied)} assets; rewrote {count} links.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, nargs='?', default=ROOT.parent / 'queens-own/dragonlords.fans')
    args = parser.parse_args()
    migrate(args.source.resolve())
