"""Tests for legacy HTML nesting normalization."""
import unittest

from bs4 import BeautifulSoup

from markup_normalize import normalize_soup


def normalized(html):
    soup = BeautifulSoup(html, 'lxml')
    return normalize_soup(soup)


class NormalizeHeadingTests(unittest.TestCase):
    def test_content_h1_becomes_h2(self):
        soup = normalized('<h1>Queen\'s Own</h1><h2>More</h2>')
        self.assertIsNone(soup.find('h1'))
        self.assertEqual(soup.find('h2').get_text(), "Queen's Own")

    def test_skipped_level_is_filled(self):
        soup = normalized('<h2>One</h2><h4>Two</h4>')
        self.assertEqual([h.name for h in soup.find_all(['h2', 'h3', 'h4'])], ['h2', 'h3'])

    def test_empty_heading_is_removed(self):
        soup = normalized('<h2>Keep</h2><h3></h3>')
        self.assertIsNone(soup.find('h3'))


    def test_grin_emoticon_becomes_text(self):
        soup = normalized('<p>grin <g> and more</p>')
        self.assertIsNone(soup.find('g'))
        self.assertIn('&lt;g&gt;', str(soup))


class NormalizeListTests(unittest.TestCase):
    def test_unclosed_pseudo_tag_does_not_nest_following_items(self):
        soup = normalized('<ol><li>one <g><li>two</li><li>three</li></ol>')
        items = soup.find('ol').find_all('li', recursive=False)
        self.assertEqual([item.get_text(' ', strip=True) for item in items],
                         ['one <g>', 'two', 'three'])

    def test_genuine_nested_list_is_left_alone(self):
        soup = normalized('<ul><li>outer<ul><li>inner</li></ul></li></ul>')
        outer = soup.find('ul')
        self.assertEqual(len(outer.find_all('li', recursive=False)), 1)
        self.assertIsNotNone(outer.find('li').find('ul'))


class NormalizeAnchorTests(unittest.TestCase):
    def test_named_anchor_wrapping_heading_moves_id_onto_heading(self):
        soup = normalized('<a id="s" name="s"><h2>Section</h2></a>')
        self.assertEqual(str(soup.find('h2')), '<h2 id="s">Section</h2>')
        self.assertEqual(soup.find('a'), None)

    def test_heading_link_keeps_the_link_inside_the_heading(self):
        soup = normalized('<a href="/reviews/#bwe"><h3>Beyond World\'s End</h3></a>')
        heading = soup.find(['h1', 'h2', 'h3', 'h4'])
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
