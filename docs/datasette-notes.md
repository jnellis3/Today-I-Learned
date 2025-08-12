# Datasette: Patterns, Tips, and Gotchas

This project uses [Datasette](https://datasette.io/) to serve a generated SQLite database as a website. These notes capture practical guidance for building and reusing Datasette-backed sites.

## Core concepts
- Tables and rows are rendered with Jinja templates. Datasette looks for override templates with names like `table-<db>-<table>.html` and `row-<db>-<table>.html`.
- A global `metadata.yml` configures site metadata and plugins.
- Plugins extend Datasette. Here we use:
  - `datasette-atom` to expose an Atom feed.
  - `datasette-template-sql` to execute SQL blocks within templates in the `pages/` directory.

## Useful URLs and helpers
- `{{ urls.database(database) }}` → `/<db>`
- `{{ urls.table(database, table) }}` → `/<db>/<table>`
- `{{ urls.row(database, table, row_path) }}` → row URL (you must pass the encoded PK path — see encoding below).
- `{{ urls.database(database, format='json') }}` → JSON API endpoint for running SQL queries via `?sql=...` (be mindful of settings).

## Row URL encoding (tilde-encoding)
Datasette encodes special characters in URL segments using “tilde-encoding”. Examples:
- `/` → `~2F`
- `.` → `~2E`
- `%` → `~25`
- `~` → `~7E`

When constructing row URLs yourself, ensure PK values are tilde-encoded. Options:
- Prefer Datasette helpers where possible:
  - Build the PK path with `path_from_row_pks()` (server-side utility) and pass it to `urls.row(...)` in view code.
- In templates without those helpers, minimally replace `.` with `~2E` for filenames like `*.md`. For a fully robust approach, expose a `tilde_encode` filter from a tiny plugin, or generate links server-side.

## Template contexts: row vs rows
- Table views provide `rows` (a list of dict-like rows) and other pagination/filter variables.
- Row views provide `rows` too, but it’s the single selected record as a list — use `rows[0]` in templates, not `row`.

## Searching with FTS
- Datasette’s table view can integrate with FTS if the table has an FTS virtual table.
- Avoid submitting an empty `_search=` string. For FTS5, `match ''` can cause a syntax error. Client-side validation to strip empty inputs is sufficient.

## Async in Jinja templates
- Datasette enables async Jinja, and the `datasette-template-sql` plugin can provide an async `sql()` function inside templates.
- In some environments (e.g., slim Docker images), inline `await` in control structures can conflict with the Jinja parser. If you hit template syntax errors like “expected token … got …”, consider:
  - Using `pages/` with `{% sql %}…{% endsql %}` blocks (works well for content pages).
  - Moving data-loading to client-side via the JSON API (as we did for the Topic dropdown), or into a server-side plugin/view.

## Overriding templates cleanly
- Place overrides in `templates/` and pass `--template-dir` when running Datasette.
- Filenames follow:
  - Table: `table-<db>-<table>.html` (e.g., `table-tils-til.html`).
  - Row: `row-<db>-<table>.html`.
  - Fallbacks: `table.html`, `row.html` in Datasette’s defaults.

## Pages directory
- With `datasette-template-sql`, any file in `pages/` can extend templates and run SQL blocks using:
  ```
  {% sql %}
  select ... from ...
  {% endsql %}
  {% for row in sql_rows %}
    ...
  {% endfor %}
  ```
- These are served at `/-/pages/<name>`.

## Feeds
- `datasette-atom` can expose queries as Atom feeds. Configure in `metadata.yml`:
  - Provide a title, base URL, and one or more named queries that return `title`, `url`, `datetime`, and `summary`.

## Deployment tips
- Keep the runtime image slim: install only what’s needed to serve (`requirements.web.txt`).
- Bake the SQLite database into the image (or mount it) and point `datasette serve` at it.
- Expose port and run with `--host 0.0.0.0`.

## Patterns to reuse
- “Markdown → SQLite → Datasette” pipeline for lightweight blogs, notes, or docs.
- Custom table/row templates for simple CMS-like rendering.
- `pages/` for hub pages, dashboards, or category indexes.
- Client-side enhancements calling the DB JSON API for dynamic UI pieces.

## Pitfalls encountered in this project
- Row links: needed tilde-encoding for `.` in `*.md` filenames — otherwise row pages 404.
- Row page context: used `rows[0]` instead of `row` to avoid `UndefinedError: 'row' is undefined`.
- Empty FTS searches: submitting `_search=` empty caused FTS5 syntax errors — prevented via client-side form sanitation.
- Jinja async `await` in Docker: inline awaits inside loop expressions caused syntax errors — replaced with a client-side fetch for topics.

## Next-level customizations
- Add a tiny plugin to expose `tilde_encode` as a Jinja filter to fix links everywhere.
- Add counts to topic dropdown via `select topic, count(*) ...` and render in options.
- Add tag support with a join table and FTS tokens.
- Use `datasette-hashed-urls` if you need hashed asset URLs.

