"""Tests for moving presentational markup into shared classes."""
import unittest

from bs4 import BeautifulSoup

from markup_destyle import destyle_soup


def destyled(html):
    soup = BeautifulSoup(html, 'lxml')
    return destyle_soup(soup)


class DestyleTests(unittest.TestCase):
    def test_font_becomes_span_with_classes(self):
        soup = destyled('<font face="Comic Sans MS" size="4" color="red">x</font>')
        span = soup.find('span')
        self.assertEqual(sorted(span.get('class')), ['c-red', 'ff-comic-sans', 'fs-4'])
        self.assertIsNone(soup.find('font'))

    def test_center_becomes_centered_div(self):
        soup = destyled('<center><h2>Title</h2></center>')
        self.assertEqual(soup.find('div')['class'], ['center'])
        self.assertIsNone(soup.find('center'))

    def test_table_attributes_become_classes(self):
        soup = destyled('<table border="2" cellpadding="2" cellspacing="2"></table>')
        classes = soup.find('table')['class']
        self.assertEqual(sorted(classes), ['border-2', 'cellpadding-2', 'cellspacing-2'])

    def test_zero_border_is_dropped(self):
        soup = destyled('<img border="0" src="a.gif"/>')
        self.assertIsNone(soup.find('img').get('class'))
        self.assertFalse(soup.find('img').has_attr('border'))

    def test_alignment_becomes_classes(self):
        soup = destyled('<td align="center" valign="middle">x</td>')
        self.assertEqual(sorted(soup.find('td')['class']), ['align-center', 'valign-middle'])

    def test_image_alignment_becomes_float(self):
        soup = destyled('<img align="right" src="a.gif"/>')
        self.assertIn('float-right', soup.find('img')['class'])

    def test_dimensions_become_inline_styles(self):
        soup = destyled('<td width="33%" height="43">x</td>')
        style = soup.find('td')['style']
        self.assertIn('width:33%', style)
        self.assertIn('height:43px', style)

    def test_bgcolor_becomes_inline_style(self):
        soup = destyled('<table bgcolor="gray"></table>')
        self.assertIn('background-color:gray', soup.find('table')['style'])

    def test_valid_and_code_sample_elements_are_untouched(self):
        soup = destyled('<p><u>underlined</u></p><xmp>&lt;a href="/"&gt;</xmp>')
        self.assertIsNotNone(soup.find('u'))
        self.assertIsNotNone(soup.find('xmp'))


if __name__ == '__main__':
    unittest.main()
