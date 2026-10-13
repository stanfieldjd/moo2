#!/usr/bin/env python3
"""Static structural checks for the public-source Game Lab site shell.

No original game data, authentication credentials, installed browser,
network access, or privately converted assets are required.
"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1] / "web/site"

PAGES = ("index.html", "games/space-strategy/index.html")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.references = []
        self.headings = []
        self.title = False
        self.in_title = False
        self.body_views = []
        self.bad_links = []
    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "id" in values:
            assert values["id"] not in self.ids, "duplicate id"
            self.ids.add(values["id"])
        if tag in ("a", "link", "script"):
            name = {"a":"href","link":"href","script":"src"}[tag]
            if values.get(name):
                self.references.append((tag, values[name]))
        if tag=="title":
            self.in_title = True
        if tag=="body":
            self.body_views.append(values.get("data-view"))
        if tag in ("h1","h2","h3"):
            self.headings.append(tag)
        if tag=="a" and values.get("aria-disabled") == "true":
            self.bad_links.append("disabled anchor has href")
    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
            self.title = True


def main():
    assert (ROOT / "site.css").is_file()
    assert (ROOT / "site.mjs").is_file()
    assert (ROOT / "site-nav.mjs").is_file()
    assert (ROOT / "tests/site-nav.test.mjs").is_file()
    for name in PAGES:
        page_path = ROOT / name
        body = page_path.read_text(encoding="utf8")
        lower = body.lower()
        assert "<!doctype html>" in lower, name
        assert "game lab" in lower, name
        # Original protected game branding belongs only in private research.
        for forbidden in ("master of orion", "orion ii", "orion2web", "galactic turn lab"):
            assert forbidden not in lower, (name, forbidden)
        assert "in development" in lower, name
        assert "<h1" in lower and "<main" in lower, name
        assert "controllerStatus" in body, name
        assert "play now" not in lower and ">play<" not in lower, name
        parser=Page()
        parser.feed(body)
        parser.close()
        assert parser.title and parser.headings.count("h1")==1, name
        assert not parser.bad_links, (name, parser.bad_links)
        assert parser.body_views==(["home"] if name=="index.html" else ["game"])
        for tag, ref in parser.references:
            parts=urlsplit(ref)
            assert parts.scheme == "" and not parts.netloc, (name, ref)
            # A hash-only link must resolve within the current page.
            file_path = (page_path.parent / parts.path).resolve() if parts.path else page_path
            assert file_path.is_relative_to(ROOT.resolve()), (name, ref)
            if file_path.is_dir():
                file_path /= "index.html"
            assert file_path.is_file(), (name, ref)
            if parts.fragment:
                target = Page()
                target.feed(file_path.read_text(encoding="utf8"))
                assert parts.fragment in target.ids, (name, ref)
        print("SITE_STRUCTURE_PASS", name, "local_links", len(parser.references))
    print("GAME_LAB_SITE_SECURITY_SCOPE_PASS: no external script/style or original game artwork")


if __name__ == "__main__":
    main()
