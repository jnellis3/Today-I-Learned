from __future__ import annotations

from xml.sax.saxutils import escape as xml_escape

try:
    from datasette import Response, hookimpl
except Exception:  # pragma: no cover - allow importing without datasette installed
    Response = None

    def hookimpl(*args, **kwargs):
        def decorator(fn):
            return fn

        return decorator


def render_rss(metadata: dict, rows: list[dict]) -> str:
    title = xml_escape((metadata.get("title") or "Today I Learned"))
    link = xml_escape(metadata.get("source_url") or "")
    description = xml_escape(metadata.get("description") or "")

    items = []
    for row in rows:
        item_title = xml_escape(row.get("title") or "")
        item_link = xml_escape(row.get("url") or "")
        item_guid = item_link
        item_date = xml_escape(row.get("created_utc") or "")
        item_summary = xml_escape(row.get("summary") or "")
        items.append(
            "\n".join(
                [
                    "    <item>",
                    f"      <title>{item_title}</title>",
                    f"      <link>{item_link}</link>",
                    f"      <guid>{item_guid}</guid>",
                    f"      <pubDate>{item_date}</pubDate>",
                    f"      <description>{item_summary}</description>",
                    "    </item>",
                ]
            )
        )

    items_xml = "\n".join(items)
    return "\n".join(
        [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<rss version="2.0">',
            "  <channel>",
            f"    <title>{title}</title>",
            f"    <link>{link}</link>",
            f"    <description>{description}</description>",
            items_xml,
            "  </channel>",
            "</rss>",
        ]
    )


def _tilde_encode(value: str) -> str:
    return (
        value.replace("~", "~7E")
        .replace("%", "~25")
        .replace("/", "~2F")
        .replace(".", "~2E")
    )


@hookimpl
def register_routes():
    return [
        ("/-/rss.xml", rss_view),
    ]


async def rss_view(request, datasette):
    db = datasette.databases.get("tils")
    if db is None:
        db = next(iter(datasette.databases.values()))

    result = await db.execute(
        """
        select title,
               summary,
               created_utc,
               [path]
        from til
        order by datetime(created_utc) desc
        limit 50
        """
    )
    rows = [dict(zip(result.columns, row)) for row in result.rows]
    for row in rows:
        row["url"] = "/tils/til/" + _tilde_encode(row.get("path") or "")

    metadata = datasette.metadata()
    content = render_rss(metadata, rows)
    return Response(content, content_type="application/rss+xml; charset=utf-8")
