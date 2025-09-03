from bs4 import BeautifulSoup
from datetime import timezone, datetime
import httpx
import git
import os
import pathlib
from urllib.parse import urlencode, urlparse
import sqlite_utils
from sqlite_utils.db import NotFoundError
import time

root = pathlib.Path(__file__).parent.resolve()


def first_paragraph_text_only(html):
    soup = BeautifulSoup(html, "html.parser")
    return " ".join(soup.find("p").stripped_strings)


def created_changed_times(repo_path, ref=None):
    created_changed_times = {}
    try:
        repo = git.Repo(repo_path, odbt=git.GitDB)
    except Exception:
        return created_changed_times

    # Determine a valid revision to walk
    rev_candidates = []
    if ref:
        rev_candidates.append(ref)
    try:
        rev_candidates.append(repo.active_branch.name)
    except Exception:
        pass
    rev_candidates.extend(["main", "master", "HEAD"])

    commits = None
    for candidate in rev_candidates:
        try:
            commits = reversed(list(repo.iter_commits(candidate)))
            break
        except Exception:
            continue

    if commits is None:
        return created_changed_times

    for commit in commits:
        dt = commit.committed_datetime
        affected_files = list(commit.stats.files.keys())
        for filepath in affected_files:
            if filepath not in created_changed_times:
                created_changed_times[filepath] = {
                    "created": dt.isoformat(),
                    "created_utc": dt.astimezone(timezone.utc).isoformat(),
                }
            created_changed_times[filepath].update(
                {
                    "updated": dt.isoformat(),
                    "updated_utc": dt.astimezone(timezone.utc).isoformat(),
                }
            )
    return created_changed_times


def detect_branch(repo_path):
    try:
        repo = git.Repo(repo_path, odbt=git.GitDB)
    except Exception:
        return "main"
    try:
        return repo.active_branch.name
    except Exception:
        for candidate in ("main", "master"):
            try:
                repo.rev_parse(candidate)
                return candidate
            except Exception:
                continue
        return "main"

def _normalize_remote_to_https(remote_url: str) -> str:
    # Convert URLs like git@github.com:user/repo.git to https://github.com/user/repo
    if remote_url.startswith("git@"):
        host_and_path = remote_url.split("@", 1)[1]
        host, path = host_and_path.split(":", 1)
        if path.endswith(".git"):
            path = path[:-4]
        return f"https://{host}/{path}"
    # Trim .git from https remotes
    if remote_url.startswith("http://") or remote_url.startswith("https://"):
        if remote_url.endswith(".git"):
            return remote_url[:-4]
    return remote_url


def compute_file_url(repo_path, branch: str, path: str) -> str:
    base = "https://git.gvoserver1.com/jnellis/Today-I-Learned"
    try:
        repo = git.Repo(repo_path, odbt=git.GitDB)
        remote_url = None
        if repo.remotes:
            try:
                remote_url = next((r.url for r in repo.remotes if r.name == "origin"), None) or repo.remotes[0].url
            except Exception:
                pass
        if remote_url:
            https_url = _normalize_remote_to_https(remote_url)
            parsed = urlparse(https_url)
            base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            # base ends with /owner/repo
            if "github.com" in parsed.netloc:
                return f"{base}/blob/{branch}/{path}"
            else:
                # Assume Gitea-like
                return f"{base}/src/branch/{branch}/{path}"
    except Exception:
        pass
    # Fallback
    return f"{base}/src/branch/{branch}/{path}"


def build_database(repo_path):
    all_times = created_changed_times(repo_path)
    default_now = datetime.now(timezone.utc)
    default_times = {
        "created": default_now.isoformat(),
        "created_utc": default_now.isoformat(),
        "updated": default_now.isoformat(),
        "updated_utc": default_now.isoformat(),
    }
    branch = detect_branch(repo_path)
    db = sqlite_utils.Database(repo_path / "tils.db")
    table = db.table("til", pk="path")
    # Recursively include markdown in any subfolder; skip root-level files like README.md
    for filepath in root.rglob("*.md"):
        if filepath.parent == root:
            continue
        fp = filepath.open()
        title = fp.readline().lstrip("#").strip()
        body = fp.read().strip()
        path = str(filepath.relative_to(root))
        slug = filepath.stem
        url = compute_file_url(repo_path, branch, path)
        # Do we need to render the markdown?
        path_slug = path.replace("/", "_")
        try:
            row = table.get(path_slug)
            previous_body = row["body"]
            previous_html = row["html"]
        except (NotFoundError, KeyError):
            previous_body = None
            previous_html = None
        record = {
            "path": path_slug,
            "slug": slug,
            "topic": path.split("/")[0],
            "title": title,
            "url": url,
            "body": body,
        }
        if (body != previous_body) or not previous_html:
            retries = 0
            response = None
            while retries < 3:
                headers = {}
                if os.environ.get("MARKDOWN_GITHUB_TOKEN"):
                    headers = {
                        "authorization": "Bearer {}".format(
                            os.environ["MARKDOWN_GITHUB_TOKEN"]
                        )
                    }
                response = httpx.post(
                    "https://api.github.com/markdown",
                    json={
                        # mode=gfm would expand #13 issue links and suchlike
                        "mode": "markdown",
                        "text": body,
                    },
                    headers=headers,
                )
                if response.status_code == 200:
                    record["html"] = response.text
                    print("Rendered HTML for {}".format(path))
                    break
                elif response.status_code == 401:
                    assert False, "401 Unauthorized error rendering markdown"
                else:
                    print(response.status_code, response.headers)
                    print("  sleeping 60s")
                    time.sleep(60)
                    retries += 1
            else:
                assert False, "Could not render {} - last response was {}".format(
                    path, response.headers
                )
        # Populate summary
        record["summary"] = first_paragraph_text_only(
            record.get("html") or previous_html or ""
        )
        record.update(all_times.get(path, default_times))
        with db.conn:
            table.upsert(record, alter=True)

    table.enable_fts(
        ["title", "body"], tokenize="porter", create_triggers=True, replace=True
    )


if __name__ == "__main__":
    build_database(root)
