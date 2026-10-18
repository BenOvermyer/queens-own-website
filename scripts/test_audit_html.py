"""Regression tests for the legacy-HTML audit and its content-preservation baseline."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import audit_html
from audit_html import audit, audit_file, read_body

FRONT = '+++\ntitle = "T"\n[extra]\nlegacy_source = "sample.htm"\n+++\n'


class HtmlAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'content').mkdir()
        (self.root / 'data').mkdir()
        self.patcher = patch.object(audit_html, 'ROOT', self.root)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def write(self, relative, body, front=FRONT):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(front + body)
        return path

    def findings(self, body):
        path = self.write('content/sample.md', body)
        result = audit_file(path, path.read_text(), self.root)
        return {finding['rule']: finding for finding in result['findings']}, result

    def test_unterminated_attribute_is_a_structural_error(self):
        found, _ = self.findings('<a href="mailto:x@y.com>Site</a>. Email <a href="/next/">next</a>')
        self.assertEqual(found['malformed_attribute']['severity'], 'error')

    def test_balanced_markup_has_no_structural_errors(self):
        found, _ = self.findings('<div><p><a href="/">x</a></p><table><tr><th>h</th></tr></table></div>')
        self.assertNotIn('mismatched_end_tag', found)
        self.assertNotIn('unclosed_element', found)

    def test_anchor_wrapping_a_heading_is_reported(self):
        found, _ = self.findings('<a name="s"><h2>Section</h2></a>')
        self.assertIn('block_in_anchor', found)

    def test_block_that_implicitly_closes_paragraph_is_not_flagged(self):
        found, _ = self.findings('<p>text</p><p>more<h2>Next</h2></p>')
        self.assertNotIn('block_in_paragraph', found)

    def test_block_that_cannot_close_a_paragraph_is_flagged(self):
        found, _ = self.findings('<p>text<center>kept</center></p>')
        self.assertIn('block_in_paragraph', found)

    def test_unknown_element_is_reported(self):
        found, _ = self.findings('<p><g> and more</p>')
        self.assertIn('unknown_element', found)

    def test_obsolete_and_presentational_markup_is_reported(self):
        found, _ = self.findings('<font color="red"><center>x</center></font>')
        self.assertIn('obsolete_element', found)
        self.assertIn('presentational_attribute', found)

    def test_migration_image_placeholder_is_not_a_missing_source(self):
        found, _ = self.findings('<img alt="unavailable" data-unavailable-target="https://e/x.jpg"/>')
        self.assertNotIn('image_missing_src', found)

    def test_image_without_alt_is_reported(self):
        found, _ = self.findings('<img src="/a.gif"/>')
        self.assertIn('image_missing_alt', found)

    def test_duplicate_anchor_id_is_reported(self):
        found, _ = self.findings('<h2 id="special">A</h2><h3 id="special">B</h3>')
        self.assertIn('duplicate_id', found)

    def test_duplicate_ids_helper_catches_template_collisions(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup('<main id="main"><a id="main"></a></main>', 'lxml')
        self.assertEqual(audit_html.duplicate_ids(soup), ['main'])
        self.assertEqual(audit_html.duplicate_ids(BeautifulSoup('<a id="a"></a><b id="b"></b>', 'lxml')), [])

    def test_headerless_table_is_flagged_as_a_candidate(self):
        found, _ = self.findings('<table><tr><td>a</td><td>b</td></tr></table>')
        self.assertIn('table_without_header', found)

    def test_presentational_layout_table_is_not_flagged(self):
        found, _ = self.findings('<table role="presentation"><tr><td>a</td><td>b</td></tr></table>')
        self.assertNotIn('table_without_header', found)

    def test_images_without_dimensions_flags_only_local_unsized_images(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(
            '<img src="/a.jpg"><img src="/b.jpg" width="1" height="1">'
            '<img alt="placeholder"><img src="https://e/x.png">',
            'lxml')
        self.assertEqual(audit_html.images_without_dimensions(soup), ['/a.jpg'])

    def test_image_dimensions_are_not_treated_as_presentational(self):
        found, _ = self.findings('<img src="/a.gif" width="10" height="10" alt="a"/>')
        self.assertNotIn('presentational_attribute', found)

    def test_layout_dimensions_are_still_presentational(self):
        found, _ = self.findings('<table width="100"><tr><td>x</td></tr></table>')
        self.assertIn('presentational_attribute', found)

    def test_heading_semantics_are_reported(self):
        found, _ = self.findings('<h1>A</h1><h1>B</h1><h3>C</h3>')
        self.assertIn('multiple_h1', found)
        self.assertIn('heading_level_skipped', found)

    def test_baseline_records_structure_and_notices_text_changes(self):
        _, first = self.findings('<p>Hello <a href="/">world</a></p><img src="/i.gif" alt="i"/>')
        _, second = self.findings('<p>Goodbye <a href="/">world</a></p><img src="/i.gif" alt="i"/>')
        self.assertEqual(first['baseline']['links'], 1)
        self.assertEqual(first['baseline']['images'], 1)
        self.assertNotEqual(first['baseline']['visible_text_sha256'], second['baseline']['visible_text_sha256'])

    def test_exception_acknowledges_a_finding_and_clears_the_error(self):
        self.write('content/sample.md', '<h2 id="s">A</h2><h3 id="s">B</h3>')
        (self.root / 'data/html-exceptions.json').write_text(json.dumps([{'file': 'content/sample.md', 'rule': 'duplicate_id', 'reason': 'sample'}]))
        report = audit()
        self.assertEqual(report['summary']['acknowledged_findings'], 1)
        self.assertEqual(report['summary']['unresolved_errors'], 0)

    def test_audit_writes_the_report_and_counts_files(self):
        self.write('content/sample.md', '<p>text</p>')
        report = audit()
        self.assertEqual(report['summary']['files_scanned'], 1)
        written = json.loads((self.root / 'data/html-audit-report.json').read_text())
        self.assertEqual(written['summary']['files_scanned'], 1)

    def test_documents_without_html_are_skipped(self):
        path = self.write('content/plain.md', 'Just [Markdown](/here/).')
        self.assertIsNone(audit_file(path, path.read_text(), self.root))

    def test_read_body_splits_front_matter(self):
        meta, body = read_body(FRONT + '<p>hi</p>')
        self.assertEqual(meta['extra']['legacy_source'], 'sample.htm')
        self.assertEqual(body.strip(), '<p>hi</p>')


if __name__ == '__main__':
    unittest.main()
