#!/usr/bin/env python3

import unittest
import tempfile
from pathlib import Path
from noapp import Template

class TestTemplate(unittest.TestCase):
    def test_render_template(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            template_dir = Path(temp_dir)
            (template_dir / "layout.html").write_text(
                "<title>{{ title }}</title>"
                "<h1>{{ heading }}</h1>"
            )
            template = Template(
                directory=template_dir,
            )
            result = template.response(
                "layout.html",
                title="what is up...",
                heading="Hello, World!",
            )
            self.assertEqual(
                result,
                "<title>what is up...</title><h1>Hello, World!</h1>",
            )

if __name__ == "__main__":
    unittest.main()

