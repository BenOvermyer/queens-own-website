"""Tests for legacy HTML nesting normalization."""
import unittest

from bs4 import BeautifulSoup

from markup_normalize import normalize_soup


def normalized(html):
    soup = BeautifulSoup(html, 'lxml')
    return normalize_soup(soup)


class NormalizeAnchorTests(unittest.TestCase):
    def test_named_anchor_wrapping_heading_moves_id_onto_heading(self):
        soup = normalized('<a id="s" name="s"><h2>Section</h2></a>')
        self.assertEqual(str(soup.find('h2')), '<h2 id="s">Section</h2>')
        self.assertEqual(soup.find('a'), None)

    def test_heading_link_keeps_the_link_inside_the_heading(self):
        soup = normalized('<a href="/reviews/#bwe"><h3>Beyond World\'s End</h3></a>')
        heading = soup.find('h3')
        self.assertEqual(heading.get_text(), "Beyond World's End")
        self.assertEqual(heading.find('a')['href'], '/reviews/#bwe')

    def test_stray_anchor_releases_block_content(self):
        soup = normalized('<a href="http://e/">intro<p>one</p><h2>two</h2></a>')
        anchor = soup.find('a')
        self.assertEqual(anchor.get_text(strip=True), 'intro')
        self.assertIsNone(anchor.find(['p', 'h2']))
        self.assertIsNotNone(soup.find('p'))
        self.assertIsNotNone(soup.find('h2'))

    def test_nested_block_is_released_even_inside_an_inline_wrapper(self):
        soup = normalized('<a href="http://e/">x<font><p>one</p></font></a>')
        self.assertIsNone(soup.find('a').find('p'))
        self.assertIsNotNone(soup.find('p'))

    def test_empty_anchor_is_removed(self):
        soup = normalized('<div><a></a><p>keep</p></div>')
        self.assertIsNone(soup.find('a'))
        self.assertIsNotNone(soup.find('p'))

    def test_targetless_anchor_keeps_its_text(self):
        soup = normalized('<p><a>orphan</a></p>')
        self.assertIsNone(soup.find('a'))
        self.assertEqual(soup.get_text(strip=True), 'orphan')

    def test_normalization_is_idempotent(self):
        html = '<a href="http://e/">intro<p>one</p></a><a id="s"><h2>Section</h2></a>'
        once = BeautifulSoup(html, 'lxml')
        normalize_soup(once)
        twice = BeautifulSoup(str(once), 'lxml')
        normalize_soup(twice)
        self.assertEqual(str(once.body), str(twice.body))


if __name__ == '__main__':
    unittest.main()
