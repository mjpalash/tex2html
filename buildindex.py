#!/usr/bin/env python3
import pathlib
import configparser
import html as pyhtml
import re
from datetime import datetime
from typing import Optional, List


# ----------------------------------------------------------
# Load config (same as Script A & B)
# ----------------------------------------------------------
def load_config() -> str:
    cfg_path = pathlib.Path("texpub.cfg")
    if not cfg_path.exists():
        raise SystemExit("ERROR: texpub.cfg not found. Run Script A first.")

    config = configparser.ConfigParser()
    config.read(cfg_path)

    if "github" not in config or "repo_path" not in config["github"]:
        raise SystemExit("ERROR: texpub.cfg missing [github]/repo_path")

    repo_path = config["github"]["repo_path"].strip()
    return repo_path


# ----------------------------------------------------------
# HTML parsing helpers
# ----------------------------------------------------------
def strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def prettify(stem: str) -> str:
    s = stem.replace("_", " ").replace("-", " ")
    return " ".join(w.capitalize() for w in s.split())


def extract_title(html_text: str, fallback: str) -> str:
    m = re.search(r"<title>(.*?)</title>", html_text, re.IGNORECASE | re.DOTALL)
    if not m:
        m = re.search(r"<h1[^>]*>(.*?)</h1>", html_text, re.IGNORECASE | re.DOTALL)
    if not m:
        return fallback
    return strip_tags(m.group(1)).strip() or fallback


def extract_excerpt(html_text: str, max_words: int = 20) -> str:
    m = re.search(r"<p[^>]*>(.*?)</p>", html_text, re.IGNORECASE | re.DOTALL)
    if not m:
        return ""
    text = strip_tags(m.group(1))
    words = text.split()
    if len(words) <= max_words:
        return " ".join(words)
    return " ".join(words[:max_words]) + "…"


def extract_image(html_text: str, article_rel: str) -> Optional[str]:
    """
    Extract first <img src="..."> and rewrite relative path
    so it works from repo_root/index.html
    """
    m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html_text, re.IGNORECASE)
    if not m:
        return None
    src = m.group(1).strip()

    # absolute URLs and data URLs are fine
    if src.startswith(("http://", "https://", "//", "data:")):
        return src

    # Already prefixed path
    if src.startswith("articles/"):
        return src

    # src relative to the article dir → prefix it
    return f"{article_rel}/{src.lstrip('./')}"


def format_date(index_file: pathlib.Path) -> str:
    dt = datetime.fromtimestamp(index_file.stat().st_mtime)
    return dt.strftime("%B %d, %Y")


# ----------------------------------------------------------
# MAIN
# ----------------------------------------------------------
def main():
    repo_root = pathlib.Path(load_config())     # e.g., /Users/mkumar/code/latex-web
    articles_dir = repo_root / "articles"

    if not articles_dir.exists():
        raise SystemExit(f"ERROR: articles directory not found at {articles_dir}")

    template_path = repo_root / "index.template.html"
    if not template_path.exists():
        raise SystemExit(f"ERROR: index.template.html not found at {template_path}")

    output_path = repo_root / "index.html"

    # Find article folders
    folders = []
    for folder in articles_dir.iterdir():
        if folder.is_dir():
            index_file = folder / "index.html"
            if index_file.exists():
                folders.append((folder, index_file))

    # Sort newest first
    folders.sort(key=lambda f: f[1].stat().st_mtime, reverse=True)

    items: List[str] = []

    for folder, index_file in folders:
        raw = index_file.read_text(encoding="utf-8", errors="ignore")
        fallback_title = prettify(folder.name)

        title = extract_title(raw, fallback_title)
        excerpt = extract_excerpt(raw)
        date_str = format_date(index_file)

        article_rel = f"articles/{folder.name}"
        img_src = extract_image(raw, article_rel)

        # link to the article folder → index.html auto-serves
        href = article_rel + "/"

        title_html = pyhtml.escape(title)
        excerpt_html = pyhtml.escape(excerpt)

        if img_src:
            img_block = (
                f'<div class="post-image-wrap">'
                f'<img src="{pyhtml.escape(img_src)}" alt="{title_html}" loading="lazy" />'
                f'</div>'
            )
        else:
            img_block = '<div class="post-image-wrap post-image-placeholder"></div>'

        card = f"""
        <li class="post-card">
          <a class="post-card-link" href="{href}">
            {img_block}
            <div class="post-body">
              <h2 class="post-title">{title_html}</h2>
              <div class="post-meta">{date_str}</div>
              <p class="post-excerpt">{excerpt_html}</p>
              <span class="post-read-more">Read more</span>
            </div>
          </a>
        </li>
        """
        items.append(card)

    # Build page
    if items:
        summary = f"{len(items)} articles"
        content_html = "\n".join(items)
    else:
        summary = "No articles yet."
        content_html = """
        <li class="post-card">
          <div class="post-card-link">
            <div class="post-body">
              <h2 class="post-title">No articles found</h2>
              <p class="post-excerpt">Add folders inside <code>articles/</code> and run build_index.py.</p>
            </div>
          </div>
        </li>
        """

    template = template_path.read_text(encoding="utf-8")
    template = template.replace("{{ARTICLE_SUMMARY}}", summary)
    template = template.replace("<!-- ARTICLE_LIST -->", content_html)

    output_path.write_text(template, encoding="utf-8")
    print(f"✓ Generated {output_path} with {summary}")


if __name__ == "__main__":
    main()
