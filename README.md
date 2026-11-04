# sotkaretsos.github.io

Personal academic site of Sotirios T. Karetsos, in English and Greek, published with GitHub Pages.

| Page | English | Greek |
|---|---|---|
| Home: news, research themes, publications, projects, teaching, experience, posters | `index.html` | `el/index.html` |
| All posters with abstracts and PDFs | `posters.html` | `el/posters.html` |
| Full publication list with filters | `publications.html` | `el/publications.html` |
| Farmer revenue calculator | `tools/revenue-calculator.html` | — |

## Editing

The pages are generated. Edit the texts in `scripts/build.py` (each text has an English and a Greek version) or the publication list in `assets/data/publications.json`, then run:

```bash
python3 scripts/build.py
```

and commit the regenerated HTML, `sitemap.xml` and `robots.txt`. Styles are in `assets/css/site.css`; images and poster PDFs in `assets/img/` and `assets/docs/`.
