"""Regression tests for internal-link normalization and historical gap accounting."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import audit_links
from bs4 import BeautifulSoup
from link_repairs import repair_anchors


class LinkAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'public').mkdir()
        (self.root / 'data').mkdir()
        (self.root / 'config.toml').write_text('base_url = "https://example.netlify.app"\n[extra]\npdf_base_url = "https://files.queensown.org"\n')
        (self.root / 'data/pdf-manifest.json').write_text('[]')
        (self.root / 'public/index.html').write_text('<a class="brand" href="https://example.netlify.app">Home</a>')
        self.patcher = patch.object(audit_links, 'ROOT', self.root)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def run_audit(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return audit_links.audit()

    def test_encoded_filename_and_fragment_resolve_case_sensitively(self):
        (self.root / 'public/index.html').write_text('<a href="/With%20Space.htm#part%20one">Page</a>')
        (self.root / 'public/With Space.htm').write_text('<h2 id="part one">Section</h2>')
        records = self.run_audit()['targets']
        self.assertEqual(records[0]['status'], 'local_available')
        (self.root / 'public/index.html').write_text('<a href="/with%20space.htm#part%20one">Page</a>')
        with self.assertRaises(SystemExit):
            self.run_audit()

    def test_known_gap_stays_missing_and_new_referrer_fails(self):
        (self.root / 'public/index.html').write_text('<a href="/missing.htm">Missing</a>')
        (self.root / 'data/link-dispositions.json').write_text(json.dumps({'/missing.htm': {'referring_pages': ['index.html'], 'resolution': 'pending_recovery'}}))
        self.assertEqual(self.run_audit()['targets'][0]['status'], 'missing_file')
        (self.root / 'public/new.htm').write_text('<a href="/missing.htm">Missing</a>')
        with self.assertRaises(SystemExit):
            self.run_audit()

    def test_new_missing_anchor_fails(self):
        (self.root / 'public/index.html').write_text('<a href="#lost">Missing section</a>')
        with self.assertRaises(SystemExit):
            self.run_audit()

    def test_missing_image_notice_remains_in_inventory(self):
        (self.root / 'public/index.html').write_text('<img data-unavailable-target="https://queensown.org/lost.jpg" alt="Unavailable">')
        (self.root / 'data/link-dispositions.json').write_text(json.dumps({'/lost.jpg': {'referring_pages': ['index.html']}}))
        self.assertEqual(self.run_audit()['targets'][0]['target'], '/lost.jpg')

    def test_successful_html_response_does_not_count_as_available_pdf(self):
        url = 'https://files.queensown.org/Missing.pdf'
        (self.root / 'public/index.html').write_text(f'<a href="{url}">PDF</a>')
        (self.root / 'data/link-http-evidence.json').write_text(json.dumps({url: {'status': 200, 'content_type': 'text/html'}}))
        with self.assertRaises(SystemExit):
            self.run_audit()

    def test_original_name_only_anchor_gets_alias_without_losing_old_target(self):
        soup = BeautifulSoup('<a name="teacher"></a><h3>Teacher</h3>', 'lxml')
        repair_anchors(soup, 'qob.htm')
        repair_anchors(soup, 'qob.htm')
        self.assertIsNotNone(soup.find('a', attrs={'name': 'teacher'}))
        self.assertEqual(len(soup.find_all(id='teach')), 1)


if __name__ == '__main__':
    unittest.main()
