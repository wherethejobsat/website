# Michael Dalton academic website

Static academic website for `michaeldaltoneconomics.org`, maintained as a dependency-light HTML/CSS/JS site.

## Local preview

Run from the repository root:

```sh
python3 -m http.server 8000
```

Then open:

- `http://localhost:8000/`
- `http://localhost:8000/research/`
- `http://localhost:8000/cv/`

## Validate

```sh
python3 tools/check_site.py
```

The checker verifies required pages and routes, starter strings, local internal links and anchors, canonical metadata, sitemap domain, `CNAME`, local CV PDF paths, the Research Network JSON contract, and the required `Zombie Papers` section heading.

## File structure

- `index.html`: home page
- `research/index.html`: canonical `/research/` page
- `cv/index.html`: canonical `/cv/` page
- `contact/index.html`: static contact page with no form dependency
- `research.html`, `cv.html`, `contact.html`: redirect/canonical helper stubs
- `assets/css/style.css`: color tokens, layout, and component styles
- `assets/js/main.js`: theme toggle and active navigation
- `assets/js/research-network.js`: vanilla SVG Research Network behavior
- `assets/data/research-network.json`: Research Network paper, topic, data, and method links
- `assets/img/data-mark-logo.svg`: header data-mark logo
- `favicon.svg`: browser favicon
- `assets/docs/michael-dalton-cv.pdf`: canonical local CV PDF
- `assets/docs/cv.pdf`: compatibility copy for older links
- `migration_content_inventory.md`: fetched current-site content inventory
- `MIGRATION_REPORT.md`: migration summary and preserved links
- `DEPLOYMENT.md`: GitHub Pages and Cloudflare Pages launch runbook

## Editing

- Keep the site static: no CMS, database, paid form service, analytics tracker, or server runtime.
- Preserve public routes `/`, `/research`, and `/cv`.
- Keep the research heading `Zombie Papers` exactly as written.
- Keep Palette A and the data-mark logo in `assets/css/style.css`, `assets/img/data-mark-logo.svg`, and `favicon.svg`.
- Edit research cards directly in `research/index.html`; preserve titles, coauthors, abstracts, publication status, and outbound links.
- Edit homepage graph data in `assets/data/research-network.json`; keep paper `href` values synchronized with IDs in `research/index.html`.
- Edit homepage graph behavior in `assets/js/research-network.js`; keep it dependency-free vanilla JavaScript and SVG.
- Keep CV links local. Do not hotlink the legacy GoDaddy PDF.
- When adding a page, update `sitemap.xml`, canonical URLs, navigation if needed, and `tools/check_site.py` if the page becomes required.
- Use the obfuscated email display `Dalton.Michael at BLS dot gov` in HTML unless Michael explicitly wants a mailto link.

## Launch checklist

1. Run `python3 tools/check_site.py`.
2. Preview with `python3 -m http.server 8000`.
3. Confirm `/`, `/research/`, and `/cv/` load locally.
4. Confirm `assets/docs/michael-dalton-cv.pdf` downloads locally.
5. Deploy through GitHub Pages or Cloudflare Pages using `DEPLOYMENT.md`.
6. Do not cancel or delete the old GoDaddy site until the custom domain resolves to the new host and HTTPS works.
