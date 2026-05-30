# Michael Dalton academic website

Static academic website for `michaeldaltoneconomics.org`, migrated from the paid GoDaddy website builder to a dependency-light HTML/CSS/JS site based on the academic-site-template layout.

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

The checker verifies required pages and routes, placeholder strings, local internal links, canonical metadata, sitemap domain, `CNAME`, and local CV PDF paths.

## File structure

- `index.html`: home page
- `research/index.html`: canonical `/research/` page
- `cv/index.html`: canonical `/cv/` page
- `contact/index.html`: static contact page with no form dependency
- `research.html`, `cv.html`, `contact.html`: redirect/canonical helper stubs
- `assets/css/style.css`: template-derived site styles
- `assets/js/main.js`: theme toggle and active navigation
- `assets/docs/michael-dalton-cv.pdf`: canonical local CV PDF
- `assets/docs/cv.pdf`: compatibility copy for template-era links
- `migration_content_inventory.md`: fetched current-site content inventory
- `MIGRATION_REPORT.md`: migration summary and preserved links
- `DEPLOYMENT.md`: GitHub Pages and Cloudflare Pages launch runbook

## Editing

- Keep the site static: no CMS, database, paid form service, analytics tracker, or server runtime.
- Preserve public routes `/`, `/research`, and `/cv`.
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
