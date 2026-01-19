import unittest

from plugins import rss


class RenderRssTests(unittest.TestCase):
    def test_render_rss_escapes_content(self):
        metadata = {
            "title": "My & Feed",
            "source_url": "https://example.com?x=1&y=2",
            "description": "5 > 3",
        }
        rows = [
            {
                "title": "AT&T",
                "url": "/tils/til/example~2E.md",
                "created_utc": "2024-01-01",
                "summary": "Cats < Dogs",
            }
        ]

        xml = rss.render_rss(metadata, rows)

        self.assertIn("<title>My &amp; Feed</title>", xml)
        self.assertIn("<link>https://example.com?x=1&amp;y=2</link>", xml)
        self.assertIn("<description>5 &gt; 3</description>", xml)
        self.assertIn("<title>AT&amp;T</title>", xml)
        self.assertIn("<description>Cats &lt; Dogs</description>", xml)
