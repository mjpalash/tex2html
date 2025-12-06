#!/usr/bin/env python3
"""
Script A: One-time setup for LaTeX → HTML → GitHub Pages publishing.

Creates/overwrites a texpub.cfg file with:
- [github] repo_path
- [publish] push_mode  (yes / no / ask)
"""

import os
import sys
import configparser
from pathlib import Path


CONFIG_FILENAME = "texpub.cfg"


def prompt_repo_path() -> str:
    while True:
        repo_path = input("Enter the local path to your GitHub Pages repo: ").strip()
        if not repo_path:
            print("Path cannot be empty. Please enter a valid directory path.")
            continue

        repo_path = os.path.expanduser(repo_path)
        repo_path = os.path.abspath(repo_path)

        if not os.path.isdir(repo_path):
            print(f"Warning: '{repo_path}' does not exist or is not a directory.")
            choice = input("Use this path anyway? (y/n) [n]: ").strip().lower()
            if choice == "" or choice == "n":
                continue

        return repo_path


def prompt_push_mode() -> str:
    valid_modes = {"yes", "no", "ask"}
    default_mode = "ask"

    while True:
        answer = input("Auto-push changes? (yes / no / ask) [ask]: ").strip().lower()
        if answer == "":
            return default_mode
        if answer in valid_modes:
            return answer
        print("Invalid choice. Please enter 'yes', 'no', or 'ask'.")


def write_config(repo_path: str, push_mode: str, config_path: Path) -> None:
    config = configparser.ConfigParser()

    config["github"] = {
        "repo_path": repo_path,
    }

    config["publish"] = {
        "push_mode": push_mode,
    }

    with config_path.open("w", encoding="utf-8") as f:
        config.write(f)


def main() -> int:
    print("=== LaTeX → GitHub Pages setup (Script A) ===")

    # 1. Ask for repo path
    repo_path = prompt_repo_path()

    # 2. Ask for push behavior
    push_mode = prompt_push_mode()

    # 3. Write config file to current working directory
    config_path = Path(os.getcwd()) / CONFIG_FILENAME
    write_config(repo_path, push_mode, config_path)

    print("\nConfiguration saved to:", config_path)
    print("Values:")
    print(f"  repo_path = {repo_path}")
    print(f"  push_mode = {push_mode}")
    print("\nYou can re-run this script anytime to update these settings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
