"""Regression tests for the accessibility auditor."""
import json
from pathlib import Path
import tempfile
import unittest

from bs4 import BeautifulSoup

import audit_a11y

GOOD = (
    '<!doctype html><html lang="en"><head><title>T</title></head><body>'
    '<a class="skip" href="#main">Skip</a>'
    '<main id="main"><h1>Hi</h1>'
    '<img src="/a.gif" alt="a"><a href="/x/">Next</a>'
    '</main></body></html>'
)


def soup(html):
    return BeautifulSoup(html, 'lxml')


def rules(html):
    return {finding['rule'] for finding in audit_a11y.check_document(soup(html))}


class A11yTests(unittest.TestCase):
    def test_clean_document_has_no_findings(self):
        self.assertEqual(rules(GOOD), set())

    def test_missing_lang_is_flagged(self):
        self.assertIn('html-has-lang', rules(GOOD.replace(' lang="en"', '')))

    def test_image_without_alt_is_flagged(self):
        self.assertIn('image-alt', rules(GOOD.replace('<img src="/a.gif" alt="a">', '<img src="/a.gif">')))

    def test_image_with_empty_alt_is_allowed(self):
        self.assertNotIn('image-alt', rules(GOOD.replace('alt="a"', 'alt=""')))

    def test_link_named_only_by_decorative_image_is_flagged(self):
        html = GOOD.replace('<a href="/x/">Next</a>', '<a href="/x/"><img src="/b.gif" alt=""></a>')
        self.assertIn('link-name', rules(html))

    def test_link_named_by_image_alt_is_allowed(self):
        html = GOOD.replace('<a href="/x/">Next</a>', '<a href="/x/"><img src="/b.gif" alt="Next"></a>')
        self.assertNotIn('link-name', rules(html))

    def test_generic_link_text_is_flagged(self):
        self.assertIn('link-text', rules(GOOD.replace('>Next<', '>here<')))

    def test_heading_skip_is_flagged(self):
        self.assertIn('heading-order', rules(GOOD.replace('<h1>Hi</h1>', '<h1>Hi</h1><h3>Deep</h3>')))

    def test_two_h1_elements_are_flagged(self):
        self.assertIn('page-has-one-h1', rules(GOOD.replace('<h1>Hi</h1>', '<h1>Hi</h1><h1>Again</h1>')))

    def test_missing_skip_link_is_flagged(self):
        self.assertIn('skip-link', rules(GOOD.replace('<a class="skip" href="#main">Skip</a>', '')))

    def test_presentational_table_is_allowed(self):
        html = GOOD.replace('</main>', '<table role="presentation"><tr><td>a</td></tr></table></main>')
        self.assertNotIn('table-header', rules(html))

    def test_headerless_data_table_is_flagged(self):
        html = GOOD.replace('</main>', '<table><tr><td>a</td></tr></table></main>')
        self.assertIn('table-header', rules(html))

    def test_exceptions_acknowledge_findings(self):
        with tempfile.TemporaryDirectory() as work:
            root = Path(work)
            output = root / 'public'
            output.mkdir()
            (output / 'index.html').write_text(GOOD.replace('<img src="/a.gif" alt="a">', '<img src="/a.gif">'))
            exceptions = root / 'exceptions.json'
            exceptions.write_text(json.dumps([{'file': 'index.html', 'rule': 'image-alt', 'reason': 'sample'}]))
            report = audit_a11y.audit(output, exceptions=exceptions)
            self.assertEqual(report['summary']['unacknowledged'], 0)
            self.assertEqual(report['summary']['acknowledged'], 1)


if __name__ == '__main__':
    unittest.main()
