"""Verify the migration boundary, preserved credits, routes, and repeatability."""
import contextlib
import hashlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import migrate_dragonlords


class DragonlordsMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'destination'
        self.source = Path(self.temp.name) / 'source'
        self.source.mkdir()
        for folder in ('content', 'static', 'data'):
            (self.root / folder).mkdir(parents=True)
        self.patches = [patch.object(migrate_dragonlords, 'ROOT', self.root),
                        patch.object(migrate_dragonlords, 'ROUTES', {'danc.htm': 'companions-choices'})]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)
        (self.source / 'bkstore.htm').write_text('<h1>Dragonlords bookstore</h1>')
        (self.source / 'portrait.gif').write_bytes(b'original-artwork')
        (self.source / 'danc.htm').write_text('''<html><head><title>Companions’ Choices</title></head>
<body bgcolor="blue"><h1>Companions’ Choices</h1><p>Original club article.</p>
<p>Artwork by the credited artist.</p><img src="portrait.gif">
<p>Visit the <a href="bkstore.htm">Dragonlords Bookstore</a>.</p>
<a href="index.htm">Return to the Dragonlords of Dumnonia Home Page</a></body></html>''')
        (self.root / 'content/old.md').write_text('<a href="https://dragonlords.fans/danc.htm">Choices</a>')
        (self.root / 'content/archive.md').write_text('+++\ntitle="Archive"\n+++\n# Archive\n')

    def migrate(self):
        with contextlib.redirect_stdout(io.StringIO()):
            migrate_dragonlords.migrate(self.source)

    def test_import_preserves_article_and_credit_without_importing_store(self):
        self.migrate()
        text = (self.root / 'content/imported-companions-choices.md').read_text()
        self.assertIn('Original club article.', text)
        self.assertIn('Artwork by the credited artist.', text)
        self.assertNotIn('Dragonlords Bookstore', text)
        self.assertNotIn('Return to the Dragonlords', text)
        self.assertIn('path = "companions-choices"', text)
        self.assertFalse((self.root / 'static/bkstore.htm').exists())
        self.assertEqual((self.root / 'static/portrait.gif').read_bytes(), b'original-artwork')

    def test_source_files_are_unchanged_and_second_import_is_idempotent(self):
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.source.iterdir()}
        self.migrate()
        first = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.migrate()
        second = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(first, second)
        self.assertEqual(before, {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.source.iterdir()})

    def test_existing_links_and_legacy_redirects_use_the_new_route(self):
        self.migrate()
        self.assertIn('href="/companions-choices/"', (self.root / 'content/old.md').read_text())
        self.assertIn('/danc.htm /companions-choices/ 301', (self.root / 'static/_redirects').read_text())
        self.assertIn('](/companions-choices/)', (self.root / 'content/archive.md').read_text())


if __name__ == '__main__':
    unittest.main()
