# Michael Dalton — Academic Website

[![Validate site](https://github.com/wherethejobsat/website/actions/workflows/validate.yml/badge.svg)](https://github.com/wherethejobsat/website/actions/workflows/validate.yml)

This repository contains the source for:

https://michaeldaltoneconomics.org

It is a dependency-light static academic website.

## Site architecture

- Vanilla HTML, CSS, and JavaScript.
- No build step.
- No third-party frontend dependencies.
- Deployment directly from the repository root.
- Dependency-free Python standard-library validation.

## Local preview

```sh
python3 -m http.server 8000
```

Main local routes:

- `http://localhost:8000/`
- `http://localhost:8000/research/`
- `http://localhost:8000/research-map/`
- `http://localhost:8000/cv/`
- `http://localhost:8000/contact/`

## Validation

```sh
python3 tools/check_site.py
```

The checker validates required files and routes, metadata, internal links and anchors, document compatibility, sitemap and CNAME values, and the Research Map data contract.

## Repository structure

- Canonical page directories: `/`, `research/`, `research-map/`, `cv/`, and `contact/`.
- Compatibility redirect files: `research.html`, `cv.html`, and `contact.html`.
- `assets/css/`: site styling.
- `assets/js/`: theme toggle, navigation state, and Research Map behavior.
- `assets/data/`: local Research Map data.
- `assets/img/`: local image and icon assets.
- `assets/docs/`: local CV and resume PDFs.
- `tools/check_site.py`: dependency-free validation.
- `docs/DEPLOYMENT.md`: GitHub Pages deployment runbook.

## Content maintenance

Maintainers must preserve:

- The canonical routes.
- The exact `Zombie Papers` heading.
- Local CV and resume links.
- The obfuscated email display `Dalton.Michael at BLS dot gov`.
- The BLS disclaimer.
- Synchronization between Research Map paper links and research-page anchor IDs.

## Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).
