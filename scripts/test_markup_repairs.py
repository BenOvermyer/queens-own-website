"""Tests for the raw legacy-markup repair applied before parsing."""
import unittest

from markup_repairs import repair_markup


class MarkupRepairTests(unittest.TestCase):
    def test_double_quote_closed_with_single(self):
        self.assertEqual(repair_markup(b'<a href=\'http://x/page.htm\">x</a>'),
                         b'<a href="http://x/page.htm">x</a>')

    def test_double_quote_never_closed(self):
        self.assertEqual(repair_markup(b'<a href="mailto:a@b.com>a@b.com</a>'),
                         b'<a href="mailto:a@b.com">a@b.com</a>')

    def test_single_quote_closed_with_double(self):
        self.assertEqual(repair_markup(b"<img src='a.gif\">"),
                         b'<img src="a.gif">')

    def test_duplicated_mailto_fragment(self):
        self.assertEqual(repair_markup(b'<a href="mailto:<a href="a@b.com">a@b.com</a>'),
                         b'<a href="mailto:a@b.com">a@b.com</a>')

    def test_mailto_that_swallowed_its_closing_tag(self):
        self.assertEqual(repair_markup(b'<a href="mailto:a@b.com</a>.'),
                         b'<a href="mailto:a@b.com">a@b.com</a>.')

    def test_targeted_display_name_mailto(self):
        broken = b'<a href="mailto:Sacree Noir <sn.keeper@yahoo.com>">Sacree Noir <sn.keeper@yahoo.com></a>'
        self.assertEqual(repair_markup(broken),
                         b'<a href="mailto:sn.keeper@yahoo.com">Sacree Noir &lt;sn.keeper@yahoo.com&gt;</a>')

    def test_space_after_opening_angle_bracket(self):
        self.assertEqual(repair_markup(b'Website: < a href="page.htm">x</a>'),
                         b'Website: <a href="page.htm">x</a>')

    def test_well_formed_markup_is_unchanged(self):
        markup = b'<a href="page.htm" title="a &gt; b">x</a><img src=\'a.gif\' alt="">'
        self.assertEqual(repair_markup(markup), markup)

    def test_repair_is_idempotent(self):
        broken = b'<a href="mailto:a@b.com>a@b.com</a>'
        once = repair_markup(broken)
        self.assertEqual(repair_markup(once), once)


if __name__ == '__main__':
    unittest.main()
