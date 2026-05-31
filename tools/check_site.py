#!/usr/bin/env python3
"""Validate the static Michael Dalton academic site.

Run from the repository root:
    python3 tools/check_site.py
"""

from html.parser import HTMLParser
import json
import os
from pathlib import Path
from urllib.parse import urlparse
import sys


ROOT = Path.cwd()
DOMAIN = "https://michaeldaltoneconomics.org"
UNWANTED_STRINGS = (
    "Your " + "Name",
    "you@" + "university.edu",
    "USERNAME" + ".github.io",
    "mirrored from " + "the current site",
    "from the " + "live site",
    "Abstracts are in " + "the page HTML",
    "This static site does " + "not use a contact form",
    "place" + "holder",
)
DISCLAIMER = "Views expressed here are my own and do not necessarily reflect the views of the Bureau of Labor Statistics."
BANNED_ZOMBIE_RENAMES = (
    "Earlier " + "Work",
    "Archived " + "Papers",
)
SKIP_DIRS = {
    ".git",
    ".idea",
    ".venv",
    "__pycache__",
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
        self.ids = set()
        self.generic_image_labels = []
        self.visible_text = []
        self.h1_count = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        for attr in ("alt", "aria-label"):
            if attrs.get(attr, "").strip() == "Image":
                self.generic_image_labels.append((tag, attr))
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
        stripped = data.strip()
        if stripped:
            self.visible_text.append(stripped)

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


def route_file(url_path):
    parsed = urlparse(url_path)
    path = parsed.path
    if not path or path == "/":
        candidate = ROOT / "index.html"
        return candidate if candidate.exists() else None
    if path.endswith("/"):
        candidate = ROOT / path.lstrip("/") / "index.html"
        return candidate if candidate.exists() else None
    local = ROOT / path.lstrip("/")
    if local.exists():
        return local
    return None


def route_exists(url_path):
    return route_file(url_path) is not None


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
        "assets/js/research-network.js",
        "assets/data/research-network.json",
        "assets/img/data-mark-logo.svg",
        "assets/img/favicon.svg",
        "favicon.svg",
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


def check_unwanted_strings(errors):
    for path in iter_site_files():
        if path.suffix.lower() in {".pdf", ".jpg", ".png", ".ico"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for marker in UNWANTED_STRINGS:
            if marker in text:
                rel = path.relative_to(ROOT)
                errors.append(f"unwanted string remains in {rel}: {marker}")


def check_html(errors):
    titles = {}
    parsed_cache = {}
    html_files = [p for p in iter_site_files() if p.suffix.lower() == ".html"]

    def parsed_page(path):
        if path not in parsed_cache:
            parsed_cache[path] = parse_html(path)
        return parsed_cache[path]

    for path in html_files:
        rel = path.relative_to(ROOT)
        parser = parsed_page(path)
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
        if parser.generic_image_labels:
            for tag, attr in parser.generic_image_labels:
                errors.append(f"{rel} has generic {attr} on <{tag}>")
        if any(text == "Image" for text in parser.visible_text):
            errors.append(f"{rel} contains visible generic image text")

        for tag, href in parser.links:
            if href.startswith(("mailto:", "tel:", "data:")):
                continue
            parsed = urlparse(href)
            if parsed.scheme in {"http", "https"}:
                continue
            if href.startswith("//"):
                continue
            if href.startswith("#"):
                if href[1:] and href[1:] not in parser.ids:
                    errors.append(f"{rel} has missing same-page anchor target: {href}")
                continue
            target = resolve_relative_link(path, href)
            target_file = route_file(target)
            if not target_file:
                errors.append(f"{rel} has missing internal {tag} target: {href}")
                continue
            fragment = urlparse(target).fragment
            if fragment and target_file.suffix.lower() == ".html":
                target_parser = parsed_page(target_file)
                if fragment not in target_parser.ids:
                    errors.append(f"{rel} has missing internal anchor target: {href}")


def check_research_network(errors):
    network_path = ROOT / "assets" / "data" / "research-network.json"
    script_path = ROOT / "assets" / "js" / "research-network.js"
    index_path = ROOT / "index.html"
    research_path = ROOT / "research" / "index.html"

    if not network_path.exists():
        errors.append("assets/data/research-network.json is missing")
        return
    if not script_path.exists():
        errors.append("assets/js/research-network.js is missing")

    try:
        data = json.loads(network_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"research-network.json is invalid JSON: {exc}")
        return

    nodes = data.get("nodes")
    edges = data.get("edges")
    if not isinstance(nodes, list):
        errors.append("research-network.json nodes must be a list")
        nodes = []
    if not isinstance(edges, list):
        errors.append("research-network.json edges must be a list")
        edges = []

    ids = []
    node_by_id = {}
    for node in nodes:
        node_id = node.get("id") if isinstance(node, dict) else None
        if not node_id:
            errors.append("research-network.json contains a node without an id")
            continue
        ids.append(node_id)
        node_by_id[node_id] = node

    duplicates = sorted({node_id for node_id in ids if ids.count(node_id) > 1})
    for node_id in duplicates:
        errors.append(f"research-network.json has duplicate node id: {node_id}")

    for edge in edges:
        if not isinstance(edge, list) or len(edge) != 2:
            errors.append(f"research-network.json has invalid edge: {edge}")
            continue
        for endpoint in edge:
            if endpoint not in node_by_id:
                errors.append(f"research-network.json edge references missing node: {endpoint}")

    paper_nodes = [node for node in nodes if isinstance(node, dict) and node.get("type") == "paper"]
    for node in paper_nodes:
        missing = [key for key in ("id", "label", "title", "href") if not node.get(key)]
        if missing:
            errors.append(f"paper node {node.get('id', '<missing>')} is missing required fields: {', '.join(missing)}")

    type_counts = {}
    for node in nodes:
        if isinstance(node, dict):
            type_counts[node.get("type")] = type_counts.get(node.get("type"), 0) + 1
    for required_type in ("topic", "data", "method"):
        if type_counts.get(required_type, 0) < 1:
            errors.append(f"research-network.json must include at least one {required_type} node")

    categories = {node.get("category") for node in paper_nodes if node.get("category")}
    if "Zombie Papers" not in categories:
        errors.append("research-network.json must preserve the exact category spelling: Zombie Papers")
    for category in categories:
        if isinstance(category, str) and category.lower() == "zombie papers" and category != "Zombie Papers":
            errors.append(f"research-network.json misspells Zombie Papers category: {category}")

    if research_path.exists():
        research_ids = parse_html(research_path).ids
        for node in paper_nodes:
            href = node.get("href", "")
            parsed = urlparse(href)
            if parsed.path == "/research/" and parsed.fragment and parsed.fragment not in research_ids:
                errors.append(f"paper node {node['id']} href does not resolve to a research page anchor: {href}")

    if index_path.exists():
        text = index_path.read_text(encoding="utf-8", errors="ignore")
        if "Research Network" not in text:
            errors.append("index.html is missing the Research Network section")
        if "Papers connected by topics, datasets, and measurement questions." not in text:
            errors.append("index.html is missing the required Research Network subtitle")
        marker = 'id="research-network"'
        marker_at = text.find(marker)
        main_end = text.find("</main>", marker_at if marker_at != -1 else 0)
        if marker_at == -1:
            errors.append("index.html is missing id=\"research-network\"")
        else:
            after_network = text[marker_at:main_end if main_end != -1 else len(text)]
            repeated_profile_markers = (
                'class="profile"',
                'class="avatar"',
                "Michael R. Dalton",
                "Research Economist, Bureau of Labor Statistics",
                "Washington, DC",
                "Office of Employment and Unemployment Statistics",
            )
            for marker_text in repeated_profile_markers:
                if marker_text in after_network:
                    errors.append(f"index.html repeats profile/contact material after the Research Network: {marker_text}")


def check_no_cv_hotlink(errors):
    for path in iter_site_files():
        if path.suffix.lower() != ".html":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "blobby/go/de39cd4b-4868-47c8-bdb3-a2c6f7313984/CV.pdf" in text:
            errors.append(f"legacy CV PDF hotlink remains in {path.relative_to(ROOT)}")


def check_research_section_names(errors):
    research = ROOT / "research" / "index.html"
    if not research.exists():
        return
    text = research.read_text(encoding="utf-8", errors="ignore")
    if "Zombie Papers" not in text:
        errors.append("research/index.html is missing the required heading: Zombie Papers")
    if 'href="#working-papers"' in text and 'href="#zombie-papers"' not in text:
        errors.append("research section jump links omit Zombie Papers")
    for heading in BANNED_ZOMBIE_RENAMES:
        if heading in text:
            errors.append(f"research/index.html contains a banned replacement heading: {heading}")


def check_contact_disclaimer(errors):
    contact = ROOT / "contact" / "index.html"
    if not contact.exists():
        return
    text = contact.read_text(encoding="utf-8", errors="ignore")
    if text.count(DISCLAIMER) > 1:
        errors.append("contact/index.html repeats the BLS disclaimer more than once")


def main():
    errors = []
    check_required_files(errors)
    check_cname_and_sitemap(errors)
    check_unwanted_strings(errors)
    check_html(errors)
    check_research_network(errors)
    check_no_cv_hotlink(errors)
    check_research_section_names(errors)
    check_contact_disclaimer(errors)

    if errors:
        print("Site validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Site validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
