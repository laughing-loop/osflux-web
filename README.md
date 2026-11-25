# osflux-web

The OSflux website: one static page that explains OSflux, offers the download and invites contributors.

Live at **https://laughing-loop.github.io/osflux-web/**

Plain HTML and CSS. No framework, no build step, no JavaScript, no trackers and no cookies. Fonts are self-hosted.

## What's where

| Path | What it is |
|---|---|
| `site/` | Everything that is published. Only this folder is deployed. |
| `site/index.html` | The page. The release switch is at the top (see below). |
| `site/404.html` | Shown by GitHub Pages for any missing address. |
| `site/assets/css/site.css` | All styles. Colours, type and shape follow OSflux Studio v2. |
| `site/assets/fonts/` | IBM Plex Sans (300, 400, 600) and IBM Plex Mono (400, 500) as WOFF2, subset to Latin, with `OFL.txt`. |
| `site/assets/brand/` | The OSflux lockups (ink for light, white for dark) and the three-bar small mark used as the SVG favicon. |
| `site/assets/icons/` | `favicon-32.png` (the full mark at 32 px) and the Apple touch icon. |
| `site/favicon.ico` | The 16, 32 and 48 px frames of OSflux's Windows icon, for older browsers. |
| `site/assets/img/` | Studio design frames 02 and 07, dark and light, as WebP. |
| `site/og-image.png` | The 1200 × 630 Open Graph and Twitter image. |
| `tools/build_assets.py` | Regenerates the fonts, frames, icons and Open Graph image from a checkout of `laughing-loop/OSflux`. |
| `.github/workflows/pages.yml` | Deploys `site/` to GitHub Pages. |

## Preview locally

Serve the `site/` folder with any static server, then open the address it prints. For example:

```sh
python -m http.server 8000 --directory site
# or
npx serve site
```

Then open http://localhost:8000/. Opening `site/index.html` straight from disk works too.

`404.html` uses `<base href="/osflux-web/">`, so its styles only load when it is served under `/osflux-web/`, as it is on GitHub Pages.

## Switch on the download button

There is no OSflux release yet, so the hero shows "Coming soon — first release in preparation" instead of a download link. Once https://github.com/laughing-loop/OSflux/releases/latest exists, change one attribute near the top of `site/index.html`:

```html
<html lang="en-GB" data-release="soon">       <!-- before -->
<html lang="en-GB" data-release="available">  <!-- after -->
```

The button then reads "Download for Windows" and links to the latest release page. Push to `main` and it is live a minute later.

## How it deploys

Every push to `main` runs `.github/workflows/pages.yml`, which uploads the `site/` folder and publishes it with GitHub Pages (Settings → Pages → Source: GitHub Actions). It can also be run by hand from the Actions tab. There is no build step: what is in `site/` is what is served.

## Regenerating assets

The fonts, Studio frames, favicons and Open Graph image are made from the OSflux repository, which is only read. The favicons are copied from its brand pack as drawn, not redrawn:

```sh
python -m pip install pillow fonttools brotli
python tools/build_assets.py ../OSflux
```

## Adding a custom domain later

No custom domain is set up yet; `osflux.org` is the likely choice. When it is ready:

1. Add a file `site/CNAME` containing just the domain, for example `osflux.org`.
2. At the DNS provider, point the domain at GitHub Pages: `A` records for the apex to `185.199.108.153`, `185.199.109.153`, `185.199.110.153` and `185.199.111.153` (and the matching `AAAA` records), and a `CNAME` for `www` to `laughing-loop.github.io`.
3. In the repo's Settings → Pages, enter the domain and tick **Enforce HTTPS** once the certificate is issued.
4. Replace `https://laughing-loop.github.io/osflux-web/` with `https://osflux.org/` in `site/index.html` (canonical, `og:` and `twitter:` tags), `site/robots.txt` and `site/sitemap.xml`.
5. In `site/404.html`, change `<base href="/osflux-web/">` to `<base href="/">`.

## Licences

- The website's own code (the HTML, CSS, workflow and `tools/` script) is under the MIT License: see `LICENSE`.
- The OSflux name and logo, including the files in `site/assets/brand/`, the favicons and the Open Graph image, belong to HOD Technologies Limited, which keeps all rights to them. They are not covered by the MIT License or by OSflux's GPL-3.0-or-later licence.
- IBM Plex is under the SIL Open Font License 1.1: `site/assets/fonts/OFL.txt`.
- The Studio design frames in `site/assets/img/` come from the OSflux repository.
- OSflux itself is GPL-3.0-or-later; OSflux Studio is distributed under GPL-3.0 only, because it uses Slint under the GPL-3.0.

© 2026 HOD Technologies Limited
