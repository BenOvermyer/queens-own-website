"""Check redirect coverage and reject published legacy routes or redirect chains."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from verify_routes import validate


class RedirectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for folder in ('data', 'content/world', 'public/bards-faq'):
            (self.root / folder).mkdir(parents=True)
        record = {'canonical_path': '/bards-faq/', 'content_file': 'world/bards-faq.md', 'aliases': ['/qofaqb.htm'], 'redirect_target': '/bards-faq/'}
        (self.root / 'data/site-routes.json').write_text(json.dumps({'qofaqb.htm': record}))
        (self.root / 'content/world/bards-faq.md').write_text('Bards FAQ')
        (self.root / 'public/index.html').write_text('<a class="brand" href="https://preview.netlify.app">Home</a>')
        (self.root / 'public/bards-faq/index.html').write_text('<h1>Bards FAQ</h1>')
        (self.root / 'public/_redirects').write_text('/qofaqb.htm /bards-faq/ 301!\n')
        (self.root / 'public/sitemap.xml').write_text('<urlset><url><loc>https://preview.netlify.app/bards-faq/</loc></url></urlset>')

    def run_check(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return validate(self.root)

    def test_forced_permanent_redirect_has_real_destination(self):
        self.assertEqual(self.run_check()['/qofaqb.htm'], '/bards-faq/')

    def test_missing_legacy_redirect_fails(self):
        (self.root / 'public/_redirects').write_text('')
        with self.assertRaises(SystemExit):
            self.run_check()

    def test_internal_legacy_link_fails_even_if_redirect_exists(self):
        (self.root / 'public/bards-faq/index.html').write_text('<a href="/qofaqb.htm">Old path</a>')
        with self.assertRaises(SystemExit):
            self.run_check()

    def test_redirect_chain_fails(self):
        with (self.root / 'public/_redirects').open('a') as f:
            f.write('/bards-faq/ / 301!\n')
        with self.assertRaises(SystemExit):
            self.run_check()


if __name__ == '__main__':
    unittest.main()
