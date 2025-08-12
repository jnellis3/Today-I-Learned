# Today-I-Learned: Repo Overview

This repository powers a small TIL (Today I Learned) site using a generated SQLite database and Datasette for the web UI. Markdown files are the source-of-truth; a build script compiles them into a database with full-text search and metadata.

## Structure
- `*/*.md`: Markdown posts organized by topic folder (e.g. `AWS/…`, `python/…`).
- `build_database.py`: Converts Markdown into a SQLite database (`tils.db`).
- `tils.db`: Generated database served by Datasette.
- `templates/`: Custom Jinja templates overriding Datasette’s defaults.
  - `table-tils-til.html`: All-posts table view.
  - `row-tils-til.html`: Single post view.
  - `_base.html`: Site-wide base layout.
- `pages/index.html`: A custom landing page using `datasette-template-sql` blocks.
- `metadata.yml`: Datasette metadata and plugin configuration (title, feed, etc.).
- `Dockerfile`: Minimal image to serve `tils.db` with Datasette.

## Build: Markdown → SQLite
`build_database.py` walks `*/*.md` files and builds/updates `tils.db`:
- Extracts post `title` from the first line (`# Heading`).
- Stores raw Markdown as `body`, and renders to HTML via GitHub’s Markdown API (respecting `MARKDOWN_GITHUB_TOKEN` if provided to avoid rate limits).
- Derives `path` (primary key) as a slug: original path with `/` replaced by `_` (e.g. `AWS/AWS_lightsale.md` → `AWS_AWS_lightsale.md`).
- Captures `topic` from the directory name, plus `created`/`updated` timestamps from the Git history.
- Computes a `summary` from the first HTML paragraph.
- Enables FTS on `title` and `body` with Porter stemming.

Rebuild locally:
- Ensure a virtualenv with `requirements.txt` (or run inside your dev container).
- `python build_database.py` — regenerates `tils.db` in-place.

Notes:
- Rendering uses GitHub API. Set `MARKDOWN_GITHUB_TOKEN` to reduce errors/rate limits.
- If a post’s Markdown changes, the script re-renders the HTML.

## Serving the site
Two main options:

1) Local Datasette (dev):
- `datasette serve tils.db -m metadata.yml --template-dir templates`
- Visit `http://localhost:8001` (or as configured).

2) Docker (prod-like):
- `Dockerfile` installs only runtime deps from `requirements.web.txt` and copies `tils.db`, templates, pages, and `metadata.yml`.
- Build and run:
  - `docker build -t til_dev .`
  - `docker run -p 8000:8000 til_dev`

## Templates and customizations
- Table view (`templates/table-tils-til.html`):
  - Displays title, topic, created date, summary.
  - Default sort is newest first (`created_utc` desc) unless the user chooses another sort.
  - Search form: disables empty `_search`/`topic` params on submit to avoid FTS errors.
  - Topic filter: a dropdown populated client-side by querying the database JSON API.
  - Row links: primary keys use tilde-encoding for dots (`.` → `~2E`) to match Datasette’s routing.

- Row view (`templates/row-tils-til.html`):
  - Displays a single post’s title, meta, and rendered HTML.
  - Uses `rows[0]` (Datasette passes a list named `rows` for the selected record).
  - Slightly reduced typography for better readability.

- Base layout (`templates/_base.html`):
  - PicoCSS for simple styling.
  - Navigation to index, all posts, and Atom feed.

- Landing page (`pages/index.html`):
  - Uses `datasette-template-sql` blocks to show topics with counts and per-topic latest posts.
  - Note: The per-post links here may need tilde-encoding for special characters in PKs; see “URL encoding” below.

## URL encoding for row pages
Datasette uses tilde-encoding for path segments in row URLs. For example:
- `AWS_lightsale.md` becomes `AWS_lightsale~2Emd` in the URL.

We handle this in the table template by replacing `.` with `~2E` when constructing row links. If you add posts with additional special characters, consider a more complete tilde-encoding step (see the Datasette guide) or switch to generating row URLs using `urls.row()` from Datasette.

## Atom feed
Configured in `metadata.yml` via `datasette-atom`. It selects latest posts from the `til` table and orders by `created_utc`.

## Common tasks
- Add a new post: drop a Markdown file into a topic folder (e.g., `AWS/`). Run `build_database.py` to update `tils.db`.
- Adjust site title/description: edit `metadata.yml`.
- Change styling/layout: edit `templates/_base.html` and the other templates.
- Ship a new build: run `build_database.py`, then rebuild the Docker image.

## Known quirks and tips
- Blank search queries can cause FTS errors. We prevent those by disabling empty form fields before submit.
- Jinja async calls (`await sql(...)`) can fail depending on environment. We populate the topic dropdown client-side using the database JSON API to avoid those issues.
- Row template context: use `rows[0]`, not `row` — Datasette’s RowView provides a list.
- Index page links may need tilde-encoding for `.` to match row routes.

## Extending this project
- Add new fields to posts (e.g., tags) by extending `build_database.py` and re-running.
- Add more pages using `pages/` and the `datasette-template-sql` plugin.
- Customize search and filtering with additional form fields and SQL facets.

