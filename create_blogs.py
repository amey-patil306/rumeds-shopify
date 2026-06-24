import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SHOP = os.environ.get("SHOPIFY_STORE", "wagyxq-cj.myshopify.com")
BLOGS_DIR = ROOT / "blogs"
BLOG_HANDLE = "doctors-lounge"
BLOG_TITLE = "Doctor's Lounge"
SHOPIFY_CLI = shutil.which("shopify.cmd") or shutil.which("shopify") or "shopify"

QUERY_LIST_BLOGS = """
query {
  blogs(first: 20) {
    nodes { id title handle }
  }
}
"""

QUERY_BLOG_ARTICLES = """
query($id: ID!, $cursor: String) {
  blog(id: $id) {
    articles(first: 100, after: $cursor) {
      pageInfo { hasNextPage endCursor }
      nodes { title }
    }
  }
}
"""

MUTATION_BLOG_CREATE = """
mutation blogCreate($blog: BlogCreateInput!) {
  blogCreate(blog: $blog) {
    blog { id handle }
    userErrors { field message }
  }
}
"""

MUTATION_ARTICLE_CREATE = """
mutation articleCreate($article: ArticleCreateInput!) {
  articleCreate(article: $article) {
    article { id title handle }
    userErrors { field message }
  }
}
"""


def shopify_gql(query, variables=None):
    with tempfile.NamedTemporaryFile("w", suffix=".graphql", delete=False, encoding="utf-8") as f:
        f.write(query.strip())
        query_file = f.name

    var_file = None
    if variables:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(variables, f)
            var_file = f.name

    cmd = [
        SHOPIFY_CLI,
        "store",
        "execute",
        "--store",
        SHOP,
        "--query-file",
        query_file,
        "--allow-mutations",
        "-j",
    ]
    if var_file:
        cmd.extend(["--variable-file", var_file])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    finally:
        os.unlink(query_file)
        if var_file:
            os.unlink(var_file)

    if result.returncode != 0:
        print(result.stderr or result.stdout)
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(result.stdout)
        return None


def md_to_html(md):
    md = re.sub(r"^## (.+)$", r"<h2>\1</h2>", md, flags=re.MULTILINE)
    md = re.sub(r"^### (.+)$", r"<h3>\1</h3>", md, flags=re.MULTILINE)
    md = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", md)
    lines, result, in_list = md.split("\n"), [], False
    for line in lines:
        m = re.match(r"^\d+\.\s+(.+)$", line)
        if m:
            if not in_list:
                result.append("<ol>")
                in_list = True
            result.append(f"<li>{m.group(1)}</li>")
        else:
            if in_list:
                result.append("</ol>")
                in_list = False
            s = line.strip()
            if s and not s.startswith("<h"):
                result.append(f"<p>{s}</p>")
            elif s:
                result.append(s)
    if in_list:
        result.append("</ol>")
    return "\n".join(result)


def slugify(title):
    s = title.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def parse_post(path):
    content = path.read_text(encoding="utf-8")
    title_m = re.search(r"^# (.+)$", content, re.MULTILINE)
    title = title_m.group(1).strip() if title_m else path.stem
    tags_m = re.search(r"\*\*Tags:\*\*\s*(.+)", content)
    tags_raw = tags_m.group(1).strip() if tags_m else "Scrubs, Medical Apparel, Doctors"
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
    author_m = re.search(r"\*\*Author:\*\*\s*(.+)", content)
    author = author_m.group(1).strip() if author_m else "Rumeds Team"
    meta_m = re.search(r"\*\*Meta Description:\*\*\s*(.+)", content)
    summary = meta_m.group(1).strip() if meta_m else ""

    body = re.sub(r"^# .+$", "", content, count=1, flags=re.MULTILINE)
    for pat in [
        r"\*\*Meta Description:\*\*.*$",
        r"\*\*Tags:\*\*.*$",
        r"\*\*Author:\*\*.*$",
        r"^\-{3,}$",
    ]:
        body = re.sub(pat, "", body, flags=re.MULTILINE)
    body = re.sub(r"\*\(Note to Admin:.*?\)\*", "", body, flags=re.DOTALL).strip()

    return {
        "title": title,
        "author": author,
        "tags": tags,
        "summary": summary,
        "body_html": md_to_html(body),
        "handle": slugify(title),
    }


def get_or_create_blog():
    data = shopify_gql(QUERY_LIST_BLOGS)
    if not data:
        return None

    for blog in data.get("blogs", {}).get("nodes", []):
        if blog.get("handle") == BLOG_HANDLE or "doctor" in blog.get("title", "").lower():
            return blog["id"]

    print("Creating Doctor's Lounge blog...")
    created = shopify_gql(
        MUTATION_BLOG_CREATE,
        {"blog": {"title": BLOG_TITLE, "handle": BLOG_HANDLE}},
    )
    if not created:
        return None
    result = created.get("blogCreate", {})
    errors = result.get("userErrors", [])
    if errors:
        print(errors)
        return None
    return result.get("blog", {}).get("id")


def fetch_existing_titles(blog_id):
    titles = set()
    cursor = None
    while True:
        data = shopify_gql(QUERY_BLOG_ARTICLES, {"id": blog_id, "cursor": cursor})
        if not data:
            break
        articles = data.get("blog", {}).get("articles", {})
        for node in articles.get("nodes", []):
            titles.add(node["title"].strip().lower())
        page = articles.get("pageInfo", {})
        if not page.get("hasNextPage"):
            break
        cursor = page.get("endCursor")
    return titles


def create_article(blog_id, post):
    variables = {
        "article": {
            "blogId": blog_id,
            "title": post["title"],
            "handle": post["handle"],
            "author": {"name": post["author"]},
            "tags": post["tags"],
            "body": post["body_html"],
            "isPublished": True,
        }
    }
    if post["summary"]:
        variables["article"]["summary"] = post["summary"]

    data = shopify_gql(MUTATION_ARTICLE_CREATE, variables)
    if not data:
        return False
    result = data.get("articleCreate", {})
    errors = result.get("userErrors", [])
    if errors:
        print(f"    {errors}")
        return False
    return bool(result.get("article"))


def main():
    dry_run = "--dry-run" in sys.argv

    if not BLOGS_DIR.is_dir():
        print(f"Blog folder not found: {BLOGS_DIR}")
        sys.exit(1)

    files = sorted({p.resolve() for p in BLOGS_DIR.glob("*.md")})
    print(f"Store: {SHOP}")
    print(f"Found {len(files)} posts")

    if dry_run:
        for path in files:
            print(f"  [DRY] {parse_post(path)['title']}")
        return

    blog_id = get_or_create_blog()
    if not blog_id:
        print("Failed to find or create blog. Run: shopify store auth --store wagyxq-cj.myshopify.com --scopes read_content,write_content")
        sys.exit(1)
    print(f"Blog ID: {blog_id}")

    existing = fetch_existing_titles(blog_id)
    created = skipped = failed = 0

    for path in sorted(files):
        post = parse_post(path)
        if post["title"].strip().lower() in existing:
            print(f"  [SKIP] {post['title']}")
            skipped += 1
            continue
        if create_article(blog_id, post):
            print(f"  [OK] {post['title']}")
            created += 1
            existing.add(post["title"].strip().lower())
        else:
            print(f"  [FAIL] {post['title']}")
            failed += 1

    print(f"\nDone: {created} created, {skipped} skipped, {failed} failed")
    print("Visit: https://rumeds.myshopify.com/blogs/doctors-lounge")


if __name__ == "__main__":
    main()
