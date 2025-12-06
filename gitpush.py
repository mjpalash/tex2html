#!/usr/bin/env python3
"""
Script C: Git add/commit/push for the GitHub Pages repo used by tex-html workflow.

Steps:
1. Read texpub.cfg to get repo_path (and optionally push_mode).
2. Show repo_path and current git status summary.
3. If there are no changes, exit.
4. Ask for a commit message (default: "Publish updates").
5. Confirm and then run: git add ., git commit, git push origin main.
"""

import configparser
import subprocess
import sys
from pathlib import Path
from typing import Optional

CONFIG_FILENAME = "texpub.cfg"


def load_config(config_path: Path) -> configparser.ConfigParser:
    if not config_path.is_file():
        print(f"Error: config file '{config_path}' not found. Run Script A first.")
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(config_path)

    if "github" not in config or "repo_path" not in config["github"]:
        print("Error: [github].repo_path missing in config.")
        sys.exit(1)

    return config


def prompt_yes_no(message: str, default: Optional[bool] = None) -> bool:
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


def repo_status(repo_path: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(repo_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
    except FileNotFoundError:
        print("Error: git not found. Please install git and ensure it is in your PATH.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error: git status failed with exit code {e.returncode}.")
        print(result.stderr)
        sys.exit(1)

    return result.stdout


def main() -> int:
    print("=== Git publish for tex-html workflow (Script C) ===")

    config_path = Path.cwd() / CONFIG_FILENAME
    config = load_config(config_path)

    repo_path = Path(config["github"]["repo_path"]).expanduser().resolve()
    push_mode = config["publish"]["push_mode"].strip().lower() if "publish" in config and "push_mode" in config["publish"] else "ask"

    print(f"\nRepo path: {repo_path}")
    print(f"Configured push_mode (from texpub.cfg): {push_mode}")

    if not repo_path.is_dir():
        print(f"Error: repo_path '{repo_path}' does not exist or is not a directory.")
        return 1

    if not prompt_yes_no("Use this repository for git operations?", default=True):
        print("Aborting as per user choice.")
        return 0

    print("\nGit status (short):")
    status = repo_status(repo_path)
    if status.strip() == "":
        print("  Working tree clean. No changes to commit.")
        return 0
    else:
        print(status)

    default_msg = "Publish updates"
    msg = input(f"\nCommit message [{default_msg}]: ").strip()
    if not msg:
        msg = default_msg

    if not prompt_yes_no(f"Proceed with 'git add .', 'git commit -m \"{msg}\"', and 'git push origin main'?", default=True):
        print("Aborting as per user choice.")
        return 0

    try:
        print("\nRunning: git add .")
        subprocess.run(["git", "add", "."], cwd=str(repo_path), check=True)

        print(f"Running: git commit -m \"{msg}\"")
        subprocess.run(["git", "commit", "-m", msg], cwd=str(repo_path), check=True)

        print("Running: git push origin main")
        subprocess.run(["git", "push", "origin", "main"], cwd=str(repo_path), check=True)

    except subprocess.CalledProcessError as e:
        print(f"Error: git command failed with exit code {e.returncode}.")
        return 1

    print("\nGit publish complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
