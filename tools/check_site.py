#!/usr/bin/env python3
"""Validate the static Michael Dalton academic site.

Run from the repository root:
    python3 tools/check_site.py
"""

from html.parser import HTMLParser
import os
from pathlib import Path
from urllib.parse import urlparse
import sys


ROOT = Path.cwd()
DOMAIN = "https://michaeldaltoneconomics.org"
PLACEHOLDERS = (
    "Your " + "Name",
    "you@" + "university",
    "USERNAME" + ".github.io",
    "YYYY" + "-MM-DD",
    "your" + "FormId",
    "Form" + "spree",
)
SKIP_DIRS = {
    ".git",
    ".idea",
    ".venv",
    ".codex",
    ".agents",
    "academic-site-template",
}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.title_parts = []
        self.description = None
        self.canonical = None
        self.links = []
        self.h1_count = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "meta" and attrs.get("name") == "description":
            self.description = attrs.get("content", "").strip()
        elif tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href", "").strip()
        elif tag in {"a", "link", "script", "img"}:
            attr = "href" if tag in {"a", "link"} else "src"
            value = attrs.get(attr)
            if value:
                self.links.append((tag, value))
        elif tag == "h1":
            self.h1_count += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)

    @property
    def title(self):
        return "".join(self.title_parts).strip()


def iter_site_files():
    for current, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        base = Path(current)
        for name in files:
            yield base / name


def parse_html(path):
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
    return parser


def route_exists(url_path):
    parsed = urlparse(url_path)
    path = parsed.path
    if not path or path == "/":
        return (ROOT / "index.html").exists()
    if path.endswith("/"):
        return (ROOT / path.lstrip("/") / "index.html").exists()
    local = ROOT / path.lstrip("/")
    return local.exists()


def resolve_relative_link(page, href):
    if href.startswith("/"):
        return href
    base = page.parent
    target = (base / href).resolve()
    try:
        return "/" + str(target.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return href


def check_required_files(errors):
    required = [
        "index.html",
        "research/index.html",
        "cv/index.html",
        "research.html",
        "cv.html",
        "404.html",
        "robots.txt",
        "sitemap.xml",
        "CNAME",
        ".nojekyll",
        "assets/css/style.css",
        "assets/js/main.js",
        "assets/img/profile.svg",
        "assets/img/postal-square-building.jpg",
        "assets/docs/michael-dalton-cv.pdf",
        "assets/docs/cv.pdf",
    ]
    for rel in required:
        if not (ROOT / rel).exists():
            errors.append(f"missing required file: {rel}")

    required_routes = ["/", "/research/", "/cv/"]
    for route in required_routes:
        if not route_exists(route):
            errors.append(f"required route is not represented: {route}")


def check_cname_and_sitemap(errors):
    cname = ROOT / "CNAME"
    if cname.exists() and cname.read_text(encoding="utf-8").strip() != "michaeldaltoneconomics.org":
        errors.append("CNAME must contain exactly michaeldaltoneconomics.org")

    sitemap = ROOT / "sitemap.xml"
    if sitemap.exists():
        text = sitemap.read_text(encoding="utf-8")
        if "https://michaeldaltoneconomics.org/" not in text:
            errors.append("sitemap.xml does not reference the canonical domain")
        for bad in ("USERNAME" + ".github.io", "example" + ".com", "michaeldaltoneconomics" + ".com"):
            if bad in text:
                errors.append(f"sitemap.xml contains wrong domain marker: {bad}")


def check_placeholders(errors):
    for path in iter_site_files():
        if path.suffix.lower() in {".pdf", ".jpg", ".png", ".ico"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for marker in PLACEHOLDERS:
            if marker in text:
                rel = path.relative_to(ROOT)
                errors.append(f"placeholder remains in {rel}: {marker}")


def check_html(errors):
    titles = {}
    html_files = [p for p in iter_site_files() if p.suffix.lower() == ".html"]
    for path in html_files:
        rel = path.relative_to(ROOT)
        parser = parse_html(path)
        if not parser.title:
            errors.append(f"{rel} is missing <title>")
        elif parser.title in titles:
            errors.append(f"duplicate <title>: {parser.title} in {rel} and {titles[parser.title]}")
        else:
            titles[parser.title] = rel

        if not parser.description:
            errors.append(f"{rel} is missing meta description")
        if not parser.canonical:
            errors.append(f"{rel} is missing canonical URL")
        elif not parser.canonical.startswith(DOMAIN):
            errors.append(f"{rel} canonical does not use {DOMAIN}: {parser.canonical}")
        if parser.h1_count != 1:
            errors.append(f"{rel} must have exactly one h1; found {parser.h1_count}")

        for tag, href in parser.links:
            if href.startswith(("#", "mailto:", "tel:", "data:")):
                continue
            parsed = urlparse(href)
            if parsed.scheme in {"http", "https"}:
                continue
            if href.startswith("//"):
                continue
            target = resolve_relative_link(path, href)
            if not route_exists(target):
                errors.append(f"{rel} has missing internal {tag} target: {href}")


def check_no_cv_hotlink(errors):
    for path in iter_site_files():
        if path.suffix.lower() != ".html":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "blobby/go/de39cd4b-4868-47c8-bdb3-a2c6f7313984/CV.pdf" in text:
            errors.append(f"legacy CV PDF hotlink remains in {path.relative_to(ROOT)}")


def main():
    errors = []
    check_required_files(errors)
    check_cname_and_sitemap(errors)
    check_placeholders(errors)
    check_html(errors)
    check_no_cv_hotlink(errors)

    if errors:
        print("Site validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Site validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
