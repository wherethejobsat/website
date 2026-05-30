# Changelog

## 2026-05-30 - Static site migration

- Migrated the Michael Dalton academic site into a static academic-site-template layout.
- Added clean routes for `/`, `/research/`, `/cv/`, and `/contact/`.
- Added redirect/canonical helper stubs for `research.html`, `cv.html`, and `contact.html`.
- Rehosted the CV PDF locally at `assets/docs/michael-dalton-cv.pdf` with a compatibility copy at `assets/docs/cv.pdf`.
- Added local static assets, SEO metadata, `CNAME`, `.nojekyll`, `robots.txt`, `sitemap.xml`, and `404.html`.
- Added `tools/check_site.py`, `README.md`, `DEPLOYMENT.md`, `MIGRATION_REPORT.md`, and `migration_content_inventory.md`.
