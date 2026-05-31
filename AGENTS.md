# AGENTS.md: michaeldaltoneconomics.org static site

## Project Rules

- Keep the site static: no CMS, database, server runtime, analytics tracker, paid form service, or heavy JavaScript.
- Preserve public routes `/`, `/research`, `/research-map`, `/cv`, and `/contact` while the contact page exists.
- Preserve deployment files when present: `CNAME`, `.nojekyll`, `robots.txt`, and `sitemap.xml`.
- Keep the custom domain canonical as `https://michaeldaltoneconomics.org/`.
- Keep CV links local and use `assets/docs/michael-dalton-cv.pdf` as the canonical PDF path.
- Keep the Research Map static and dependency-free: local JSON plus vanilla JavaScript/SVG only unless Michael explicitly approves another dependency.
- Keep `assets/data/research-network.json` paper `href` values synchronized with stable IDs in `research/index.html`.
- Use the obfuscated email display `Dalton.Michael at BLS dot gov` unless Michael explicitly asks for a mailto link.
- Do not add credentials, API keys, DNS secrets, form-service tokens, or deployment secrets to the repo.

## Visual System

- Use the data-mark logo at `assets/img/data-mark-logo.svg` and `favicon.svg`; do not use official BLS logos, seals, or branding.
- Keep Palette A in `assets/css/style.css` through these variables:
  - `--color-bg: #fbfaf7`
  - `--color-text: #172033`
  - `--color-muted: #5c6575`
  - `--color-primary: #1f4e79`
  - `--color-accent: #b45309`
  - `--color-surface: #ffffff`
  - `--color-border: #e6e1d8`
- Prefer system font stacks, plain HTML, CSS, and minimal vanilla JS.
- Keep the header compact: data mark, `Michael Dalton` wordmark, Research, CV, Contact, and a quiet theme toggle if retained.

## Content Rules

- Do not change research paper titles, coauthors, publication status, abstracts, or external links except to fix clearly broken internal paths.
- Keep the research section heading exactly as `Zombie Papers`.
- Do not add a contact form.
- Do not delete the BLS disclaimer:
  `Views expressed here are my own and do not necessarily reflect the views of the Bureau of Labor Statistics.`
- Preserve accessibility basics: skip link, semantic landmarks, one `h1` per page, visible focus states, keyboard-accessible nav, and sufficient contrast.

## Validation

Run before declaring the site ready:

```sh
python3 tools/check_site.py
```

For local preview:

```sh
python3 -m http.server 8000
```
