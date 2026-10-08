"""Exercise route changes, archive precision, preservation, and repeatable organization."""
import contextlib
import html
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

import organize_site


class OrganizationTests(unittest.TestCase):
    def test_route_rewrite_preserves_query_and_fragment_and_leaves_bookstore_external(self):
        aliases = {'/qob.htm': '/bard-handout/'}
        result = organize_site.rewrite_url('https://queensown.org/qob.htm?x=1&amp;y=2#teacher', 'qohandouts.htm', aliases, {})
        parsed = urlsplit(html.unescape(result))
        self.assertEqual((parsed.path, parsed.query, parsed.fragment), ('/bard-handout/', 'x=1&y=2', 'teacher'))
        bookstore = 'https://dragonlords.fans/bkstore.htm'
        self.assertEqual(organize_site.rewrite_url(bookstore, 'qofun.htm', aliases, {}), bookstore)

    def test_publication_periods_keep_centuries_and_season_labels(self):
        self.assertEqual(organize_site.classify('qomar90.htm', {}, {})['issue']['year'], 1990)
        self.assertEqual(organize_site.classify('qojan05.htm', {}, {})['issue']['year'], 2005)
        self.assertEqual(organize_site.pdf_period('qoWinter2024.pdf', 'Winter'), (2024, 1, 'Winter 2024'))
        self.assertEqual(organize_site.pdf_period('qoJune-July2021.pdf', 'June–July'), (2021, 6, 'June–July 2021'))

    def test_organization_preserves_prose_anchors_and_curated_hubs_on_repeat(self):
        with tempfile.TemporaryDirectory() as work:
            root = Path(work)
            (root / 'content').mkdir()
            (root / 'data').mkdir()
            (root / 'static').mkdir()
            (root / 'config.toml').write_text('[extra]\npdf_base_url="https://files.queensown.org"\n')
            for name in ('dragonlords-route-map.json', 'link-http-evidence.json', 'link-dispositions.json'):
                (root / 'data' / name).write_text('{}')
            samples = {
                'qob.htm': '<a id="teacher" name="teacher"></a><p>Original bard prose.</p>',
                'qofaqb.htm': '<a href="/qob.htm#teacher">Bard handout</a>',
                'qojan05.htm': '<p>January 2005 newsletter text.</p>',
                'qonews.htm': '<a href="__PDF_BASE_URL__/qoWinter2024.pdf">Winter</a>',
                'qofanfic.htm': '<p>Original fiction credits and permissions.</p>',
            }
            for source, body in samples.items():
                path = root / 'content' / ('_index.md' if source == 'index.html' else source + '.md')
                path.write_text('+++\ntitle="Original"\n[extra]\nlegacy_source=' + json.dumps(source) + '\n+++\n\n' + body)
            home = root / 'content/_index.md'
            home.write_text('+++\ntitle="Queen’s Own"\n[extra]\nnavigation_hub=true\n+++\n\nEditorial home text to retain.\n')
            (root / 'content/retired.md').write_text('+++\ntitle="Old home"\n[extra]\nlegacy_source="index.html"\n+++\n\nRetired content.\n')
            with patch.object(organize_site, 'ROOT', root), contextlib.redirect_stdout(io.StringIO()):
                organize_site.organize()
                bard = (root / 'content/personas/bard-handout.md').read_text()
                self.assertIn('Original bard prose.', bard)
                self.assertIn('id="teacher" name="teacher"', bard)
                self.assertIn('/bard-handout/#teacher', (root / 'content/world/bards-faq.md').read_text())
                self.assertIn('Editorial home text to retain.', home.read_text())
                self.assertFalse((root / 'content/retired.md').exists())
                routes = json.loads((root / 'data/site-routes.json').read_text())
                self.assertNotIn('index.html', routes)
                self.assertIn('/index.html / 301!', (root / 'static/_redirects').read_text())
                hub = root / 'content/membership/_index.md'
                hub.write_text(hub.read_text() + '\nEditorial note to retain.\n')
                first = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
                organize_site.organize()
                second = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
                self.assertEqual(first, second)
                self.assertIn('Editorial note to retain.', hub.read_text())


if __name__ == '__main__':
    unittest.main()
