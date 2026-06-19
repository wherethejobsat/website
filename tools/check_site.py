#!/usr/bin/env python3
"""Validate the static Michael Dalton academic site."""

from html.parser import HTMLParser
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://michaeldaltoneconomics.org"
SOCIAL_IMAGE_URL = f"{DOMAIN}/assets/img/site-mark.png"
SOCIAL_IMAGE_ALT = "Michael Dalton data mark"
DISCLAIMER = "Views expressed here are my own and do not necessarily reflect the views of the Bureau of Labor Statistics."

REQUIRED_FILES = (
    ".editorconfig",
    ".github/workflows/validate.yml",
    ".nojekyll",
    "CNAME",
    "README.md",
    "docs/DEPLOYMENT.md",
    "index.html",
    "research/index.html",
    "research-map/index.html",
    "cv/index.html",
    "contact/index.html",
    "research.html",
    "cv.html",
    "contact.html",
    "404.html",
    "robots.txt",
    "sitemap.xml",
    "assets/css/style.css",
    "assets/js/main.js",
    "assets/js/research-network.js",
    "assets/data/research-network.json",
    "assets/img/data-mark-logo.svg",
    "assets/img/site-mark.png",
    "assets/img/linkedin.svg",
    "assets/img/google-scholar.svg",
    "favicon.svg",
    "assets/docs/michael-dalton-cv.pdf",
    "assets/docs/cv.pdf",
    "assets/docs/michael-dalton-resume.pdf",
)
REQUIRED_ROUTES = (
    "/",
    "/research/",
    "/research-map/",
    "/cv/",
    "/contact/",
)
CANONICAL_PAGE_URLS = {
    "index.html": f"{DOMAIN}/",
    "research/index.html": f"{DOMAIN}/research/",
    "research-map/index.html": f"{DOMAIN}/research-map/",
    "cv/index.html": f"{DOMAIN}/cv/",
    "contact/index.html": f"{DOMAIN}/contact/",
}
EXPECTED_CANONICALS = {
    **CANONICAL_PAGE_URLS,
    "404.html": f"{DOMAIN}/404.html",
    "research.html": f"{DOMAIN}/research/",
    "cv.html": f"{DOMAIN}/cv/",
    "contact.html": f"{DOMAIN}/contact/",
}
NOINDEX_PAGES = {
    "404.html",
    "research.html",
    "cv.html",
    "contact.html",
}
REDIRECT_DESTINATIONS = {
    "research.html": "/research/",
    "cv.html": "/cv/",
    "contact.html": "/contact/",
}
FORBIDDEN_PATHS = (
    "requirements.txt",
    "data/.gitkeep",
    "MIGRATION_REPORT.md",
    "migration_content_inventory.md",
    "CHANGELOG.md",
    "assets/img/img_4.png",
    "assets/img/favicon.svg",
)
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
BANNED_ZOMBIE_RENAMES = (
    "Earlier " + "Work",
    "Archived " + "Papers",
)
SKIP_DIRS = {
    ".git",
    ".idea",
    ".venv",
    ".vscode",
    "__pycache__",
    ".codex",
    ".agents",
}
TEXT_FILE_NAMES = {
    ".editorconfig",
    ".gitignore",
    ".nojekyll",
    "CNAME",
}
TEXT_SUFFIXES = {
    ".css",
    ".html",
    ".js",
    ".json",
    ".md",
    ".svg",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}
LOCAL_STATIC_SUFFIXES = (
    ".css",
    ".js",
    ".json",
    ".png",
    ".svg",
    ".jpg",
    ".jpeg",
)


def marker(*parts):
    return "".join(parts)


STALE_REFERENCE_MARKERS = (
    (marker("assets/img/", "img_4.png"), "obsolete image path"),
    (marker("assets/img/", "favicon.svg"), "obsolete duplicate favicon path"),
    (marker("MIGRATION", "_REPORT.md"), "obsolete migration report"),
    (marker("migration", "_content_inventory.md"), "obsolete migration inventory"),
    (marker("requirements", ".txt"), "obsolete requirements file"),
    (marker("academic-site", "-template"), "obsolete template source"),
    (marker("/tmp/", "dalton_site_fetch"), "temporary migration directory"),
    (marker("Go", "Daddy"), "former hosting provider"),
    (marker("Cloud", "flare"), "discarded alternate deployment provider"),
    (marker("Basic data", "-analysis stack"), "obsolete data-analysis scaffold"),
)


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.html_lang = None
        self.charset_declared = False
        self.viewport = None
        self.in_title = False
        self.title_parts = []
        self.description = None
        self.canonical = None
        self.links = []
        self.ids = set()
        self.generic_image_labels = []
        self.visible_text = []
        self.h1_count = 0
        self.meta_names = {}
        self.meta_properties = {}
        self.refresh_url = None

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs = {name.lower(): value for name, value in attrs}

        if tag == "html":
            self.html_lang = (attrs.get("lang") or "").strip()
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        for attr in ("alt", "aria-label"):
            if attrs.get(attr, "").strip() == "Image":
                self.generic_image_labels.append((tag, attr))
        if tag == "h1":
            self.h1_count += 1

        if tag == "title":
            self.in_title = True
            return

        if tag == "meta":
            content = (attrs.get("content") or "").strip()
            name = (attrs.get("name") or "").strip().lower()
            prop = (attrs.get("property") or "").strip()
            http_equiv = (attrs.get("http-equiv") or "").strip().lower()
            if attrs.get("charset") or (http_equiv == "content-type" and "charset=" in content.lower()):
                self.charset_declared = True
            if name:
                self.meta_names[name] = content
            if prop:
                self.meta_properties[prop] = content
            if name == "description":
                self.description = content
            elif name == "viewport":
                self.viewport = content
            elif http_equiv == "refresh":
                self.refresh_url = parse_refresh_url(content)
                if self.refresh_url:
                    self.links.append((tag, self.refresh_url, "content"))
            return

        if tag == "link":
            rel_values = (attrs.get("rel") or "").lower().split()
            if "canonical" in rel_values:
                self.canonical = (attrs.get("href") or "").strip()

        for attr in ("href", "src", "data-network-src"):
            value = attrs.get(attr)
            if value:
                self.links.append((tag, value, attr))

    def handle_endtag(self, tag):
        if tag.lower() == "title":
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


def parse_refresh_url(content):
    lower = content.lower()
    marker_text = "url="
    index = lower.find(marker_text)
    if index == -1:
        return None
    return content[index + len(marker_text):].strip().strip("'\"")


def iter_site_files():
    for current, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        base = Path(current)
        for name in files:
            yield base / name


def is_text_file(path):
    return path.name in TEXT_FILE_NAMES or path.suffix.lower() in TEXT_SUFFIXES


def parse_html(path):
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
    return parser


def route_file(url_path):
    parsed = urlparse(url_path)
    path = unquote(parsed.path)
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
    parsed = urlparse(href)
    if href.startswith("/") or parsed.scheme or href.startswith("//"):
        return href
    target = (page.parent / unquote(parsed.path)).resolve()
    try:
        route = "/" + str(target.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return href
    if parsed.query:
        route += "?" + parsed.query
    if parsed.fragment:
        route += "#" + parsed.fragment
    return route


def check_required_files(errors):
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).exists():
            errors.append(f"missing required file: {rel}")

    for route in REQUIRED_ROUTES:
        if not route_exists(route):
            errors.append(f"required route is not represented: {route}")


def check_forbidden_paths(errors):
    for rel in FORBIDDEN_PATHS:
        if (ROOT / rel).exists():
            errors.append(f"forbidden obsolete path exists: {rel}")


def check_cname_and_sitemap(errors):
    cname = ROOT / "CNAME"
    if cname.exists() and cname.read_text(encoding="utf-8").strip() != "michaeldaltoneconomics.org":
        errors.append("CNAME must contain exactly michaeldaltoneconomics.org")

    sitemap = ROOT / "sitemap.xml"
    if sitemap.exists():
        text = sitemap.read_text(encoding="utf-8")
        if "https://michaeldaltoneconomics.org/" not in text:
            errors.append("sitemap.xml does not reference the canonical domain")
        for route in REQUIRED_ROUTES:
            if f"{DOMAIN}{route}" not in text:
                errors.append(f"sitemap.xml omits required route: {route}")
        for bad in ("USERNAME" + ".github.io", "example" + ".com", "michaeldaltoneconomics" + ".com"):
            if bad in text:
                errors.append(f"sitemap.xml contains wrong domain marker: {bad}")


def check_unwanted_strings(errors):
    for path in iter_site_files():
        if not is_text_file(path):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for unwanted in UNWANTED_STRINGS:
            if unwanted in text:
                rel = path.relative_to(ROOT)
                errors.append(f"unwanted string remains in {rel}: {unwanted}")


def check_stale_references(errors):
    validator = Path(__file__).resolve()
    for path in iter_site_files():
        if path.resolve() == validator or not is_text_file(path):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for stale_text, label in STALE_REFERENCE_MARKERS:
            if stale_text in text:
                rel = path.relative_to(ROOT)
                errors.append(f"stale reference remains in {rel}: {label}")


def png_dimensions(path, errors):
    if not path.exists():
        return None
    data = path.read_bytes()
    if len(data) < 24 or not data.startswith(b"\x89PNG\r\n\x1a\n") or data[12:16] != b"IHDR":
        errors.append(f"{path.relative_to(ROOT)} must be a PNG image")
        return None
    return struct.unpack(">II", data[16:24])


def has_noindex(parser):
    robots = parser.meta_names.get("robots", "").lower()
    return "noindex" in {token.strip() for token in robots.replace(";", ",").split(",")}


def check_social_metadata(rel, parser, site_mark_size, errors):
    expected_url = CANONICAL_PAGE_URLS[rel]
    required_properties = (
        "og:title",
        "og:description",
        "og:type",
        "og:url",
        "og:image",
        "og:image:alt",
        "og:image:width",
        "og:image:height",
    )
    required_names = (
        "twitter:card",
        "twitter:title",
        "twitter:description",
        "twitter:image",
        "twitter:image:alt",
    )
    for key in required_properties:
        if not parser.meta_properties.get(key):
            errors.append(f"{rel} is missing {key}")
    for key in required_names:
        if not parser.meta_names.get(key):
            errors.append(f"{rel} is missing {key}")

    if parser.meta_properties.get("og:type") != "website":
        errors.append(f"{rel} og:type must be website")
    if parser.meta_properties.get("og:url") != expected_url:
        errors.append(f"{rel} og:url must be {expected_url}")
    if parser.meta_properties.get("og:image") != SOCIAL_IMAGE_URL:
        errors.append(f"{rel} og:image must be {SOCIAL_IMAGE_URL}")
    if parser.meta_properties.get("og:image:alt") != SOCIAL_IMAGE_ALT:
        errors.append(f"{rel} og:image:alt must be {SOCIAL_IMAGE_ALT}")
    if parser.meta_names.get("twitter:card") != "summary":
        errors.append(f"{rel} twitter:card must be summary")
    if parser.meta_names.get("twitter:image") != SOCIAL_IMAGE_URL:
        errors.append(f"{rel} twitter:image must be {SOCIAL_IMAGE_URL}")
    if parser.meta_names.get("twitter:image:alt") != SOCIAL_IMAGE_ALT:
        errors.append(f"{rel} twitter:image:alt must be {SOCIAL_IMAGE_ALT}")

    if site_mark_size:
        expected_width, expected_height = (str(value) for value in site_mark_size)
        if parser.meta_properties.get("og:image:width") != expected_width:
            errors.append(f"{rel} og:image:width must be {expected_width}")
        if parser.meta_properties.get("og:image:height") != expected_height:
            errors.append(f"{rel} og:image:height must be {expected_height}")


def check_local_link(rel, path, tag, href, attr, parser, parsed_page, errors):
    if href.startswith(("mailto:", "tel:", "data:")):
        return
    parsed = urlparse(href)
    if parsed.scheme in {"http", "https"} or href.startswith("//"):
        return
    if parsed.query and parsed.path.lower().endswith(LOCAL_STATIC_SUFFIXES):
        errors.append(f"{rel} has a query string on local asset URL: {href}")
    if href.startswith("#"):
        if href[1:] and href[1:] not in parser.ids:
            errors.append(f"{rel} has missing same-page anchor target: {href}")
        return
    target = resolve_relative_link(path, href)
    target_file = route_file(target)
    if not target_file:
        errors.append(f"{rel} has missing internal {tag} {attr} target: {href}")
        return
    fragment = urlparse(target).fragment
    if fragment and target_file.suffix.lower() == ".html":
        target_parser = parsed_page(target_file)
        if fragment not in target_parser.ids:
            errors.append(f"{rel} has missing internal anchor target: {href}")


def check_html(errors):
    titles = {}
    parsed_cache = {}
    html_files = [p for p in iter_site_files() if p.suffix.lower() == ".html"]
    site_mark_size = png_dimensions(ROOT / "assets" / "img" / "site-mark.png", errors)

    def parsed_page(path):
        if path not in parsed_cache:
            parsed_cache[path] = parse_html(path)
        return parsed_cache[path]

    for path in html_files:
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        parser = parsed_page(path)
        if parser.html_lang != "en":
            errors.append(f"{rel} must declare <html lang=\"en\">")
        if not parser.charset_declared:
            errors.append(f"{rel} is missing a character-encoding declaration")
        if not parser.viewport:
            errors.append(f"{rel} is missing viewport metadata")
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
        if rel in EXPECTED_CANONICALS and parser.canonical != EXPECTED_CANONICALS[rel]:
            errors.append(f"{rel} canonical must be {EXPECTED_CANONICALS[rel]}")
        if parser.h1_count != 1:
            errors.append(f"{rel} must have exactly one h1; found {parser.h1_count}")
        if parser.generic_image_labels:
            for tag, attr in parser.generic_image_labels:
                errors.append(f"{rel} has generic {attr} on <{tag}>")
        if any(text == "Image" for text in parser.visible_text):
            errors.append(f"{rel} contains visible generic image text")
        if rel in NOINDEX_PAGES and not has_noindex(parser):
            errors.append(f"{rel} must include a noindex robots directive")
        if rel in REDIRECT_DESTINATIONS and parser.refresh_url != REDIRECT_DESTINATIONS[rel]:
            errors.append(f"{rel} redirect target must be {REDIRECT_DESTINATIONS[rel]}")
        if rel in CANONICAL_PAGE_URLS:
            check_social_metadata(rel, parser, site_mark_size, errors)

        for tag, href, attr in parser.links:
            check_local_link(rel, path, tag, href, attr, parser, parsed_page, errors)


def check_pdf_compatibility(errors):
    canonical = ROOT / "assets" / "docs" / "michael-dalton-cv.pdf"
    compatibility = ROOT / "assets" / "docs" / "cv.pdf"
    if not canonical.exists() or not compatibility.exists():
        return
    canonical_hash = hashlib.sha256(canonical.read_bytes()).hexdigest()
    compatibility_hash = hashlib.sha256(compatibility.read_bytes()).hexdigest()
    if canonical_hash != compatibility_hash:
        errors.append("assets/docs/cv.pdf must be byte-for-byte identical to assets/docs/michael-dalton-cv.pdf")


def check_research_network(errors):
    network_path = ROOT / "assets" / "data" / "research-network.json"
    script_path = ROOT / "assets" / "js" / "research-network.js"
    index_path = ROOT / "index.html"
    map_path = ROOT / "research-map" / "index.html"
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
    structured_fields = {
        "topics": "topic",
        "data_sources": "data_source",
        "techniques": "technique",
        "empirical_objects": "empirical_object",
        "outcomes": "outcome",
    }
    required_paper_fields = tuple(structured_fields) + ("data_type",)
    for node in paper_nodes:
        missing = [key for key in ("id", "label", "title", "href") if not node.get(key)]
        if missing:
            errors.append(f"paper node {node.get('id', '<missing>')} is missing required fields: {', '.join(missing)}")
        for field in required_paper_fields:
            values = node.get(field)
            if not isinstance(values, list) or not values:
                errors.append(f"paper node {node.get('id', '<missing>')} must define nonempty {field}")
            elif not all(isinstance(value, str) and value.strip() for value in values):
                errors.append(f"paper node {node.get('id', '<missing>')} has invalid {field} labels")

    type_counts = {}
    for node in nodes:
        if isinstance(node, dict):
            type_counts[node.get("type")] = type_counts.get(node.get("type"), 0) + 1
    for field, required_type in structured_fields.items():
        has_structured_labels = any(
            isinstance(node.get(field), list) and node.get(field)
            for node in paper_nodes
        )
        if type_counts.get(required_type, 0) < 1 and not has_structured_labels:
            errors.append(
                f"research-network.json must include at least one {required_type} node or structured {field}"
            )

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
        if 'href="/research-map/"' not in text:
            errors.append("index.html must link to the separate Research Map page")
        if 'data-research-network' in text or 'data-network-svg' in text:
            errors.append("index.html should link to the Research Map, not embed the interactive network")

    if map_path.exists():
        text = map_path.read_text(encoding="utf-8", errors="ignore")
        if "Research Map" not in text:
            errors.append("research-map/index.html is missing the Research Map page heading")
        if "Research Network" not in text:
            errors.append("research-map/index.html is missing the Research Network section")
        if "Papers connected by topics, datasets, and measurement questions." not in text:
            errors.append("research-map/index.html is missing the required Research Network subtitle")
        if 'id="research-network"' not in text or 'data-research-network' not in text:
            errors.append("research-map/index.html is missing the interactive network mount")


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
    check_forbidden_paths(errors)
    check_cname_and_sitemap(errors)
    check_unwanted_strings(errors)
    check_stale_references(errors)
    check_html(errors)
    check_pdf_compatibility(errors)
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
