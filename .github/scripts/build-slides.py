#!/usr/bin/env python3
"""Build the participant presentation decks into the MkDocs staging directory.

Sources use ordinary Markdown, separated by a standalone ``---`` outside code
fences. All URLs are resolved from the source file before conversion to Pages
URLs; the finished decks therefore work at both / and a project Pages prefix.
"""

from __future__ import annotations

import argparse
import html
import posixpath
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path
from string import Template
from urllib.parse import quote, unquote, urlsplit, urlunsplit

import markdown
from mkdocs.structure.files import File

ROOT = Path(__file__).resolve().parents[2]
DECKS = {
    "prep": ("事前準備", "PREPARATION", "00"),
    "part1": ("前半", "FIRST SESSION", "01"),
    "part2": ("後半", "SECOND SESSION", "02"),
}
DECK_SOURCES = {f"slides/{name}.md": name for name in DECKS}
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
INLINE_LINK = re.compile(r"(?P<prefix>!?\[[^\]\n]*\]\(\s*)(?P<url><[^>\n]+>|[^\s)]+)")
REFERENCE_LINK = re.compile(r"(?m)^(?P<prefix> {0,3}\[[^\]\n]+\]:\s*)(?P<url><[^>\n]+>|\S+)")
FOOTER = re.compile(r'\s*<p>(<a\b[^>]*>教材で手順を見る</a>)</p>\s*$', re.DOTALL)


def fenced_lines(text):
    """Yield (line, inside_fence), including opening and closing fence lines."""
    fence_char = None
    fence_length = 0
    for line in text.splitlines(keepends=True):
        match = FENCE.match(line.rstrip("\r\n"))
        if fence_char is not None:
            yield line, True
            if (match and match[1][0] == fence_char
                    and len(match[1]) >= fence_length and not match[2].strip()):
                fence_char = None
        elif match and (match[1][0] != "`" or "`" not in match[2]):
            fence_char, fence_length = match[1][0], len(match[1])
            yield line, True
        else:
            yield line, False


def split_slides(text):
    """Split only standalone separators, leaving fenced examples intact."""
    slides, current = [], []
    for line, fenced in fenced_lines(text):
        if not fenced and line.strip() == "---":
            body = "".join(current).strip()
            if not body:
                raise ValueError("空のスライドがあります。冒頭・末尾や連続した --- を確認してください")
            slides.append(body)
            current = []
        else:
            current.append(line)
    body = "".join(current).strip()
    if not body:
        raise ValueError("最後のスライドが空です")
    slides.append(body)
    return slides


def source_target(url, source):
    """Return a repository-relative target for a local URL, or None."""
    parts = urlsplit(url)
    if parts.scheme or parts.netloc or not parts.path or parts.path.startswith("/"):
        return None
    target = posixpath.normpath(posixpath.join(posixpath.dirname(source), unquote(parts.path)))
    if target == ".." or target.startswith("../"):
        raise ValueError(f"リポジトリ外への相対リンクです: {source}: {url}")
    return target


def pages_url(url, source, output_dir, root=ROOT):
    """Resolve a source URL, then make its MkDocs destination relative to a deck."""
    target = source_target(url, source)
    if target is None:
        return url
    parts = urlsplit(url)
    if parts.path.endswith("/") and (Path(root) / target / "README.md").is_file():
        target = posixpath.join(target, "README.md")
    if target.endswith(".md"):
        destination = unquote(File(target, str(root), str(root), use_directory_urls=True).url)
    else:
        destination = target + ("/" if parts.path.endswith("/") else "")
    relative = posixpath.relpath(destination, output_dir)
    if destination.endswith("/"):
        relative += "/"
    return urlunsplit(("", "", quote(relative, safe="/:@"), parts.query, parts.fragment))


def rewrite_deck_links(text, source):
    """Point MkDocs source links at generated HTML without changing GitHub sources."""
    def replace(match):
        original = match["url"]
        angle = original.startswith("<") and original.endswith(">")
        url = original[1:-1] if angle else original
        target = source_target(url, source)
        if target not in DECK_SOURCES:
            return match[0]
        parts = urlsplit(url)
        destination = f"slides/{DECK_SOURCES[target]}/index.html"
        relative = posixpath.relpath(destination, posixpath.dirname(source) or ".")
        replacement = urlunsplit(("", "", relative, parts.query, parts.fragment))
        return match["prefix"] + (f"<{replacement}>" if angle else replacement)

    return "".join(
        line if fenced else REFERENCE_LINK.sub(replace, INLINE_LINK.sub(replace, line))
        for line, fenced in fenced_lines(text)
    )


class LinkRewriter(HTMLParser):
    """Rewrite parsed HTML attributes, without modifying code-block contents."""

    def __init__(self, source, output_dir, root, stage):
        super().__init__(convert_charrefs=False)
        self.source, self.output_dir = source, output_dir
        self.root, self.stage = root, stage
        self.output = []

    def rewrite(self, url):
        target = source_target(url, self.source)
        if target is not None:
            path = self.root / target
            if not path.exists():
                raise ValueError(f"リンク先がありません: {self.source}: {url}")
            if target not in DECK_SOURCES and not (self.stage / target).exists():
                raise ValueError(f"公開対象外へのリンクです: {self.source}: {url}")
        return pages_url(url, self.source, self.output_dir, self.root)

    def tag(self, tag, attrs, closing=""):
        attributes = []
        for name, value in attrs:
            if value is not None and name in {"href", "src"}:
                value = self.rewrite(value)
            attributes.append(name if value is None else f'{name}="{html.escape(value, quote=True)}"')
        self.output.append("<" + tag + (" " + " ".join(attributes) if attributes else "") + closing + ">")

    def handle_starttag(self, tag, attrs):
        self.tag(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self.tag(tag, attrs, " /")

    def handle_endtag(self, tag):
        self.output.append(f"</{tag}>")

    def handle_data(self, data):
        self.output.append(data)

    def handle_entityref(self, name):
        self.output.append(f"&{name};")

    def handle_charref(self, name):
        self.output.append(f"&#{name};")

    def handle_comment(self, data):
        self.output.append(f"<!--{data}-->")


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def heading_text(fragment):
    parser = PlainText()
    parser.feed(fragment)
    return "".join(parser.parts)


def build_deck(name, stage, root=ROOT):
    source = f"slides/{name}.md"
    source_path = root / source
    chunks = split_slides(source_path.read_text(encoding="utf-8"))
    sections, options = [], []
    deck_title = ""
    label, eyebrow, chapter = DECKS[name]
    for index, chunk in enumerate(chunks, start=1):
        rendered = markdown.markdown(chunk, extensions=[
            "fenced_code", "tables", "sane_lists", "attr_list", "pymdownx.tasklist",
        ])
        level = 1 if index == 1 else 2
        heading = re.match(fr"<h{level}>(.*?)</h{level}>", rendered, re.DOTALL)
        if not heading:
            raise ValueError(f"{source}: スライド {index} は H{level} 見出しで始めてください")
        title = heading_text(heading[1])
        if index == 1:
            deck_title = title
        rendered = rendered.replace(f"<h{level}>", f'<h{level} id="slide-{index}-title">', 1)
        rewriter = LinkRewriter(source, f"slides/{name}", root, stage)
        rewriter.feed(rendered)
        rendered = "".join(rewriter.output)
        footer_match = FOOTER.search(rendered)
        footer = footer_match[1] if footer_match else ""
        if footer_match:
            rendered = rendered[:footer_match.start()]
        classes = "slide slide--cover" if index == 1 else "slide"
        sections.append(
            f'<section class="{classes}" id="slide-{index}" tabindex="-1" '
            f'role="group" aria-roledescription="スライド" aria-labelledby="slide-{index}-title">\n'
            f'  <div class="slide-kicker"><span>{eyebrow} / {chapter}</span>'
            f'<a href="#slide-{index}" data-slide-link="{index}" aria-label="スライド {index} を開く">'
            f'{index:02d} <span aria-hidden="true">/ {len(chunks):02d}</span></a></div>\n'
            f'  <div class="slide-content">{rendered}</div>\n'
            f'  <footer class="slide-footer">{footer}</footer>\n'
            '</section>'
        )
        options.append(f'<option value="{index}">{index:02d}　{html.escape(title)}</option>')
    template = Template((root / "slide-theme" / "deck.html").read_text(encoding="utf-8"))
    page = template.substitute(
        title=html.escape(deck_title), label=html.escape(label),
        sections="\n".join(sections), options="\n".join(options), total=len(chunks),
    )
    destination = stage / "slides" / name / "index.html"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(page, encoding="utf-8")
    return len(chunks)


def build_slides(stage, root=ROOT):
    stage, root = Path(stage), Path(root)
    assets = stage / "slides" / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    for name in ("slides.css", "slides.js"):
        shutil.copy2(root / "slide-theme" / name, assets / name)
    for name in DECKS:
        count = build_deck(name, stage, root)
        print(f"  slides/{name}/index.html: {count} 枚")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path, default=ROOT / ".site-src")
    args = parser.parse_args()
    build_slides(args.stage)
