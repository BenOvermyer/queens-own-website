"""Check that the public persona directories omit member names and emails."""
import json
import unittest

import sanitize_persona_directories as sanitize


class PersonaDirectoryRendererTests(unittest.TestCase):
    def test_entry_omits_player_and_email(self):
        entry = {
            'persona': 'Herald Aini Halfstock',
            'persona_url': None,
            'player': 'Bainin',
            'email': 'Irishanam21@gmail.com',
            'details': [
                {'type': 'date', 'text': '[March 2005](/newsletters/2005/march/)'},
                {'type': 'gifts', 'text': 'Mindspeech and Farsight'},
            ],
        }
        line = sanitize.render_entry(entry)
        self.assertEqual(
            line,
            'Herald Aini Halfstock ([March 2005](/newsletters/2005/march/)) '
            '(Mindspeech and Farsight)',
        )
        self.assertNotIn('Bainin', line)
        self.assertNotIn('Irishanam21@gmail.com', line)

    def test_entry_keeps_public_persona_link(self):
        entry = {
            'persona': 'Herald Raina Kelbrunn',
            'persona_url': 'http://www.glbtfantasy.com/',
            'player': 'Dabry',
            'email': None,
            'details': [{'type': 'date', 'text': 'October 1993'}],
        }
        self.assertEqual(
            sanitize.render_entry(entry),
            '[Herald Raina Kelbrunn](http://www.glbtfantasy.com/) (October 1993)',
        )

    def test_raw_details_preserve_original_spacing(self):
        entry = {
            'persona': 'Example',
            'persona_url': None,
            'player': None,
            'email': None,
            'details': [
                {'type': 'note', 'text': 'also Mercenary'},
                {'type': 'raw', 'text': ' Foresight) '},
                {'type': 'note', 'text': 'Also a Herald'},
            ],
        }
        self.assertEqual(
            sanitize.render_entry(entry),
            'Example (also Mercenary) Foresight) (Also a Herald)',
        )

    def test_public_text_removes_contact_links(self):
        text = 'please contact [me](mailto:Legend@malcor.com).'
        self.assertEqual(sanitize.sanitize_public_text(text), 'please contact the club.')
        text = '[Herald Someone](mailto:someone@example.com) and [a link](/x/)'
        self.assertEqual(
            sanitize.sanitize_public_text(text),
            'Herald Someone and [a link](/x/)',
        )

    def test_document_renders_sections_and_front_matter(self):
        document = {
            'schema_version': 1,
            'front_matter': {
                'title': 'Example',
                'path': 'example',
                'template': 'page.html',
                'extra': {'legacy_source': 'x.htm', 'historical': True},
            },
            'preamble': ['## Title'],
            'sections': [
                {
                    'title': 'Heralds',
                    'url': '/herald-handout/',
                    'notes': ['Note.'],
                    'entries': [
                        {
                            'persona': 'Herald One',
                            'persona_url': None,
                            'player': 'Private Name',
                            'email': 'private@example.com',
                            'details': [{'type': 'date', 'text': 'January 2000'}],
                        }
                    ],
                }
            ],
            'postamble': ['Footer.'],
        }
        rendered = sanitize.render_document(document)
        self.assertIn('title = "Example"', rendered)
        self.assertIn('legacy_source = "x.htm"', rendered)
        self.assertIn('historical = true', rendered)
        self.assertIn('## [Heralds](/herald-handout/)', rendered)
        self.assertIn('1. Herald One (January 2000)', rendered)
        self.assertNotIn('Private Name', rendered)
        self.assertNotIn('private@example.com', rendered)

    def test_checked_in_public_directories_match_json(self):
        for source, destination in sanitize.SOURCES.items():
            self.assertTrue(source.exists(), source)
            self.assertEqual(destination.read_text(), sanitize.render_source(source))

    def test_public_directories_have_no_contact_details(self):
        for _, destination in sanitize.SOURCES.items():
            text = destination.read_text()
            self.assertNotIn('mailto:', text)
            self.assertNotRegex(text, r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')

    def test_json_sources_keep_private_fields(self):
        for source, _ in sanitize.SOURCES.items():
            document = json.loads(source.read_text())
            entries = [entry for section in document['sections'] for entry in section['entries']]
            self.assertTrue(entries)
            for entry in entries:
                self.assertIn('persona', entry)
                self.assertIn('player', entry)
                self.assertIn('email', entry)
                self.assertIn('details', entry)


if __name__ == '__main__':
    unittest.main()
