"""Regression tests for source boundaries and links in the Pages presentation build."""

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
SPEC = importlib.util.spec_from_file_location("build_slides", SCRIPT_DIR / "build-slides.py")
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class SlideSplittingTests(unittest.TestCase):
    def test_both_fence_styles_keep_separator_and_shorter_fences_inside_code(self):
        source = "# Cover\n\n---\n\n## Example\n\n````markdown\n```yaml\n---\n```\n````\n\n~~~text\n---\n~~~\n\n---\n\n## End\n"
        slides = builder.split_slides(source)
        self.assertEqual(len(slides), 3)
        self.assertIn("```yaml\n---\n```", slides[1])
        self.assertIn("~~~text\n---\n~~~", slides[1])

    def test_crlf_and_indented_fences(self):
        slides = builder.split_slides("# Cover\r\n---\r\n## Code\r\n   ```\r\n---\r\n   ```\r\n")
        self.assertEqual(len(slides), 2)
        self.assertIn("---", slides[1])

    def test_fence_with_text_does_not_close_the_fence(self):
        source = "# Cover\n\n```text\n``` still inside\n---\n```\n\n---\n\n## Next"
        slides = builder.split_slides(source)
        self.assertEqual(len(slides), 2)
        self.assertIn("``` still inside\n---", slides[0])

    def test_empty_slides_and_yaml_front_matter_fail_instead_of_disappearing(self):
        for source in ("", "---\n# Cover", "# Cover\n---", "# Cover\n---\n---\n## End", "---\ntitle: Deck\n---\n# Cover"):
            with self.subTest(source=source), self.assertRaises(ValueError):
                builder.split_slides(source)


class LinkTests(unittest.TestCase):
    def test_source_paths_follow_mkdocs_directory_urls(self):
        cases = {
            "../README.md": "../../",
            "../docs/01-part1.md#最初の一歩": "../../docs/01-part1/#最初の一歩",
            "../skills/tsumete/SKILL.md": "../../skills/tsumete/SKILL/",
            "../starters/a-pomodoro-timer/README.md?mode=read#start": "../../starters/a-pomodoro-timer/?mode=read#start",
            "part2.md#slide-3": "../part2/#slide-3",
            "README.md": "../",
            "../site-theme/logo.png": "../../site-theme/logo.png",
            "../docs/with%20spaces.md": "../../docs/with%20spaces/",
            "../docs/日本語.md": "../../docs/%E6%97%A5%E6%9C%AC%E8%AA%9E/",
        }
        for source, expected in cases.items():
            with self.subTest(source=source):
                self.assertEqual(builder.pages_url(source, "slides/part1.md", "slides/part1"), expected)

    def test_directory_readme_and_external_urls(self):
        self.assertEqual(builder.pages_url("../starters/", "slides/part1.md", "slides/part1"), "../../starters/")
        for url in ("#slide-4", "https://example.com/readme.md?q=1#top", "//example.com/image.png", "mailto:test@example.com", "/root/path"):
            self.assertEqual(builder.pages_url(url, "slides/part1.md", "slides/part1"), url)
        with self.assertRaises(ValueError):
            builder.pages_url("../../private.md", "slides/part1.md", "slides/part1")

    def test_staged_landing_links_and_references_point_to_html(self):
        source = '[前半](part1.md#slide-2)\n[後半](<part2.md> "解説")\n[準備][prep]\n[prep]: prep.md\n[教材](../docs/01-part1.md)\n'
        expected = '[前半](part1/index.html#slide-2)\n[後半](<part2/index.html> "解説")\n[準備][prep]\n[prep]: prep/index.html\n[教材](../docs/01-part1.md)\n'
        self.assertEqual(builder.rewrite_deck_links(source, "slides/README.md"), expected)
        self.assertEqual(builder.rewrite_deck_links("[前半](slides/part1.md)", "README.md"), "[前半](slides/part1/index.html)")

    def test_staging_does_not_rewrite_links_inside_fenced_examples(self):
        source = "```markdown\n[前半](part1.md)\n```\n[前半](part1.md)\n"
        expected = "```markdown\n[前半](part1.md)\n```\n[前半](part1/index.html)\n"
        self.assertEqual(builder.rewrite_deck_links(source, "slides/README.md"), expected)


class DeckBuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.stage = self.root / ".site-src"
        (self.root / "slides").mkdir()
        (self.root / "docs").mkdir()
        (self.stage / "docs").mkdir(parents=True)
        (self.root / "docs/01-part1.md").write_text("# 教材", encoding="utf-8")
        (self.stage / "docs/01-part1.md").write_text("# 教材", encoding="utf-8")
        shutil.copytree(ROOT / "slide-theme", self.root / "slide-theme")

    def source(self, text):
        (self.root / "slides/part1.md").write_text(text, encoding="utf-8")

    def test_generated_deck_has_stable_ids_and_footer_and_keeps_code_literal(self):
        self.source('# A <em>deck</em>\n\n[教材で手順を見る](../docs/01-part1.md#手順)\n\n---\n\n## Example\n\n```html\n<a href="../docs/01-part1.md">code only</a>\n```\n')
        self.assertEqual(builder.build_deck("part1", self.stage, self.root), 2)
        output = (self.stage / "slides/part1/index.html").read_text(encoding="utf-8")
        self.assertIn('id="slide-1"', output)
        self.assertIn('id="slide-2"', output)
        self.assertIn('<title>A deck |', output)
        self.assertIn('<footer class="slide-footer"><a href="../../docs/01-part1/#手順">', output)
        self.assertIn('&lt;a href=&quot;../docs/01-part1.md&quot;&gt;code only&lt;/a&gt;', output)

    def test_wrong_heading_and_missing_or_private_targets_fail_build(self):
        (self.root / "instructor").mkdir()
        (self.root / "instructor/guide.md").write_text("Private", encoding="utf-8")
        for source in (
            "## Cover needs H1",
            "# Cover\n---\n# Second needs H2",
            "# Cover\n[missing](../docs/missing.md)",
            "# Cover\n[private](../instructor/guide.md)",
        ):
            with self.subTest(source=source):
                self.source(source)
                with self.assertRaises(ValueError):
                    builder.build_deck("part1", self.stage, self.root)


if __name__ == "__main__":
    unittest.main()
