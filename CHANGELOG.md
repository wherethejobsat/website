# Changelog

## 2026-05-31 - Homepage Research Network

- Replaced the static homepage research-theme motif with a dependency-free Research Network using local JSON, vanilla JavaScript, and SVG.
- Connected research papers to supported topics, data sources, and method or measurement objects while preserving the exact `Zombie Papers` heading and category text.
- Removed the repeated homepage profile/contact sidebar so the page now ends with the Research Network, compact links, and the global footer.
- Expanded validation for network JSON structure, paper anchor resolution, generic image labels, and repeated profile material after the network.

## 2026-05-31 - Second aesthetic refinement

- Removed repeated profile/logo panels from the research, CV, and contact pages.
- Tightened homepage feature cards, research hierarchy, CV-at-a-glance presentation, and the static contact page.
- Added the `Zombie Papers` research jump link while preserving the section heading exactly.
- Removed implementation-sounding public copy and kept the BLS disclaimer to the footer on each page.
- Updated validation checks for public-copy residue, research jump links, and duplicate contact disclaimers.

## 2026-05-31 - Visual refinement

- Added a compact data-mark logo and favicon using the Palette A blue and copper colors.
- Reworked the header, homepage, research cards, CV sidebar, contact page, and footer for a calmer data-forward academic presentation.
- Preserved static routes, local CV links, the BLS disclaimer, and the exact `Zombie Papers` research heading.
- Updated the validation script, README, and project instructions for the refined visual system.

## 2026-05-30 - Static site migration

- Migrated the Michael Dalton academic site into a static academic-site-template layout.
- Added clean routes for `/`, `/research/`, `/cv/`, and `/contact/`.
- Added redirect/canonical helper stubs for `research.html`, `cv.html`, and `contact.html`.
- Rehosted the CV PDF locally at `assets/docs/michael-dalton-cv.pdf` with a compatibility copy at `assets/docs/cv.pdf`.
- Added local static assets, SEO metadata, `CNAME`, `.nojekyll`, `robots.txt`, `sitemap.xml`, and `404.html`.
- Added `tools/check_site.py`, `README.md`, `DEPLOYMENT.md`, `MIGRATION_REPORT.md`, and `migration_content_inventory.md`.
