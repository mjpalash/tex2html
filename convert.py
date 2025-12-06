#!/usr/bin/env python3
"""
Script B: Publish a LaTeX article into the GitHub Pages repo (files only).

Steps:
1. Read texpub.cfg (created by Script A). Show settings and ask to continue.
2. Ask for main .tex file (Overleaf project root).
3. Ask for output HTML base name (default = input tex basename).
4. Run pandoc with:
   - all .bib files in the parent folder
   - --mathjax
   - --standalone
   - --citeproc
   - a common HTML template
5. Create articles/<output-name>/ in the GitHub repo (with overwrite prompt).
6. Copy HTML as index.html into that folder.
7. Copy all image-like files from the project, preserving folder structure.

Git add/commit/push is **not** done here anymore.
"""

import configparser
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, List

CONFIG_FILENAME = "texpub.cfg"

# Adjust this to point to your shared template.
# By default, it expects a file "article_template.html" in the same directory as this script.
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_TEMPLATE_PATH = SCRIPT_DIR / "article_template.html"

# File extensions treated as "images" to copy over.
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf"}


def load_config(config_path: Path) -> configparser.ConfigParser:
    if not config_path.is_file():
        print(f"Error: config file '{config_path}' not found. "
              f"Run Script A to create it.")
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(config_path)

    if "github" not in config:
        print("Error: 'github' section missing in config.")
        sys.exit(1)

    if "repo_path" not in config["github"]:
        print("Error: 'repo_path' missing in [github] section.")
        sys.exit(1)

    # publish.push_mode may exist but is not used here anymore
    return config


def prompt_yes_no(message: str, default: Optional[bool] = None) -> bool:
    """
    Ask a yes/no question.

    default=True  -> [y] default
    default=False -> [n] default
    default=None  -> no default (must type y/n)
    """
    while True:
        if default is True:
            prompt = " (y/n) [y]: "
        elif default is False:
            prompt = " (y/n) [n]: "
        else:
            prompt = " (y/n): "

        ans = input(message + prompt).strip().lower()

        if ans == "" and default is not None:
            return default
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False

        print("Please enter 'y' or 'n'.")


def choose_main_tex() -> Path:
    while True:
        path_str = input("Enter path to main .tex file: ").strip()
        if not path_str:
            print("Main .tex path cannot be empty.")
            continue

        tex_path = Path(path_str).expanduser().resolve()
        if not tex_path.is_file() or tex_path.suffix.lower() != ".tex":
            print(f"'{tex_path}' is not a .tex file. Please enter a valid file path.")
            continue

        return tex_path


def choose_output_name(tex_path: Path) -> str:
    default_name = tex_path.stem
    ans = input(f"Output file name (without .html) [{default_name}]: ").strip()
    if not ans:
        return default_name
    return ans


def find_bib_files(parent_folder: Path) -> List[Path]:
    return sorted(parent_folder.glob("*.bib"))


def run_pandoc(
    parent_folder: Path,
    tex_file: Path,
    output_name: str,
    bib_files: List[Path],
    template_path: Path,
) -> Path:
    if not template_path.is_file():
        print(f"Error: template file not found at '{template_path}'.")
        sys.exit(1)

    output_html = parent_folder / f"{output_name}.html"

    cmd = [
        "pandoc",
        tex_file.name,
        "--from=latex",
        "--to=html5",
        "--standalone",
        "--mathjax",
        "--citeproc",
        "--template",
        str(template_path),
        "-o",
        output_html.name,
    ]

    for bib in bib_files:
        cmd.extend(["--bibliography", bib.name])

    print("\nRunning pandoc:")
    print(" ", " ".join(cmd))

    try:
        subprocess.run(cmd, check=True, cwd=str(parent_folder))
    except FileNotFoundError:
        print("Error: pandoc not found. Please install pandoc and ensure it is in your PATH.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error: pandoc failed with exit code {e.returncode}.")
        sys.exit(1)

    if not output_html.is_file():
        print(f"Error: expected output HTML '{output_html}' was not created.")
        sys.exit(1)

    return output_html


def ensure_articles_folder(repo_path: Path) -> Path:
    articles_root = repo_path / "articles"
    if not articles_root.exists():
        print(f"'articles' folder not found under repo. Creating: {articles_root}")
        articles_root.mkdir(parents=True, exist_ok=True)
    return articles_root


def prepare_article_folder(articles_root: Path, output_name: str) -> Path:
    article_folder = articles_root / output_name

    if article_folder.exists():
        print(f"\nTarget folder already exists: {article_folder}")
        overwrite = prompt_yes_no("Overwrite this folder?", default=True)
        if not overwrite:
            print("Aborting as per user choice.")
            sys.exit(0)
        # Remove and recreate to avoid stale files
        shutil.rmtree(article_folder)

    article_folder.mkdir(parents=True, exist_ok=True)
    return article_folder


def copy_html_as_index(output_html: Path, article_folder: Path) -> None:
    dest_html = article_folder / "index.html"
    print(f"\nCopying HTML to {dest_html}")
    shutil.copy2(output_html, dest_html)


def copy_images(parent_folder: Path, article_folder: Path) -> None:
    print("\nCopying image files (preserving structure)...")

    parent_folder = parent_folder.resolve()
    for root, dirs, files in os.walk(parent_folder):
        root_path = Path(root)
        for fname in files:
            src = root_path / fname
            ext = src.suffix.lower()
            if ext not in IMAGE_EXTENSIONS:
                continue

            rel_path = src.relative_to(parent_folder)
            dest = article_folder / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)

    print("Image copy complete.")


def main() -> int:
    print("=== LaTeX → GitHub Pages publishing (Script B: files only) ===")

    # 1. Read config
    config_path = Path(os.getcwd()) / CONFIG_FILENAME
    config = load_config(config_path)

    repo_path = Path(config["github"]["repo_path"]).expanduser().resolve()
    push_mode = config["publish"]["push_mode"].strip().lower() if "publish" in config and "push_mode" in config["publish"] else "(unused)"

    print("\nCurrent configuration:")
    print(f"  repo_path = {repo_path}")
    print(f"  push_mode = {push_mode}  (note: push_mode is not used by this script)")

    if not prompt_yes_no("Continue with these settings?", default=True):
        print("Aborting as per user choice.")
        return 0

    if not repo_path.is_dir():
        print(f"Error: repo_path '{repo_path}' does not exist or is not a directory.")
        return 1

    # 2. Ask for main .tex file
    tex_path = choose_main_tex()
    parent_folder = tex_path.parent

    # 3. Ask for output base name
    output_name = choose_output_name(tex_path)

    # 4. Run pandoc
    bib_files = find_bib_files(parent_folder)
    if bib_files:
        print("\nFound bibliography files:")
        for bib in bib_files:
            print(" ", bib.name)
    else:
        print("\nNo .bib files found in parent folder. Proceeding without bibliographies.")

    template_path = DEFAULT_TEMPLATE_PATH
    print(f"\nUsing template: {template_path}")

    output_html = run_pandoc(
        parent_folder=parent_folder,
        tex_file=tex_path,
        output_name=output_name,
        bib_files=bib_files,
        template_path=template_path,
    )

    # 5. Prepare article folder in repo
    articles_root = ensure_articles_folder(repo_path)
    article_folder = prepare_article_folder(articles_root, output_name)

    # 6. Copy HTML + images
    copy_html_as_index(output_html, article_folder)
    copy_images(parent_folder, article_folder)

    print(f"\nArticle prepared at: {article_folder}")
    # print("NOTE: Git add/commit/push is now handled by a separate script.")
    # print("      Run git_publish_texpub.py to push changes if desired.\n")

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
