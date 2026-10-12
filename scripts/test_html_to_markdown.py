"""Tests for the HTML-to-Markdown content conversion."""
import unittest

from html_to_markdown import convert


def md(html):
    return convert(html).strip()


class ConvertTests(unittest.TestCase):
    def test_headings_and_paragraphs(self):
        self.assertEqual(md('<div><h2>Title</h2><p>Body text.</p></div>'),
                         '## Title\n\nBody text.')

    def test_bold_italic_and_soft_break(self):
        self.assertEqual(md('<p>a <b>bold</b> <i>it</i><br/>next</p>'),
                         'a **bold** *it* next')

    def test_unordered_and_ordered_lists(self):
        self.assertEqual(md('<ul><li>one</li><li>two</li></ul>'), '- one\n- two')
        self.assertEqual(md('<ol><li>one</li><li>two</li></ol>'), '1. one\n2. two')

    def test_loose_list_content_is_preserved(self):
        self.assertEqual(md('<ul><li>one</li>stray<b>two</b><li>three</li></ul>'),
                         '- one\n- stray**two**\n- three')

    def test_block_content_inside_paragraph_is_not_flattened(self):
        self.assertEqual(
            md('<p>intro<font color="black"><h2>Ren Faires</h2><p>Here.</p><h3>Florida</h3></font></p>'),
            'intro\n\n## Ren Faires\n\nHere.\n\n### Florida')

    def test_list_item_block_is_separated_from_following_text(self):
        self.assertEqual(
            md('<ol><li>Q1</li><li>Q2<img src="a.gif" alt=""/><h2>Heading</h2><p>Body</p></li></ol>'),
            '1. Q1\n2. Q2<img alt="" src="a.gif"/>\n\n  ## Heading\n\n  Body')

    def test_links_convert_to_markdown(self):
        self.assertEqual(md('<p><a href="/here/">Here</a></p>'), '[Here](/here/)')
        self.assertEqual(md('<p><a href="mailto:a@b.com">a@b.com</a></p>'),
                         '[a@b.com](mailto:a@b.com)')

    def test_named_anchor_stays_html(self):
        self.assertEqual(md('<h2 id="s">Section</h2>'), '<a id="s"></a>\n\n## Section')
        self.assertEqual(md('<p><a name="x"></a>text</p>'), '<a id="x"></a>text')

    def test_image_only_link_stays_html(self):
        self.assertEqual(md('<p><a href="/go/"><img src="a.gif" alt=""/></a></p>'),
                         '<a href="/go/"><img alt="" src="a.gif"/></a>')

    def test_image_stays_html(self):
        self.assertEqual(md('<p>see <img src="a.gif" alt="a"/> now</p>'),
                         'see <img alt="a" src="a.gif"/> now')

    def test_data_table_stays_html_without_presentational_wrappers(self):
        out = md('<table border="2"><tr><td><span class="fs-4">a</span></td><td>b</td></tr>'
                 '<tr><td>c</td><td>d</td></tr></table>')
        self.assertTrue(out.startswith('<table'))
        self.assertNotIn('span', out)
        self.assertIn('<td>a</td>', out)

    def test_layout_table_is_converted_to_markdown(self):
        out = md('<table><tr><td><h2>Title</h2><ul><li><a href="/x/">X</a></li></ul></td></tr></table>')
        self.assertTrue(out.startswith('## Title'))
        self.assertIn('- [X](/x/)', out)
        self.assertNotIn('<table', out)

    def test_pre_and_xmp_become_code_blocks(self):
        self.assertEqual(md('<xmp>&lt;a href="/"&gt;</xmp>'), '```\n<a href="/">\n```')

    def test_div_center_and_presentational_tags_are_dropped(self):
        self.assertEqual(md('<center><span class="c-red"><u>x</u></span></center>'), 'x')

    def test_grin_emoticon_is_literal_text(self):
        self.assertEqual(md('<p>grin <g> more</p>'), 'grin &lt;g>more')

    def test_underscores_and_brackets_need_no_escapes(self):
        self.assertEqual(md('<p>oww_scholarship [Ed. note]</p>'), 'oww_scholarship [Ed. note]')

    def test_literal_asterisk_uses_an_entity(self):
        self.assertEqual(md('<p>7.60* and $5</p>'), '7.60&#42; and $5')

    def test_conversion_introduces_no_backslash_escapes(self):
        self.assertNotIn('\\', md('<p>a_b [x] 7.60* <g> <br/>next</p>'))


if __name__ == '__main__':
    unittest.main()
