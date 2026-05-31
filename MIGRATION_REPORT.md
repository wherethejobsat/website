# Migration report

## Migrated pages and output paths

- Home: `index.html` serves `/`
- Research: `research/index.html` serves `/research/` and `/research`
- CV: `cv/index.html` serves `/cv/` and `/cv`
- Contact: `contact/index.html` serves `/contact/`
- Compatibility stubs:
  - `research.html` redirects to `/research/`
  - `cv.html` redirects to `/cv/`
  - `contact.html` redirects to `/contact/`

## Local assets

- Canonical CV PDF: `assets/docs/michael-dalton-cv.pdf`
- Compatibility CV PDF copy: `assets/docs/cv.pdf`
- Data-mark logo: `assets/img/data-mark-logo.svg`
- Favicon: `favicon.svg`
- CSS: `assets/css/style.css`
- JavaScript: `assets/js/main.js`

## Content preserved

- Home page identity text: Michael Dalton, Research Economist, Bureau of Labor Statistics, obfuscated email display, LinkedIn profile link, and Google Scholar profile link.
- Home page research links were preserved and presented as featured research cards with links to full research entries.
- Research page section headers were preserved:
  - Working Papers
  - Works in Progress
  - Publications
  - Bureau of Labor Statistics Publications
  - Zombie Papers
- Research entries preserve titles, coauthors, years, venues where present, external links, and live-site abstract text.
- CV page preserves the live PDF by serving it locally and adds a short HTML summary based on the PDF text.

## Preserved external links

- `https://www.linkedin.com/in/mdaltonecon/`
- `https://scholar.google.com/citations?hl=en&user=C-mmySYAAAAJ`
- `https://scholar.google.com/citations?view_op=view_citation&hl=en&user=C-mmySYAAAAJ&citation_for_view=C-mmySYAAAAJ:u-x6o8ySG0sC`
- `https://www.nber.org/papers/w34012`
- `https://doi.org/10.3386/w34012`
- `https://www.journals.uchicago.edu/doi/abs/10.1086/724591`
- `https://doi.org/10.1086/724591`
- `https://www.bls.gov/osmr/research-papers/2022/pdf/ec220080.pdf`
- `https://youtu.be/KF2GBaFShL4?t=13023`
- `https://www.bls.gov/osmr/research-papers/2021/pdf/ec210080.pdf`
- `https://www.nytimes.com/2022/02/01/business/paycheck-protection-program-costs.html`
- `https://www.nytimes.com/interactive/2022/03/11/us/how-covid-stimulus-money-was-spent.html`
- `https://www.bls.gov/osmr/research-papers/2020/ec200140.htm`
- `https://www.bls.gov/osmr/research-papers/2020/pdf/ec200140.pdf`
- `https://conference.nber.org/conf_papers/f152529/f152529.slides.pdf`
- `https://www.wsj.com/articles/for-small-firms-covid-19-cuts-deeper-its-getting-worse-every-day-11608354002`
- `https://www.apatrickbehrer.com/`
- `http://rjisungpark.com/`
- `https://sites.google.com/site/lbkahn/`
- `https://sites.google.com/view/andreasimueller/`
- `https://link.springer.com/article/10.1007/s10888-021-09506-6`
- `https://link.springer.com/content/pdf/10.1007/s10888-021-09506-6.pdf`
- `https://img1.wsimg.com/blobby/go/de39cd4b-4868-47c8-bdb3-a2c6f7313984/downloads/nba_FINAL.pdf?ver=1591229303181`
- `https://sites.google.com/site/peterlandryecon/home`
- `http://web.colby.edu/drlafave/files/2017/03/daltonlafave2017jhe.pdf`
- `http://web.colby.edu/drlafave/`
- `https://doi.org/10.21916/mlr.2022.8`
- `https://doi.org/10.21916/mlr.2020.23`
- `https://www.bls.gov/opub/btn/volume-9/how-do-jobseekers-search-for-jobs.htm`
- `https://www.bls.gov/opub/btn/volume-9/pdf/how-do-jobseekers-search-for-jobs.pdf`
- `https://doi.org/10.21916/mlr.2020.17`

## Intentional text changes

- The GoDaddy footer, builder scripts, web fonts, tracking/signals scripts, and messaging widgets were removed.
- The duplicate New York Times PPP link from the live research page was collapsed into one article link plus the separate interactive link.
- Home page update text was shortened into scannable summaries with links to full research entries.
- Email is displayed as `Dalton.Michael at BLS dot gov` instead of a direct mailto link.
- Added disclaimer: "Views expressed here are my own and do not necessarily reflect the views of the Bureau of Labor Statistics."

## Static hosting files created

- `CNAME`
- `.nojekyll`
- `robots.txt`
- `sitemap.xml`
- `404.html`
- `README.md`
- `DEPLOYMENT.md`
- `CHANGELOG.md`
- `tools/check_site.py`

## Validation

Run:

```sh
python3 tools/check_site.py
```

The checker covers route presence, required files, starter strings, local internal links, HTML title/meta/canonical coverage, sitemap domain, CNAME contents, required research headings, and legacy CV hotlinks.
