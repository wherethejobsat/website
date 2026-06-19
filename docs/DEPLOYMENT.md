# GitHub Pages Deployment

This site is intended to deploy with GitHub Pages from the `main` branch, using the repository root as the publication source.

## Required repository state

- The root `CNAME` file must contain exactly `michaeldaltoneconomics.org`.
- The expected GitHub Pages account domain is `wherethejobsat.github.io`.
- Repository Pages settings must be confirmed manually in GitHub.
- Use the current GitHub custom-domain documentation as the authoritative source for DNS values.
- Do not maintain hardcoded GitHub Pages IP addresses in this repository.

## DNS scope

Only web-hosting DNS records should be changed.

Preserve all MX, SPF, DKIM, DMARC, TXT, and domain-verification records.

## Pre-deployment validation

Run from the repository root:

```sh
python3 tools/check_site.py
```

## Manual GitHub Pages settings

Confirm in repository settings:

- Source: deploy from a branch.
- Branch: `main`.
- Folder: repository root.
- Custom domain: `michaeldaltoneconomics.org`.
- HTTPS enforcement enabled when available.

## Verification

After deployment and DNS propagation, verify the public routes:

```sh
curl -I https://michaeldaltoneconomics.org/
curl -I https://michaeldaltoneconomics.org/research/
curl -I https://michaeldaltoneconomics.org/research-map/
curl -I https://michaeldaltoneconomics.org/cv/
curl -I https://michaeldaltoneconomics.org/contact/
```
