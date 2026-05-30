# AGENTS.md: michaeldaltoneconomics.org migration (use academic-site-template)

## One-line goal

Port https://michaeldaltoneconomics.org/ to the academic-site-template look and file structure, keep /research and /cv working, and remove dependence on the current paid builder.

## Baseline UI (REQUIRED): academic-site-template

This repo must start from the academic-site-template that was provided earlier (the zip with index.html, research.html, cv.html, assets/, etc).

Treat the template as the canonical design system:
- keep the hero header, top nav, and right-side profile/contact card layout
- only change CSS when needed to fit migrated content
- do not introduce a new framework unless explicitly requested

Template files expected (either at repo root or after the clean-URL conversion described below):
- index.html
- research.html
- cv.html
- contact.html (optional)
- teaching.html (optional; safe to delete)
- assets/css/style.css
- assets/js/main.js
- assets/img/hero.*
- assets/img/profile.*
- assets/docs/michael-dalton-cv.pdf (canonical local CV)
- assets/docs/cv.pdf (compatibility copy if needed)

If the template is missing, recreate this structure first, then port content into it.

## Content sources (mirror these pages)

Legacy pages to migrate (content should remain verbatim except for trivial formatting fixes):
- https://michaeldaltoneconomics.org/
- https://michaeldaltoneconomics.org/research
- https://michaeldaltoneconomics.org/cv

The CV PDF is currently hotlinked from img1.wsimg.com. Download it once and serve it locally from this repo.

## Required URL behavior (do not break inbound links)

Public URLs must resolve:
- /
- /research
- /cv

Static-host implementation (GitHub Pages, Cloudflare Pages):
- Convert template pages into clean folders:
  - research/index.html serves /research (and /research/)
  - cv/index.html serves /cv (and /cv/)
- Keep compatibility stubs at repo root:
  - research.html redirects (meta refresh) to /research/
  - cv.html redirects (meta refresh) to /cv/

Redirect stub rules:
- include rel=canonical
- include a visible link in the body

## Page mapping into the template layout

### Home (/)
- Keep the template hero + sidebar card.
- Replace placeholder bio with your real bio and affiliations.
- Create a "Recent updates" section that mirrors the legacy home page entries.
- Preserve all outbound links and their anchor text.

### Research (/research)
Preserve these section headers:
- Working Papers
- Works in Progress
- Publications
- Bureau of Labor Statistics Publications
- Zombie Papers

For each entry, preserve:
- title
- coauthors
- year
- venue (if present)
- all external links (paper, slides, coverage, DOI)
- abstract text

Rendering requirements:
- abstracts must be in HTML (not loaded via JS after page load)
- use <details><summary>Abstract</summary>...</details> for collapsible abstracts

### CV (/cv)
- Prominent "Download PDF" button.
- Store the canonical PDF at assets/docs/michael-dalton-cv.pdf and link to it from:
  - /cv
  - the site-wide sidebar card (if present)
- Keep assets/docs/cv.pdf only as a compatibility copy for template-era assumptions.
- Do not hotlink the legacy PDF in the final site.

### Contact (optional)
- Repeat email, affiliation, and key links.
- No trackers by default.

## Migration playbook (execute in this order)

1) Bootstrap from template
- Ensure the academic-site-template file tree exists in the repo.
- Delete teaching.html if not needed and remove its nav link everywhere.

2) Convert to clean URLs
- Create research/index.html and cv/index.html using the existing research.html and cv.html content as starting points.
- Replace root research.html and cv.html with redirect stubs to the folders.
- Update nav links to /research/ and /cv/ everywhere.

3) Re-host the CV PDF
- Download the current CV PDF and save it as assets/docs/cv.pdf.
- Update all CV links accordingly.

4) Port Research content
- Move all content from the legacy /research into the template design.
- Replace separator lines with proper headings and spacing.
- Make abstracts collapsible via <details>.

5) Port Home content
- Mirror the legacy home content into the template home page.
- Ensure "Recent updates" is readable and scannable.

6) Add site hygiene files
- sitemap.xml
- robots.txt
- 404.html
- favicon (optional)

7) Verify
- local preview on a static server
- link check
- mobile sanity

## Content modeling (recommended for low maintenance)

Preferred:
- Store research entries in one structured file:
  - data/research.yaml (preferred) OR data/research.json
- Add a deterministic generator:
  - scripts/render_research.py
    - input: data/research.*
    - output: research/index.html
    - no heavy templating engine; generate simple HTML deterministically

Commit both the data file and the generated HTML so the deployed site has zero build requirements.

## Codex CLI operating procedure (best practice defaults)

## Maintenance rules for future sessions

- Preserve the public routes `/`, `/research`, and `/cv`.
- Keep the site static and dependency-light: no paid CMS, database, server runtime, analytics tracker, or contact-form service unless explicitly requested.
- Do not store GoDaddy, GitHub, Cloudflare, form-service, email, DNS, or other credentials in the repo.
- Use the obfuscated email display `Dalton.Michael at BLS dot gov` unless Michael explicitly asks for a mailto link.
- Keep CV links local and use `assets/docs/michael-dalton-cv.pdf` as the canonical PDF path.
- Update `sitemap.xml`, canonical URLs, and navigation when adding or removing pages.
- Run `python3 tools/check_site.py` before declaring the site ready.

Interactive sessions:
- Start in Read Only and inspect the repo.
- Use /plan before multi-file edits.
- Use /permissions to relax approvals only when needed.
- Use /diff before considering a task done.
- Use /review to check requirements and obvious regressions.
- Use /compact after long sessions to keep context tight.
- Use /status to confirm model, approvals, and writable roots.
- Use /debug-config if behavior differs from expected config.

Non-interactive mode:
- Use codex exec for repeatable automation steps (render, checks, CI jobs).

Permissions:
- Require explicit approval before:
  - enabling network access
  - running shell commands that mutate system state
  - writing outside the repository

Network policy:
- Assume network is disabled by default.
- Enable network only to fetch legacy content and the CV PDF once.
- When enabled, restrict fetches to:
  - michaeldaltoneconomics.org
  - img1.wsimg.com (CV PDF only)

## Acceptance tests (must pass)

- / , /research , /cv all load locally.
- No broken internal links.
- CV downloads from assets/docs/cv.pdf.
- Mobile layout is usable (nav, sidebar card, research entries).
- Each page has:
  - unique <title>
  - meta description
  - canonical URL
- sitemap.xml and robots.txt exist and reference the canonical domain.

Deliver MIGRATION_REPORT.md containing:
- migrated pages and output paths
- list of preserved external links
- any intentional text changes (should be minimal)
- redirects/stubs created

## Deployment (static hosting + domain cutover)

Preferred hosts:
- GitHub Pages OR Cloudflare Pages

Create docs/DEPLOYMENT.md with:
- build and deploy steps
- custom domain hookup for michaeldaltoneconomics.org
- www vs apex decision and redirect handling
- DNS record preservation (do not delete MX/TXT records used for email)
- rollback plan (how to revert DNS quickly)

Do not instruct destructive DNS edits.
