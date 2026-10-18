"""Tests for the responsive-image pipeline."""
import tempfile
from pathlib import Path
import unittest

from PIL import Image

import optimize_images


class OptimizeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name) / 'public'
        (self.out / 'images').mkdir(parents=True)
        Image.new('RGB', (600, 400), (10, 20, 30)).save(self.out / 'images/big.png')
        Image.new('RGB', (40, 40), (1, 2, 3)).save(self.out / 'images/small.png')

    def test_variant_widths_include_intrinsic_and_smaller_standards(self):
        self.assertEqual(optimize_images.variant_widths(600), [480, 600])
        self.assertEqual(optimize_images.variant_widths(300), [300])
        self.assertEqual(optimize_images.variant_widths(2000), [480, 768, 1200, 2000])

    def test_local_path_resolves_same_site_urls_only(self):
        self.assertIsNotNone(optimize_images.local_path('/images/big.png', self.out))
        self.assertIsNone(optimize_images.local_path('https://example.com/x.png', self.out))
        self.assertIsNone(optimize_images.local_path('data:image/png;base64,AAAA', self.out))

    def test_large_image_is_wrapped_in_picture_with_widths(self):
        tag = '<img src="/images/big.png" width="600" height="400" alt="big">'
        wrapped = optimize_images.rewrite_tag(tag, self.out, {})
        self.assertTrue(wrapped.startswith('<picture><source type="image/webp"'))
        self.assertIn('480w', wrapped)
        self.assertIn('600w', wrapped)
        self.assertIn(tag, wrapped)
        self.assertTrue((self.out / 'images/responsive/images_big.png.480.webp').is_file())

    def test_small_image_is_left_alone(self):
        tag = '<img src="/images/small.png" width="40" height="40" alt="">'
        self.assertEqual(optimize_images.rewrite_tag(tag, self.out, {}), tag)

    def test_external_image_is_left_alone(self):
        tag = '<img src="https://example.com/x.png" alt="">'
        self.assertEqual(optimize_images.rewrite_tag(tag, self.out, {}), tag)

    def test_code_and_pre_blocks_are_not_rewritten(self):
        tag = '<img src="/images/big.png" width="600" height="400" alt="">'
        html = f'<pre>{tag}</pre><p>{tag}</p>'
        out = optimize_images.rewrite_page(html, self.out, {})
        self.assertEqual(out.count('<picture>'), 1)
        self.assertIn(f'<pre>{tag}</pre>', out)

    def test_validate_reports_missing_srcset_targets(self):
        (self.out / 'index.html').write_text('<source srcset="/images/responsive/nope.webp 480w">')
        self.assertEqual(optimize_images.validate(self.out), ['index.html: /images/responsive/nope.webp'])

    def test_validate_accepts_present_targets(self):
        (self.out / 'images/responsive').mkdir()
        (self.out / 'images/responsive/yes.webp').write_bytes(b'x')
        (self.out / 'index.html').write_text('<source srcset="/images/responsive/yes.webp 480w">')
        self.assertEqual(optimize_images.validate(self.out), [])


if __name__ == '__main__':
    unittest.main()
