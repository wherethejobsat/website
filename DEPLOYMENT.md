# Deployment

Default target: GitHub Pages. Cloudflare Pages is documented as an alternative.

Current official references checked on 2026-05-30:

- GitHub Pages custom domains: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site
- Cloudflare Pages custom domains: https://developers.cloudflare.com/pages/configuration/custom-domains/

## Before launch

Run:

```sh
python3 tools/check_site.py
python3 -m http.server 8000
```

Confirm locally:

- `http://localhost:8000/`
- `http://localhost:8000/research/`
- `http://localhost:8000/cv/`
- `http://localhost:8000/assets/docs/michael-dalton-cv.pdf`

## GitHub Pages default path

1. Use the existing GitHub repository that contains this site. A separate repository is only needed if you intentionally want the website isolated from the current repo.
2. Make sure the repository root contains `CNAME`, `.nojekyll`, `index.html`, `research/`, `cv/`, `assets/`, and `tools/check_site.py`, then commit and push.
3. In GitHub, open repository Settings, then Pages.
4. Set Build and deployment to deploy from the main branch, root folder.
5. Set the custom domain to:

```text
michaeldaltoneconomics.org
```

6. Keep the root-level `CNAME` file exactly:

```text
michaeldaltoneconomics.org
```

7. Enable Enforce HTTPS once GitHub allows it. GitHub notes DNS and HTTPS availability can take up to 24 hours.

## DNS for GitHub Pages

At the DNS provider, likely GoDaddy today, preserve all existing email and verification records. Do not delete MX, TXT, DKIM, SPF, DMARC, or unrelated records.

For the apex domain `michaeldaltoneconomics.org`, GitHub's current documented A records are:

```text
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

Optional IPv6 AAAA records currently documented by GitHub:

```text
2606:50c0:8000::153
2606:50c0:8001::153
2606:50c0:8002::153
2606:50c0:8003::153
```

For `www.michaeldaltoneconomics.org`, create a CNAME pointing to the GitHub Pages default domain for the repository account, for example:

```text
<github-account>.github.io
```

Use the actual GitHub account or organization default Pages domain. Do not include a repository path in the CNAME target.

Recommended canonical decision: use apex `michaeldaltoneconomics.org` as the canonical domain. GitHub Pages can redirect `www` to the apex when both are configured correctly.

## Verification commands

Run after DNS has had time to propagate:

```sh
dig michaeldaltoneconomics.org
dig www.michaeldaltoneconomics.org
curl -I https://michaeldaltoneconomics.org/
curl -I https://michaeldaltoneconomics.org/cv
curl -I https://michaeldaltoneconomics.org/research
```

Expected result: the domain resolves to GitHub Pages, HTTPS works, and the three public routes return a successful response or a clean redirect to the trailing-slash route.

Do not delete or cancel the old GoDaddy website-builder site until the new domain resolves correctly and HTTPS is active.

## Rollback

Before changing DNS, take a screenshot or export of the current DNS records. If the launch fails and needs rollback, restore the previous web-hosting DNS records from that snapshot while preserving all email-related records.

Do not make destructive DNS edits. Change only the web records needed for the host cutover, and keep a record of the old values.

## Cloudflare Pages alternative

Cloudflare Pages can host this static HTML site without a build step.

1. Create a Cloudflare Pages project connected to the GitHub repository, or upload the static files directly.
2. Use no build command and set the output directory to the repository root if prompted.
3. Add the custom domain in Workers & Pages, then Project, then Custom domains.
4. For an apex domain on Cloudflare Pages, Cloudflare's current documentation says the domain must be a Cloudflare zone and nameservers must point to Cloudflare. The domain can remain registered at GoDaddy; changing nameservers is not the same as transferring registrar ownership.
5. If using a subdomain only, Cloudflare documents a CNAME from that subdomain to the Pages subdomain.

Cloudflare should remain an alternative unless Michael explicitly chooses to move DNS management there.
